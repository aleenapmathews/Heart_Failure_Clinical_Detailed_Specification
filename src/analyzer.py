import numpy as np
import pandas as pd
class CardioRiskProfiler:
    BIOMARKERS = ('Oldpeak', 'MaxHR', 'Age')
    def __init__(self):
        self.df = None

    def load_from_csv(self, path):
        df = pd.read_csv(path)
        median = df[df['Cholesterol'] > 0]['Cholesterol'].median()
        df['chol_was_zero'] = df['Cholesterol'] == 0
        df['cholesterol_imputed'] = df['Cholesterol'].where(df['Cholesterol'] > 0, median)
        self.df = df
        return self

    
    def get_groups(self, biomarker):
        sick = self.df.loc[self.df['HeartDisease'] == 1, biomarker].to_numpy()
        well = self.df.loc[self.df['HeartDisease'] == 0, biomarker].to_numpy()
        return sick, well
    
    def compute_cohens_d(self, biomarker):
        sick, well = self.get_groups(biomarker)
        mean_sick = np.mean(sick)
        mean_well = np.mean(well)
        variance_sick = np.var(sick, ddof=1)
        variance_well = np.var(well, ddof=1)
        n1 = len(sick)
        n2 = len(well)
        pooled_std = np.sqrt(((n1 - 1) * variance_sick + (n2 - 1) * variance_well)/ (n1 + n2 - 2))
        d = (mean_sick - mean_well) / pooled_std
        return d
    
    def verify_cohens_d(self, biomarker):
        sick, well = self.get_groups(biomarker)
        mean_sick = sum(sick) / len(sick)
        mean_well = sum(well) / len(well)
        var_sick = sum((x - mean_sick) ** 2 for x in sick) / (len(sick) - 1)
        var_well = sum((x - mean_well) ** 2 for x in well) / (len(well) - 1)
        n1 = len(sick)
        n2 = len(well)
        pooled_std = (((n1 - 1) * var_sick + (n2 - 1) * var_well)
            / (n1 + n2 - 2)) ** 0.5
        d = (mean_sick - mean_well) / pooled_std
        return d
    
    def check_cohens_d(self):
        for biomarker in ['Oldpeak', 'MaxHR', 'Age']:
            numpy_d = self.compute_cohens_d(biomarker)
            verified_d = self.verify_cohens_d(biomarker)
            if not np.allclose(numpy_d, verified_d):
                return False
        return True


    def high_risk_masks(self):
        oldpeak_cut = 2.0
        oldpeak_values = self.df['Oldpeak'].to_numpy()
        angina = (self.df['ExerciseAngina'] == 'Y').to_numpy()
        asy = (self.df['ChestPainType'] == 'ASY').to_numpy()
        high = (oldpeak_values > oldpeak_cut) & angina
        overlap = high & asy
        high_not_asy = high & (~asy)
        return { 'high_risk': np.sum(high),'asy': np.sum(asy),
            'overlap': np.sum(overlap) ,
            'high_not_asy': np.sum(high_not_asy) }


    def ols_disease_model(self):
        y = self.df['HeartDisease'].to_numpy()
        X = np.column_stack([np.ones(len(y)),self.df['Oldpeak'],self.df['MaxHR'] ,
            self.df['Age']])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        prediction_error = ((y - X @ beta) ** 2).sum()
        total_sum_of_squares = ((y - y.mean()) ** 2).sum()
        r2 = 1 - prediction_error / total_sum_of_squares if total_sum_of_squares else float('nan')
        std_w = beta[1:] * X[:, 1:].std(axis=0) / y.std()
        return beta, r2, dict(zip(['Oldpeak', 'MaxHR', 'Age'], std_w))
    
    def chest_pain_audit(self):
        d = self.df
        pain_type_counts = d.groupby('ChestPainType').agg(patients=('HeartDisease', 'size'),
            disease_rate=('HeartDisease', 'mean'),zero_chol=('chol_was_zero', 'sum') )
        counts = d['ChestPainType'].value_counts()
        raw_c_corr = d['Cholesterol'].corr(d['HeartDisease'])
        imputed_c_corr = d['cholesterol_imputed'].corr(d['HeartDisease'])
        return pain_type_counts, counts, raw_c_corr, imputed_c_corr

    def prevalence_pivot(self):
        d = self.df.assign(
            age_range=pd.cut(self.df['Age'],[40, 50, 60, np.inf],right=False,
            labels=['40-50', '50-60', '60+']),
            hr_range = pd.cut(self.df['MaxHR'],[0, 120, 150, np.inf],right=False,
            labels=['Low', 'Normal', 'High']))

        return d.pivot_table( index='age_range', columns='hr_range',
            values='HeartDisease',aggfunc='mean' , 
             margins=True, observed=False )
    
    def top_risk_profiles(self):
        wide_format = self.df[['RestingBP', 'cholesterol_imputed', 'MaxHR', 'Oldpeak']]
        long_format = wide_format.melt(var_name ='Biomarker', value_name ='value')
        long_format['severity'] = 0.0
        for biomarker in long_format['Biomarker'].unique():
            biomarkervalues = long_format.loc[long_format['Biomarker'] == biomarker, 'value']
            severity = (biomarkervalues - biomarkervalues.mean()) / biomarkervalues.std(ddof=0)
            if biomarker == 'MaxHR':
                severity = -severity
            rows = long_format['Biomarker'] == biomarker
            long_format.loc[rows, 'severity'] = severity
        top_risk_index = long_format.groupby('Biomarker')['severity'].nlargest(5)
        return long_format.loc[top_risk_index.index.get_level_values(1)]
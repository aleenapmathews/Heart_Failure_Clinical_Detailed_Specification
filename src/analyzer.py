import numpy as np
import pandas as pd
class CardioRiskProfiler:
    BIOMARKERS = ('Oldpeak', 'MaxHR', 'Age', 'RestingBP', 'cholesterol_imputed')
    def __init__(self):
        self.df = None
    def load_from_csv(self, path):
        df = pd.read_csv(path)
        median = df.loc[df['Cholesterol'] > 0, 'Cholesterol'].median()
        df['chol_was_zero'] = df['Cholesterol'] == 0
        df['cholesterol_imputed'] = df['Cholesterol'].where(df['Cholesterol'] > 0, median)
        self.df = df
        return self
    def _cohorts(self, biomarker):
        if biomarker not in self.BIOMARKERS:
            raise ValueError(f'unknown biomarker {biomarker!r}; choose from {self.BIOMARKERS}')
        sick = self.df.loc[self.df['HeartDisease'] == 1, biomarker].to_numpy(dtype=float)
        well = self.df.loc[self.df['HeartDisease'] == 0, biomarker].to_numpy(dtype=float)
        return sick, well
    def compute_cohens_d(self, biomarker='Oldpeak'):
        '''Q3/Q4: Cohen's d = (mean_disease - mean_normal) / pooled std.'''
        sick, well = self._cohorts(biomarker)
        n1, n2 = len(sick), len(well)
        pooled = np.sqrt(((n1 - 1) * np.var(sick, ddof=1) + (n2 - 1) * np.var(well, ddof=1))
        / (n1 + n2 - 2))
        return (sick.mean() - well.mean()) / pooled
    def summary_report(self):
        return (f"Patients: {len(self.df)} | Disease rate: {self.df['HeartDisease'].mean():.1%} | "
        f"Zero-cholesterol imputed: {int(self.df['chol_was_zero'].sum())}")


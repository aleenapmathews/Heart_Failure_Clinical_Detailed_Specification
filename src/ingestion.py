import csv
import statistics
from datetime import datetime
cols=['Age','Sex','ChestPainType','RestingBP','Cholesterol','FastingBS','RestingECG','MaxHR','ExerciseAngina','Oldpeak','ST_Slope','HeartDisease']
int_cols=['Age','RestingBP','Cholesterol','FastingBS','MaxHR','HeartDisease']
categories={
    'Sex':{'M','F'},
    'ChestPainType':{'TA','ATA','NAP','ASY'},
    'RestingECG':{'Normal','ST','LVH'},
    'ExerciseAngina':{'Y','N'},
    'ST_Slope':{'Up','Flat','Down'}
}

def parse_record(fields):
    if len(fields)!=len(cols):
        raise ValueError(f'Expected {len(cols)} fields, got {len(fields)}')
    row=dict(zip(cols,fields))
    for col,allowed in categories.items():
        if row[col] not in allowed:
            raise ValueError(f'Invalid value for {col}: {row[col]!r}')
    for col in int_cols:
        row[col]=int(row[col])
    row['Oldpeak']=float(row['Oldpeak'])
    if not 18<=row['Age']<=100:
        raise ValueError(f'Age {row["Age"]} out of range(18-100)')
    if not 50<=row['RestingBP']<=250:
        raise ValueError(f'RestingBP {row["RestingBP"]} out of range(50-250)')
    if row['Cholesterol']<0:
        raise ValueError('negative Cholesterol')
    return row

def ingest(path):
    clean,reject,flagged=[],[],[]
    try:
        f=open(path,'rb')
    except FileNotFoundError:
        raise FileNotFoundError(f'File not found: {path}') from None
    with f:
        f.readline()
        for line_no,raw in enumerate(f,start=2):
            try:
                line=raw.decode('utf-8').strip()
                row=parse_record(line.split(','))
            except UnicodeDecodeError:
                reject.append((line_no,'invalid encoding'))
            except ValueError as e:
                reject.append((line_no,str(e)))
            else:
                clean.append(row)
                if row['Cholesterol']==0:
                    flagged.append((line_no,'zero cholesterol (median-imputed later)'))
    return clean,reject,flagged


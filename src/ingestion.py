import csv
import statistics
from datetime import datetime
col=['Age','Sex','ChestPainType','RestingBP','Cholosterol','FastingBS','RestingECG','MaxHR','ExerciseAngina','Oldpeak','ST_Slope','HeartDisease']

def ingest(path):
    clean,reject=[],[]
    with open(path,encoding='utf-8') as f:
        next(f)
        for line_no,line in enumerate(f,start=2):
            row=dict(zip(col,line.strip().split(',')))
            bp=int(row['RestingBP'])
            if bp<50 or bp>250:
                reject.append((line_no,'RestingBP out of range'))
                continue
            clean.append(row)
    return clean,reject
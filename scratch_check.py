from src.ingestion import ingest, write_clean_csv, write_audit_log

clean, rejected, flagged = ingest('data/raw/heart_failure_clinical_raw.csv')
write_clean_csv(clean, 'data/processed/clean_heart_failure.csv')
write_audit_log(rejected, flagged, len(clean),
                'data/processed/cardio_clinical_audit.log')
print(f'clean={len(clean)} rejected={len(rejected)} flagged={len(flagged)}')
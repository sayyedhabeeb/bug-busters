import pandas as pd
import numpy as np
import os

p = os.path.join(os.getcwd(), 'feature_store', 'feature_matrix_enhanced.csv')
if not os.path.exists(p):
    print('Feature matrix not found at', p)
    raise SystemExit(1)

df = pd.read_csv(p)
print('File:', p)
print('Shape:', df.shape)
print('Missing total:', int(df.isnull().sum().sum()))
print('\nMissing by column (top 10):')
print(df.isnull().sum().sort_values(ascending=False).head(10))

# Numeric finiteness
num = df.select_dtypes(include=[np.number])
all_finite = np.isfinite(num).all().all() if not num.empty else True
print('\nAll numeric finite:', all_finite)

# Label distribution
label_cols = [c for c in df.columns if c.lower() in ('label','match')]
if label_cols:
    for c in label_cols:
        print('\nLabel column:', c)
        print(df[c].value_counts(dropna=False))
else:
    print('\nNo label column found')

# Basic stats for selected features
for f in ('tfidf_cosine','resume_len','job_len','shared_skills_count'):
    if f in df.columns:
        print(f"\n{f} stats:\n", df[f].describe())

# Quick sanity checks
if df.shape[0] == 0:
    print('\nERROR: Empty feature matrix')

# Save a tiny sample
sample_path = os.path.join(os.getcwd(), 'feature_store', 'feature_matrix_sample.csv')
df.head(10).to_csv(sample_path, index=False)
print('\nSaved sample to', sample_path)

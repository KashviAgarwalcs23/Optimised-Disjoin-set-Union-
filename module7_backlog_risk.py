import pandas as pd
import numpy as np

print("MODULE 7: Backlog Risk Analysis\n")

# Load inputs
profile = pd.read_csv('profile.csv')
academics = pd.read_csv('academics.csv')
friend_evo = pd.read_csv('friendship_evolution.csv')

# Prepare academic score
if '5thSemPercentage' in academics.columns:
    academics['5thSemPercentage'] = pd.to_numeric(academics['5thSemPercentage'], errors='coerce')
else:
    academics['5thSemPercentage'] = np.nan
if '6thSemPercentage' in academics.columns:
    academics['6thSemPercentage'] = pd.to_numeric(academics['6thSemPercentage'], errors='coerce')
else:
    academics['6thSemPercentage'] = np.nan

academics['AcademicScore'] = academics[['5thSemPercentage','6thSemPercentage']].mean(axis=1, skipna=True)
subj_cols = [c for c in academics.columns if c not in ['StudentID','Name','5thSemPercentage','6thSemPercentage','AcademicScore']]
academics['AcademicScore'] = academics['AcademicScore'].fillna(academics[subj_cols].apply(pd.to_numeric, errors='coerce').mean(axis=1, skipna=True))

# Merge dataframes
df = profile.merge(academics[['StudentID','AcademicScore']], on='StudentID', how='left')
df = df.merge(friend_evo[['StudentID','Stability','Growth','OriginalFriends','NewFriends','LostFriends']], on='StudentID', how='left')

# Fill missing values
df['AcademicScore'] = df['AcademicScore'].fillna(df['AcademicScore'].mean())
df['Stability'] = df['Stability'].fillna(0.0)
df['Growth'] = df['Growth'].fillna(0.0)
df['Backlog'] = pd.to_numeric(df['Backlog'], errors='coerce').fillna(0)

# Normalization helper
def minmax(series):
    if series.max()==series.min():
        return pd.Series(0.5, index=series.index)
    return (series - series.min())/(series.max()-series.min())

# Feature normals
df['A_norm'] = minmax(df['AcademicScore'])
# Higher backlog -> higher risk; normalize
df['B_norm'] = minmax(df['Backlog'])
# Stability: lower stability -> higher risk
df['S_norm'] = minmax(df['Stability'])
# Growth: lower growth -> higher risk
df['G_norm'] = minmax(df['Growth'])

# Risk model weights (tunable)
w_acad = 0.5    # academic performance
w_backlog = 0.3 # existing backlog
w_social = 0.15 # stability
w_growth = 0.05 # growth

# Compute raw risk: low academic increases risk, so use (1 - A_norm)
df['RiskRaw'] = w_acad*(1 - df['A_norm']) + w_backlog*df['B_norm'] + w_social*(1 - df['S_norm']) + w_growth*(1 - df['G_norm'])

# Account for dropout history: if Dropout2nd/3rd flagged, boost risk
df['DropoutFactor'] = 1 + 0.5*pd.to_numeric(df['Dropout2nd'], errors='coerce').fillna(0) + 0.7*pd.to_numeric(df['Dropout3rd'], errors='coerce').fillna(0)
df['RiskRaw'] = df['RiskRaw'] * df['DropoutFactor']

# Normalize final risk to 0-1
df['RiskScore'] = minmax(df['RiskRaw'])

# Risk category
def category(r):
    if r>=0.7: return 'High'
    if r>=0.4: return 'Medium'
    return 'Low'

df['RiskCategory'] = df['RiskScore'].apply(category)

# Save full risk file
out_cols = ['StudentID','Name','Gender','Locality','LateralEntry','Backlog','Dropout2nd','Dropout3rd','AcademicScore','Stability','Growth','RiskScore','RiskCategory']

df_out = df[out_cols]
df_out.to_csv('module7_backlog_risk.csv', index=False)
print('Saved module7_backlog_risk.csv')

# Save top at-risk students
top = df_out.sort_values('RiskScore', ascending=False).head(50)
top.to_csv('module7_top_at_risk.csv', index=False)
print('Saved module7_top_at_risk.csv')

# Print quick summary
print('\nTop 10 at-risk students:')
print(top.head(10).to_string(index=False))

print('\nMODULE 7 complete.')

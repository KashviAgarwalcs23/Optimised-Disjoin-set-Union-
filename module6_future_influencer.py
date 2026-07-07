import pandas as pd
import numpy as np
from collections import defaultdict

print("MODULE 6: Future Influencer Prediction\n")

# Load data
academics = pd.read_csv('academics.csv')
friend_evo = pd.read_csv('friendship_evolution.csv')
friendships = pd.read_csv('friendships.csv')

# Build academic score: average of 5th and 6th sem percentages
if '5thSemPercentage' in academics.columns:
    academics['5thSemPercentage'] = pd.to_numeric(academics['5thSemPercentage'], errors='coerce')
else:
    academics['5thSemPercentage'] = np.nan
if '6thSemPercentage' in academics.columns:
    academics['6thSemPercentage'] = pd.to_numeric(academics['6thSemPercentage'], errors='coerce')
else:
    academics['6thSemPercentage'] = np.nan

academics['AcademicScore'] = academics[['5thSemPercentage','6thSemPercentage']].mean(axis=1, skipna=True)
# If both NaN, fallback to mean of subject columns
if academics['AcademicScore'].isna().any():
    subj_cols = [c for c in academics.columns if c not in ['StudentID','Name','5thSemPercentage','6thSemPercentage','AcademicScore']]
    academics['AcademicScore'] = academics['AcademicScore'].fillna(academics[subj_cols].apply(pd.to_numeric, errors='coerce').mean(axis=1, skipna=True))

# Merge with friendship evolution
df = academics[['StudentID','Name','AcademicScore']].merge(friend_evo, on='StudentID', how='left')

# Fill missing social metrics
df['Stability'] = df['Stability'].fillna(0.0)
df['Growth'] = df['Growth'].fillna(0.0)

# Normalise columns (min-max)
def minmax(s):
    if s.max()==s.min():
        return pd.Series([0.5]*len(s), index=s.index)
    return (s - s.min())/(s.max()-s.min())

df['A_norm'] = minmax(df['AcademicScore'].fillna(df['AcademicScore'].mean()))
df['S_norm'] = minmax(df['Stability'])
df['G_norm'] = minmax(df['Growth'])

# Influencer score weights
w_acad = 0.6
w_stab = 0.3
w_growth = 0.1

df['InfluencerScore'] = w_acad*df['A_norm'] + w_stab*df['S_norm'] + w_growth*df['G_norm']

# Rebuild DSU for community mapping
class DSU:
    def __init__(self, n):
        self.parent = list(range(n+1))
        self.rank = [0]*(n+1)
    def find(self,x):
        if self.parent[x]!=x:
            self.parent[x]=self.find(self.parent[x])
        return self.parent[x]
    def union(self,x,y):
        px,py = self.find(x),self.find(y)
        if px==py: return
        if self.rank[px]<self.rank[py]: px,py = py,px
        self.parent[py]=px
        if self.rank[px]==self.rank[py]: self.rank[px]+=1

max_id = int(friendships['StudentID'].max())
dsu = DSU(max_id)
# friend columns
friends_cols = [f'Friends{i}' for i in range(1,10) if f'Friends{i}' in friendships.columns]
for _, row in friendships.iterrows():
    sid = int(row['StudentID'])
    for c in friends_cols:
        val = row.get(c)
        if pd.notna(val) and str(val).strip()!='':
            try:
                fid = int(val)
                if 1<=fid<=max_id:
                    dsu.union(sid,fid)
            except:
                pass

# Map community
df['CommunityRoot'] = df['StudentID'].apply(lambda x: dsu.find(int(x)) if not pd.isna(x) else None)

# Global rank
df['GlobalRank'] = df['InfluencerScore'].rank(method='dense', ascending=False).astype(int)

# Rank within community
df['CommunityRank'] = df.groupby('CommunityRoot')['InfluencerScore'].rank(method='dense', ascending=False).astype(int)

# Save outputs
df_out = df[['StudentID','Name','CommunityRoot','AcademicScore','Stability','Growth','InfluencerScore','CommunityRank','GlobalRank']]
df_out.to_csv('module6_influencer_scores.csv', index=False)
print('Saved influencer scores to module6_influencer_scores.csv')

# Top 5 per community
top_rows = df_out.sort_values(['CommunityRoot','InfluencerScore'], ascending=[True, False]).groupby('CommunityRoot').head(5)
top_rows.to_csv('module6_top_influencers.csv', index=False)
print('Saved top influencers per community to module6_top_influencers.csv')

# Print quick summary
print('\nTop 10 global influencers:')
print(df_out.sort_values('InfluencerScore', ascending=False).head(10))

print('\nMODULE 6 complete.')

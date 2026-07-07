import pandas as pd
import numpy as np
from collections import defaultdict

print("MODULE 5: Friendship Evolution Analysis\n")

# Load friendships
friendships = pd.read_csv('friendships.csv')

# Columns pattern
friends_cols = [f'Friends{i}' for i in range(1,10) if f'Friends{i}' in friendships.columns]
new_cols = [f'NewFriends{i}' for i in range(1,13) if f'NewFriends{i}' in friendships.columns]
lost_cols = [f'LostFriends{i}' for i in range(1,6) if f'LostFriends{i}' in friendships.columns]

print(f"Found columns - friends: {len(friends_cols)}, new: {len(new_cols)}, lost: {len(lost_cols)}")

records = []

for _, row in friendships.iterrows():
    sid = int(row['StudentID'])
    # count original friends
    orig = 0
    for c in friends_cols:
        if pd.notna(row.get(c)) and str(row.get(c)).strip()!='':
            try:
                int(row.get(c))
                orig += 1
            except:
                pass
    # count new friends
    newf = 0
    for c in new_cols:
        if pd.notna(row.get(c)) and str(row.get(c)).strip()!='':
            try:
                int(row.get(c))
                newf += 1
            except:
                pass
    # count lost friends
    lost = 0
    for c in lost_cols:
        if pd.notna(row.get(c)) and str(row.get(c)).strip()!='':
            try:
                int(row.get(c))
                lost += 1
            except:
                pass
    remaining = max(orig - lost, 0)
    growth = newf - lost
    stability = remaining / orig if orig>0 else np.nan
    records.append({
        'StudentID': sid,
        'OriginalFriends': orig,
        'NewFriends': newf,
        'LostFriends': lost,
        'RemainingFriends': remaining,
        'Growth': growth,
        'Stability': stability
    })

out_df = pd.DataFrame(records)
out_df.to_csv('friendship_evolution.csv', index=False)
print('Saved per-student friendship evolution to friendship_evolution.csv')

# Build DSU communities again for aggregation
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

# Group students by root
communities = defaultdict(list)
for sid in friendships['StudentID']:
    sid = int(sid)
    r = dsu.find(sid)
    communities[r].append(sid)

# Aggregate per community
comm_records = []
for root, members in communities.items():
    subset = out_df[out_df['StudentID'].isin(members)]
    if subset.empty: continue
    comm_records.append({
        'CommunityRoot': root,
        'Members': len(members),
        'AvgOriginalFriends': subset['OriginalFriends'].mean(),
        'AvgNewFriends': subset['NewFriends'].mean(),
        'AvgLostFriends': subset['LostFriends'].mean(),
        'AvgGrowth': subset['Growth'].mean(),
        'AvgStability': subset['Stability'].mean()
    })

comm_df = pd.DataFrame(comm_records)
comm_df.to_csv('community_friendship_evolution.csv', index=False)
print('Saved community-level friendship evolution to community_friendship_evolution.csv')

# Print summary
print('\nTop 5 students by Growth (new - lost):')
print(out_df.sort_values('Growth', ascending=False).head(5))

print('\nTop 5 communities by AvgGrowth:')
print(comm_df.sort_values('AvgGrowth', ascending=False).head(5))

print('\nMODULE 5 complete.')

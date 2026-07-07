import pandas as pd
import numpy as np
from collections import defaultdict

print('EVALUATION METRICS: Community stats, recommendation coverage, influencer distribution')

# Load data
friends = pd.read_csv('friendships.csv')
rec_top1 = pd.read_csv('module8_recommendations_top1.csv')
infl = pd.read_csv('module6_influencer_scores.csv')
comm_exp = pd.read_csv('community_experts.csv') if pd.io.common.file_exists('community_experts.csv') else pd.DataFrame()

# Build DSU
class DSU:
    def __init__(self,n):
        self.parent=list(range(n+1))
        self.rank=[0]*(n+1)
    def find(self,x):
        if self.parent[x]!=x:
            self.parent[x]=self.find(self.parent[x])
        return self.parent[x]
    def union(self,x,y):
        px,py=self.find(x),self.find(y)
        if px==py: return
        if self.rank[px]<self.rank[py]: px,py=py,px
        self.parent[py]=px
        if self.rank[px]==self.rank[py]: self.rank[px]+=1

max_id = int(friends['StudentID'].max())
dsu = DSU(max_id)
friend_cols = [f'Friends{i}' for i in range(1,10) if f'Friends{i}' in friends.columns]
for _,r in friends.iterrows():
    sid=int(r['StudentID'])
    for c in friend_cols:
        v=r.get(c)
        if pd.notna(v) and str(v).strip()!='':
            try:
                fid=int(v)
                if 1<=fid<=max_id:
                    dsu.union(sid,fid)
            except:
                pass

# community groups
groups=defaultdict(list)
for sid in friends['StudentID']:
    sid=int(sid)
    groups[dsu.find(sid)].append(sid)

num_students = len(friends)
num_communities = len(groups)
sizes = [len(m) for m in groups.values()]
largest = max(sizes)
smallest = min(sizes)
avg_size = sum(sizes)/len(sizes)

comm_stats = pd.DataFrame([{
    'TotalStudents':num_students,
    'CommunitiesFound':num_communities,
    'LargestCommunity':largest,
    'SmallestCommunity':smallest,
    'AverageCommunitySize':round(avg_size,2)
}])
comm_stats.to_csv('evaluation_community_stats.csv', index=False)
print('Saved evaluation_community_stats.csv')

# Recommendation coverage
# rec_top1 has CandidateType column from module8
coverage = rec_top1['CandidateType'].value_counts().rename_axis('Source').reset_index(name='Count')
coverage['Percent'] = (coverage['Count']/coverage['Count'].sum()*100).round(2)
coverage.to_csv('evaluation_recommendation_coverage.csv', index=False)
print('Saved evaluation_recommendation_coverage.csv')

# Influencer distribution
infl_stats = {}
infl_stats['Top10'] = infl.sort_values('InfluencerScore', ascending=False).head(10)[['StudentID','Name','InfluencerScore']]
infl_stats['AverageInfluencerScore'] = infl['InfluencerScore'].mean()
infl_stats['HighestInfluencerScore'] = infl['InfluencerScore'].max()
# save
infl_stats['Top10'].to_csv('evaluation_top10_influencers.csv', index=False)
with open('evaluation_influencer_summary.txt','w') as f:
    f.write(f"AverageInfluencerScore,{infl_stats['AverageInfluencerScore']}\n")
    f.write(f"HighestInfluencerScore,{infl_stats['HighestInfluencerScore']}\n")
print('Saved evaluation_top10_influencers.csv and evaluation_influencer_summary.txt')

# Community expert verification samples: pick up to 5 communities and check top subject matches
verification = []
if not comm_exp.empty:
    sample_comms = comm_exp['Community'].unique()[:5]
    acad = pd.read_csv('academics.csv').set_index('StudentID')
    for comm in sample_comms:
        subset = comm_exp[comm_exp['Community']==comm]
        for _,row in subset.iterrows():
            subj = row['Subject']
            expert_id = int(row['ExpertID'])
            max_score_in_comm = None
            # find members of community
            members = groups.get(comm, [])
            scores = []
            for m in members:
                try:
                    sc = float(pd.to_numeric(acad.loc[m][subj], errors='coerce'))
                    scores.append((m,sc))
                except:
                    pass
            if scores:
                top = max(scores, key=lambda x: (np.nan_to_num(x[1],-1), x[0]))
                verification.append({'Community':comm,'Subject':subj,'ExpertID':expert_id,'ExpertScore':row['Score'],'TopInCommunityID':top[0],'TopScore':top[1]})
    pd.DataFrame(verification).to_csv('evaluation_community_expert_verification.csv', index=False)
    print('Saved evaluation_community_expert_verification.csv')
else:
    print('No community_experts.csv found — skipping verification sample')

print('\nEVALUATION METRICS complete.')

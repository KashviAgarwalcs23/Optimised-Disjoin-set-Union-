import pandas as pd
import numpy as np
from collections import defaultdict

print("MODULE 8: Smart Recommendation Engine\n")

# Load inputs
academics = pd.read_csv('academics.csv')
friends_df = pd.read_csv('friendships.csv')
community_experts = pd.read_csv('community_experts.csv') if pd.io.common.file_exists('community_experts.csv') else pd.DataFrame()
global_mentors = pd.read_csv('global_mentors_top5.csv') if pd.io.common.file_exists('global_mentors_top5.csv') else pd.DataFrame()
influencers = pd.read_csv('module6_influencer_scores.csv') if pd.io.common.file_exists('module6_influencer_scores.csv') else pd.DataFrame()
risk = pd.read_csv('module7_backlog_risk.csv') if pd.io.common.file_exists('module7_backlog_risk.csv') else pd.DataFrame()

# Determine subject columns (exclude metadata)
exclude = {'StudentID','Name','5thSemPercentage','6thSemPercentage','AcademicScore'}
subject_cols = [c for c in academics.columns if c not in exclude]
# Filter out non-subject columns that are likely not scores by checking numeric conversion
numeric_subjects = []
for c in subject_cols:
    try:
        pd.to_numeric(academics[c], errors='coerce')
        numeric_subjects.append(c)
    except:
        pass
subjects = [c for c in numeric_subjects if c.strip()!='']
print(f"Detected {len(subjects)} subjects: {subjects[:8]}{'...' if len(subjects)>8 else ''}")

# Build DSU to get community mapping
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

max_id = int(friends_df['StudentID'].max())
dsu = DSU(max_id)
friend_cols = [f'Friends{i}' for i in range(1,10) if f'Friends{i}' in friends_df.columns]
for _, row in friends_df.iterrows():
    sid = int(row['StudentID'])
    for c in friend_cols:
        val = row.get(c)
        if pd.notna(val) and str(val).strip()!='':
            try:
                fid = int(val)
                if 1<=fid<=max_id:
                    dsu.union(sid,fid)
            except:
                pass

# community mapping
comm_map = {sid: dsu.find(int(sid)) for sid in friends_df['StudentID']}

# Precompute subject score norms per subject
subject_norm = {}
for subj in subjects:
    scores = pd.to_numeric(academics[subj], errors='coerce')
    if scores.max()==scores.min():
        subject_norm[subj] = (scores.fillna(scores.mean()).apply(lambda x:0.5))
    else:
        subject_norm[subj] = (scores - scores.min())/(scores.max()-scores.min())

# normalize influencer and risk
if not influencers.empty:
    influencers['InfluencerNorm'] = (influencers['InfluencerScore'] - influencers['InfluencerScore'].min())/(influencers['InfluencerScore'].max()-influencers['InfluencerScore'].min())
else:
    influencers['InfluencerNorm'] = []
if not risk.empty:
    risk['RiskNorm'] = (risk['RiskScore'] - risk['RiskScore'].min())/(risk['RiskScore'].max()-risk['RiskScore'].min())
else:
    risk['RiskNorm'] = []

# Helper maps
academics_map = academics.set_index('StudentID')
influ_map = influencers.set_index('StudentID') if not influencers.empty else pd.DataFrame()
risk_map = risk.set_index('StudentID') if not risk.empty else pd.DataFrame()

# community experts map: (community,subject)->expertID
comm_exp_map = {}
if not community_experts.empty:
    for _, r in community_experts.iterrows():
        try:
            comm = int(r.get('Community')) if 'Community' in r else int(r.get('CommunityRoot'))
        except:
            comm = None
        subj = r.get('Subject')
        eid = r.get('ExpertID') if 'ExpertID' in r else r.get('Expert')
        try:
            eid = int(eid)
        except:
            eid = None
        if comm is not None and subj and eid:
            comm_exp_map[(comm, subj)] = eid

# global mentors map: subject -> list of mentor IDs
global_map = defaultdict(list)
if not global_mentors.empty:
    for _, r in global_mentors.iterrows():
        subj = r.get('Subject')
        eid = r.get('ExpertID') if 'ExpertID' in r else r.get('Expert')
        try:
            eid = int(eid)
        except:
            eid = None
        if subj and eid:
            global_map[subj].append(eid)

# Friends map
each_friends = {}
for _, r in friends_df.iterrows():
    sid = int(r['StudentID'])
    lst = []
    for c in friend_cols:
        val = r.get(c)
        if pd.notna(val) and str(val).strip()!='':
            try:
                fid = int(val); lst.append(fid)
            except: pass
    each_friends[sid] = lst

# Scoring parameters
w_subj = 0.6
w_influ = 0.25
w_risk = 0.15

recommendations = []

students = list(academics['StudentID'])
for target in students:
    t_comm = comm_map.get(target, None)
    for subj in subjects:
        candidates = {}
        # community expert preferential
        if t_comm is not None and (t_comm, subj) in comm_exp_map:
            eid = comm_exp_map[(t_comm, subj)]
            if eid!=target:
                candidates[eid] = {'type':'community_expert'}
        # global mentors
        for eid in global_map.get(subj, [])[:5]:
            if eid!=target:
                candidates.setdefault(eid, {'type':'global_mentor'})
        # friends
        for fid in each_friends.get(target,[]):
            if fid!=target:
                candidates.setdefault(fid, {'type':'friend'})
        # ensure there is at least some candidates: fallback to global top 5
        if not candidates:
            for eid in global_map.get(subj, [])[:5]:
                if eid!=target:
                    candidates.setdefault(eid, {'type':'global_mentor'})
        # compute score
        scored = []
        for cid, meta in candidates.items():
            # subject score
            try:
                subj_series = subject_norm[subj]
                subj_score = subj_series.get(cid-1, np.nan) if hasattr(subj_series, 'get') else np.nan
                # subj_series index may be 0-based; try lookup by position
                if np.isnan(subj_score):
                    subj_score = float(pd.to_numeric(academics_map.loc[cid][subj], errors='coerce'))
                    # normalize fallback
                    subj_score = (subj_score - pd.to_numeric(academics[subj], errors='coerce').min())/(pd.to_numeric(academics[subj], errors='coerce').max()-pd.to_numeric(academics[subj], errors='coerce').min()) if pd.to_numeric(academics[subj], errors='coerce').max()!=pd.to_numeric(academics[subj], errors='coerce').min() else 0.5
            except Exception:
                subj_score = 0.5
            # influencer
            try:
                influ = influ_map.loc[cid]['InfluencerNorm'] if cid in influ_map.index else 0.5
            except:
                influ = 0.5
            # risk
            try:
                r = risk_map.loc[cid]['RiskNorm'] if cid in risk_map.index else 0.0
            except:
                r = 0.0
            final = w_subj*float(subj_score) + w_influ*float(influ) - w_risk*float(r)
            scored.append((cid, meta['type'], final, float(subj_score), float(influ), float(r)))
        # sort and pick top3
        scored.sort(key=lambda x: x[2], reverse=True)
        topk = scored[:3]
        for cid, ctype, final, subj_s, influ_s, r_s in topk:
            conf = 'High' if final>=0.7 else ('Medium' if final>=0.5 else 'Low')
            recommendations.append({'TargetID':target,'TargetName':academics_map.loc[target]['Name'],'Subject':subj,'CandidateID':cid,'CandidateName':academics_map.loc[cid]['Name'],'CandidateType':ctype,'FinalScore':round(final,4),'SubjectScore':round(subj_s,4),'InfluencerNorm':round(influ_s,4),'RiskNorm':round(r_s,4),'Confidence':conf})

# Save recommendations
rec_df = pd.DataFrame(recommendations)
rec_df.to_csv('module8_recommendations.csv', index=False)
print('Saved module8_recommendations.csv with', len(rec_df), 'rows')

# Save condensed top-1 per target-subject
top1 = rec_df.sort_values(['TargetID','Subject','FinalScore'], ascending=[True,True,False]).groupby(['TargetID','Subject']).first().reset_index()
top1.to_csv('module8_recommendations_top1.csv', index=False)
print('Saved module8_recommendations_top1.csv with', len(top1), 'rows')

print('\nMODULE 8 complete.')

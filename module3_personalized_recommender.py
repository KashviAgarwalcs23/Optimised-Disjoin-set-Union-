import pandas as pd
from collections import defaultdict

print("MODULE 3: Personalized Helper Recommendation\n")

# Load normalized data and module outputs
friendships = pd.read_csv('friendships.csv')
academics = pd.read_csv('academics.csv')
profile = pd.read_csv('profile.csv')
community_experts = pd.read_csv('community_experts.csv')

# Build DSU from friendships (Friends1-9)
class DSU:
    def __init__(self, n):
        self.parent = list(range(n+1))
        self.rank = [0]*(n+1)
    def find(self,x):
        if self.parent[x]!=x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self,x,y):
        px,py = self.find(x), self.find(y)
        if px==py: return
        if self.rank[px]<self.rank[py]: px,py = py,px
        self.parent[py]=px
        if self.rank[px]==self.rank[py]: self.rank[px]+=1

max_id = int(friendships['StudentID'].max())
dsu = DSU(max_id)

friends_map = defaultdict(list)
for _, row in friendships.iterrows():
    sid = int(row['StudentID'])
    for i in range(1,10):
        col = f'Friends{i}'
        if col in row and pd.notna(row[col]) and row[col]!='':
            try:
                fid = int(row[col])
                if 1 <= fid <= max_id:
                    dsu.union(sid, fid)
                    friends_map[sid].append(fid)
            except:
                pass

# Group communities and assign ranks same as module2 (by size desc)
communities = defaultdict(list)
for sid in friendships['StudentID']:
    sid = int(sid)
    root = dsu.find(sid)
    communities[root].append(sid)

sorted_comms = sorted([(r,len(m)) for r,m in communities.items()], key=lambda x: x[1], reverse=True)
root_to_rank = {root: idx+1 for idx, (root,_) in enumerate(sorted_comms)}
student_to_rank = {}
for root,members in communities.items():
    rank = root_to_rank[root]
    for s in members:
        student_to_rank[s] = rank

print(f"Detected {len(communities)} communities; using rank mapping for lookups\n")

# Helper: get academic score for student and subject
def get_score(student_id, subject):
    row = academics[academics['StudentID']==student_id]
    if row.empty: return None
    val = row.iloc[0].get(subject)
    try:
        if pd.isna(val) or val=='':
            return None
        return float(val)
    except:
        return None

# Recommendation function
def recommend(student_id, subject):
    student_id = int(student_id)
    # Determine student's community rank
    rank = student_to_rank.get(student_id)
    recommended = None
    reason = []

    if rank is not None:
        # Look up community expert for this subject
        expert_row = community_experts[
            (community_experts['Community']==rank) & (community_experts['Subject'].str.lower()==subject.lower())
        ]
        if not expert_row.empty:
            eid = int(expert_row.iloc[0]['ExpertID'])
            escore = float(expert_row.iloc[0]['Score'])
            recommended = (eid, escore, 'community_expert')
            reason.append('community expert')

    # If no community expert, fall back to best friend in subject
    if recommended is None:
        # check friends
        best_friend = None
        best_score = -1
        for f in friends_map.get(student_id,[]):
            s = get_score(f, subject)
            if s is not None and s > best_score:
                best_score = s
                best_friend = f
        if best_friend is not None:
            recommended = (best_friend, best_score, 'friend')
            reason.append('friend best score')

    # If still none, fallback to global best for subject
    if recommended is None:
        # search academics globally
        candidates = academics[['StudentID','Name',subject]].dropna(subset=[subject])
        if not candidates.empty:
            candidates['num'] = pd.to_numeric(candidates[subject], errors='coerce')
            candidates = candidates.dropna(subset=['num'])
            if not candidates.empty:
                top = candidates.sort_values('num', ascending=False).iloc[0]
                recommended = (int(top['StudentID']), float(top['num']), 'global')
                reason.append('global best')

    if recommended is None:
        return None

    # Compute confidence
    eid, escore, source = recommended
    if escore >= 85 and source=='community_expert':
        confidence = 'High'
    elif escore >= 80 and source in ('community_expert','friend'):
        confidence = 'Medium'
    else:
        confidence = 'Low'

    # Prepare output
    name_row = academics[academics['StudentID']==eid]
    name = name_row.iloc[0]['Name'] if not name_row.empty else 'Unknown'

    return {
        'StudentID': student_id,
        'Subject': subject,
        'RecommendedID': eid,
        'RecommendedName': name,
        'Score': escore,
        'Source': source,
        'Confidence': confidence,
        'CommunityRank': rank
    }

# Run quick demo recommendations
demo_cases = [ (1,'ML'), (1,'Java'), (30,'ML'), (96,'CSharp') ]
results = []
for sid, subj in demo_cases:
    rec = recommend(sid, subj)
    print(f"Request: Student {sid} needs help in {subj}")
    if rec:
        print(f"  → Recommend: Student {rec['RecommendedID']} ({rec['RecommendedName']}) | Score: {rec['Score']} | Source: {rec['Source']} | Confidence: {rec['Confidence']} | CommunityRank: {rec['CommunityRank']}\n")
        results.append(rec)
    else:
        print("  → No recommendation found.\n")

# Save recommendations
if results:
    pd.DataFrame(results).to_csv('recommendations_demo.csv', index=False)
    print("Saved demo recommendations to recommendations_demo.csv")
else:
    print("No recommendations to save.")

print("\nMODULE 3 complete (demo run).")

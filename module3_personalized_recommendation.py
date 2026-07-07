import pandas as pd
from collections import defaultdict

# Module 3: Personalized Helper Recommendation
# Loads normalized data, rebuilds communities, finds subject experts per community,
# and provides recommendation(s) for a given student and subject.

# Load data
friendships_df = pd.read_csv('friendships.csv')
academics_df = pd.read_csv('academics.csv')
profile_df = pd.read_csv('profile.csv')

# Build student lookup
student_names = dict(zip(academics_df['StudentID'], academics_df['Name']))

# Simple DSU implementation to recreate communities from friendships
class DSU:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.rank = [0] * (n + 1)
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

max_id = int(friendships_df['StudentID'].max())

dsu = DSU(max_id)

# Build friend adjacency for quick lookups
adj = defaultdict(list)
for _, row in friendships_df.iterrows():
    sid = int(row['StudentID'])
    for i in range(1, 10):
        col = f'Friends{i}'
        if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
            try:
                fid = int(row[col])
                if 1 <= fid <= max_id:
                    dsu.union(sid, fid)
                    adj[sid].append(fid)
            except:
                pass

# Group students by root
communities = defaultdict(list)
for _, row in friendships_df.iterrows():
    sid = int(row['StudentID'])
    root = dsu.find(sid)
    communities[root].append(sid)

# Subjects to consider
subjects_5th = ['Java', 'DBMS', 'DCN', 'WEP', 'DMG', 'AIN', 'PYP']
subjects_6th = ['SEOOD', 'CNS', 'EM', 'CSharp', 'SNA', 'VCS', 'ML', 'ParallelComputing']
all_subjects = subjects_5th + subjects_6th

# Build academic score lookup (as floats, NaN if missing)
acad_scores = {}
for _, row in academics_df.iterrows():
    sid = int(row['StudentID'])
    acad_scores[sid] = {}
    for subj in all_subjects + ['5thSemPercentage', '6thSemPercentage']:
        if subj in row:
            try:
                val = float(row[subj])
            except:
                val = float('nan')
            acad_scores[sid][subj] = val

# Compute community experts (subject -> (student, score)) by root
community_experts = {}
for root, members in communities.items():
    experts = {}
    for subj in all_subjects:
        best_sid = None
        best_score = -1
        for sid in members:
            if sid in acad_scores and subj in acad_scores[sid]:
                sc = acad_scores[sid].get(subj)
                if pd.notna(sc) and sc > best_score:
                    best_score = sc
                    best_sid = sid
        if best_sid is not None and best_score >= 0:
            experts[subj] = (best_sid, best_score)
    community_experts[root] = experts

# Recommendation logic

def confidence_label(score):
    if pd.isna(score):
        return 'Unknown'
    if score >= 85:
        return 'High'
    if score >= 70:
        return 'Medium'
    return 'Low'


def recommend_helper(student_id: int, subject: str, top_n: int = 3):
    """Return a list of recommended helpers for student_id for the requested subject.

    Strategy:
    1. Look for community expert in student's community.
    2. Look for best performing friend(s) in the subject.
    3. Fallback to best global students if community/friends missing.

    Returns list of dicts with keys: role, student_id, name, score, confidence, reason
    """
    if subject not in all_subjects:
        raise ValueError(f"Subject '{subject}' not recognized. Available: {all_subjects}")

    root = dsu.find(student_id)
    members = communities.get(root, [])

    recs = []

    # 1) Community expert
    expert = community_experts.get(root, {}).get(subject)
    if expert:
        esid, escore = expert
        recs.append({
            'role': 'Community Expert',
            'student_id': int(esid),
            'name': student_names.get(esid, 'Unknown'),
            'score': float(escore),
            'confidence': confidence_label(escore),
            'reason': 'Top scorer in community'
        })

    # 2) Best friend(s)
    friend_candidates = []
    for fid in adj.get(student_id, []):
        sc = acad_scores.get(fid, {}).get(subject, float('nan'))
        if pd.notna(sc):
            friend_candidates.append((fid, sc))
    friend_candidates.sort(key=lambda x: x[1], reverse=True)
    for fid, sc in friend_candidates[:top_n]:
        recs.append({
            'role': 'Friend',
            'student_id': int(fid),
            'name': student_names.get(fid, 'Unknown'),
            'score': float(sc),
            'confidence': confidence_label(sc),
            'reason': 'Direct friend with good score'
        })

    # 3) Global top performers (if still empty)
    if not recs:
        global_candidates = []
        for sid, subs in acad_scores.items():
            sc = subs.get(subject, float('nan'))
            if pd.notna(sc):
                global_candidates.append((sid, sc))
        global_candidates.sort(key=lambda x: x[1], reverse=True)
        for sid, sc in global_candidates[:top_n]:
            recs.append({
                'role': 'Global Top',
                'student_id': int(sid),
                'name': student_names.get(sid, 'Unknown'),
                'score': float(sc),
                'confidence': confidence_label(sc),
                'reason': 'Top performer across class'
            })

    return recs


# Demo: generate example recommendations for a few students
example_students = [1, 7, 18, 83]
example_subjects = ['ML', 'Java', 'DBMS']

rows = []
for sid in example_students:
    for subj in example_subjects:
        try:
            recs = recommend_helper(sid, subj, top_n=2)
        except ValueError:
            recs = []
        if recs:
            primary = recs[0]
            rows.append({
                'StudentID': sid,
                'Subject': subj,
                'RecommendedID': primary['student_id'],
                'RecommendedName': primary['name'],
                'Score': primary['score'],
                'Confidence': primary['confidence'],
                'Role': primary['role'],
                'Reason': primary['reason']
            })

rec_df = pd.DataFrame(rows)
rec_df.to_csv('recommendations_example.csv', index=False)
print('✓ recommendations_example.csv created with', len(rec_df), 'rows')

# Print the example recommendations
print('\nExample Recommendations:')
print(rec_df.to_string(index=False))

# CLI support
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Personalized helper recommendation')
    parser.add_argument('--student', type=int, help='Student ID requesting help')
    parser.add_argument('--subject', type=str, help='Subject name')
    args = parser.parse_args()
    if args.student and args.subject:
        try:
            recs = recommend_helper(args.student, args.subject, top_n=3)
            print('\nRecommendations for Student', args.student, 'Subject', args.subject)
            for r in recs:
                print(f"- {r['role']}: Student {r['student_id']} ({r['name']}) Score={r['score']} Confidence={r['confidence']} Reason={r['reason']}")
        except Exception as e:
            print('Error:', e)

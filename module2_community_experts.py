import pandas as pd
import numpy as np
from collections import defaultdict

# ============================================================
# MODULE 2: COMMUNITY SUBJECT EXPERTS
# ============================================================
# For every community detected by DSU:
# Find the best expert in each subject
#
# Example Output:
# Community 1
#   Java Expert: Student 7 (Score: 90)
#   DBMS Expert: Student 8 (Score: 92)
#   ML Expert: Student 18 (Score: 90)
# ============================================================

print("="*70)
print("MODULE 2: COMMUNITY SUBJECT EXPERTS")
print("="*70)

# Load data
friendships_df = pd.read_csv('friendships.csv')
academics_df = pd.read_csv('academics.csv')
profile_df = pd.read_csv('profile.csv')

print("\n✓ Loaded data:")
print(f"  - {len(friendships_df)} students")
print(f"  - {len(academics_df.columns)-2} academic subjects")

# ============================================================
# DISJOINT SET UNION (DSU) - Community Detection
# ============================================================

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

# Build DSU from friendships
max_student_id = int(friendships_df['StudentID'].max())
dsu = DSU(max_student_id)

print(f"\n✓ Building friendship graph (max student ID: {max_student_id})")

for idx, row in friendships_df.iterrows():
    student_id = int(row['StudentID'])
    
    # Union with all friends in Friends1-9
    for i in range(1, 10):
        friend_col = f'Friends{i}'
        if pd.notna(row[friend_col]) and row[friend_col] != '':
            try:
                friend_id = int(row[friend_col])
                if 1 <= friend_id <= max_student_id:
                    dsu.union(student_id, friend_id)
            except:
                pass

# Group students by community
communities = defaultdict(list)
for idx, row in friendships_df.iterrows():
    student_id = int(row['StudentID'])
    root = dsu.find(student_id)
    communities[root].append(student_id)

print(f"✓ Detected {len(communities)} communities")

# ============================================================
# FIND SUBJECT EXPERTS PER COMMUNITY
# ============================================================

# Define all subjects
subjects_5th = ['Java', 'DBMS', 'DCN', 'WEP', 'DMG', 'AIN', 'PYP']
subjects_6th = ['SEOOD', 'CNS', 'EM', 'CSharp', 'SNA', 'VCS', 'ML', 'ParallelComputing']
all_subjects = subjects_5th + subjects_6th

# Create a mapping of StudentID to academics data
student_academics = {}
for idx, row in academics_df.iterrows():
    student_id = int(row['StudentID'])
    student_academics[student_id] = row

# Find experts per community
community_experts = {}

for root, students_in_community in communities.items():
    experts = {}
    
    for subject in all_subjects:
        best_student = None
        best_score = -1
        
        for student_id in students_in_community:
            if student_id in student_academics:
                row = student_academics[student_id]
                score = row.get(subject)
                
                # Handle NaN and empty values
                try:
                    score = float(score) if pd.notna(score) and score != '' else -1
                except:
                    score = -1
                
                if score > best_score:
                    best_score = score
                    best_student = student_id
        
        if best_student is not None and best_score >= 0:
            experts[subject] = (best_student, best_score)
    
    if experts:  # Only keep communities with at least one expert
        community_experts[root] = experts

print(f"✓ Identified subject experts in {len(community_experts)} communities")

# ============================================================
# OUTPUT: COMMUNITY-WISE EXPERTS
# ============================================================

output_data = []

print("\n" + "="*70)
print("COMMUNITY SUBJECT EXPERTS REPORT")
print("="*70)

# Sort communities by size
sorted_communities = sorted(
    [(root, len(students_in_community)) for root, students_in_community in communities.items()],
    key=lambda x: x[1],
    reverse=True
)

for rank, (root, comm_size) in enumerate(sorted_communities, 1):
    if root not in community_experts:
        continue
    
    print(f"\n{'─'*70}")
    print(f"Community {rank} (Root: {root}, Size: {comm_size})")
    print(f"Members: {sorted(communities[root])}")
    print(f"{'─'*70}")
    
    experts = community_experts[root]
    
    # 5th Semester Experts
    print("\n5th Semester Experts:")
    for subject in subjects_5th:
        if subject in experts:
            student_id, score = experts[subject]
            student_name = academics_df[academics_df['StudentID'] == student_id]['Name'].values
            student_name = student_name[0] if len(student_name) > 0 else "Unknown"
            print(f"  {subject:12} → Student {student_id:3} ({student_name:20}) Score: {score:.0f}")
            
            output_data.append({
                'Community': rank,
                'Semester': '5th',
                'Subject': subject,
                'ExpertID': student_id,
                'ExpertName': student_name,
                'Score': score,
                'CommunitySize': comm_size,
                'CommunityMembers': len(communities[root])
            })
        else:
            print(f"  {subject:12} → No expert available")
    
    # 6th Semester Experts
    print("\n6th Semester Experts:")
    for subject in subjects_6th:
        if subject in experts:
            student_id, score = experts[subject]
            student_name = academics_df[academics_df['StudentID'] == student_id]['Name'].values
            student_name = student_name[0] if len(student_name) > 0 else "Unknown"
            print(f"  {subject:20} → Student {student_id:3} ({student_name:20}) Score: {score:.0f}")
            
            output_data.append({
                'Community': rank,
                'Semester': '6th',
                'Subject': subject,
                'ExpertID': student_id,
                'ExpertName': student_name,
                'Score': score,
                'CommunitySize': comm_size,
                'CommunityMembers': len(communities[root])
            })
        else:
            print(f"  {subject:20} → No expert available")

# ============================================================
# SAVE RESULTS TO CSV
# ============================================================

output_df = pd.DataFrame(output_data)
output_df.to_csv('community_experts.csv', index=False)

print(f"\n{'='*70}")
print("✓ Results saved to: community_experts.csv")
print(f"{'='*70}\n")

# ============================================================
# STATISTICS
# ============================================================

print("SUMMARY STATISTICS:")
print("-" * 70)
print(f"Total Communities: {len(community_experts)}")
print(f"Total Subject Experts Identified: {len(output_df)}")
print(f"\nExpert Distribution by Semester:")
print(f"  5th Semester: {len(output_df[output_df['Semester'] == '5th'])} experts")
print(f"  6th Semester: {len(output_df[output_df['Semester'] == '6th'])} experts")

print(f"\nTop Communities (by size):")
for rank, (root, comm_size) in enumerate(sorted_communities[:5], 1):
    print(f"  {rank}. Community {rank} - {comm_size} students")

# Find most expert students (appear as expert in most subjects)
expert_frequency = output_df['ExpertID'].value_counts()
print(f"\nMost Versatile Experts (experts in most subjects):")
for student_id, count in expert_frequency.head(5).items():
    student_name = academics_df[academics_df['StudentID'] == student_id]['Name'].values
    student_name = student_name[0] if len(student_name) > 0 else "Unknown"
    print(f"  Student {student_id}: {student_name} - Expert in {count} subjects")

print(f"\nAverage Expert Score: {output_df['Score'].mean():.2f}")
print(f"Highest Expert Score: {output_df['Score'].max():.0f}")
print(f"Lowest Expert Score: {output_df['Score'].min():.0f}")

print("\n" + "="*70)
print("MODULE 2 COMPLETE ✓")
print("="*70)

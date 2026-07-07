import pandas as pd
import os

# Read the 5th semester data
df = pd.read_csv('5thsemester30_12.csv')

print("Original data shape:", df.shape)
print("Columns:", list(df.columns))

# ============================================================
# 1. FRIENDSHIPS CSV
# ============================================================
friendships_cols = ['Sl No', 'Names'] + [f'Friends{i}' for i in range(1, 10)] + \
                   [f'NewFriends{i}' for i in range(1, 13)] + \
                   [f'Lostfriends{i}' for i in range(1, 6)]

friendships_df = df[friendships_cols].copy()
friendships_df.rename(columns={'Sl No': 'StudentID', 'Names': 'Name'}, inplace=True)

# Standardize "Lostfriends" column names to "LostFriends" for consistency
friendships_df.columns = [col.replace('Lostfriends', 'LostFriends') for col in friendships_df.columns]

friendships_df.to_csv('friendships.csv', index=False)
print("\n✓ Created: friendships.csv")
print(f"  Rows: {len(friendships_df)}, Columns: {len(friendships_df.columns)}")
print(f"  Sample columns: {list(friendships_df.columns[:5])}")

# ============================================================
# 2. ACADEMICS CSV
# ============================================================
# 5th Semester subject columns with standardized names
subject_mapping = {
    '16IS5DCJAV': 'Java',
    '16IS5DCDBM': 'DBMS',
    '16IS5DCDCN': 'DCN',
    '16IS5DCWEP': 'WEP',
    '16IS5DEDMG': 'DMG',
    '16IS5DEAIN': 'AIN',
    '16IS5DEPYP': 'PYP',
    '5thSemPercentage': '5thSemPercentage',
    'Software Engineering and Object Oriented Design': 'SEOOD',
    'Computer Networks and Security': 'CNS',
    'Entrepreneurship and Management': 'EM',
    'C# and .NET': 'CSharp',
    'Social Network Analysis': 'SNA',
    'Virtualization': 'VCS',
    'ML': 'ML',
    'Parallel Computing': 'ParallelComputing',
    '6thSemPercentage': '6thSemPercentage'
}

academics_cols = ['Sl No', 'Names'] + list(subject_mapping.keys())
academics_df = df[academics_cols].copy()
academics_df.rename(columns={'Sl No': 'StudentID', 'Names': 'Name'}, inplace=True)
academics_df.rename(columns=subject_mapping, inplace=True)

academics_df.to_csv('academics.csv', index=False)
print("\n✓ Created: academics.csv")
print(f"  Rows: {len(academics_df)}, Columns: {len(academics_df.columns)}")
print(f"  Subjects (5th): Java, DBMS, DCN, WEP, DMG, AIN, PYP")
print(f"  Subjects (6th): SEOOD, CNS, EM, CSharp, SNA, VCS, ML, ParallelComputing")

# ============================================================
# 3. PROFILE CSV
# ============================================================
profile_cols = ['Sl No', 'Names', 'Gender', 'Locality', 'Lateral Entry', 'Backlog', 
                '2nd Year Dropout', '3rd Year Dropout']

profile_df = df[profile_cols].copy()
profile_df.rename(columns={
    'Sl No': 'StudentID', 
    'Names': 'Name',
    'Lateral Entry': 'LateralEntry',
    '2nd Year Dropout': 'Dropout2nd',
    '3rd Year Dropout': 'Dropout3rd'
}, inplace=True)

profile_df.to_csv('profile.csv', index=False)
print("\n✓ Created: profile.csv")
print(f"  Rows: {len(profile_df)}, Columns: {len(profile_df.columns)}")
print(f"  Columns: StudentID, Name, Gender, Locality, LateralEntry, Backlog, Dropout2nd, Dropout3rd")

# ============================================================
# Summary Statistics
# ============================================================
print("\n" + "="*60)
print("DATA SUMMARY")
print("="*60)

print(f"\nTotal Students: {len(academics_df)}")
print(f"\nGender Distribution:")
print(profile_df['Gender'].value_counts())
print(f"\nLocality Distribution:")
print(profile_df['Locality'].value_counts())
print(f"\nBacklog Students: {profile_df['Backlog'].sum()}")
print(f"Dropout 2nd Year: {profile_df['Dropout2nd'].sum()}")
print(f"Dropout 3rd Year: {profile_df['Dropout3rd'].sum()}")

print(f"\n5th Semester Average: {pd.to_numeric(academics_df['5thSemPercentage'], errors='coerce').mean():.2f}%")
print(f"6th Semester Average: {pd.to_numeric(academics_df['6thSemPercentage'], errors='coerce').mean():.2f}%")

print("\n5th Semester Subject Averages:")
for subject in ['Java', 'DBMS', 'DCN', 'WEP', 'DMG', 'AIN', 'PYP']:
    try:
        # Convert to numeric, ignoring errors
        values = pd.to_numeric(academics_df[subject], errors='coerce')
        avg = values.mean()
        if pd.notna(avg):
            print(f"  {subject}: {avg:.2f}")
    except:
        pass

print("\n6th Semester Subject Averages:")
for subject in ['SEOOD', 'CNS', 'EM', 'CSharp', 'SNA', 'VCS', 'ML', 'ParallelComputing']:
    try:
        values = pd.to_numeric(academics_df[subject], errors='coerce')
        avg = values.mean()
        if pd.notna(avg):
            print(f"  {subject}: {avg:.2f}")
    except:
        pass

print("\n" + "="*60)
print("✓ All CSV files created successfully!")
print("="*60)

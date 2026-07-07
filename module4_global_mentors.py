import pandas as pd

print("MODULE 4: Global Top Mentors\n")

academics = pd.read_csv('academics.csv')

subjects_5th = ['Java','DBMS','DCN','WEP','DMG','AIN','PYP']
subjects_6th = ['SEOOD','CNS','EM','CSharp','SNA','VCS','ML','ParallelComputing']
all_subjects = [(s,'5th') for s in subjects_5th] + [(s,'6th') for s in subjects_6th]

results = []

for subj, sem in all_subjects:
    if subj not in academics.columns:
        continue
    col = pd.to_numeric(academics[subj], errors='coerce')
    data = academics[['StudentID','Name']].copy()
    data['score'] = col
    data = data.dropna(subset=['score'])
    if data.empty:
        continue
    # top 5
    topn = data.sort_values('score', ascending=False).head(5)
    rank = 1
    for _, row in topn.iterrows():
        results.append({
            'Subject': subj,
            'Semester': sem,
            'Rank': rank,
            'ExpertID': int(row['StudentID']),
            'ExpertName': row['Name'],
            'Score': float(row['score'])
        })
        rank += 1

out_df = pd.DataFrame(results)
out_df.to_csv('global_mentors_top5.csv', index=False)

print(f"Saved global mentors (top5 per subject) to global_mentors_top5.csv")

# Summary print
for subj, sem in all_subjects:
    subset = out_df[(out_df['Subject']==subj) & (out_df['Semester']==sem)]
    if subset.empty:
        continue
    top = subset[subset['Rank']==1].iloc[0]
    print(f"{subj} ({sem}) -> Student {top['ExpertID']} ({top['ExpertName']}) Score: {top['Score']}")

print('\nMODULE 4 complete.')

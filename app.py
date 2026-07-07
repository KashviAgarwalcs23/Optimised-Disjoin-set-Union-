import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Student Network Dashboard", layout="wide")
st.title("Student Network Analysis Dashboard")
st.markdown("This dashboard shows the student dataset and basic network metrics for the DSU social analytics project.")

# Sidebar navigation
page = st.sidebar.selectbox("Page", ["Overview", "Recommendation", "Community Explorer"]) 

# Try load students.csv for overview
try:
    df_students = pd.read_csv("students.csv")
except FileNotFoundError:
    df_students = pd.DataFrame()

if page == 'Overview':
    if df_students.empty:
        st.error("students.csv not found. Please place the dataset in the code folder to use the Overview page.")
        st.stop()

    st.subheader("Dataset")
    st.dataframe(df_students)

    st.subheader("Basic Stats")
    total = len(df_students)

    # Friend columns detection
    friend_start = None
    friend_end = None
    for i, col in enumerate(df_students.columns):
        if str(col).strip().lower() == "friends":
            friend_start = i
            break
    academic_labels = {"pcp", "tfcs", "dms", "ds", "java", "ml"}
    for i, col in enumerate(df_students.columns):
        if str(col).strip().lower() in academic_labels:
            friend_end = i
            break

    if friend_start is None:
        st.warning("No Friends column detected. Ensure students.csv has a Friends column.")
        df_students["friend_count"] = 0
    else:
        if friend_end is None or friend_end <= friend_start:
            friend_end = min(friend_start + 10, len(df_students.columns))
        friend_df = df_students.iloc[:, friend_start:friend_end]
        df_students["friend_count"] = friend_df.apply(lambda row: row.notna() & row.astype(str).str.strip().ne(""), axis=1).sum(axis=1)

    st.metric("Total Students", total)
    st.metric("Average Friends", round(df_students["friend_count"].mean(), 2))
    st.metric("Max Friends", int(df_students["friend_count"].max()))

    st.subheader("Friend Count Distribution")
    st.bar_chart(df_students["friend_count"])

    if "DMS" in df_students.columns or "DS" in df_students.columns or "PCP" in df_students.columns or "TFCS" in df_students.columns:
        st.subheader("Academic Helper Columns")
        helper_cols = [c for c in ["DMS", "DS", "PCP", "TFCS"] if c in df_students.columns]
        st.write("Detected helper columns:", helper_cols)
        st.dataframe(df_students[helper_cols].head(20))

    st.write("**Run the C++ program to generate detailed community analytics, bridge detection, and influencer outputs.**")

    if st.button("Run DSU analysis now"):
        import subprocess
        try:
            subprocess.run([".\\social.exe"], cwd=".", stdout=open("output.txt", "w", encoding="utf-8"), stderr=subprocess.STDOUT, check=True)
            st.success("Analysis run complete. Output refreshed.")
        except Exception as e:
            st.error(f"Failed to run social.exe: {e}")

    st.subheader("Bridge + Future Influencer Summary")
    try:
        with open("output.txt", "r", encoding="utf-8", errors="ignore") as f:
            out = f.read().splitlines()
    except FileNotFoundError:
        st.warning("output.txt not found. Run social.exe > output.txt first.")
        out = []

    bridge_lines = []
    future_lines = []
    section = None
    for line in out:
        line = line.strip()
        if line.startswith("===== BRIDGE STUDENTS ====="):
            section = "bridge"
            continue
        if line.startswith("===== FUTURE INFLUENCERS ====="):
            section = "future"
            continue
        if line.startswith("====="):
            section = None
        if section == "bridge" and line:
            bridge_lines.append(line)
        if section == "future" and line:
            future_lines.append(line)

    if bridge_lines:
        st.markdown("**Bridge Students (connectors):**")
        for l in bridge_lines:
            st.write(l)
    else:
        st.write("No bridge students were detected in the current graph. This is valid for this dataset.")

    if future_lines:
        st.markdown("**Future Influencers (top 5):**")
        for l in future_lines:
            st.write(l)
    else:
        st.write("No future influencer lines found yet. Run the analysis button to refresh results.")


elif page == 'Recommendation':
    st.header('Recommendation')
    try:
        top1 = pd.read_csv('module8_recommendations_top1.csv')
    except FileNotFoundError:
        st.error('module8_recommendations_top1.csv not found. Run Module 8 first.')
        st.stop()

    try:
        academics = pd.read_csv('academics.csv')
    except FileNotFoundError:
        academics = pd.DataFrame()

    # selection
    student_id = st.selectbox('Select Student', options=sorted(list(top1['TargetID'].unique())))
    subject = st.selectbox('Select Subject', options=sorted(list(top1[top1['TargetID']==student_id]['Subject'].unique())))

    row = top1[(top1['TargetID']==student_id) & (top1['Subject']==subject)].iloc[0]
    st.subheader(f"Recommendation for {row['TargetName']} — {subject}")

    # Layout: left = details & explanation, right = charts + candidates
    left, right = st.columns([1,1])

    with left:
        st.markdown(f"**Recommended Helper:** {row['CandidateName']} (ID {int(row['CandidateID'])})")
        st.markdown(f"**Helper Type:** {row['CandidateType']}  \n                 **Score:** {row['FinalScore']}  \n                 **Confidence:** {row['Confidence']}")

        # Explanation text
        reason = ''
        if row['CandidateType'] == 'community_expert':
            reason = 'Selected because this student is the community expert in the subject.'
        elif row['CandidateType'] == 'friend':
            reason = 'Selected because this friend has the highest subject score among the student\'s friends.'
        elif row['CandidateType'] == 'global_mentor':
            reason = 'Selected from global top mentors as a fallback recommendation.'
        else:
            reason = 'Selected by combined scoring (subject competence + influence - risk).'

        st.markdown('**Explanation**')
        st.info(reason)

        # Export buttons (top1 and top-k)
        try:
            export_df = pd.DataFrame([row])
            csv1 = export_df.to_csv(index=False).encode('utf-8')
            st.download_button('Download this recommendation (CSV)', data=csv1, file_name=f'recommendation_{student_id}_{subject}.csv', mime='text/csv')
        except Exception:
            pass

    with right:
        st.markdown('**Supporting metrics**')
        metrics = {'SubjectScore': float(row['SubjectScore']), 'InfluencerNorm': float(row['InfluencerNorm']), 'RiskNorm': float(row['RiskNorm'])}
        # bar chart
        mdf = pd.DataFrame(list(metrics.items()), columns=['Metric','Value']).set_index('Metric')
        st.bar_chart(mdf)

        try:
            all_recs = pd.read_csv('module8_recommendations.csv')
            candidates = all_recs[(all_recs['TargetID']==student_id)&(all_recs['Subject']==subject)].sort_values('FinalScore', ascending=False).head(5)
            st.subheader('Top candidates')
            st.dataframe(candidates[['CandidateID','CandidateName','CandidateType','FinalScore','Confidence']])
            csvk = candidates.to_csv(index=False).encode('utf-8')
            st.download_button('Export top candidates (CSV)', data=csvk, file_name=f'recommendation_candidates_{student_id}_{subject}.csv', mime='text/csv')
        except FileNotFoundError:
            pass

elif page == 'Community Explorer':
    st.header('Community Explorer')
    try:
        comm_exp = pd.read_csv('community_experts.csv')
    except FileNotFoundError:
        comm_exp = pd.DataFrame()
    try:
        influencers = pd.read_csv('module6_influencer_scores.csv')
    except FileNotFoundError:
        influencers = pd.DataFrame()
    try:
        risk = pd.read_csv('module7_backlog_risk.csv')
    except FileNotFoundError:
        risk = pd.DataFrame()
    try:
        academics = pd.read_csv('academics.csv')
    except FileNotFoundError:
        academics = pd.DataFrame()

    comm_ids = sorted(list(set(comm_exp['Community'].tolist()))) if not comm_exp.empty else []
    if not comm_ids:
        st.warning('No community_experts.csv found; run Module 2 to generate community mappings.')
        st.stop()

    comm = st.selectbox('Select Community', options=comm_ids)
    st.subheader(f'Community {comm}')

    experts = comm_exp[comm_exp['Community']==comm]
    # layout: experts + members | influencer + risk + chart
    left, right = st.columns([1,1])
    with left:
        st.markdown('**Experts in this community**')
        st.dataframe(experts[['Semester','Subject','ExpertID','ExpertName','Score']])
        if not academics.empty and 'StudentID' in academics.columns and 'Name' in academics.columns:
            st.markdown('**Sample members (from academics file)**')
            st.dataframe(academics[['StudentID','Name']].sample(min(10,len(academics))))

    with right:
        if not influencers.empty:
            top_inf = influencers[influencers['CommunityRoot']==comm].sort_values('InfluencerScore', ascending=False).head(1)
            if not top_inf.empty:
                t = top_inf.iloc[0]
                st.markdown('**Top Influencer**')
                st.write(f"{t['Name']} (ID {int(t['StudentID'])}) — Score {round(t['InfluencerScore'],3)}")

        if not risk.empty:
            risk_high = risk[(risk['RiskCategory']=='High')]
            st.markdown('**High risk students (global)**')
            st.dataframe(risk_high[['StudentID','Name','RiskScore']].head(10))

        # small chart: distribution of experts by subject in this community
        try:
            subj_counts = experts['Subject'].value_counts().rename_axis('Subject').reset_index(name='Count')
            if not subj_counts.empty:
                st.markdown('**Expert subject counts**')
                st.bar_chart(subj_counts.set_index('Subject'))
        except Exception:
            pass

    # Embed interactive graph (graph_view.html) if available
    try:
        if st.checkbox('Show interactive community graph (embed)', value=False):
            with open('graph_view.html', 'r', encoding='utf-8') as gf:
                graph_html = gf.read()
            components.html(graph_html, height=720, scrolling=True)
    except FileNotFoundError:
        st.warning('graph_view.html not found. Run the graph_viewer script to generate it.')

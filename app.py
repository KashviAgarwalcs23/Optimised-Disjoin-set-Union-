import pandas as pd
import streamlit as st

st.set_page_config(page_title="Student Network Dashboard", layout="wide")

st.title("Student Network Analysis Dashboard")

st.markdown("This dashboard shows the student dataset and basic network metrics for the DSU social analytics project.")

try:
    df = pd.read_csv("students.csv")
except FileNotFoundError:
    st.error("students.csv not found. Please place the dataset in the code folder.")
    st.stop()

st.subheader("Dataset")
st.dataframe(df)

st.subheader("Basic Stats")
total = len(df)

# Friend columns are the second through the columns before the academic labels.
friend_start = None
friend_end = None
for i, col in enumerate(df.columns):
    if str(col).strip().lower() == "friends":
        friend_start = i
        break

# Find first academic/score column by label names if present
academic_labels = {"pcp", "tfcs", "dms", "ds", "java", "ml"}
for i, col in enumerate(df.columns):
    if str(col).strip().lower() in academic_labels:
        friend_end = i
        break

if friend_start is None:
    st.warning("No Friends column detected. Ensure students.csv has a Friends column.")
    df["friend_count"] = 0
else:
    if friend_end is None or friend_end <= friend_start:
        friend_end = min(friend_start + 10, len(df.columns))
    friend_df = df.iloc[:, friend_start:friend_end]
    df["friend_count"] = friend_df.apply(lambda row: row.notna() & row.astype(str).str.strip().ne(""), axis=1).sum(axis=1)

st.metric("Total Students", total)
st.metric("Average Friends", round(df["friend_count"].mean(), 2))
st.metric("Max Friends", int(df["friend_count"].max()))

st.subheader("Friend Count Distribution")
st.bar_chart(df["friend_count"])

if "DMS" in df.columns or "DS" in df.columns or "PCP" in df.columns or "TFCS" in df.columns:
    st.subheader("Academic Helper Columns")
    helper_cols = [c for c in ["DMS", "DS", "PCP", "TFCS"] if c in df.columns]
    st.write("Detected helper columns:", helper_cols)
    st.dataframe(df[helper_cols].head(20))

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


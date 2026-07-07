# Student Network Analysis Dashboard

A comprehensive social network analysis system for DSU students, combining graph algorithms, data visualization, and interactive dashboards to identify communities, influencers, and bridge students.

## Features

- **Community Detection**: Uses Disjoint Set Union (DSU) algorithm to group students into connected communities based on friendships.
- **Community Subject Experts**: Identifies the best expert in each subject (Java, DBMS, ML, etc.) within every community.
- **Influencer Analysis**: Identifies top academic tutors per subject and ranks "future influencers" based on combined academic and social metrics.
- **Bridge Student Detection**: Finds students who connect different communities.
- **Friendship Evolution**: Tracks friend gain/loss, and social stability over time.
- **Interactive Dashboard**: Web-based UI built with Streamlit for data exploration and analysis execution.
- **Graph Visualization**: Interactive HTML network graph using vis.js library with physics-based layout.
- **Performance Comparison**: Benchmarks optimized DSU vs. naive implementation.
- **Data Insights**: Friend count distributions, academic helper columns, and community-wise rankings.

## Project Structure

```
Ads_aat_project/
├── code/
│   ├── app.py                      # Streamlit web dashboard
│   ├── dsu_social.cpp              # Core C++ DSU analysis engine (legacy)
│   ├── normalize_data.py            # Data normalization script
│   ├── module2_community_experts.py # Module 2: Community Subject Experts
│   │
│   ├── Data Files (Input)
│   ├── 3rdsemester30_12.csv         # 3rd semester raw data
│   ├── 5thsemester30_12.csv         # 5th semester raw data (used for analysis)
│   ├── 7thsemester30_12.csv         # 7th semester raw data
│   │
│   ├── Normalized Data (Generated)
│   ├── friendships.csv              # StudentID, Name, Friends1-9, NewFriends1-12, LostFriends1-5
│   ├── academics.csv                # StudentID, Name, Java, DBMS, ..., ML, 5thSemPercentage, 6thSemPercentage
│   ├── profile.csv                  # StudentID, Name, Gender, Locality, LateralEntry, Backlog, Dropout info
│   │
│   ├── Output Files
│   ├── community_experts.csv        # Module 2 output: experts per community per subject
│   ├── output.txt                   # Legacy analysis results
│   ├── graph_edges.txt              # Edge list for visualization
│   ├── graph_view.html              # Interactive network graph
│   │
│   ├── Visualization Scripts
│   ├── graph_viewer.py              # Python script for HTML graph generation
│   ├── plot_graph.py                # Static NetworkX visualization
│   ├── plot.py                      # Basic graph extraction
│   ├── dsu_social.exe               # Compiled C++ executable (legacy)
│   │
│   └── __pycache__/
│
├── dataset/
│   └── facebook_combined.txt        # Reference social network dataset
│
├── results/                         # Directory for additional outputs
│
└── README.md                        # This file
```

## Installation

### Prerequisites
- **Python 3.8+** with virtual environment support
- **C++ Compiler** (e.g., g++ for Windows/Linux, Xcode for macOS)
- **Git** for cloning (optional)

### Setup Steps

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd Ads_aat_project
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   # Install dependencies
   pip install pandas streamlit networkx matplotlib vis-network
   ```

3. **Compile C++ Program**
   ```bash
   cd code
   g++ -o social.exe dsu_social.cpp
   # Or on Linux/macOS: g++ -o social dsu_social.cpp
   ```

4. **Verify Dataset**
   - Ensure `students.csv` is in the `code/` folder.
   - The file contains ~120 students with columns: ID, Friends (space-separated), PCP, TFCS, DMS, DS (helper IDs).

## Usage

### Running the Data Normalization
1. Navigate to the `code/` directory.
2. Run the normalization script:
   ```bash
   python normalize_data.py
   ```
   This creates `friendships.csv`, `academics.csv`, and `profile.csv`.

### Running Module 2: Community Subject Experts
1. After normalization, run:
   ```bash
   python module2_community_experts.py
   ```
   This generates `community_experts.csv` with expert rankings per community.

2. View results:
   - Console output shows detailed community breakdown
   - CSV file contains structured data for further analysis

### Running the Dashboard (Legacy)
1. Navigate to the `code/` directory.
2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Open the provided local URL (e.g., http://localhost:8501) in your browser.

### Dashboard Features
- **Dataset View**: Displays the full student CSV with filtering.
- **Basic Stats**: Total students, average/max friends, friend count distribution bar chart.
- **Academic Helpers**: Preview of tutoring columns.
- **Run Analysis**: Button to execute the C++ program (`social.exe`) and refresh results.
- **Results Display**: Shows bridge students and future influencers parsed from `output.txt`.

### Running Analysis Manually
1. In the `code/` directory:
   ```bash
   # Windows
   .\social.exe > output.txt
   # Linux/macOS
   ./social > output.txt
   ```
2. View results in `output.txt` or open `graph_view.html` for visualization.

### Visualizations
- **Interactive Graph**: Open `graph_view.html` in a browser for zoomable, draggable network view.
- **Static Graphs**: Run `python plot_graph.py` for matplotlib visualizations.

## Output Files

### Normalized Data (Generated by `normalize_data.py`)

#### friendships.csv
- **Columns:** StudentID, Name, Friends1-9, NewFriends1-12, LostFriends1-5
- **Purpose:** Social network data organized for analysis
- **Records:** 118 students

#### academics.csv
- **Columns:** StudentID, Name, Java, DBMS, DCN, WEP, DMG, AIN, PYP, 5thSemPercentage, SEOOD, CNS, EM, CSharp, SNA, VCS, ML, ParallelComputing, 6thSemPercentage
- **Purpose:** Academic performance data for all subjects
- **Records:** 118 students
- **Coverage:** 5th & 6th semester subjects with percentage scores

#### profile.csv
- **Columns:** StudentID, Name, Gender, Locality, LateralEntry, Backlog, Dropout2nd, Dropout3rd
- **Purpose:** Student demographic and status information
- **Records:** 118 students

### Analysis Output Files

#### community_experts.csv (Module 2)
- **Columns:** Community, Semester, Subject, ExpertID, ExpertName, Score, CommunitySize, CommunityMembers
- **Purpose:** Top expert in each subject for each community
- **Example:** Community 1, Java → Student 12 (Score: 95)
- **Records:** 105 expert assignments across 15 communities

### Legacy Output Files

#### output.txt
Contains detailed analysis results from C++ DSU:
- **Communities**: Detected groups with student IDs.
- **Community Rankings**: Sizes from largest to smallest.
- **Global Influencers**: Top tutor per subject.
- **Influencer vs Connectivity**: Compares academic help with friend count.
- **Bridge Students**: Connectors between communities.
- **Future Influencers**: Top 5 students by score.
- **Community-wise Influencers**: Local experts per subject per community.

#### graph_view.html
Interactive vis.js network graph:
- Nodes: Students (labeled by ID).
- Edges: Friendships.
- Physics: Barnes-Hut simulation for natural layout.
- Features: Zoom, pan, drag nodes.

#### graph_edges.txt
Simple edge list (e.g., `1 7`) for external graph tools.

## Academic Mentor Recommendation System Modules

The system is built on 8 modular components. Currently implemented:

### ✅ Module 1: DSU Community Detection (Legacy/C++)
**Status:** Complete  
**Input:** Friendship connections  
**Output:** 15 communities detected (largest has 102 students)  
**Purpose:** Group students based on transitive friendship relationships.

### ✅ Module 2: Community Subject Experts
**Status:** Complete  
**File:** `module2_community_experts.py`  
**Input:** `friendships.csv`, `academics.csv`  
**Output:** `community_experts.csv`  
**Purpose:** For each community, identify the best expert in each subject (Java, DBMS, ML, etc.)

**Example Output:**
```
Community 1 (102 students)
  5th Semester:
    Java     → Student 12 (Score: 95)
    DBMS     → Student 9  (Score: 95)
    ML       → Student 13 (Score: 95)
  
  6th Semester:
    SEOOD    → Student 13 (Score: 95)
    CNS      → Student 13 (Score: 95)
    ML       → Student 13 (Score: 95)
```

**Statistics:**
- 15 communities detected
- 105 subject experts identified across all communities
- Most versatile expert: Student 13 (expert in 8 subjects)
- Average expert score: 82.30 / 100

### ✅ Module 3: Personalized Helper Recommendation
**Status:** Complete  
**File:** `module3_personalized_recommender.py`  
**Input:** `friendships.csv`, `academics.csv`, `community_experts.csv`  
**Output:** `recommendations_demo.csv` (demo run)  
**Purpose:** Given a student and a subject, recommend the best helper using community experts (preferred), friends fallback, then global best.

**Logic Summary:**
- Find the student's community (DSU on friendships).
- Look for a community expert for the subject (from `community_experts.csv`). If present, recommend them.
- If no community expert, search the student's friends for the highest subject score and recommend the best-performing friend.
- If still none, recommend the global top performer for that subject.
- Confidence: High/Medium/Low based on recommended expert's score and source.

**Example Usage:**
```
cd code
python module3_personalized_recommender.py
```
This produces `recommendations_demo.csv` with sample recommendations. Example rows:
```
StudentID,Subject,RecommendedID,RecommendedName,Score,Source,Confidence,CommunityRank
1,ML,13,AVEESHA JINDAL,95.0,community_expert,High,1
30,ML,13,AVEESHA JINDAL,95.0,community_expert,High,1
96,CSharp,96,VEERESH TOTAR,75.0,community_expert,Low,2
```

### ✅ Module 4: Top Mentors Across Entire Class
**Status:** Complete  
**File:** `module4_global_mentors.py`  
**Input:** `academics.csv`  
**Output:** `global_mentors_top5.csv`  
**Purpose:** Produce global rankings of top mentors per subject (top-5). Useful for cross-community recommendations and global leaderboards.

**Example Usage:**
```
cd code
python module4_global_mentors.py
```

**Example Output (top-1 per subject):**
```
Java (5th) -> Student 12 (ASHUTOSH KUMAR TIWARI) Score: 95
DBMS (5th) -> Student 13 (AVEESHA JINDAL) Score: 95
ML (6th) -> Student 13 (AVEESHA JINDAL) Score: 95
ParallelComputing (6th) -> Student 72 (RAJATH R JINGADE) Score: 90
```

The script produces `global_mentors_top5.csv` containing the top 5 students per subject.

### ✅ Module 5: Friendship Evolution Analysis
**Status:** Complete
**File:** `module5_friendship_evolution.py`
**Input:** `friendships.csv`
**Output:** `friendship_evolution.csv`, `community_friendship_evolution.csv`
**Purpose:** Computes per-student friend gain/loss, remaining friends, growth and a social stability score; aggregates these metrics at the community level for downstream modules.

### ✅ Module 6: Future Influencer Prediction
**Status:** Complete
**File:** `module6_future_influencer.py`
**Input:** `academics.csv`, `friendship_evolution.csv`
**Output:** `module6_influencer_scores.csv`, `module6_top_influencers.csv`
**Purpose:** Produces a normalized influencer score combining academic performance and social metrics (stability/growth). Ranks students globally and within communities for targeted recommendations.

### ✅ Module 7: Backlog Risk Analysis
**Status:** Complete
**File:** `module7_backlog_risk.py`
**Input:** `profile.csv`, `academics.csv`, `friendship_evolution.csv`
**Output:** `module7_backlog_risk.csv`, `module7_top_at_risk.csv`
**Purpose:** Computes a per-student risk score (Academic performance, existing backlog, social stability, dropout history) and categorizes students into `High`/`Medium`/`Low` risk for targeted interventions.

### ✅ Module 8: Smart Recommendation Engine
**Status:** Complete
**File:** `module8_smart_recommender.py`
**Input:** `academics.csv`, `friendships.csv`, `community_experts.csv`, `global_mentors_top5.csv`, `module6_influencer_scores.csv`, `module7_backlog_risk.csv`
**Output:** `module8_recommendations.csv`, `module8_recommendations_top1.csv`
**Purpose:** Produces ranked helper recommendations per student+subject by combining subject competence (community & global), friend availability, influencer signal and risk score. Outputs top-k candidates and a condensed top-1 recommendation per student-subject pair.

## Dependencies

### Python
- `pandas`: Data manipulation
- `streamlit`: Web dashboard
- `networkx`: Graph algorithms
- `matplotlib`: Static plotting
- `vis-network`: Interactive HTML graphs (via CDN)

### C++
- Standard libraries: `<iostream>`, `<vector>`, `<map>`, etc.
- No external dependencies.

## Algorithm Overview

### Disjoint Set Union (DSU)
- **Optimized Version**: Path compression + union by rank for near-linear time.
- **Naive Version**: Basic implementation for comparison.
- **Purpose**: Groups students into communities based on transitive friendships.

### Influencer Scoring
- **Academic Influence**: Count of help instances per subject.
- **Social Connectivity**: Friend count.
- **Combined Score**: (Academic × 2) + Friends for "future influencers".

### Bridge Detection
- Students whose neighbors belong to different communities.

## Troubleshooting

- **CSV Not Found**: Ensure `students.csv` is in `code/` and the app is run from there.
- **Compilation Errors**: Check C++ compiler installation and path.
- **Streamlit Issues**: Activate virtual environment and install packages.
- **Empty Results**: Verify CSV format (comma-separated, quoted friend lists).
- **Performance**: Optimized DSU handles 120+ students efficiently; naive version may be slower.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make changes and test thoroughly.
4. Submit a pull request with a clear description.

## License

This project is open-source. Use at your own risk. No warranties provided.

## Contact

For questions or issues, please open an issue in the repository or contact the maintainers.

.venv) PS D:\Ads_aat_project> cd code
>> streamlit run app.py

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.29.225:8501

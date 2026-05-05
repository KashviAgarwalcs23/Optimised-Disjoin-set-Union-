# Student Network Analysis Dashboard

A comprehensive social network analysis system for DSU students, combining graph algorithms, data visualization, and interactive dashboards to identify communities, influencers, and bridge students.

## Features

- **Community Detection**: Uses Disjoint Set Union (DSU) algorithm to group students into connected communities based on friendships.
- **Influencer Analysis**: Identifies top academic tutors per subject and ranks "future influencers" based on combined academic and social metrics.
- **Bridge Student Detection**: Finds students who connect different communities.
- **Interactive Dashboard**: Web-based UI built with Streamlit for data exploration and analysis execution.
- **Graph Visualization**: Interactive HTML network graph using vis.js library with physics-based layout.
- **Performance Comparison**: Benchmarks optimized DSU vs. naive implementation.
- **Data Insights**: Friend count distributions, academic helper columns, and community-wise rankings.

## Project Structure

```
Ads_aat_project/
├── code/
│   ├── app.py                 # Streamlit web dashboard
│   ├── dsu_social.cpp         # Core C++ DSU analysis engine
│   ├── students.csv           # Student dataset (ID, friends, academic helpers)
│   ├── output.txt             # Analysis results (generated)
│   ├── graph_edges.txt        # Edge list for visualization (generated)
│   ├── graph_view.html        # Interactive network graph (generated)
│   ├── graph_viewer.py        # Python script for HTML graph generation
│   ├── plot_graph.py          # Static NetworkX visualization
│   ├── plot.py                # Basic graph extraction
│   └── dsu_social.exe         # Compiled C++ executable (generated)
├── dataset/
│   └── facebook_combined.txt  # Reference social network dataset
├── results/                   # Directory for additional outputs
└── README.md                  # This file
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

### Running the Dashboard
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

### output.txt
Contains detailed analysis results:
- **Communities**: 36 detected groups with student IDs.
- **Community Rankings**: Sizes from largest (14 students) to smallest.
- **Global Influencers**: Top tutor per subject (e.g., Student 88 for DS).
- **Influencer vs Connectivity**: Compares academic help with friend count for each student.
- **Bridge Students**: Connectors between communities (may be empty).
- **Future Influencers**: Top 5 students by score (2× academic + social).
- **Community-wise Influencers**: Local experts per subject per community.

### graph_view.html
Interactive vis.js network graph:
- Nodes: Students (labeled by ID).
- Edges: Friendships.
- Physics: Barnes-Hut simulation for natural layout.
- Features: Zoom, pan, drag nodes.

### graph_edges.txt
Simple edge list (e.g., `1 7`) for external graph tools.

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
"""
Create PNG images for inclusion in the presentation from available CSVs and graph_edges.txt.
Generates:
 - community_stats.png
 - recommendation_coverage.png
 - top_influencers.png
 - graph_view.png (static network snapshot)

Run from code/:
  python create_images_for_ppt.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

OUT = Path('.')

# community_stats.png
comm_stats = Path('evaluation_community_stats.csv')
if comm_stats.exists():
    try:
        df = pd.read_csv(comm_stats)
        # If aggregated stats only, produce a simple text-like image
        fig, ax = plt.subplots(figsize=(6,3))
        ax.axis('off')
        txt = '\n'.join([f"{c}: {df.iloc[0][c]}" for c in df.columns])
        ax.text(0,0.5, txt, fontsize=12, va='center')
        plt.savefig(OUT / 'community_stats.png', bbox_inches='tight')
        plt.close()
        print('Saved community_stats.png')
    except Exception as e:
        print('Failed community_stats.png:', e)

# recommendation_coverage.png
cov = Path('evaluation_recommendation_coverage.csv')
if cov.exists():
    try:
        df = pd.read_csv(cov)
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(df['Source'], df['Count'], color=['#2b83ba','#fdae61','#abdda4'][:len(df)])
        ax.set_ylabel('Count')
        ax.set_title('Recommendation Coverage by Source')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUT / 'recommendation_coverage.png')
        plt.close()
        print('Saved recommendation_coverage.png')
    except Exception as e:
        print('Failed recommendation_coverage.png:', e)

# top_influencers.png
inf = Path('evaluation_top10_influencers.csv')
if inf.exists():
    try:
        df = pd.read_csv(inf).head(10)
        fig, ax = plt.subplots(figsize=(8,4))
        ax.barh(df['Name'].astype(str), df['InfluencerScore'].astype(float), color='#6a3d9a')
        ax.invert_yaxis()
        ax.set_xlabel('Influencer Score')
        ax.set_title('Top 10 Influencers')
        plt.tight_layout()
        plt.savefig(OUT / 'top_influencers.png')
        plt.close()
        print('Saved top_influencers.png')
    except Exception as e:
        print('Failed top_influencers.png:', e)

# graph_view.png - generate static network snapshot from graph_edges.txt and community mapping if available
edges_file = Path('graph_edges.txt')
if edges_file.exists():
    try:
        G = nx.Graph()
        with open(edges_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 2:
                    continue
                G.add_edge(int(parts[0]), int(parts[1]))
        # load community mapping
        comm_map = {}
        cm_path = Path('module6_influencer_scores.csv')
        if cm_path.exists():
            try:
                cm = pd.read_csv(cm_path)
                for _, r in cm.iterrows():
                    comm_map[int(r['StudentID'])] = int(r['CommunityRoot']) if not pd.isna(r['CommunityRoot']) else None
            except Exception:
                comm_map = {}
        # color by community
        unique_comms = sorted(set([v for v in comm_map.values() if v is not None]))
        palette = ["#1f78b4","#33a02c","#e31a1c","#ff7f00","#6a3d9a","#b15928","#a6cee3","#b2df8a","#fb9a99","#fdbf6f"]
        node_colors = []
        for n in G.nodes():
            c = comm_map.get(n)
            if c is None:
                node_colors.append('#888')
            else:
                idx = unique_comms.index(c) if c in unique_comms else 0
                node_colors.append(palette[idx % len(palette)])
        plt.figure(figsize=(10,8))
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=60, node_color=node_colors)
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(OUT / 'graph_view.png', dpi=150)
        plt.close()
        print('Saved graph_view.png')
    except Exception as e:
        print('Failed graph_view.png:', e)
else:
    print('graph_edges.txt not found; skipping graph image')

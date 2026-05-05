import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
with open("graph_edges.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        u, v = map(int, parts)
        G.add_edge(u, v)

plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", edge_color="gray", font_size=8)
plt.title("Student Communities Graph")
plt.tight_layout()
plt.show()

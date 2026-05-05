import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

with open("students.csv") as f:
    next(f)
    for line in f:
        parts = line.strip().split(",")
        student = int(parts[0])
        friends = parts[1].replace('"','').split()

        for f in friends:
            G.add_edge(student, int(f))

nx.draw(G, with_labels=True)
plt.show()
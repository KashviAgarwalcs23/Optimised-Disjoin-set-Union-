import json

nodes = set()
edges = []
with open("graph_edges.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        u, v = parts
        nodes.add(u)
        nodes.add(v)
        edges.append({"from": u, "to": v})

html = f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Graph Viewer</title>
  <script type='text/javascript' src='https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js'></script>
  <link href='https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.css' rel='stylesheet' type='text/css' />
  <style>
    body {{ margin: 0; padding: 0; }}
    #mynetwork {{ width: 100vw; height: 100vh; border: 1px solid lightgray; }}
  </style>
</head>
<body>
<div id='mynetwork'></div>
<script>
  const nodes = new vis.DataSet({json.dumps([{"id": n, "label": n} for n in sorted(nodes, key=int)])});
  const edges = new vis.DataSet({json.dumps(edges)});
  const container = document.getElementById('mynetwork');
  const data = {{ nodes: nodes, edges: edges }};
  const options = {{
    nodes: {{ shape: 'dot', size: 12 }},
    edges: {{ color: '#888' }},
    physics: {{ stabilization: true, barnesHut: {{ gravitationalConstant: -2000 }} }}
  }};
  new vis.Network(container, data, options);
</script>
</body>
</html>
"""

with open("graph_view.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Generated graph_view.html. Open it in your browser.")

import json
import pandas as pd

# Read edges
nodes_set = set()
edges = []
with open("graph_edges.txt") as f:
  for line in f:
    parts = line.strip().split()
    if len(parts) != 2:
      continue
    u, v = parts
    nodes_set.add(u)
    nodes_set.add(v)
    edges.append({"from": u, "to": v})

# Load academic names (for labels) and community/influencer data if available
names = {}
try:
  acad = pd.read_csv('academics.csv')
  for _, r in acad.iterrows():
    names[str(int(r['StudentID']))] = r['Name']
except Exception:
  pass

comm_map = {}
try:
  infl = pd.read_csv('module6_influencer_scores.csv')
  for _, r in infl.iterrows():
    comm_map[str(int(r['StudentID']))] = int(r['CommunityRoot']) if not pd.isna(r['CommunityRoot']) else None
except Exception:
  pass

experts = set()
try:
  comm_exp = pd.read_csv('community_experts.csv')
  for _, r in comm_exp.iterrows():
    try:
      experts.add(str(int(r['ExpertID'])))
    except Exception:
      pass
except Exception:
  pass

influencers = set()
try:
  topinf = pd.read_csv('module6_top_influencers.csv')
  for _, r in topinf.iterrows():
    try:
      influencers.add(str(int(r['StudentID'])))
    except Exception:
      pass
except Exception:
  pass

# Assign colors to communities
comm_ids = sorted(set([v for v in comm_map.values() if v is not None]))
palette = ["#1f78b4","#33a02c","#e31a1c","#ff7f00","#6a3d9a","#b15928","#a6cee3","#b2df8a","#fb9a99","#fdbf6f"]
comm_color = {c: palette[i % len(palette)] for i, c in enumerate(comm_ids)}

# Build node list with shapes and colors and metadata
nodes = []
for n in sorted(nodes_set, key=lambda x: int(x)):
  label = names.get(n, n)
  comm = comm_map.get(n)
  color = comm_color.get(comm, '#888')
  shape = 'dot'
  ntype = 'normal'
  if n in experts:
    shape = 'star'
    ntype = 'expert'
  elif n in influencers:
    shape = 'diamond'
    ntype = 'influencer'
  nodes.append({
    "id": int(n),
    "label": f"{n} : {label}",
    "color": {"background": color},
    "shape": shape,
    "community": int(comm) if comm is not None else None,
    "type": ntype
  })

html = """<!doctype html>
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
<div style='position:fixed; right:12px; top:12px; z-index:999; background:#fff; padding:8px; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.15);'>
  <strong>Legend / Layers</strong><br/>
  <div id='legend'></div>
  <hr style='margin:6px 0;'>
  <label><input type='checkbox' id='chk_experts' checked onchange='applyFilters()'/> Show Experts</label><br/>
  <label><input type='checkbox' id='chk_infl' checked onchange='applyFilters()'/> Show Influencers</label>
</div>

<div id='mynetwork'></div>
<script>
  const nodes = new vis.DataSet(NODES_JSON);
  const edges = new vis.DataSet(EDGES_JSON);
  const container = document.getElementById('mynetwork');
  const data = { nodes: nodes, edges: edges };
  const options = {
  nodes: { size: 18, font: {size:12} },
  edges: { color: '#888' },
  physics: { stabilization: true, barnesHut: { gravitationalConstant: -2000 } }
  };
  new vis.Network(container, data, options);

  // Build legend checkboxes for communities
  const legend = document.getElementById('legend');
  const commColors = COMM_COLOR_JSON;
  Object.keys(commColors).forEach(function(c){
    const color = commColors[c];
    const id = 'comm_' + c;
    const div = document.createElement('div');
    div.innerHTML = '<label style="display:flex;align-items:center;gap:6px;">'<
      + "<input type=\'checkbox\' id='" + id + "' checked onchange='applyFilters()'/> "
      + "<span style='display:inline-block;width:14px;height:14px;background:" + color + ";border-radius:3px;'></span> Community " + c + "</label>";
    legend.appendChild(div);
  });

  function applyFilters(){
    const showExperts = document.getElementById('chk_experts').checked;
    const showInfl = document.getElementById('chk_infl').checked;
    const all = nodes.get();
    const updates = [];
    all.forEach(function(n){
      let hide = false;
      if(n.type === 'expert' && !showExperts) hide = true;
      if(n.type === 'influencer' && !showInfl) hide = true;
      if(n.community !== null && n.community !== undefined){
        const el = document.getElementById('comm_' + n.community);
        if(el && !el.checked) hide = true;
      }
      updates.push({id: n.id, hidden: hide});
    });
    nodes.update(updates);
  }

</script>
</body>
</html>
"""

html = html.replace('NODES_JSON', json.dumps(nodes))
html = html.replace('EDGES_JSON', json.dumps(edges))
html = html.replace('COMM_COLOR_JSON', json.dumps(comm_color))

with open("graph_view.html", "w", encoding="utf-8") as f:
  f.write(html)

print("Generated graph_view.html with community colors and expert/influencer shapes. Open it in your browser.")

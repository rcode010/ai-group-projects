export const solvePath = async (nodes, edges, startNode, goalNode) => {
  const resp = await fetch('http://localhost:8000/api/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      nodes: nodes.map(n => ({ id: n.id, x: n.x, y: n.y })), 
      edges: edges.map(e => ({ source: e.source, target: e.target, weight: e.weight })), 
      start_node: startNode, 
      goal_node: goalNode 
    })
  });
  if (!resp.ok) throw new Error("Backend error");
  return await resp.json();
};

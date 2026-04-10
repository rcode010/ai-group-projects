export const solvePath = async (nodes, edges, startNode, goalNode) => {
  const resp = await fetch('http://localhost:8000/api/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nodes: nodes.map(n => ({ id: n.id, x: Math.round(n.x), y: Math.round(n.y) })),
      edges: edges.map(e => ({ source: e.source, target: e.target, weight: e.weight ?? 1 })),
      start_node: startNode,
      goal_node: goalNode
    })
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Backend error' }));
    throw new Error(err.detail || 'Backend error');
  }

  return await resp.json();
};
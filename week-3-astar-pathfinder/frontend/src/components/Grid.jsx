import React from 'react';
import { cn } from '../utils';

const GRID_SIZE = 40;

export default function Grid({
  nodes, edges, mode, startNode, goalNode,
  selectedEdgeNode, solveResult,
  onBoardClick, onNodeClick, onNodeRightClick, onNodeMouseDown,
  boardRef,
}) {
  const toGrid = (px) => Math.round(px / GRID_SIZE);

  const getChebyshev = (node) => {
    const gNode = nodes.find(n => n.id === goalNode);
    if (!gNode) return '';
    const dx = Math.abs(toGrid(node.x) - toGrid(gNode.x));
    const dy = Math.abs(toGrid(node.y) - toGrid(gNode.y));
    return Math.max(dx, dy);
  };

  const isOnPath = (edgeSource, edgeTarget) => {
    if (!solveResult?.path) return false;
    const path = solveResult.path;
    const si = path.indexOf(edgeSource);
    const ti = path.indexOf(edgeTarget);
    return si !== -1 && ti !== -1 && Math.abs(si - ti) === 1;
  };

  const boardCursor =
    mode === 'add_node' ? 'cursor-crosshair' :
    mode === 'select'   ? 'cursor-default'   :
    'cursor-default';

  return (
    <div
      ref={boardRef}
      onClick={onBoardClick}
      className={cn('absolute inset-0 overflow-hidden select-none', boardCursor)}
      style={{
        backgroundImage: `radial-gradient(circle at 1px 1px, #cbd5e1 1px, transparent 0)`,
        backgroundSize: `${GRID_SIZE}px ${GRID_SIZE}px`,
        backgroundColor: '#f8fafc',
      }}
    >
      {/* Hint banner */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200 rounded-full px-4 py-1.5 text-xs text-slate-500 shadow-sm font-medium whitespace-nowrap">
          {mode === 'add_node' && '🖱 Click the grid to place a node'}
          {mode === 'add_edge' && (selectedEdgeNode
            ? `✅ Now click another node to connect to "${selectedEdgeNode}"`
            : '🔗 Click a node to start an edge')}
          {mode === 'set_start' && '🟢 Click a node to set it as Start'}
          {mode === 'set_goal'  && '🔴 Click a node to set it as Goal'}
          {mode === 'select'    && '↕ Drag nodes to move · Right-click to delete'}
        </div>
      </div>

      {/* SVG edges layer */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <filter id="glow" filterUnits="userSpaceOnUse">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {edges.map((edge, i) => {
          const n1 = nodes.find(n => n.id === edge.source);
          const n2 = nodes.find(n => n.id === edge.target);
          if (!n1 || !n2) return null;
          const onPath = isOnPath(edge.source, edge.target);

          return (
            <g key={i}>
              <line
                x1={n1.x} y1={n1.y}
                x2={n2.x} y2={n2.y}
                stroke={onPath ? '#4f46e5' : '#cbd5e1'}
                strokeWidth={onPath ? 4 : 2}
                filter={onPath ? 'url(#glow)' : undefined}
                strokeDasharray={onPath ? undefined : '6 3'}
                className="transition-all duration-500"
              />
              {/* Weight pill */}
              <rect
                x={(n1.x + n2.x) / 2 - 14} y={(n1.y + n2.y) / 2 - 10}
                width={28} height={18} rx={4}
                fill="white" stroke={onPath ? '#4f46e5' : '#e2e8f0'} strokeWidth={1}
              />
              <text
                x={(n1.x + n2.x) / 2} y={(n1.y + n2.y) / 2 + 4}
                textAnchor="middle" fill={onPath ? '#4f46e5' : '#94a3b8'} fontSize="10"
                fontWeight={onPath ? 'bold' : 'normal'} fontFamily="monospace"
              >
                {edge.weight}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Node layer */}
      {nodes.map(n => {
        const isStart    = n.id === startNode;
        const isGoal     = n.id === goalNode;
        const isSelected = n.id === selectedEdgeNode;
        const isPath     = solveResult?.path?.includes(n.id);
        const chebyshev  = getChebyshev(n);
        const isDraggable = mode === 'select';

        return (
          <div
            key={n.id}
            onMouseDown={(e) => onNodeMouseDown(e, n.id)}
            onClick={(e) => onNodeClick(e, n.id)}
            onContextMenu={(e) => onNodeRightClick(e, n.id)}
            className={cn(
              'absolute w-14 h-14 rounded-full flex flex-col items-center justify-center',
              'transition-colors duration-200 z-10 border-2 shadow-md group',
              isDraggable ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer',
              isStart
                ? 'bg-emerald-50 border-emerald-500 text-emerald-700 shadow-emerald-200'
                : isGoal
                ? 'bg-rose-50 border-rose-500 text-rose-700 shadow-rose-200'
                : isSelected
                ? 'bg-amber-50 border-amber-400 text-amber-700 shadow-amber-200'
                : isPath
                ? 'bg-indigo-50 border-indigo-500 text-indigo-700 shadow-indigo-200'
                : 'bg-white border-slate-300 text-slate-700 hover:border-indigo-400 hover:shadow-indigo-100'
            )}
            style={{
              left: n.x,
              top: n.y,
              transform: `translate(-50%, -50%) scale(${isSelected ? 1.1 : isPath ? 1.05 : 1})`,
            }}
          >
            <span className="font-bold text-sm leading-none">{n.id}</span>
            {chebyshev !== '' && (
              <span className="text-[9px] font-mono mt-0.5 opacity-70">h={chebyshev}</span>
            )}

            {/* Tooltip */}
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-30">
              <div className="bg-slate-900 text-white text-[10px] px-2 py-1 rounded-md whitespace-nowrap shadow-lg">
                {isStart ? '🟢 Start' : isGoal ? '🔴 Goal' : `Node ${n.id}`}
                {chebyshev !== '' && ` · h=${chebyshev}`}
                {isDraggable && ' · RClick=delete'}
              </div>
            </div>

            {/* Pulsing ring when selected for edge */}
            {isSelected && (
              <div className="absolute inset-0 rounded-full border-4 border-amber-400 animate-ping opacity-30 pointer-events-none" />
            )}
          </div>
        );
      })}
    </div>
  );
}
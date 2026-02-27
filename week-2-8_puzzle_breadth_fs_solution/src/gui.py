HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>8-Puzzle — Glassmorphic Neon</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg-primary: #0a0a1a;
  --bg-secondary: #0f0f2e;
  --glass-bg: rgba(255,255,255,0.04);
  --glass-border: rgba(255,255,255,0.08);
  --glass-hover: rgba(255,255,255,0.08);
  --accent-cyan: #00e5ff;
  --accent-purple: #a855f7;
  --accent-pink: #ec4899;
  --accent-green: #34d399;
  --accent-gold: #fbbf24;
  --text-primary: #f0f0ff;
  --text-secondary: rgba(255,255,255,0.45);
  --tile-shadow: rgba(0,0,0,0.5);
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-display: 'Space Grotesk', 'Inter', sans-serif;
}

html, body {
  width: 100%; height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-body);
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}

/* ── Animated Mesh Background ── */
.bg-mesh {
  position: fixed; inset: 0; z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 80%, rgba(168,85,247,0.15) 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 20%, rgba(0,229,255,0.10) 0%, transparent 60%),
    radial-gradient(ellipse 50% 50% at 50% 50%, rgba(236,72,153,0.06) 0%, transparent 50%),
    var(--bg-primary);
}
.bg-mesh::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  opacity: 0.4;
}

/* ── Floating Orbs ── */
.orb {
  position: fixed; border-radius: 50%; filter: blur(80px);
  z-index: 0; pointer-events: none; will-change: transform;
}
.orb-1 { width: 300px; height: 300px; background: rgba(168,85,247,0.18); top: -50px; left: -50px; animation: orb-float 18s ease-in-out infinite; }
.orb-2 { width: 250px; height: 250px; background: rgba(0,229,255,0.12); bottom: -30px; right: -30px; animation: orb-float 22s ease-in-out infinite reverse; }
.orb-3 { width: 200px; height: 200px; background: rgba(236,72,153,0.10); top: 50%; left: 60%; animation: orb-float 15s ease-in-out infinite 3s; }
@keyframes orb-float {
  0%,100% { transform: translate(0,0) scale(1); }
  33% { transform: translate(30px,-40px) scale(1.1); }
  66% { transform: translate(-20px,30px) scale(0.95); }
}

/* ── Main Layout ── */
.app {
  position: relative; z-index: 1;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 100vh; padding: 20px;
  gap: 20px;
}

/* ── Header ── */
.header { text-align: center; }
.header h1 {
  font-family: var(--font-display); font-size: 42px; font-weight: 700;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 3px;
  filter: drop-shadow(0 0 30px rgba(0,229,255,0.3));
  animation: title-glow 4s ease-in-out infinite alternate;
}
@keyframes title-glow {
  0% { filter: drop-shadow(0 0 20px rgba(0,229,255,0.2)); }
  100% { filter: drop-shadow(0 0 40px rgba(168,85,247,0.4)); }
}
.header .subtitle {
  font-size: 12px; letter-spacing: 5px; text-transform: uppercase;
  color: var(--text-secondary); margin-top: 4px;
  font-weight: 600;
}

/* ── Glass Card ── */
.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  padding: 28px;
  box-shadow:
    0 8px 32px rgba(0,0,0,0.3),
    inset 0 1px 0 rgba(255,255,255,0.05);
}

/* ── Puzzle Grid ── */
.grid-wrapper {
  position: relative;
  display: inline-block;
}
.grid-wrapper::before {
  content: '';
  position: absolute; inset: -2px; border-radius: 26px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
  opacity: 0.3; z-index: -1;
  filter: blur(1px);
}
.puzzle-grid {
  display: grid;
  grid-template-columns: repeat(3, 110px);
  grid-template-rows: repeat(3, 110px);
  gap: 8px;
  position: relative;
}

/* ── Tiles ── */
.tile {
  width: 110px; height: 110px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: 36px; font-weight: 700;
  color: #fff;
  cursor: pointer;
  position: relative;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.35s ease;
  will-change: transform;
  border: 1px solid rgba(255,255,255,0.1);
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.tile:hover:not(.empty):not(.solving) {
  transform: translateY(-4px) scale(1.03);
  z-index: 10;
}
.tile:active:not(.empty):not(.solving) {
  transform: translateY(-1px) scale(0.98);
}

.tile.empty {
  background: rgba(0,0,0,0.3) !important;
  border: 2px dashed rgba(255,255,255,0.06);
  box-shadow: inset 0 4px 12px rgba(0,0,0,0.4) !important;
  cursor: default;
}

/* Tile Gradients */
.tile-1 { background: linear-gradient(135deg, #1e88e5, #1565c0); box-shadow: 0 4px 20px rgba(30,136,229,0.35); }
.tile-2 { background: linear-gradient(135deg, #43a047, #2e7d32); box-shadow: 0 4px 20px rgba(67,160,71,0.35); }
.tile-3 { background: linear-gradient(135deg, #e53935, #c62828); box-shadow: 0 4px 20px rgba(229,57,53,0.35); }
.tile-4 { background: linear-gradient(135deg, #8e24aa, #6a1b9a); box-shadow: 0 4px 20px rgba(142,36,170,0.35); }
.tile-5 { background: linear-gradient(135deg, #f4511e, #d84315); box-shadow: 0 4px 20px rgba(244,81,30,0.35); }
.tile-6 { background: linear-gradient(135deg, #00acc1, #00838f); box-shadow: 0 4px 20px rgba(0,172,193,0.35); }
.tile-7 { background: linear-gradient(135deg, #d81b60, #ad1457); box-shadow: 0 4px 20px rgba(216,27,96,0.35); }
.tile-8 { background: linear-gradient(135deg, #5e35b1, #4527a0); box-shadow: 0 4px 20px rgba(94,53,177,0.35); }

.tile-1:hover:not(.solving) { box-shadow: 0 8px 30px rgba(30,136,229,0.5); }
.tile-2:hover:not(.solving) { box-shadow: 0 8px 30px rgba(67,160,71,0.5); }
.tile-3:hover:not(.solving) { box-shadow: 0 8px 30px rgba(229,57,53,0.5); }
.tile-4:hover:not(.solving) { box-shadow: 0 8px 30px rgba(142,36,170,0.5); }
.tile-5:hover:not(.solving) { box-shadow: 0 8px 30px rgba(244,81,30,0.5); }
.tile-6:hover:not(.solving) { box-shadow: 0 8px 30px rgba(0,172,193,0.5); }
.tile-7:hover:not(.solving) { box-shadow: 0 8px 30px rgba(216,27,96,0.5); }
.tile-8:hover:not(.solving) { box-shadow: 0 8px 30px rgba(94,53,177,0.5); }

/* ── Slide Animation ── */
.tile.sliding {
  transition: none !important;
  animation: tile-slide 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  z-index: 20;
}

/* ── Info Panel ── */
.info-panel {
  display: flex; gap: 24px; justify-content: center;
  flex-wrap: wrap;
}
.info-item {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
}
.info-item .label {
  font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
  color: var(--text-secondary); font-weight: 600;
}
.info-item .value {
  font-family: var(--font-display); font-size: 28px; font-weight: 700;
}
.info-item .value.cyan { color: var(--accent-cyan); text-shadow: 0 0 20px rgba(0,229,255,0.3); }
.info-item .value.purple { color: var(--accent-purple); text-shadow: 0 0 20px rgba(168,85,247,0.3); }
.info-item .value.pink { color: var(--accent-pink); text-shadow: 0 0 20px rgba(236,72,153,0.3); }

/* ── Status Bar ── */
.status-bar {
  text-align: center;
  min-height: 28px;
}
.status-text {
  font-size: 13px; font-weight: 600;
  letter-spacing: 1px;
  display: inline-flex; align-items: center; gap: 8px;
}
.status-text .dot {
  width: 8px; height: 8px; border-radius: 50%;
  display: inline-block;
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
.status-ready .dot { background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); }
.status-ready { color: var(--accent-green); }
.status-solving .dot { background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan); }
.status-solving { color: var(--accent-cyan); }
.status-solved .dot { background: var(--accent-gold); box-shadow: 0 0 8px var(--accent-gold); }
.status-solved { color: var(--accent-gold); }

/* ── Progress Bar ── */
.progress-container {
  width: 100%; height: 4px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px; overflow: hidden;
  margin-top: 8px;
  opacity: 0; transition: opacity 0.3s;
}
.progress-container.active { opacity: 1; }
.progress-bar {
  height: 100%; width: 0%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
  border-radius: 2px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px var(--accent-cyan);
}

/* ── Buttons ── */
.controls {
  display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;
}
.btn {
  font-family: var(--font-body);
  font-size: 14px; font-weight: 700;
  padding: 14px 28px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
  display: inline-flex; align-items: center; gap: 8px;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative; overflow: hidden;
  -webkit-appearance: none;
}
.btn::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.btn:hover::before { opacity: 1; }
.btn:active { transform: scale(0.96); }

.btn-solve {
  background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(0,229,255,0.05));
  color: var(--accent-cyan);
  border-color: rgba(0,229,255,0.25);
}
.btn-solve:hover {
  box-shadow: 0 0 30px rgba(0,229,255,0.2), inset 0 0 30px rgba(0,229,255,0.05);
  transform: translateY(-2px);
  border-color: rgba(0,229,255,0.5);
}
.btn-shuffle {
  background: linear-gradient(135deg, rgba(236,72,153,0.15), rgba(236,72,153,0.05));
  color: var(--accent-pink);
  border-color: rgba(236,72,153,0.25);
}
.btn-shuffle:hover {
  box-shadow: 0 0 30px rgba(236,72,153,0.2), inset 0 0 30px rgba(236,72,153,0.05);
  transform: translateY(-2px);
  border-color: rgba(236,72,153,0.5);
}
.btn-reset {
  background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05));
  color: var(--accent-gold);
  border-color: rgba(251,191,36,0.25);
}
.btn-reset:hover {
  box-shadow: 0 0 30px rgba(251,191,36,0.2), inset 0 0 30px rgba(251,191,36,0.05);
  transform: translateY(-2px);
  border-color: rgba(251,191,36,0.5);
}
.btn:disabled {
  opacity: 0.3; cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* ── Confetti Canvas ── */
#confetti-canvas {
  position: fixed; inset: 0; z-index: 100;
  pointer-events: none;
}

/* ── Solved Celebration ── */
.puzzle-grid.solved .tile:not(.empty) {
  animation: solved-pulse 1.5s ease-in-out infinite alternate;
}
@keyframes solved-pulse {
  0% { transform: scale(1); }
  100% { transform: scale(1.02); }
}

/* ── Keyboard hint ── */
.keyboard-hint {
  font-size: 11px;
  color: var(--text-secondary);
  text-align: center;
  letter-spacing: 1px;
}
.keyboard-hint kbd {
  display: inline-block; padding: 2px 6px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px; font-size: 10px;
  font-family: var(--font-body);
}
</style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<canvas id="confetti-canvas"></canvas>

<div class="app">
  <!-- Header -->
  <div class="header">
    <h1>8 PUZZLE</h1>
    <div class="subtitle">Glassmorphic Solver Engine</div>
  </div>

  <!-- Info Panel -->
  <div class="info-panel">
    <div class="info-item">
      <span class="label">Moves</span>
      <span class="value cyan" id="moves-val">0</span>
    </div>
    <div class="info-item">
      <span class="label">Manhattan</span>
      <span class="value purple" id="manhattan-val">0</span>
    </div>
    <div class="info-item">
      <span class="label">Status</span>
      <span class="value pink" id="status-icon">●</span>
    </div>
  </div>

  <!-- Puzzle Board -->
  <div class="grid-wrapper glass-card">
    <div class="puzzle-grid" id="puzzle-grid"></div>
  </div>

  <!-- Status -->
  <div class="status-bar">
    <span class="status-text status-ready" id="status-text">
      <span class="dot"></span> READY
    </span>
    <div class="progress-container" id="progress-container">
      <div class="progress-bar" id="progress-bar"></div>
    </div>
  </div>

  <!-- Controls -->
  <div class="controls">
    <button class="btn btn-solve" id="btn-solve" onclick="solvePuzzle()">⚡ SOLVE</button>
    <button class="btn btn-shuffle" id="btn-shuffle" onclick="shuffleBoard()">✦ SHUFFLE</button>
    <button class="btn btn-reset" id="btn-reset" onclick="resetBoard()">↺ RESET</button>
  </div>

  <div class="keyboard-hint">
    Click tiles to move · <kbd>S</kbd> Solve · <kbd>R</kbd> Shuffle · <kbd>G</kbd> Goal
  </div>
</div>

<script>
// ── State ──
let board = [];
let moves = 0;
let solving = false;

// ── Init ──
async function init() {
  const result = await pywebview.api.get_state();
  const data = JSON.parse(result);
  board = data.board;
  document.getElementById('manhattan-val').textContent = data.manhattan;
  renderBoard();
}

// ── Render Board ──
function renderBoard(animate = false) {
  const grid = document.getElementById('puzzle-grid');
  grid.innerHTML = '';
  grid.classList.remove('solved');
  for (let i = 0; i < 9; i++) {
    const val = board[i];
    const tile = document.createElement('div');
    tile.className = `tile ${val === 0 ? 'empty' : `tile-${val}`}`;
    if (solving) tile.classList.add('solving');
    tile.textContent = val === 0 ? '' : val;
    tile.dataset.index = i;
    if (val !== 0) {
      tile.addEventListener('click', () => onTileClick(i));
    }
    if (animate) {
      tile.style.opacity = '0';
      tile.style.transform = 'scale(0.8)';
      setTimeout(() => {
        tile.style.transition = 'all 0.3s cubic-bezier(0.34,1.56,0.64,1)';
        tile.style.opacity = '1';
        tile.style.transform = 'scale(1)';
      }, i * 40);
    }
    grid.appendChild(tile);
  }
}

// ── Slide Animation ──
function slideTile(fromIdx, toIdx) {
  return new Promise(resolve => {
    const grid = document.getElementById('puzzle-grid');
    const tiles = grid.children;
    const fromTile = tiles[fromIdx];
    const toTile = tiles[toIdx];

    const fromRow = Math.floor(fromIdx / 3);
    const fromCol = fromIdx % 3;
    const toRow = Math.floor(toIdx / 3);
    const toCol = toIdx % 3;

    const dx = (toCol - fromCol) * (110 + 8);
    const dy = (toRow - fromRow) * (110 + 8);

    fromTile.style.transition = 'none';
    fromTile.style.zIndex = '20';
    fromTile.style.position = 'relative';

    requestAnimationFrame(() => {
      fromTile.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      fromTile.style.transform = `translate(${dx}px, ${dy}px)`;

      setTimeout(() => {
        fromTile.style.transition = 'none';
        fromTile.style.transform = '';
        fromTile.style.zIndex = '';
        fromTile.style.position = '';
        renderBoard();
        resolve();
      }, 320);
    });
  });
}

// ── Tile Click (Manual Move) ──
async function onTileClick(index) {
  if (solving) return;
  const result = await pywebview.api.manual_move(index);
  const data = JSON.parse(result);
  if (data.moved) {
    moves++;
    document.getElementById('moves-val').textContent = moves;
    document.getElementById('manhattan-val').textContent = data.manhattan;
    board = data.board;

    await slideTileByIndices(data.from_idx, data.to_idx);

    if (data.is_goal) {
      setStatus('solved', '🎉 SOLVED!');
      celebrate();
    }
  }
}

function slideTileByIndices(fromIdx, toIdx) {
  return new Promise(resolve => {
    const grid = document.getElementById('puzzle-grid');
    const tiles = grid.children;

    // fromIdx is where the tile WAS (now it's in board at toIdx)
    const fromTile = tiles[fromIdx];
    const fromRow = Math.floor(fromIdx / 3);
    const fromCol = fromIdx % 3;
    const toRow = Math.floor(toIdx / 3);
    const toCol = toIdx % 3;
    const dx = (toCol - fromCol) * (110 + 8);
    const dy = (toRow - fromRow) * (110 + 8);

    fromTile.style.transition = 'none';
    fromTile.style.zIndex = '20';
    fromTile.style.position = 'relative';

    requestAnimationFrame(() => {
      fromTile.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      fromTile.style.transform = `translate(${dx}px, ${dy}px)`;

      setTimeout(() => {
        fromTile.style.transition = 'none';
        fromTile.style.transform = '';
        fromTile.style.zIndex = '';
        fromTile.style.position = '';
        renderBoard();
        resolve();
      }, 320);
    });
  });
}

// ── Solve ──
async function solvePuzzle() {
  if (solving) return;

  // Check if already at goal
  if (board.every((v, i) => v === (i === 8 ? 0 : i + 1))) {
    setStatus('solved', '✅ ALREADY SOLVED');
    return;
  }

  solving = true;
  setButtonsDisabled(true);
  setStatus('solving', '🔍 SEARCHING...');

  const result = await pywebview.api.solve();
  const data = JSON.parse(result);

  if (!data.solution) {
    setStatus('ready', '❌ NO SOLUTION');
    solving = false;
    setButtonsDisabled(false);
    return;
  }

  const steps = data.solution;
  const total = data.total;
  const progress = document.getElementById('progress-container');
  const bar = document.getElementById('progress-bar');
  progress.classList.add('active');

  setStatus('solving', `⚡ SOLVING 0/${total}`);

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    board = step.board;

    // Update progress
    const pct = ((i + 1) / total * 100).toFixed(0);
    bar.style.width = pct + '%';
    setStatus('solving', `⚡ Step ${i + 1}/${total}`);
    document.getElementById('manhattan-val').textContent =
      board.every((v, idx) => v === (idx === 8 ? 0 : idx + 1)) ? 0 :
      '...';

    // Slide animation
    await slideTileByIndices(step.from_idx, step.to_idx);
    moves++;
    document.getElementById('moves-val').textContent = moves;

    // Small delay between steps
    await sleep(80);
  }

  progress.classList.remove('active');
  bar.style.width = '0%';
  solving = false;
  setButtonsDisabled(false);
  document.getElementById('manhattan-val').textContent = '0';
  setStatus('solved', `🎉 SOLVED in ${total} moves!`);
  document.getElementById('puzzle-grid').classList.add('solved');
  celebrate();
}

// ── Shuffle ──
async function shuffleBoard() {
  if (solving) return;
  const result = await pywebview.api.shuffle();
  const data = JSON.parse(result);
  board = data.board;
  moves = 0;
  document.getElementById('moves-val').textContent = '0';
  document.getElementById('manhattan-val').textContent = data.manhattan;
  renderBoard(true);
  setStatus('ready', '✦ SHUFFLED');
}

// ── Reset ──
async function resetBoard() {
  if (solving) return;
  const result = await pywebview.api.reset();
  const data = JSON.parse(result);
  board = data.board;
  moves = 0;
  document.getElementById('moves-val').textContent = '0';
  document.getElementById('manhattan-val').textContent = '0';
  renderBoard(true);
  setStatus('solved', '🏁 GOAL STATE');
}

// ── Helpers ──
function setStatus(type, text) {
  const el = document.getElementById('status-text');
  el.className = `status-text status-${type}`;
  el.innerHTML = `<span class="dot"></span> ${text}`;
}

function setButtonsDisabled(disabled) {
  document.getElementById('btn-solve').disabled = disabled;
  document.getElementById('btn-shuffle').disabled = disabled;
  document.getElementById('btn-reset').disabled = disabled;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Keyboard Shortcuts ──
document.addEventListener('keydown', (e) => {
  if (e.key === 's' || e.key === 'S') solvePuzzle();
  else if (e.key === 'r' || e.key === 'R') shuffleBoard();
  else if (e.key === 'g' || e.key === 'G') resetBoard();
});

// ── Confetti ── 
function celebrate() {
  const canvas = document.getElementById('confetti-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = [];
  const colors = ['#00e5ff', '#a855f7', '#ec4899', '#34d399', '#fbbf24', '#f43f5e', '#3b82f6'];

  for (let i = 0; i < 150; i++) {
    particles.push({
      x: canvas.width / 2 + (Math.random() - 0.5) * 200,
      y: canvas.height / 2,
      vx: (Math.random() - 0.5) * 16,
      vy: (Math.random() - 1) * 18 - 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      size: Math.random() * 8 + 3,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 12,
      gravity: 0.35 + Math.random() * 0.15,
      opacity: 1,
      decay: 0.008 + Math.random() * 0.008,
      shape: Math.random() > 0.5 ? 'rect' : 'circle'
    });
  }

  let frame = 0;
  function animateConfetti() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let alive = false;
    for (const p of particles) {
      if (p.opacity <= 0) continue;
      alive = true;
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.vx *= 0.99;
      p.rotation += p.rotationSpeed;
      p.opacity -= p.decay;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation * Math.PI / 180);
      ctx.globalAlpha = Math.max(0, p.opacity);
      ctx.fillStyle = p.color;
      if (p.shape === 'rect') {
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      } else {
        ctx.beginPath();
        ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
    frame++;
    if (alive && frame < 300) {
      requestAnimationFrame(animateConfetti);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }
  animateConfetti();
}

// ── Boot ──
window.addEventListener('pywebviewready', init);
</script>
</body>
</html>
"""

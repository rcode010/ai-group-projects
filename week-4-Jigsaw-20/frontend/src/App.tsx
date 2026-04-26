import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from './api';
import type { Piece, Generation, GenerationDetail } from './api';
import './App.css';

// ─── Types ────────────────────────────────────────────────────────────────────

interface Status {
  isSolving: boolean;
  generation: number;
  fitness: number;       // 0–100
  totalSaved: number;
}

interface ToastMsg {
  text: string;
  kind: 'success' | 'error';
}

// ─── Helper: build the ordered image array from pieces + arrangement ──────────

function buildImages(
  pieces: Piece[],
  arrangement: number[],           // arrangement[position] = piece_id
): string[] {
  const map: Record<number, string> = {};
  for (const p of pieces) map[p.piece_id] = p.image_data;
  return arrangement.map((id) => map[id] ?? '');
}

// ─── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  // Puzzle state
  const [pieces, setPieces]         = useState<Piece[]>([]);
  const [boardImages, setBoardImages] = useState<string[]>([]); // 400 base64 strings, index = board position
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [activeGenId, setActiveGenId] = useState<number | null>(null);
  const [fileName, setFileName]     = useState('');

  // Solver status
  const [status, setStatus] = useState<Status>({
    isSolving: false,
    generation: 0,
    fitness: 0,
    totalSaved: 0,
  });

  // Toast
  const [toast, setToast] = useState<ToastMsg | null>(null);

  // Refs
  const fileInputRef   = useRef<HTMLInputElement>(null);
  const intervalRef    = useRef<ReturnType<typeof setInterval> | null>(null);
  const prevSavedRef   = useRef(0);   // tracks last known total_generations_saved

  // ── Toast helper ────────────────────────────────────────────────────────────
  function showToast(text: string, kind: ToastMsg['kind'] = 'success') {
    setToast({ text, kind });
    setTimeout(() => setToast(null), 3000);
  }

  // ── Upload ──────────────────────────────────────────────────────────────────
  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const { pieces: newPieces, initial_arrangement } = await api.uploadImage(file);
      setPieces(newPieces);
      setBoardImages(buildImages(newPieces, initial_arrangement));
      setGenerations([]);
      setActiveGenId(null);
      prevSavedRef.current = 0;
      setStatus({ isSolving: false, generation: 0, fitness: 0, totalSaved: 0 });
      setFileName(file.name);
      showToast(`Loaded "${file.name}" — 400 pieces ready`);
    } catch (err) {
      showToast((err as Error).message || 'Upload failed', 'error');
    }
  }

  // ── Start ───────────────────────────────────────────────────────────────────
  async function handleStart() {
    try {
      await api.startSolving();
      setStatus((s) => ({ ...s, isSolving: true }));
      showToast('Solver started');
    } catch (err) {
      showToast((err as Error).message || 'Could not start', 'error');
    }
  }

  // ── Stop ────────────────────────────────────────────────────────────────────
  async function handleStop() {
    try {
      await api.stopSolving();
      setStatus((s) => ({ ...s, isSolving: false }));
      showToast('Solver stopped');
    } catch {
      showToast('Could not stop', 'error');
    }
  }

  // ── Load Best ───────────────────────────────────────────────────────────────
  async function handleLoadBest() {
    try {
      const best = await api.getCurrentBest();
      if (!best) { showToast('No solutions yet', 'error'); return; }
      setBoardImages(best.images);
      setActiveGenId(best.generation);
      showToast(`Best — Gen ${best.generation}, Fitness: ${best.fitness.toFixed(2)}%`);
    } catch {
      showToast('Failed to load best', 'error');
    }
  }

  // ── Reset ───────────────────────────────────────────────────────────────────
  async function handleReset() {
    try {
      await api.reset();
    } catch { /* ignore */ }
    setPieces([]);
    setBoardImages([]);
    setGenerations([]);
    setActiveGenId(null);
    setFileName('');
    prevSavedRef.current = 0;
    setStatus({ isSolving: false, generation: 0, fitness: 0, totalSaved: 0 });
    if (fileInputRef.current) fileInputRef.current.value = '';
    showToast('Reset complete');
  }

  // ── Click history entry ──────────────────────────────────────────────────────
  async function handleLoadGen(genId: number) {
    try {
      const detail: GenerationDetail = await api.getGenerationDetail(genId);
      setBoardImages(detail.images);
      setActiveGenId(detail.generation);
      showToast(`Gen ${detail.generation} — Fitness: ${detail.fitness.toFixed(2)}%`);
    } catch {
      showToast('Failed to load generation', 'error');
    }
  }

  // ── Poll status every 500 ms while solving ───────────────────────────────────
  const poll = useCallback(async () => {
    try {
      const s = await api.getStatus();

      setStatus({
        isSolving: s.is_solving,
        generation: s.current_generation,
        fitness: s.best_fitness,
        totalSaved: s.total_generations_saved,
      });

      // Fetch generation history list whenever a new entry appears
      if (s.total_generations_saved > prevSavedRef.current) {
        prevSavedRef.current = s.total_generations_saved;

        // Refresh history list
        const gens = await api.getGenerations();
        setGenerations(gens);

        // Auto-show current best on the board
        const best = await api.getCurrentBest();
        if (best) {
          setBoardImages(best.images);
          setActiveGenId(best.generation);
        }
      }

      // If solver just finished, do one final history refresh
      if (!s.is_solving && s.total_generations_saved > 0) {
        const gens = await api.getGenerations();
        setGenerations(gens);
      }
    } catch {
      // network hiccup — ignore silently
    }
  }, []);

  useEffect(() => {
    if (status.isSolving) {
      intervalRef.current = setInterval(poll, 500);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [status.isSolving, poll]);

  // ─── Board dimensions ────────────────────────────────────────────────────────
  const BOARD_PX = Math.min(window.innerWidth - 340, window.innerHeight - 100, 640);

  // ─── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="layout">

      {/* ── Header ── */}
      <header className="header">
        <h1>🧩 Jigsaw Puzzle GA Solver</h1>
        <p>Genetic Algorithm · 20 × 20 grid · 400 pieces</p>
      </header>

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-inner">

          {/* Upload */}
          <div className="section">
            <div className="section-title">Upload Image</div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleUpload}
            />
            <div
              className={`upload-zone${fileName ? ' has-file' : ''}`}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-icon">📁</div>
              <div>{fileName ? 'Click to change image' : 'Click to upload an image'}</div>
              {fileName && <div className="upload-filename">{fileName}</div>}
            </div>
          </div>

          {/* Controls */}
          <div className="section">
            <div className="section-title">Controls</div>
            <div className="btn-group">
              <button
                className="btn btn-start"
                onClick={handleStart}
                disabled={pieces.length === 0 || status.isSolving}
              >
                {status.isSolving
                  ? <><span className="spinner" /> Solving…</>
                  : '▶ Start Solving'}
              </button>
              <button
                className="btn btn-stop"
                onClick={handleStop}
                disabled={!status.isSolving}
              >
                ⏹ Stop
              </button>
              <button
                className="btn btn-best"
                onClick={handleLoadBest}
                disabled={generations.length === 0}
              >
                🏆 Load Best
              </button>
              <button className="btn btn-reset" onClick={handleReset}>
                🔄 Reset
              </button>
            </div>

            {/* Status */}
            <div className="status-box">
              <div className="status-row">
                <span className="status-label">Status</span>
                <span className={`status-val ${status.isSolving ? 'solving' : 'idle'}`}>
                  {status.isSolving ? '🔄 Solving' : '⏸ Idle'}
                </span>
              </div>
              <div className="status-row">
                <span className="status-label">Generation</span>
                <span className="status-val">{status.generation}</span>
              </div>
              <div className="status-row">
                <span className="status-label">Best Fitness</span>
                <span className="status-val fitness-val">{status.fitness.toFixed(2)}%</span>
              </div>
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${Math.min(status.fitness, 100)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Generation history */}
          <div className="gen-section">
            <div className="gen-section-header">
              Generation History ({generations.length})
            </div>
            <div className="gen-list">
              {generations.length === 0 ? (
                <div className="gen-empty">
                  Start solving to see history
                </div>
              ) : (
                [...generations].reverse().map((g) => (
                  <div
                    key={g.id}
                    className={`gen-item${activeGenId === g.id ? ' active' : ''}`}
                    onClick={() => handleLoadGen(g.id)}
                  >
                    <div className="gen-label">Gen {g.generation} — Fitness: {g.fitness.toFixed(2)}%</div>
                    <div className="gen-sub">Click to view board</div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </aside>

      {/* ── Board ── */}
      <main className="board-area">
        {boardImages.length === 0 ? (
          <div className="board-empty">
            <div className="board-empty-icon">🧩</div>
            <h2>No puzzle loaded</h2>
            <p>Upload an image to create the 20 × 20 board</p>
          </div>
        ) : (
          <div
            className="puzzle-board"
            style={{ width: BOARD_PX, height: BOARD_PX }}
          >
            {boardImages.map((img, i) => (
              <div
                key={i}
                className="piece"
                style={{ backgroundImage: `url(data:image/jpeg;base64,${img})` }}
                title={`Position ${i}`}
              />
            ))}
          </div>
        )}
      </main>

      {/* ── Toast ── */}
      {toast && (
        <div className={`toast ${toast.kind}`}>
          {toast.kind === 'success' ? '✅' : '❌'} {toast.text}
        </div>
      )}

    </div>
  );
}

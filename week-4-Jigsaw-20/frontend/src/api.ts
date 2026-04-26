const API_BASE = 'http://localhost:8000/api';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Piece {
  piece_id: number;
  original_row: number;
  original_col: number;
  image_data: string; // base64, no prefix
}

export interface Generation {
  id: number;
  generation: number;
  fitness: number;
}

export interface GenerationDetail {
  generation: number;
  fitness: number;
  chromosome: number[];
  images: string[]; // base64 array, index = board position
}

export interface SolveStatus {
  is_solving: boolean;
  current_generation: number;
  best_fitness: number;
  total_generations_saved: number;
}

// ─── API client ───────────────────────────────────────────────────────────────

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      (body as { detail?: string }).detail ?? `HTTP ${res.status}`
    );
  }

  return res.json() as Promise<T>;
}

export const api = {
  // POST /api/upload — upload image
  async uploadImage(file: File): Promise<{ pieces: Piece[]; initial_arrangement: number[] }> {
    const form = new FormData();
    form.append('file', file);

    const data = await request<{
      pieces: Piece[];
      initial_arrangement: number[];
    }>(`${API_BASE}/upload`, {
      method: 'POST',
      body: form,
    });

    return {
      pieces: data.pieces,
      initial_arrangement: data.initial_arrangement,
    };
  },

  // POST /api/solve/start
  async startSolving(): Promise<void> {
    await request(`${API_BASE}/solve/start`, {
      method: 'POST',
    });
  },

  // POST /api/solve/stop
  async stopSolving(): Promise<void> {
    await fetch(`${API_BASE}/solve/stop`, {
      method: 'POST',
    });
  },

  // GET /api/solve/status
  async getStatus(): Promise<SolveStatus> {
    return request<SolveStatus>(`${API_BASE}/solve/status`);
  },

  // GET /api/generations
  async getGenerations(): Promise<Generation[]> {
    const data = await request<{ generations: Generation[] }>(
      `${API_BASE}/generations`
    );
    return data.generations;
  },

  // GET /api/generations/{id}
  async getGenerationDetail(genId: number): Promise<GenerationDetail> {
    return request<GenerationDetail>(
      `${API_BASE}/generations/${genId}`
    );
  },

  // GET /api/current-best
  async getCurrentBest(): Promise<GenerationDetail | null> {
    const data = await request<
      GenerationDetail & { message?: string }
    >(`${API_BASE}/current-best`);

    if ('message' in data) return null;
    return data;
  },

  // DELETE /api/reset
  async reset(): Promise<void> {
    await fetch(`${API_BASE}/reset`, {
      method: 'DELETE',
    });
  },
};
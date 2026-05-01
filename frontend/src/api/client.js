// Thin API client. The Vite dev server proxies /api → http://localhost:8000
// (see vite.config.js), so we can use a relative URL in dev.
const API_BASE =
  import.meta.env.VITE_API_BASE ?? ""; // empty = same origin (proxied in dev)

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function fetchModels() {
  const res = await fetch(`${API_BASE}/api/models`);
  if (!res.ok) throw new Error(`/api/models failed: ${res.status}`);
  return res.json();
}

export async function predictImage(file) {
  const form = new FormData();
  form.append("image", file);

  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = `Prediction failed (${res.status})`;
    try {
      const data = await res.json();
      if (data?.detail) detail = data.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  return res.json();
}

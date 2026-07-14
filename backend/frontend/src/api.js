import axios from "axios";

// In dev, Vite proxies /api -> http://localhost:5000 (see vite.config.js).
// In production, the Flask app serves the built frontend itself, so
// relative /api paths resolve to the same origin automatically.
const client = axios.create({ baseURL: "/api" });

export async function fetchPrices(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;
  const res = await client.get("/prices", { params });
  return res.data;
}

export async function fetchChangePoints() {
  const res = await client.get("/change-points");
  return res.data;
}

export async function fetchEvents(start, end, category) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;
  if (category) params.category = category;
  const res = await client.get("/events", { params });
  return res.data;
}

export async function fetchStats(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;
  const res = await client.get("/stats", { params });
  return res.data;
}

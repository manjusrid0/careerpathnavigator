// CareerRecommendations.jsx
// Usage: <CareerRecommendations userProfile={...} apiUrl="http://localhost:5000/recommend" />

import React, { useEffect, useState } from "react";

export default function CareerRecommendations({ userProfile, apiUrl = "/recommend" }) {
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState([]);
  const [error, setError] = useState(null);
  const [topK, setTopK] = useState(5);

  useEffect(() => {
    // auto-fetch when component mounts or when userProfile changes
    if (!userProfile) return;
    fetchRecommendations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userProfile, topK]);

  async function fetchRecommendations() {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile: userProfile, top_k: topK })
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data?.message || "Failed to fetch recommendations");
      }
      setRecs(data.recommendations || []);
    } catch (err) {
      console.error("Recommendation error:", err);
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 bg-white rounded-2xl shadow-md">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">AI Career Recommendations</h2>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-500">Top</label>
          <select
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            className="border rounded px-2 py-1"
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={8}>8</option>
            <option value={10}>10</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="text-center py-6">
          <div className="inline-block animate-pulse">Loading recommendations...</div>
        </div>
      )}

      {error && (
        <div className="text-red-600 bg-red-50 p-3 rounded mb-3">{error}</div>
      )}

      {!loading && !error && recs.length === 0 && (
        <div className="text-gray-500">No recommendations yet. Try updating your profile or refresh.</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recs.map((r) => (
          <div key={r.id} className="p-4 bg-gradient-to-br from-white to-gray-50 rounded-xl border shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-medium">{r.title}</h3>
                <div className="text-xs text-gray-500 mt-1">{r.industry} • {r.level}</div>
              </div>
              <div className="text-sm text-green-600 font-semibold">{(r.score ?? 0).toFixed(2)}</div>
            </div>
            <p className="mt-3 text-sm text-gray-700">{r.description}</p>

            {r.skills && r.skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {r.skills.map((s) => (
                  <span key={s} className="text-xs px-2 py-1 bg-gray-100 rounded-full">{s}</span>
                ))}
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => navigator.clipboard.writeText(JSON.stringify(r))}
                className="px-3 py-1 text-sm rounded-md border hover:bg-gray-50"
              >
                Copy JSON
              </button>
              <button
                onClick={() => alert(`Saved ${r.title} to saved paths (implement backend).`)}
                className="px-3 py-1 text-sm rounded-md bg-indigo-600 text-white hover:opacity-95"
              >
                Save Path
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

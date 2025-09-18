"""
ai_recommender.py

Flask app exposing an AI Career Recommendation endpoint.
- Recommender is content-based (TF-IDF over job descriptions + metadata)
- Design: Recommender class (fit / update / recommend), clear config, minimal dependencies.
- Extensible: replace TF-IDF with embeddings or add collaborative filtering.

Run:
    pip install -r requirements.txt
    python ai_recommender.py

Endpoint:
    POST /recommend  -> JSON { "profile": { ... }, "top_k": 5 }
"""

import json
from typing import List, Dict, Any
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from dataclasses import dataclass, field
from functools import lru_cache
import os

# ---------- Configuration ----------
@dataclass
class Config:
    DATA_PATH: str = os.getenv("JOBS_JSON", "jobs_sample.json")  # jobs dataset
    TOP_K_DEFAULT: int = 5
    MAX_FEATURES: int = 10000  # for TF-IDF

# ---------- Recommender Class ----------
class Recommender:
    def __init__(self, config: Config = Config()):
        self.config = config
        self.jobs_df: pd.DataFrame = pd.DataFrame()
        self.vectorizer = TfidfVectorizer(max_features=self.config.MAX_FEATURES, stop_words='english')
        self.job_tfidf = None  # TF-IDF matrix for job corpus
        self._prepared = False

    def load_jobs(self, jobs: List[Dict[str, Any]]):
        """
        jobs: list of dicts, each with keys: id, title, description, skills (list), industry, level
        """
        self.jobs_df = pd.DataFrame(jobs)
        # canonicalize textual field used for content matching
        self.jobs_df['content_for_matching'] = (
            self.jobs_df['title'].fillna('') + ' . ' +
            self.jobs_df['description'].fillna('') + ' . ' +
            self.jobs_df['skills'].apply(lambda s: ' '.join(s) if isinstance(s, list) else str(s)).fillna('')
        )
        self._prepared = False

    def fit(self):
        """Fit TF-IDF on job corpus"""
        if self.jobs_df.empty:
            raise ValueError("No jobs loaded. Call load_jobs first.")
        corpus = self.jobs_df['content_for_matching'].tolist()
        self.job_tfidf = self.vectorizer.fit_transform(corpus)
        self._prepared = True

    def update_jobs(self, jobs: List[Dict[str, Any]]):
        """Replace dataset and refit (could be extended to incremental)."""
        self.load_jobs(jobs)
        self.fit()

    def profile_to_text(self, profile: Dict[str, Any]) -> str:
        """
        Convert a user profile to a single text string for matching.
        Profile example:
            {
                "education": "B.Sc Computer Science",
                "experience_years": 1,
                "skills": ["python", "sql"],
                "interests": ["data science", "web dev"],
                "preferred_industries": ["education", "healthcare"]
            }
        """
        parts = []
        if 'education' in profile: parts.append(str(profile['education']))
        if 'experience_years' in profile: parts.append(f"{profile['experience_years']} years experience")
        if 'skills' in profile and isinstance(profile['skills'], list): parts.append(' '.join(profile['skills']))
        if 'interests' in profile and isinstance(profile['interests'], list): parts.append(' '.join(profile['interests']))
        if 'preferred_industries' in profile and isinstance(profile['preferred_industries'], list): parts.append(' '.join(profile['preferred_industries']))
        if 'summary' in profile: parts.append(profile['summary'])
        return ' . '.join(parts)

    @lru_cache(maxsize=1024)
    def _compute_similarity(self, profile_text: str) -> np.ndarray:
        """
        Compute similarity vector between the profile and all jobs.
        This function is cached for repeated identical requests.
        """
        if not self._prepared:
            raise RuntimeError("Recommender not fitted. Call fit() after load_jobs().")
        profile_vec = self.vectorizer.transform([profile_text])
        # cosine similarity via linear_kernel (fast)
        sim = linear_kernel(profile_vec, self.job_tfidf).flatten()  # shape (n_jobs,)
        return sim

    def recommend(self, profile: Dict[str, Any], top_k: int = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Returns top_k job recommendations (list of job dicts with score).
        filters: optional dict to filter jobs, e.g. {"level": "entry", "industry": "education"}
        """
        if top_k is None:
            top_k = self.config.TOP_K_DEFAULT

        profile_text = self.profile_to_text(profile)
        similarity_scores = self._compute_similarity(profile_text)

        df = self.jobs_df.copy()
        df['score'] = similarity_scores

        # Apply filters if provided
        if filters:
            for key, val in filters.items():
                if isinstance(val, (list, tuple, set)):
                    df = df[df[key].isin(val)]
                else:
                    df = df[df[key] == val]

        # sort by score desc
        df_sorted = df.sort_values('score', ascending=False).head(top_k)

        # prepare output
        results = []
        for _, row in df_sorted.iterrows():
            results.append({
                "id": row.get("id"),
                "title": row.get("title"),
                "description": row.get("description"),
                "skills": row.get("skills"),
                "industry": row.get("industry"),
                "level": row.get("level"),
                "score": float(row.get("score", 0.0))
            })
        return results

# ---------- Sample dataset (for demonstration). In production, load from DB/CSV/API ----------
SAMPLE_JOBS = [
    {
        "id": "J001",
        "title": "Junior Data Analyst",
        "description": "Analyze datasets, create dashboards, support data-driven decisions.",
        "skills": ["excel", "sql", "python", "tableau"],
        "industry": "analytics",
        "level": "entry"
    },
    {
        "id": "J002",
        "title": "Frontend Web Developer",
        "description": "Develop responsive UI, HTML/CSS/JS, React-based web applications.",
        "skills": ["javascript", "react", "html", "css"],
        "industry": "software",
        "level": "entry"
    },
    {
        "id": "J003",
        "title": "Machine Learning Intern",
        "description": "Work on model training, data preprocessing, Python, scikit-learn, basic deep learning.",
        "skills": ["python", "scikit-learn", "pandas", "numpy"],
        "industry": "ai",
        "level": "internship"
    },
    {
        "id": "J004",
        "title": "UI/UX Designer",
        "description": "Design interfaces, create wireframes, prototyping and user research.",
        "skills": ["figma", "ux", "ui", "prototyping"],
        "industry": "design",
        "level": "entry"
    },
    {
        "id": "J005",
        "title": "Digital Marketing Associate",
        "description": "Manage social media campaigns, content strategy, SEO basics.",
        "skills": ["seo", "content", "social media"],
        "industry": "marketing",
        "level": "entry"
    }
]

# ---------- Flask App ----------
app = Flask(__name__)
config = Config()
recommender = Recommender(config=config)
recommender.load_jobs(SAMPLE_JOBS)
recommender.fit()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "jobs_loaded": len(recommender.jobs_df)}), 200

@app.route("/recommend", methods=["POST"])
def recommend_endpoint():
    """
    Expects JSON:
    {
        "profile": { ... },   # user profile dict
        "top_k": 5,           # optional
        "filters": { ... }    # optional
    }
    """
    payload = request.get_json(force=True)
    profile = payload.get("profile", {})
    top_k = payload.get("top_k", None)
    filters = payload.get("filters", None)

    try:
        recs = recommender.recommend(profile=profile, top_k=top_k, filters=filters)
        return jsonify({"status": "success", "recommendations": recs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# optional: endpoint to reload jobs (admin use)
@app.route("/admin/load_jobs", methods=["POST"])
def admin_load_jobs():
    payload = request.get_json(force=True)
    jobs = payload.get("jobs")
    if not jobs:
        return jsonify({"status": "error", "message": "jobs required"}), 400
    recommender.update_jobs(jobs)
    # clear cache (lru_cache wrapper replaced function won't clear automatically; recreate recommender for simplicity)
    recommender._compute_similarity.cache_clear()
    return jsonify({"status": "success", "loaded": len(recommender.jobs_df)}), 200

if __name__ == "__main__":
    # For local dev. Use gunicorn for production.
    app.run(host="0.0.0.0", port=5000, debug=True)

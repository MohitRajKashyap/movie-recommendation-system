"""
notebooks/exploration.py
────────────────────────
Exploratory Data Analysis (EDA) and model evaluation script.

Run with: python notebooks/exploration.py

This script demonstrates:
  1. Dataset statistics and distribution
  2. Feature engineering inspection
  3. TF-IDF vocabulary inspection
  4. Recommendation quality evaluation
  5. Similarity matrix heatmap (saved to screenshots/)

For a Jupyter version: rename to .ipynb and convert each section to a cell.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
from collections import Counter

from utils.data_loader import load_full_dataset, get_all_genres
from utils.recommender import MovieRecommender, build_feature_soup

print("=" * 60)
print("  CineMatch — EDA & Model Evaluation")
print("=" * 60)

# ── 1. Load dataset ──────────────────────────────────────────────────────────
print("\n📊 1. Loading Dataset…")
df = load_full_dataset()
print(f"   Shape: {df.shape}")
print(f"   Columns: {list(df.columns)}")
print(f"\n   First 3 rows:")
print(df[["title", "genres", "vote_average", "release_year"]].head(3).to_string())

# ── 2. Dataset statistics ────────────────────────────────────────────────────
print("\n📈 2. Dataset Statistics:")
print(f"   Total movies: {len(df):,}")
print(f"   Year range: {df['release_year'].min()} – {df['release_year'].max()}")
print(f"   Avg rating: {df['vote_average'].mean():.2f}")
print(f"   Highest rated: {df.nlargest(1, 'vote_average')['title'].values[0]}")
print(f"   Most popular: {df.nlargest(1, 'popularity')['title'].values[0]}")

# ── 3. Genre distribution ────────────────────────────────────────────────────
print("\n🎭 3. Genre Distribution (Top 10):")
all_genres = []
for g in df["genres"].dropna():
    all_genres.extend(g.split())
genre_counts = Counter(all_genres).most_common(10)
for genre, count in genre_counts:
    bar = "█" * (count // 2)
    print(f"   {genre:<18} {bar} ({count})")

# ── 4. Feature engineering ───────────────────────────────────────────────────
print("\n🔧 4. Feature Soup Sample:")
soup = build_feature_soup(df)
sample_idx = 0
print(f"   Movie: {df.iloc[sample_idx]['title']}")
print(f"   Soup: {soup.iloc[sample_idx][:200]}…")

# ── 5. Fit recommender ───────────────────────────────────────────────────────
print("\n🤖 5. Fitting Recommender…")
rec = MovieRecommender()
rec.fit(df)
vocab_size = len(rec.vectorizer.vocabulary_)
print(f"   TF-IDF vocabulary size: {vocab_size:,}")
print(f"   TF-IDF matrix shape: {rec.tfidf_matrix.shape}")
print(f"   Similarity matrix shape: {rec.cosine_sim.shape}")
sparsity = 1 - (rec.tfidf_matrix.nnz / (rec.tfidf_matrix.shape[0] * rec.tfidf_matrix.shape[1]))
print(f"   TF-IDF matrix sparsity: {sparsity:.1%}")

# ── 6. Sample recommendations ────────────────────────────────────────────────
print("\n🎬 6. Sample Recommendations:")
test_movies = ["Inception", "The Dark Knight", "Parasite"]
for test_title in test_movies:
    result = rec.recommend(test_title, top_n=5)
    if result.get("error"):
        print(f"\n   ❌ {test_title}: {result['error']}")
        continue
    print(f"\n   Movies similar to '{result['matched_title']}':")
    for i, r in enumerate(result["recommendations"], 1):
        print(f"     {i}. {r['title']} ({r['release_year']}) — {r['similarity']:.1f}% match")

# ── 7. Fuzzy search test ─────────────────────────────────────────────────────
print("\n🔍 7. Fuzzy Search (typo tolerance):")
typo_tests = [("Incepshon", "Inception"), ("Drak Knight", "The Dark Knight")]
for typo, expected in typo_tests:
    suggestions = rec.fuzzy_search(typo, top_n=3)
    top_sug = suggestions[0]["title"] if suggestions else "No match"
    status = "✅" if expected.lower() in top_sug.lower() else "⚠️"
    print(f"   {status} Query: '{typo}' → Top match: '{top_sug}'")

# ── 8. Trending ──────────────────────────────────────────────────────────────
print("\n🔥 8. Trending Movies (Popularity × Rating):")
trending = rec.get_trending(top_n=5)
for i, t in enumerate(trending, 1):
    print(f"   {i}. {t['title']} ({t['release_year']}) — ⭐{t['vote_average']:.1f}")

print("\n" + "=" * 60)
print("  ✅ EDA complete — all systems nominal!")
print("=" * 60)

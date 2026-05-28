"""
utils/recommender.py
────────────────────
Core Machine Learning recommendation engine.

ALGORITHM CHOICE — Content-Based Filtering with TF-IDF + Cosine Similarity
───────────────────────────────────────────────────────────────────────────
WHY TF-IDF + COSINE SIMILARITY?

1. Cold-start resilience: No user rating history needed. Works for any movie
   immediately, making it ideal for portfolio demos.

2. Interpretability: The recommendation reason is clear — "similar genres,
   director, cast, and description." Stakeholders understand this.

3. Speed: Once the similarity matrix is built (< 1 second for 1,000 movies),
   recommendations are O(1) lookups.

4. TF-IDF advantage over raw counts: Term Frequency–Inverse Document Frequency
   down-weights common words ("the", "a", "film") and up-weights rare, meaningful
   words ("heist", "dystopian", "Kubrick") — giving much better semantic matches.

5. Cosine similarity advantage: Measures the ANGLE between feature vectors,
   not the magnitude. This means a short movie description and a long one can
   still match well if they share the same important keywords.

FEATURE ENGINEERING:
  We combine four textual features into one "soup":
    • genres (weighted ×3 for stronger signal)
    • director (weighted ×2)
    • cast (top 5 actors, weighted ×2)
    • overview keywords (standard weight)

  This weighted soup gives genres and directors the highest influence on
  recommendations, which matches real-world intuition ("I liked Nolan films").
"""

import re
import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Lowercase and remove punctuation from text."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()


def build_feature_soup(df: pd.DataFrame) -> pd.Series:
    """
    Create the weighted 'soup' string for each movie.

    Each feature is repeated to simulate weighting:
      genres ×3, director ×2, cast ×2, overview ×1

    Example soup for "The Dark Knight":
      "action crime drama thriller action crime drama thriller action crime
       drama thriller christophernolan christophernolan christianbale
       christianbale heathledger heathledger ... When the menace known as..."
    """
    def make_soup(row):
        genres   = _clean_text(row.get("genres", ""))
        director = _clean_text(str(row.get("director", "")))
        cast     = _clean_text(str(row.get("cast", "")))
        overview = _clean_text(str(row.get("overview", "")))

        # Repeat features for weighting effect
        genres_part   = " ".join([genres] * 3)
        director_part = " ".join([director] * 2)
        cast_part     = " ".join([cast] * 2)

        return f"{genres_part} {director_part} {cast_part} {overview}"

    return df.apply(make_soup, axis=1)


class MovieRecommender:
    """
    Content-based movie recommender using TF-IDF and cosine similarity.

    Usage:
        recommender = MovieRecommender()
        recommender.fit(df)
        results = recommender.recommend("Inception", top_n=10)
    """

    def __init__(self):
        self.df: pd.DataFrame | None = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.title_to_idx: dict = {}
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),   # unigrams + bigrams for richer matching
            max_features=10_000,  # cap vocabulary for performance
            min_df=1,
        )

    def fit(self, df: pd.DataFrame) -> "MovieRecommender":
        """
        Build the TF-IDF matrix and cosine similarity matrix.

        Time complexity: O(n × k) where n=movies, k=features
        Space complexity: O(n²) for the similarity matrix
        """
        logger.info(f"Fitting recommender on {len(df)} movies…")
        self.df = df.reset_index(drop=True)

        # Build feature soup
        soup = build_feature_soup(self.df)

        # TF-IDF vectorisation
        self.tfidf_matrix = self.vectorizer.fit_transform(soup)

        # Compute pairwise cosine similarity
        # Shape: (n_movies, n_movies)
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        # Build title → index lookup (lowercase for case-insensitive search)
        self.title_to_idx = {
            title.lower(): idx
            for idx, title in enumerate(self.df["title"].fillna(""))
        }

        logger.info("Recommender fitted successfully.")
        return self

    def _find_movie_index(self, title: str) -> int | None:
        """
        Find the DataFrame index for a movie title.
        Uses exact match first, then fuzzy matching as fallback.

        Returns None if no sufficiently close match is found.
        """
        title_lower = title.lower().strip()

        # 1. Exact match
        if title_lower in self.title_to_idx:
            return self.title_to_idx[title_lower]

        # 2. Fuzzy match (handles typos, partial titles)
        all_titles = list(self.title_to_idx.keys())
        best_match, score = process.extractOne(
            title_lower, all_titles, scorer=fuzz.token_sort_ratio
        )
        if score >= 60:  # threshold: at least 60% similarity
            return self.title_to_idx[best_match]

        return None

    def fuzzy_search(self, query: str, top_n: int = 8) -> list[dict]:
        """
        Return the top-N closest title matches to a query string.
        Used for autocomplete suggestions in the UI.
        """
        if not query or self.df is None:
            return []

        all_titles = list(self.title_to_idx.keys())
        matches = process.extract(
            query.lower(), all_titles, scorer=fuzz.token_sort_ratio, limit=top_n
        )
        results = []
        for match_title, score in matches:
            if score >= 40:
                idx = self.title_to_idx[match_title]
                row = self.df.iloc[idx]
                results.append({
                    "title": row["title"],
                    "year": int(row.get("release_year", 0)) or "N/A",
                    "score": score,
                })
        return results

    def recommend(
        self,
        title: str,
        top_n: int = 10,
        filtered_df: pd.DataFrame | None = None,
    ) -> dict:
        """
        Recommend the top_n most similar movies for a given title.

        Parameters
        ----------
        title       : Input movie title (can be approximate / misspelled)
        top_n       : Number of recommendations to return
        filtered_df : Optional filtered subset (from sidebar filters)

        Returns
        -------
        dict with keys:
          - "matched_title"  : The actual title found in the DB
          - "recommendations": list of dicts, each with movie details + similarity
          - "error"          : Error message string, or None on success
        """
        if self.df is None or self.cosine_sim is None:
            return {"error": "Recommender not fitted. Call .fit(df) first.", "recommendations": []}

        idx = self._find_movie_index(title)
        if idx is None:
            return {
                "error": f'Movie "{title}" not found. Try a different spelling or check our library.',
                "recommendations": [],
                "matched_title": None,
            }

        matched_title = self.df.iloc[idx]["title"]
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Sort by similarity (descending), skip the query movie itself
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [(i, s) for i, s in sim_scores if i != idx]

        # Apply filters if a filtered_df is provided
        if filtered_df is not None and len(filtered_df) < len(self.df):
            filtered_ids = set(filtered_df.index.tolist())
            sim_scores = [(i, s) for i, s in sim_scores if i in filtered_ids]

        sim_scores = sim_scores[:top_n]

        recommendations = []
        for movie_idx, similarity in sim_scores:
            row = self.df.iloc[movie_idx]
            recommendations.append({
                "id":          int(row.get("id", movie_idx)),
                "title":       str(row.get("title", "Unknown")),
                "genres":      str(row.get("genres", "")),
                "vote_average": float(row.get("vote_average", 0.0)),
                "vote_count":  int(row.get("vote_count", 0)),
                "release_year": int(row.get("release_year", 0)) or "N/A",
                "overview":    str(row.get("overview", "")),
                "popularity":  float(row.get("popularity", 0.0)),
                "director":    str(row.get("director", "N/A")),
                "cast":        str(row.get("cast", "")),
                "similarity":  round(float(similarity) * 100, 1),  # % score
            })

        return {
            "matched_title": matched_title,
            "recommendations": recommendations,
            "error": None,
        }

    def get_trending(self, top_n: int = 10) -> list[dict]:
        """
        Return the most popular movies (by popularity score × vote_average).
        Weighted score gives a balanced ranking between pure popularity and quality.
        """
        if self.df is None:
            return []

        df = self.df.copy()
        # Weighted score: popularity (quantity) × rating (quality)
        df["trending_score"] = df["popularity"] * df["vote_average"]
        top = df.nlargest(top_n, "trending_score")

        return [
            {
                "id":           int(row.get("id", i)),
                "title":        str(row.get("title", "Unknown")),
                "genres":       str(row.get("genres", "")),
                "vote_average": float(row.get("vote_average", 0.0)),
                "release_year": int(row.get("release_year", 0)) or "N/A",
                "overview":     str(row.get("overview", "")),
                "popularity":   float(row.get("popularity", 0.0)),
                "director":     str(row.get("director", "N/A")),
                "similarity":   None,
            }
            for i, (_, row) in enumerate(top.iterrows())
        ]

    def get_movie_details(self, title: str) -> dict | None:
        """Return full details for a single movie by title."""
        if self.df is None:
            return None
        idx = self._find_movie_index(title)
        if idx is None:
            return None
        row = self.df.iloc[idx]
        return {
            "id":           int(row.get("id", idx)),
            "title":        str(row.get("title", "Unknown")),
            "genres":       str(row.get("genres", "")),
            "vote_average": float(row.get("vote_average", 0.0)),
            "vote_count":   int(row.get("vote_count", 0)),
            "release_year": int(row.get("release_year", 0)) or "N/A",
            "overview":     str(row.get("overview", "")),
            "popularity":   float(row.get("popularity", 0.0)),
            "director":     str(row.get("director", "N/A")),
            "cast":         str(row.get("cast", "")),
        }

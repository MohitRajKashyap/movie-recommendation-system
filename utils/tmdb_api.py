"""
utils/tmdb_api.py
─────────────────
Handles all communication with The Movie Database (TMDB) API.

TMDB provides:
  • Movie posters and backdrops
  • Accurate ratings, vote counts, overviews
  • Search by title (useful for matching our dataset IDs to TMDB IDs)

API key setup:
  1. Sign up at https://www.themoviedb.org/
  2. Go to Settings → API → Create API Key (free)
  3. Add to .env file: TMDB_API_KEY=your_key_here

If no API key is set, the app gracefully falls back to a placeholder poster
image and uses the data from the local dataset.
"""

import os
import logging
import requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
BASE_URL     = "https://api.themoviedb.org/3"
IMAGE_BASE   = "https://image.tmdb.org/t/p/w500"

# Placeholder shown when no poster is available
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450/1a1a2e/e94560?text=No+Poster"

# Session for connection pooling (faster repeated requests)
_session = requests.Session()
_session.headers.update({"User-Agent": "MovieRecommendationSystem/1.0"})


def _api_get(endpoint: str, params: dict = None) -> dict | None:
    """
    Make a GET request to the TMDB API.
    Returns the parsed JSON dict or None on failure.
    """
    if not TMDB_API_KEY:
        return None

    url = f"{BASE_URL}/{endpoint}"
    params = params or {}
    params["api_key"] = TMDB_API_KEY

    try:
        resp = _session.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.debug(f"TMDB API error for {endpoint}: {e}")
        return None


@lru_cache(maxsize=512)
def search_movie_tmdb(title: str, year: int | None = None) -> dict | None:
    """
    Search TMDB for a movie by title.
    Returns the best-matching result dict or None.

    Results are cached (lru_cache) to avoid redundant API calls.
    """
    params = {"query": title, "include_adult": "false"}
    if year:
        params["year"] = year

    data = _api_get("search/movie", params)
    if data and data.get("results"):
        return data["results"][0]  # return the top result
    return None


@lru_cache(maxsize=512)
def get_movie_details_tmdb(tmdb_id: int) -> dict | None:
    """Fetch full movie details from TMDB by their internal movie ID."""
    return _api_get(f"movie/{tmdb_id}")


def get_poster_url(title: str, year: int | None = None, tmdb_id: int | None = None) -> str:
    """
    Return a poster image URL for the given movie.

    Priority:
      1. If tmdb_id is given, fetch directly by ID (fastest)
      2. If title is given, search TMDB and get poster from result
      3. Fall back to placeholder image

    The lru_cache on the underlying functions ensures we don't re-fetch.
    """
    if not TMDB_API_KEY:
        return PLACEHOLDER_POSTER

    movie_data = None

    if tmdb_id:
        movie_data = get_movie_details_tmdb(tmdb_id)

    if not movie_data:
        movie_data = search_movie_tmdb(title, year)

    if movie_data and movie_data.get("poster_path"):
        return f"{IMAGE_BASE}{movie_data['poster_path']}"

    return PLACEHOLDER_POSTER


def get_enriched_movie_data(title: str, year: int | None = None) -> dict:
    """
    Fetch enriched data from TMDB for a movie.
    Returns a dict with poster_url, tmdb_rating, tmdb_overview.
    Falls back gracefully if TMDB is unavailable.
    """
    defaults = {
        "poster_url":    PLACEHOLDER_POSTER,
        "tmdb_rating":   None,
        "tmdb_overview": None,
        "tmdb_id":       None,
    }

    if not TMDB_API_KEY:
        return defaults

    result = search_movie_tmdb(title, year)
    if not result:
        return defaults

    poster_path = result.get("poster_path")
    return {
        "poster_url":    f"{IMAGE_BASE}{poster_path}" if poster_path else PLACEHOLDER_POSTER,
        "tmdb_rating":   result.get("vote_average"),
        "tmdb_overview": result.get("overview"),
        "tmdb_id":       result.get("id"),
    }


def is_api_available() -> bool:
    """Check if the TMDB API key is configured and working."""
    if not TMDB_API_KEY:
        return False
    result = _api_get("configuration")
    return result is not None

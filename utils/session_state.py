"""
utils/session_state.py
──────────────────────
Manages Streamlit session state for:
  • Recently searched movies (last 10)
  • Saved / favourite movies (persisted in session)

Streamlit re-runs the entire script on every interaction. Session state
(st.session_state) is the standard way to persist data across re-runs.
"""

import streamlit as st


def init_session_state():
    """Initialise all session state keys with defaults (safe to call multiple times)."""
    defaults = {
        "search_history":    [],   # list of recently searched titles
        "favorites":         [],   # list of saved movie dicts
        "last_query":        "",   # last search query string
        "last_results":      [],   # last recommendation results
        "last_matched":      "",   # title matched in DB for last query
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Search history ─────────────────────────────────────────────────────────────

def add_to_history(title: str, max_items: int = 10):
    """Add a title to search history (avoid duplicates, cap at max_items)."""
    history = st.session_state.get("search_history", [])
    # Remove existing entry if present (to move it to top)
    history = [h for h in history if h.lower() != title.lower()]
    history.insert(0, title)
    st.session_state["search_history"] = history[:max_items]


def get_history() -> list[str]:
    """Return the list of recently searched titles."""
    return st.session_state.get("search_history", [])


def clear_history():
    """Clear the search history."""
    st.session_state["search_history"] = []


# ── Favourites ─────────────────────────────────────────────────────────────────

def add_to_favorites(movie: dict):
    """Save a movie to favourites (avoid duplicates by title)."""
    favs = st.session_state.get("favorites", [])
    titles = {f["title"] for f in favs}
    if movie["title"] not in titles:
        favs.append(movie)
        st.session_state["favorites"] = favs


def remove_from_favorites(title: str):
    """Remove a movie from favourites by title."""
    favs = st.session_state.get("favorites", [])
    st.session_state["favorites"] = [f for f in favs if f["title"] != title]


def get_favorites() -> list[dict]:
    """Return saved favourite movies."""
    return st.session_state.get("favorites", [])


def is_favorite(title: str) -> bool:
    """Check if a movie is in the favourites list."""
    return any(f["title"] == title for f in get_favorites())

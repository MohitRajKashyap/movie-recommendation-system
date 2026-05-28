"""
app.py
──────
CineMatch — AI-Powered Movie Recommendation System
Main Streamlit application entry point.

Run with:
    streamlit run app.py

Architecture:
  app.py              → Streamlit UI, tab routing, user interaction
  app/components.py   → Reusable UI widgets (cards, trending, filters)
  app/styles.py       → Dark-theme CSS injection
  utils/recommender.py→ TF-IDF + Cosine Similarity ML engine
  utils/data_loader.py→ Dataset loading, preprocessing, filtering
  utils/tmdb_api.py   → TMDB poster/metadata API integration
  utils/session_state.py → Search history + favourites management
"""

import streamlit as st

# ── Page config must be the FIRST Streamlit call ───────────────────────────
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ───────────────────────────────────────────────────────────
from app.styles import inject_css
from app.components import (
    render_movie_card,
    render_trending_section,
    render_sidebar_filters,
    render_history_section,
    render_favorites_section,
    render_stats_bar,
)
from utils.data_loader import load_full_dataset, get_all_genres, filter_movies
from utils.recommender import MovieRecommender
from utils.session_state import (
    init_session_state,
    add_to_history,
    get_history,
    clear_history,
    get_favorites,
)
from utils.tmdb_api import is_api_available

# ── Inject CSS ──────────────────────────────────────────────────────────────
inject_css()

# ── Initialise session state ────────────────────────────────────────────────
init_session_state()


# ── Cached resources (loaded once per session) ──────────────────────────────
@st.cache_resource(show_spinner=False)
def load_recommender() -> tuple[MovieRecommender, object]:
    """
    Load data and fit recommender — cached so it only runs once.

    st.cache_resource is used (not cache_data) because MovieRecommender
    is a stateful object that shouldn't be serialised/deserialised.
    """
    df = load_full_dataset()
    rec = MovieRecommender()
    rec.fit(df)
    return rec, df


# ── Load resources ──────────────────────────────────────────────────────────
with st.spinner("🎬 Loading CineMatch…"):
    recommender, full_df = load_recommender()

all_genres  = get_all_genres(full_df)
min_year    = int(full_df["release_year"].min())
max_year    = int(full_df["release_year"].max())
api_online  = is_api_available()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CineMatch")
    st.markdown(
        '<p style="color:#9b9bb4;font-size:0.8rem;">AI-powered movie recommendations</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    filters = render_sidebar_filters(all_genres, min_year, max_year)

    st.divider()

    # API status indicator
    if api_online:
        st.success("🟢 TMDB API connected — posters enabled", icon=None)
    else:
        st.warning(
            "🟡 TMDB API key not set.\n\n"
            "Add `TMDB_API_KEY` to `.env` for movie posters.\n\n"
            "[Get free API key →](https://www.themoviedb.org/settings/api)",
        )

    st.divider()
    st.markdown(
        f'<div style="color:#5a5a72;font-size:0.75rem;">📚 {len(full_df):,} movies in library</div>',
        unsafe_allow_html=True,
    )

# ── App header ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="app-header">'
    '<div class="app-logo">CINEMATCH</div>'
    '<div class="app-tagline">Discover your next favourite film · AI-powered recommendations</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Main tabs ────────────────────────────────────────────────────────────────
tab_search, tab_trending, tab_favorites = st.tabs(
    ["🔍 Recommend", "🔥 Trending", "❤️ Favourites"]
)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1: SEARCH & RECOMMEND
# ══════════════════════════════════════════════════════════════════════════════
with tab_search:

    # Search bar
    st.markdown("### Search a Movie")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        query = st.text_input(
            label="Movie title",
            placeholder="e.g. Inception, The Dark Knight, Parasite…",
            value=st.session_state.get("last_query", ""),
            key="search_input",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("🔍 Find", use_container_width=True)

    # Autocomplete suggestions (fuzzy search while typing)
    if query and len(query) >= 2:
        suggestions = recommender.fuzzy_search(query, top_n=6)
        if suggestions and query.lower() not in [s["title"].lower() for s in suggestions]:
            st.markdown("**Suggestions:**")
            sug_cols = st.columns(min(len(suggestions), 3))
            for i, sug in enumerate(suggestions[:3]):
                with sug_cols[i]:
                    label = f"🎬 {sug['title']} ({sug['year']})"
                    if st.button(label, key=f"sug_{i}_{sug['title'][:10]}"):
                        st.session_state["last_query"] = sug["title"]
                        st.rerun()

    # ── Recent searches ──────────────────────────────────────────────────────
    history = get_history()
    if history:
        render_history_section(history)
        if st.button("🗑️ Clear History", key="clear_hist"):
            clear_history()
            st.rerun()

    st.markdown("---")

    # ── Run recommendation ───────────────────────────────────────────────────
    run_query = query and (search_clicked or st.session_state.get("last_query") == query)

    # Also auto-run if triggered by trending/history button click
    if st.session_state.get("last_query") and not query:
        query = st.session_state["last_query"]
        run_query = True

    if run_query and query.strip():
        # Apply sidebar filters to narrow the search space
        filtered_df = filter_movies(
            full_df,
            genres=filters["genres"] or None,
            min_year=filters["min_year"],
            max_year=filters["max_year"],
            min_rating=filters["min_rating"],
        )

        with st.spinner(f"🤖 Finding movies similar to **{query}**…"):
            result = recommender.recommend(
                title=query,
                top_n=filters["top_n"],
                filtered_df=filtered_df if len(filtered_df) < len(full_df) else None,
            )

        # ── Error handling ────────────────────────────────────────────────────
        if result.get("error"):
            st.markdown(
                f'<div class="error-box">⚠️ {result["error"]}</div>',
                unsafe_allow_html=True,
            )
            st.info(
                "💡 **Tips:** Check spelling · Try partial title · "
                "Browse trending movies below for inspiration"
            )

        else:
            matched_title = result["matched_title"]
            recs          = result["recommendations"]

            # Save to history
            add_to_history(matched_title)
            st.session_state["last_query"]  = ""  # reset to avoid infinite loop
            st.session_state["last_results"] = recs
            st.session_state["last_matched"] = matched_title

            # ── Results header ────────────────────────────────────────────────
            st.markdown(
                f'<div class="section-header">'
                f'Movies Similar to "{matched_title}"'
                f'</div>',
                unsafe_allow_html=True,
            )
            render_stats_bar(len(full_df), matched_title, len(recs))

            # ── Display query movie details ───────────────────────────────────
            with st.expander(f"📽️ About: {matched_title}", expanded=False):
                query_movie = recommender.get_movie_details(matched_title)
                if query_movie:
                    render_movie_card(query_movie, show_similarity=False, key_prefix="query")

            # ── Recommendation cards ──────────────────────────────────────────
            if not recs:
                st.warning(
                    "No recommendations found with the current filters. "
                    "Try relaxing the genre or rating filters."
                )
            else:
                for movie in recs:
                    render_movie_card(movie, show_similarity=True, key_prefix="rec")

    elif not query:
        # Landing state — show prompt
        st.markdown(
            """
            <div style="text-align:center;padding:3rem 0;color:#5a5a72;">
                <div style="font-size:3rem;margin-bottom:1rem;">🎬</div>
                <div style="font-size:1.1rem;margin-bottom:0.5rem;color:#9b9bb4;">
                    Type a movie title above to get AI-powered recommendations
                </div>
                <div style="font-size:0.85rem;">
                    Powered by TF-IDF + Cosine Similarity · 50 curated films in the built-in library
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2: TRENDING
# ══════════════════════════════════════════════════════════════════════════════
with tab_trending:
    trending = recommender.get_trending(top_n=10)
    render_trending_section(trending)

    st.markdown('<div class="section-header">🏆 Top Rated</div>', unsafe_allow_html=True)
    top_rated = full_df.nlargest(10, "vote_average")

    for _, row in top_rated.iterrows():
        movie_dict = {
            "id":           int(row.get("id", 0)),
            "title":        str(row.get("title", "Unknown")),
            "genres":       str(row.get("genres", "")),
            "vote_average": float(row.get("vote_average", 0)),
            "vote_count":   int(row.get("vote_count", 0)),
            "release_year": int(row.get("release_year", 0)) or "N/A",
            "overview":     str(row.get("overview", "")),
            "popularity":   float(row.get("popularity", 0)),
            "director":     str(row.get("director", "N/A")),
            "cast":         str(row.get("cast", "")),
            "similarity":   None,
        }
        render_movie_card(movie_dict, show_similarity=False, key_prefix="top")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3: FAVOURITES
# ══════════════════════════════════════════════════════════════════════════════
with tab_favorites:
    st.markdown('<div class="section-header">❤️ Your Favourites</div>', unsafe_allow_html=True)
    favorites = get_favorites()
    render_favorites_section(favorites)

    if favorites:
        st.markdown("---")
        st.markdown("**Get recommendations based on your favourites:**")
        fav_cols = st.columns(min(len(favorites), 4))
        for i, fav in enumerate(favorites):
            with fav_cols[i % 4]:
                if st.button(
                    f"🎬 {fav['title'][:18]}",
                    key=f"fav_rec_{i}_{fav['title'][:8]}",
                ):
                    st.session_state["last_query"] = fav["title"]
                    st.rerun()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="custom-footer">'
    'CineMatch · Built with ❤️ using Python, Streamlit & Scikit-learn · '
    '<a href="https://github.com" target="_blank">View on GitHub</a>'
    '</div>',
    unsafe_allow_html=True,
)

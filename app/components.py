"""
app/components.py
─────────────────
Reusable Streamlit UI components for the movie recommendation app.

Each function renders a distinct piece of the UI.
Keeping components in a separate file keeps app.py clean and readable.
"""

import streamlit as st
from utils.tmdb_api import get_poster_url
from utils.session_state import add_to_favorites, remove_from_favorites, is_favorite


def render_movie_card(movie: dict, show_similarity: bool = True, key_prefix: str = "card"):
    """
    Render a single movie as a styled card.

    Displays:
      • Poster image (from TMDB if API key set, else placeholder)
      • Title, year, genres, director
      • Rating stars + score
      • Similarity % badge (if show_similarity=True)
      • Overview (truncated)
      • ❤ Favourite toggle button
    """
    title        = movie.get("title", "Unknown")
    year         = movie.get("release_year", "N/A")
    genres       = movie.get("genres", "")
    rating       = movie.get("vote_average", 0.0)
    overview     = movie.get("overview", "No description available.")
    similarity   = movie.get("similarity")
    director     = movie.get("director", "")
    tmdb_year    = int(year) if str(year).isdigit() else None

    # Fetch poster URL (cached, so fast on repeat calls)
    poster_url = get_poster_url(title, tmdb_year)

    # Unique key for Streamlit widgets
    safe_title = title.replace(" ", "_").replace(":", "")[:30]
    fav_key    = f"{key_prefix}_{safe_title}_fav"
    faved      = is_favorite(title)

    # ── Card layout ────────────────────────────────────────────────────────────
    with st.container():
        # Similarity badge
        if show_similarity and similarity is not None:
            color = "#00d2ff" if similarity >= 70 else "#f7971e" if similarity >= 40 else "#adb5bd"
            st.markdown(
                f'<div class="similarity-badge" style="border-color:{color};color:{color};">'
                f'⚡ {similarity:.1f}% match</div>',
                unsafe_allow_html=True,
            )

        col_poster, col_info = st.columns([1, 2])

        with col_poster:
            st.image(poster_url, use_container_width=True)

        with col_info:
            # Title
            st.markdown(f'<div class="movie-title">{title}</div>', unsafe_allow_html=True)

            # Year + genres
            genre_tags = " ".join(
                f'<span class="genre-tag">{g}</span>'
                for g in genres.split()[:4]
            )
            st.markdown(
                f'<div class="movie-meta">📅 {year} &nbsp;|&nbsp; {genre_tags}</div>',
                unsafe_allow_html=True,
            )

            # Director
            if director and director not in ("N/A", "nan", ""):
                st.markdown(
                    f'<div class="movie-director">🎬 <em>{director}</em></div>',
                    unsafe_allow_html=True,
                )

            # Star rating
            stars     = "⭐" * int(round(rating / 2))
            empty_str = "☆" * (5 - int(round(rating / 2)))
            st.markdown(
                f'<div class="movie-rating">{stars}{empty_str} &nbsp;<strong>{rating:.1f}</strong>/10</div>',
                unsafe_allow_html=True,
            )

            # Overview (truncated to 200 chars)
            short_overview = (overview[:200] + "…") if len(overview) > 200 else overview
            st.markdown(
                f'<div class="movie-overview">{short_overview}</div>',
                unsafe_allow_html=True,
            )

            # Favourite button
            if faved:
                if st.button("❤️ Remove from Favourites", key=fav_key):
                    remove_from_favorites(title)
                    st.rerun()
            else:
                if st.button("🤍 Save to Favourites", key=fav_key):
                    add_to_favorites(movie)
                    st.rerun()

        st.markdown('<hr class="card-divider"/>', unsafe_allow_html=True)


def render_trending_section(movies: list[dict]):
    """Render a horizontal scrollable trending movies section."""
    st.markdown('<div class="section-header">🔥 Trending Right Now</div>', unsafe_allow_html=True)

    if not movies:
        st.info("No trending data available.")
        return

    # Show trending in a 5-column grid
    cols = st.columns(5)
    for i, movie in enumerate(movies[:10]):
        title    = movie.get("title", "Unknown")
        year     = movie.get("release_year", "N/A")
        rating   = movie.get("vote_average", 0.0)
        tmdb_year = int(year) if str(year).isdigit() else None
        poster   = get_poster_url(title, tmdb_year)

        with cols[i % 5]:
            st.image(poster, use_container_width=True)
            st.markdown(
                f'<div class="trending-title">{title}</div>'
                f'<div class="trending-meta">⭐ {rating:.1f} · {year}</div>',
                unsafe_allow_html=True,
            )
            if st.button("Get Recs", key=f"trending_{i}_{title[:10]}"):
                st.session_state["last_query"] = title
                st.rerun()


def render_sidebar_filters(all_genres: list[str], min_year: int, max_year: int) -> dict:
    """
    Render sidebar filters and return the current filter state as a dict.

    Returns
    -------
    dict with keys: genres, min_year, max_year, min_rating, top_n
    """
    st.sidebar.markdown("## 🎛️ Filters")

    selected_genres = st.sidebar.multiselect(
        "Genre",
        options=all_genres,
        default=[],
        help="Filter recommendations by genre",
    )

    year_range = st.sidebar.slider(
        "Release Year",
        min_value=min_year,
        max_value=max_year,
        value=(1990, max_year),
        step=1,
    )

    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=10.0,
        value=6.0,
        step=0.5,
        format="%.1f ⭐",
    )

    top_n = st.sidebar.slider(
        "Number of Recommendations",
        min_value=3,
        max_value=20,
        value=8,
        step=1,
    )

    return {
        "genres":     selected_genres,
        "min_year":   year_range[0],
        "max_year":   year_range[1],
        "min_rating": min_rating,
        "top_n":      top_n,
    }


def render_history_section(history: list[str]):
    """Render recently searched movies as clickable chips."""
    if not history:
        return

    st.markdown('<div class="section-header">🕐 Recently Searched</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(history), 5))
    for i, title in enumerate(history[:5]):
        with cols[i]:
            if st.button(f"🎬 {title[:20]}", key=f"hist_{i}_{title[:10]}"):
                st.session_state["last_query"] = title
                st.rerun()


def render_favorites_section(favorites: list[dict]):
    """Render the saved favourites section."""
    if not favorites:
        st.info("You haven't saved any favourites yet. Click '🤍 Save' on any movie card!")
        return

    for movie in favorites:
        render_movie_card(movie, show_similarity=False, key_prefix="fav")


def render_stats_bar(df_len: int, query: str, n_results: int):
    """Show a small stats bar below the search results header."""
    st.markdown(
        f'<div class="stats-bar">'
        f'📚 Library: <strong>{df_len:,}</strong> movies &nbsp;|&nbsp; '
        f'🔍 Query: <strong>"{query}"</strong> &nbsp;|&nbsp; '
        f'✅ Found: <strong>{n_results}</strong> recommendations'
        f'</div>',
        unsafe_allow_html=True,
    )

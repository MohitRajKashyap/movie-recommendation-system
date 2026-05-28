"""
app/styles.py
─────────────
All custom CSS for the movie recommendation app.
Injects a dark, cinematic theme into the Streamlit app via st.markdown.
"""

CUSTOM_CSS = """
<style>
/* ── Import fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;1,9..40,300&display=swap');

/* ── CSS Variables ────────────────────────────────────────────────────────── */
:root {
    --bg-primary:    #0a0a0f;
    --bg-secondary:  #12121a;
    --bg-card:       #16161f;
    --bg-elevated:   #1e1e2a;
    --accent-1:      #e94560;    /* neon red */
    --accent-2:      #00d2ff;    /* electric blue */
    --accent-3:      #f7971e;    /* amber */
    --text-primary:  #f0f0f5;
    --text-secondary:#9b9bb4;
    --text-muted:    #5a5a72;
    --border:        #2a2a3d;
    --glow-red:      0 0 20px rgba(233,69,96,0.4);
    --glow-blue:     0 0 20px rgba(0,210,255,0.3);
    --radius:        12px;
    --radius-sm:     8px;
}

/* ── Global base ──────────────────────────────────────────────────────────── */
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* Hide Streamlit default branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-1); border-radius: 3px; }

/* ── App header ───────────────────────────────────────────────────────────── */
.app-header {
    text-align: center;
    padding: 2.5rem 0 1rem;
}
.app-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4rem;
    letter-spacing: 6px;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    text-shadow: none;
}
.app-tagline {
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Search bar ───────────────────────────────────────────────────────────── */
div[data-testid="stTextInput"] input {
    background-color: var(--bg-elevated) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-size: 1.05rem !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent-2) !important;
    box-shadow: var(--glow-blue) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-1), #c0392b) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 1rem !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    cursor: pointer !important;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--glow-red) !important;
    opacity: 0.92;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
    background-color: var(--bg-elevated) !important;
    border-color: var(--border) !important;
}

/* ── Section headers ──────────────────────────────────────────────────────── */
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 2px;
    color: var(--text-primary);
    padding: 1.5rem 0 0.75rem;
    border-bottom: 2px solid var(--accent-1);
    margin-bottom: 1rem;
}

/* ── Similarity badge ─────────────────────────────────────────────────────── */
.similarity-badge {
    display: inline-block;
    border: 1.5px solid;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

/* ── Movie card elements ──────────────────────────────────────────────────── */
.movie-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 1.5px;
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.movie-meta {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}
.genre-tag {
    background-color: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.7rem;
    letter-spacing: 0.3px;
    color: var(--accent-2);
    margin-right: 2px;
}
.movie-director {
    color: var(--accent-3);
    font-size: 0.82rem;
    margin-bottom: 0.5rem;
}
.movie-rating {
    color: var(--accent-3);
    font-size: 0.95rem;
    margin-bottom: 0.6rem;
}
.movie-overview {
    color: var(--text-secondary);
    font-size: 0.88rem;
    line-height: 1.6;
    font-style: italic;
}
.card-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.2rem 0;
}

/* ── Trending section ─────────────────────────────────────────────────────── */
.trending-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.trending-meta {
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* ── Stats bar ────────────────────────────────────────────────────────────── */
.stats-bar {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}
.stats-bar strong {
    color: var(--accent-2);
}

/* ── Error / warning box ──────────────────────────────────────────────────── */
.error-box {
    background: rgba(233,69,96,0.12);
    border: 1px solid var(--accent-1);
    border-radius: var(--radius-sm);
    padding: 1rem 1.25rem;
    color: var(--accent-1);
    font-size: 0.9rem;
    margin: 1rem 0;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-secondary);
    border-radius: var(--radius);
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    padding: 0.4rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-1), #c0392b) !important;
    color: white !important;
}

/* ── Spinner overlay ──────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent-1) !important;
}

/* ── Info / success messages ──────────────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-sm) !important;
}

/* ── Selectbox / multiselect ──────────────────────────────────────────────── */
.stMultiSelect [data-baseweb="tag"] {
    background-color: var(--accent-1) !important;
    color: white !important;
}

/* ── Images ───────────────────────────────────────────────────────────────── */
.stImage img {
    border-radius: var(--radius-sm) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.stImage img:hover {
    transform: scale(1.04);
    box-shadow: var(--glow-red);
}

/* ── Footer ───────────────────────────────────────────────────────────────── */
.custom-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.75rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
.custom-footer a {
    color: var(--accent-2);
    text-decoration: none;
}

/* ── Responsive columns ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .app-logo { font-size: 2.5rem; }
    .movie-title { font-size: 1.2rem; }
}
</style>
"""


def inject_css():
    """Inject the custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

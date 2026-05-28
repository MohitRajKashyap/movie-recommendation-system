# 🎬 CineMatch — AI-Powered Movie Recommendation System

<div align="center">

![CineMatch Banner](screenshots/banner.png)

**Discover your next favourite film with machine learning**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live-Demo-00d2ff?logo=streamlit)](https://your-app.streamlit.app)

</div>

---

## 📌 Overview

**CineMatch** is a full-stack, production-quality movie recommendation web app built with Python and Streamlit. It uses **TF-IDF vectorisation + Cosine Similarity** (content-based filtering) to recommend movies similar to any title you search for.

Built as a portfolio project, it demonstrates:
- Real machine learning applied to a relatable problem
- Clean, modular Python code architecture
- A polished, dark-themed responsive UI
- Integration with a real REST API (TMDB)
- Deploy-ready configuration for cloud platforms

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Smart Search** | Fuzzy search with typo-tolerance — finds movies even with misspellings |
| 🤖 **AI Recommendations** | TF-IDF + Cosine Similarity content-based engine |
| ⚡ **Similarity Score** | Shows a % match score for each recommended film |
| 🎭 **Autocomplete** | Real-time suggestions as you type |
| 🔥 **Trending Section** | Popular + top-rated movies ranked by weighted score |
| 🕐 **Search History** | Recently searched movies for quick re-access |
| ❤️ **Favourites** | Save movies to a personal favourites list |
| 🎛️ **Sidebar Filters** | Filter by genre, release year, and minimum rating |
| 🖼️ **Movie Posters** | Fetched from TMDB API (graceful fallback if unavailable) |
| 📱 **Responsive UI** | Dark cinematic theme, works on desktop and mobile |

---

## 🧠 How It Works — Machine Learning

### Algorithm: Content-Based Filtering with TF-IDF + Cosine Similarity

**Why this approach?**

1. **Cold-start friendly** — No user history needed. Works for every movie from day one.
2. **Interpretable** — You can explain *why* a movie was recommended (shared genre, director, cast).
3. **Fast** — The similarity matrix is computed once (O(n²)); all recommendations are then O(1) lookups.
4. **TF-IDF is smarter than raw counts** — It penalises generic words ("the", "and") and rewards rare, meaningful descriptors ("dystopian", "Nolan", "heist").

### Feature Engineering

For each movie, we build a weighted **"feature soup"** string:

```
soup = (genres × 3) + (director × 2) + (cast × 2) + (overview × 1)
```

Repeating features simulates importance weighting — genres and the director have the strongest influence on recommendations (just like in real life: "I want another Nolan film" or "something in the action genre").

### Pipeline

```
Raw Data → Clean & Preprocess → Build Feature Soup → TF-IDF Vectorise
    → Cosine Similarity Matrix → Ranked Recommendations
```

### Cosine Similarity Formula

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

A score of 1.0 = identical movies; 0.0 = no overlap.

---

## 🗂️ Project Structure

```
movie-recommendation-system/
│
├── app.py                    # 🚀 Main Streamlit entry point
│
├── app/
│   ├── __init__.py
│   ├── components.py         # Reusable UI widgets (cards, trending, filters)
│   └── styles.py             # Dark-theme CSS injection
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py        # Dataset loading, cleaning, preprocessing
│   ├── recommender.py        # ML engine: TF-IDF + Cosine Similarity
│   ├── tmdb_api.py           # TMDB REST API integration (posters, metadata)
│   └── session_state.py      # Streamlit session: history & favourites
│
├── data/
│   ├── .gitkeep
│   └── download_data.py      # Optional: download full TMDB/MovieLens dataset
│
├── notebooks/
│   └── exploration.py        # EDA, model evaluation, sample outputs
│
├── models/                   # Directory for saved model artefacts
│   └── .gitkeep
│
├── screenshots/              # UI screenshots for README
│
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
│
├── .env.example              # Environment variables template
├── .gitignore
├── Procfile                  # Render/Railway deployment config
├── runtime.txt               # Python version for cloud deployment
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start — Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/movie-recommendation-system.git
cd movie-recommendation-system
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables (optional but recommended)

```bash
cp .env.example .env
```

Edit `.env` and add your TMDB API key:

```
TMDB_API_KEY=your_key_here
```

> **Get a free TMDB API key:** Sign up at [themoviedb.org](https://www.themoviedb.org/settings/api) → Settings → API → Create Key (free, instant approval)

> **Without a key:** The app still works fully — it just shows placeholder images instead of movie posters.

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. 🎉

---

## 📊 Dataset

### Built-in Dataset (default — no downloads needed)

The app ships with **50 curated, well-known films** covering a wide range of genres, directors, and eras. This is enough to demonstrate all features immediately.

### Full Dataset (optional — 45,000+ movies)

For a production-grade experience, download the TMDB MovieLens dataset:

```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle API (download kaggle.json from kaggle.com/account)
mkdir ~/.kaggle && mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download dataset
python data/download_data.py
```

Place `movies_metadata.csv` and `credits.csv` in the `data/` folder. The app auto-detects and uses them on next launch.

---

## 🧪 Model Evaluation

Run the EDA and evaluation script:

```bash
python notebooks/exploration.py
```

Sample output:
```
📊 Dataset: 50 movies
🔧 TF-IDF vocabulary: 1,247 terms
🤖 Similarity matrix: (50, 50)

Movies similar to 'Inception':
  1. Interstellar       (2014) — 78.4% match
  2. The Prestige       (2006) — 74.1% match
  3. Memento            (2000) — 71.3% match
  4. The Dark Knight    (2008) — 68.9% match
  5. Blade Runner 2049  (2017) — 52.1% match
```

---

## ☁️ Deployment

### Streamlit Cloud (easiest — free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as the main file
4. Under **Advanced settings**, add `TMDB_API_KEY` as a secret
5. Click **Deploy**

### Render

1. Connect your GitHub repo at [render.com](https://render.com)
2. Create a **Web Service**
3. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add `TMDB_API_KEY` under Environment Variables
5. Deploy

### Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Set the `TMDB_API_KEY` environment variable in the Railway dashboard.

---

## 📸 Screenshots

| Search & Recommend | Trending | Favourites |
|---|---|---|
| ![Search](screenshots/search.png) | ![Trending](screenshots/trending.png) | ![Favourites](screenshots/favourites.png) |

*Screenshots taken with the built-in sample dataset and a configured TMDB API key.*

---

## 🛣️ Roadmap / Future Improvements

- [ ] **Collaborative Filtering** — User-based recommendations using MovieLens ratings matrix
- [ ] **Neural Embeddings** — Use sentence-transformers to encode movie overviews for semantic similarity
- [ ] **User Accounts** — Persistent profiles with login (Supabase / Firebase)
- [ ] **Streaming Links** — Show where each movie is available (Netflix, Prime, etc.) via JustWatch API
- [ ] **Trailer Integration** — Embed YouTube trailers via YouTube Data API
- [ ] **A/B Testing** — Compare TF-IDF vs embeddings recommendation quality
- [ ] **More Languages** — Multi-language dataset support
- [ ] **Mobile App** — React Native or Flutter wrapper

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web Framework | Streamlit |
| ML / Data | Scikit-learn, Pandas, NumPy |
| Search | FuzzyWuzzy (Levenshtein distance) |
| External API | TMDB (The Movie Database) |
| Styling | Custom CSS (dark cinematic theme) |
| Fonts | Bebas Neue, DM Sans (Google Fonts) |
| Deployment | Streamlit Cloud / Render / Railway |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please follow the existing code style and add comments for any new ML logic.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for their excellent free API
- [MovieLens Dataset](https://grouplens.org/datasets/movielens/) by GroupLens Research
- [Streamlit](https://streamlit.io) for making Python web apps a joy to build
- [Scikit-learn](https://scikit-learn.org) for the TF-IDF and cosine similarity implementations

---

<div align="center">
Built with ❤️ by <a href="https://github.com/MohitRajKashyap">Mohit Raj Kashyap</a>
</div>

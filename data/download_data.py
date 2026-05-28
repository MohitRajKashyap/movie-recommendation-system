"""
data/download_data.py
─────────────────────
Optional script to download the full MovieLens / TMDB metadata dataset
from Kaggle for a richer recommendation experience (45,000+ movies).

The app works fine WITHOUT this — it ships with 50 built-in curated films.
Run this only if you want the full dataset.

Requirements:
    pip install kaggle
    Configure Kaggle API: https://www.kaggle.com/docs/api

Usage:
    python data/download_data.py
"""

import os
import sys
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).parent


def download_movies_dataset():
    """Download the TMDB movies metadata dataset from Kaggle."""
    try:
        import kaggle  # noqa: F401
    except ImportError:
        print("❌ Kaggle API not installed. Run: pip install kaggle")
        sys.exit(1)

    print("📥 Downloading TMDB movies dataset from Kaggle…")
    print("   Dataset: rounakbanik/the-movies-dataset")
    print("   Size: ~230MB compressed\n")

    os.system(
        f"kaggle datasets download -d rounakbanik/the-movies-dataset "
        f"--path {DATA_DIR} --unzip"
    )

    # Verify the key files exist
    required = ["movies_metadata.csv", "credits.csv"]
    for fname in required:
        fpath = DATA_DIR / fname
        if fpath.exists():
            size_mb = fpath.stat().st_size / 1_000_000
            print(f"✅ {fname} ({size_mb:.1f} MB)")
        else:
            print(f"⚠️  {fname} not found — dataset may be incomplete")

    print("\n🎉 Dataset ready! Restart the Streamlit app to use the full dataset.")


if __name__ == "__main__":
    download_movies_dataset()

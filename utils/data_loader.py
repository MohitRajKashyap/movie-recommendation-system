"""
utils/data_loader.py
────────────────────
Responsible for loading, cleaning, and preprocessing the movie dataset.

We use the MovieLens + TMDB metadata dataset (movies_metadata.csv + credits.csv).
If the files aren't present, we fall back to a rich built-in sample dataset of
~100 well-known films so the app runs immediately without any downloads.

Algorithm note:
  Content-based filtering is chosen here because it:
  • Requires no user history (works for new users / cold-start problem)
  • Is fast and interpretable
  • Scales well for small-to-medium catalogs
  • Can be explained to stakeholders ("recommended because of similar genre/cast")
"""

import os
import re
import ast
import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ── paths ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
METADATA_PATH = DATA_DIR / "movies_metadata.csv"
CREDITS_PATH  = DATA_DIR / "credits.csv"

# ── built-in sample dataset ────────────────────────────────────────────────────
SAMPLE_MOVIES = [
    {"id": 1, "title": "The Shawshank Redemption", "genres": "Drama", "vote_average": 9.3, "vote_count": 24000, "release_date": "1994-09-23", "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "popularity": 85.0, "director": "Frank Darabont", "cast": "Tim Robbins Morgan Freeman Bob Gunton"},
    {"id": 2, "title": "The Godfather", "genres": "Crime Drama", "vote_average": 9.2, "vote_count": 18000, "release_date": "1972-03-24", "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.", "popularity": 90.0, "director": "Francis Ford Coppola", "cast": "Marlon Brando Al Pacino James Caan"},
    {"id": 3, "title": "The Dark Knight", "genres": "Action Crime Drama Thriller", "vote_average": 9.0, "vote_count": 29000, "release_date": "2008-07-18", "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.", "popularity": 125.0, "director": "Christopher Nolan", "cast": "Christian Bale Heath Ledger Aaron Eckhart"},
    {"id": 4, "title": "Pulp Fiction", "genres": "Crime Drama Thriller", "vote_average": 8.9, "vote_count": 25000, "release_date": "1994-10-14", "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.", "popularity": 95.0, "director": "Quentin Tarantino", "cast": "John Travolta Uma Thurman Samuel L. Jackson"},
    {"id": 5, "title": "Forrest Gump", "genres": "Comedy Drama Romance", "vote_average": 8.8, "vote_count": 23000, "release_date": "1994-07-06", "overview": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate, and other history unfold through the perspective of an Alabama man.", "popularity": 88.0, "director": "Robert Zemeckis", "cast": "Tom Hanks Robin Wright Gary Sinise"},
    {"id": 6, "title": "Inception", "genres": "Action Adventure Science Fiction Thriller", "vote_average": 8.8, "vote_count": 30000, "release_date": "2010-07-16", "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.", "popularity": 115.0, "director": "Christopher Nolan", "cast": "Leonardo DiCaprio Joseph Gordon-Levitt Ellen Page"},
    {"id": 7, "title": "The Matrix", "genres": "Action Science Fiction", "vote_average": 8.7, "vote_count": 24000, "release_date": "1999-03-31", "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", "popularity": 92.0, "director": "Lana Wachowski", "cast": "Keanu Reeves Laurence Fishburne Carrie-Anne Moss"},
    {"id": 8, "title": "Goodfellas", "genres": "Crime Drama", "vote_average": 8.7, "vote_count": 18000, "release_date": "1990-09-19", "overview": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.", "popularity": 82.0, "director": "Martin Scorsese", "cast": "Ray Liotta Robert De Niro Joe Pesci"},
    {"id": 9, "title": "Interstellar", "genres": "Adventure Drama Science Fiction", "vote_average": 8.6, "vote_count": 30000, "release_date": "2014-11-07", "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", "popularity": 105.0, "director": "Christopher Nolan", "cast": "Matthew McConaughey Anne Hathaway Jessica Chastain"},
    {"id": 10, "title": "Fight Club", "genres": "Drama Thriller", "vote_average": 8.8, "vote_count": 26000, "release_date": "1999-10-15", "overview": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.", "popularity": 97.0, "director": "David Fincher", "cast": "Brad Pitt Edward Norton Helena Bonham Carter"},
    {"id": 11, "title": "The Silence of the Lambs", "genres": "Crime Drama Thriller Horror", "vote_average": 8.6, "vote_count": 15000, "release_date": "1991-02-14", "overview": "A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.", "popularity": 79.0, "director": "Jonathan Demme", "cast": "Jodie Foster Anthony Hopkins Scott Glenn"},
    {"id": 12, "title": "Schindler's List", "genres": "Drama History War", "vote_average": 9.0, "vote_count": 15000, "release_date": "1993-11-30", "overview": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.", "popularity": 76.0, "director": "Steven Spielberg", "cast": "Liam Neeson Ben Kingsley Ralph Fiennes"},
    {"id": 13, "title": "The Lord of the Rings: The Return of the King", "genres": "Adventure Drama Fantasy", "vote_average": 8.9, "vote_count": 20000, "release_date": "2003-12-17", "overview": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom.", "popularity": 110.0, "director": "Peter Jackson", "cast": "Elijah Wood Viggo Mortensen Ian McKellen"},
    {"id": 14, "title": "Star Wars: A New Hope", "genres": "Action Adventure Science Fiction", "vote_average": 8.6, "vote_count": 17000, "release_date": "1977-05-25", "overview": "Luke Skywalker joins forces with a Jedi Knight, a cocky pilot, a Wookiee and two droids to save the galaxy from the Empire.", "popularity": 98.0, "director": "George Lucas", "cast": "Mark Hamill Harrison Ford Carrie Fisher"},
    {"id": 15, "title": "The Avengers", "genres": "Action Adventure Science Fiction", "vote_average": 8.0, "vote_count": 28000, "release_date": "2012-05-04", "overview": "Earth's mightiest heroes must come together and learn to fight as a team to stop the mischievous Loki and his alien army.", "popularity": 130.0, "director": "Joss Whedon", "cast": "Robert Downey Jr. Chris Evans Scarlett Johansson"},
    {"id": 16, "title": "Titanic", "genres": "Drama Romance", "vote_average": 7.9, "vote_count": 23000, "release_date": "1997-12-19", "overview": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.", "popularity": 88.0, "director": "James Cameron", "cast": "Leonardo DiCaprio Kate Winslet Billy Zane"},
    {"id": 17, "title": "Jurassic Park", "genres": "Adventure Science Fiction Thriller", "vote_average": 8.2, "vote_count": 16000, "release_date": "1993-06-11", "overview": "A pragmatic paleontologist touring an almost complete theme park on an island in Central America is tasked with protecting a couple of kids.", "popularity": 90.0, "director": "Steven Spielberg", "cast": "Sam Neill Laura Dern Jeff Goldblum"},
    {"id": 18, "title": "The Lion King", "genres": "Animation Adventure Drama Family", "vote_average": 8.5, "vote_count": 18000, "release_date": "1994-06-24", "overview": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.", "popularity": 94.0, "director": "Roger Allers", "cast": "Matthew Broderick James Earl Jones Jeremy Irons"},
    {"id": 19, "title": "Toy Story", "genres": "Animation Adventure Comedy Family Fantasy", "vote_average": 8.3, "vote_count": 17000, "release_date": "1995-11-22", "overview": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.", "popularity": 86.0, "director": "John Lasseter", "cast": "Tom Hanks Tim Allen Don Rickles"},
    {"id": 20, "title": "Home Alone", "genres": "Comedy Family", "vote_average": 7.7, "vote_count": 14000, "release_date": "1990-11-16", "overview": "An 8-year-old troublemaker must protect his house from a pair of burglars when he is accidentally left home alone by his family.", "popularity": 78.0, "director": "Chris Columbus", "cast": "Macaulay Culkin Joe Pesci Daniel Stern"},
    {"id": 21, "title": "Gladiator", "genres": "Action Adventure Drama", "vote_average": 8.5, "vote_count": 19000, "release_date": "2000-05-05", "overview": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.", "popularity": 93.0, "director": "Ridley Scott", "cast": "Russell Crowe Joaquin Phoenix Connie Nielsen"},
    {"id": 22, "title": "The Departed", "genres": "Crime Drama Thriller", "vote_average": 8.5, "vote_count": 16000, "release_date": "2006-10-06", "overview": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in South Boston.", "popularity": 87.0, "director": "Martin Scorsese", "cast": "Leonardo DiCaprio Matt Damon Jack Nicholson"},
    {"id": 23, "title": "Whiplash", "genres": "Drama Music", "vote_average": 8.5, "vote_count": 15000, "release_date": "2014-10-10", "overview": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an abusive instructor.", "popularity": 80.0, "director": "Damien Chazelle", "cast": "Miles Teller J.K. Simmons Melissa Benoist"},
    {"id": 24, "title": "La La Land", "genres": "Comedy Drama Music Romance", "vote_average": 8.0, "vote_count": 18000, "release_date": "2016-12-09", "overview": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations.", "popularity": 91.0, "director": "Damien Chazelle", "cast": "Ryan Gosling Emma Stone John Legend"},
    {"id": 25, "title": "Get Out", "genres": "Horror Mystery Thriller", "vote_average": 7.9, "vote_count": 14000, "release_date": "2017-02-24", "overview": "A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.", "popularity": 85.0, "director": "Jordan Peele", "cast": "Daniel Kaluuya Allison Williams Bradley Whitford"},
    {"id": 26, "title": "Parasite", "genres": "Comedy Drama Thriller", "vote_average": 8.6, "vote_count": 17000, "release_date": "2019-11-08", "overview": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.", "popularity": 96.0, "director": "Bong Joon-ho", "cast": "Kang-ho Song Sun-kyun Lee Yeo-jeong Cho"},
    {"id": 27, "title": "Avengers: Endgame", "genres": "Action Adventure Science Fiction", "vote_average": 8.4, "vote_count": 32000, "release_date": "2019-04-26", "overview": "After the devastating events of Infinity War, the universe is in ruins. The Avengers assemble once more in order to reverse Thanos' actions.", "popularity": 140.0, "director": "Anthony Russo", "cast": "Robert Downey Jr. Chris Evans Chris Hemsworth"},
    {"id": 28, "title": "Spider-Man: Into the Spider-Verse", "genres": "Animation Action Adventure", "vote_average": 8.4, "vote_count": 14000, "release_date": "2018-12-14", "overview": "Teen Miles Morales becomes the Spider-Man of his universe, and must join with five spider-powered individuals from other dimensions.", "popularity": 88.0, "director": "Bob Persichetti", "cast": "Shameik Moore Jake Johnson Hailee Steinfeld"},
    {"id": 29, "title": "Mad Max: Fury Road", "genres": "Action Adventure Science Fiction Thriller", "vote_average": 8.1, "vote_count": 18000, "release_date": "2015-05-15", "overview": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search of her homeland with the aid of a group of female prisoners.", "popularity": 99.0, "director": "George Miller", "cast": "Tom Hardy Charlize Theron Nicholas Hoult"},
    {"id": 30, "title": "The Grand Budapest Hotel", "genres": "Adventure Comedy Crime Drama", "vote_average": 8.1, "vote_count": 16000, "release_date": "2014-03-28", "overview": "A writer encounters the owner of an aging European hotel, who tells him of his early years serving as a lobby boy in the hotel's glorious years.", "popularity": 82.0, "director": "Wes Anderson", "cast": "Ralph Fiennes Tony Revolori Saoirse Ronan"},
    {"id": 31, "title": "Blade Runner 2049", "genres": "Drama Science Fiction", "vote_average": 8.0, "vote_count": 14000, "release_date": "2017-10-06", "overview": "A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard.", "popularity": 87.0, "director": "Denis Villeneuve", "cast": "Ryan Gosling Harrison Ford Ana de Armas"},
    {"id": 32, "title": "Arrival", "genres": "Drama Mystery Science Fiction Thriller", "vote_average": 7.9, "vote_count": 17000, "release_date": "2016-11-11", "overview": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world.", "popularity": 91.0, "director": "Denis Villeneuve", "cast": "Amy Adams Jeremy Renner Forest Whitaker"},
    {"id": 33, "title": "Her", "genres": "Drama Romance Science Fiction", "vote_average": 8.0, "vote_count": 15000, "release_date": "2013-12-18", "overview": "In a near future, a lonely writer develops an unlikely relationship with an operating system designed to meet his every need.", "popularity": 83.0, "director": "Spike Jonze", "cast": "Joaquin Phoenix Scarlett Johansson Amy Adams"},
    {"id": 34, "title": "No Country for Old Men", "genres": "Crime Drama Thriller Western", "vote_average": 8.1, "vote_count": 14000, "release_date": "2007-11-21", "overview": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash near the Rio Grande.", "popularity": 80.0, "director": "Joel Coen", "cast": "Tommy Lee Jones Javier Bardem Josh Brolin"},
    {"id": 35, "title": "There Will Be Blood", "genres": "Drama Western", "vote_average": 8.2, "vote_count": 11000, "release_date": "2007-12-26", "overview": "A story of family, religion, hatred, oil and madness, focusing on a turn-of-the-century prospector in the early days of the business.", "popularity": 72.0, "director": "Paul Thomas Anderson", "cast": "Daniel Day-Lewis Paul Dano Ciarán Hinds"},
    {"id": 36, "title": "The Social Network", "genres": "Biography Drama", "vote_average": 7.8, "vote_count": 16000, "release_date": "2010-10-01", "overview": "As Harvard student Mark Zuckerberg creates the social networking site that would become known as Facebook, he is sued by the twins who claim he stole their idea.", "popularity": 86.0, "director": "David Fincher", "cast": "Jesse Eisenberg Andrew Garfield Justin Timberlake"},
    {"id": 37, "title": "Moneyball", "genres": "Biography Drama Sport", "vote_average": 7.6, "vote_count": 12000, "release_date": "2011-09-23", "overview": "Oakland A's general manager Billy Beane's successful attempt to assemble a baseball team on a lean budget by employing computer-generated analysis.", "popularity": 78.0, "director": "Bennett Miller", "cast": "Brad Pitt Jonah Hill Philip Seymour Hoffman"},
    {"id": 38, "title": "The Wolf of Wall Street", "genres": "Biography Comedy Crime Drama", "vote_average": 8.2, "vote_count": 22000, "release_date": "2013-12-25", "overview": "Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker living the high life to his fall involving crime, corruption and the federal government.", "popularity": 100.0, "director": "Martin Scorsese", "cast": "Leonardo DiCaprio Jonah Hill Margot Robbie"},
    {"id": 39, "title": "Dune", "genres": "Action Adventure Drama Science Fiction", "vote_average": 8.0, "vote_count": 18000, "release_date": "2021-10-22", "overview": "Feature adaptation of Frank Herbert's science fiction novel, about the son of a noble family entrusted with the protection of the most valuable asset and most vital element in the galaxy.", "popularity": 110.0, "director": "Denis Villeneuve", "cast": "Timothée Chalamet Rebecca Ferguson Oscar Isaac"},
    {"id": 40, "title": "Everything Everywhere All at Once", "genres": "Action Adventure Comedy Science Fiction", "vote_average": 8.0, "vote_count": 14000, "release_date": "2022-03-25", "overview": "A middle-aged Chinese immigrant is swept up in an insane adventure, where she alone can save the world by exploring other universes.", "popularity": 95.0, "director": "Daniel Kwan", "cast": "Michelle Yeoh Ke Huy Quan Jamie Lee Curtis"},
    {"id": 41, "title": "Top Gun: Maverick", "genres": "Action Drama", "vote_average": 8.3, "vote_count": 20000, "release_date": "2022-05-27", "overview": "After more than thirty years of service as one of the Navy's top aviators, Pete Mitchell is where he belongs, pushing the envelope as a courageous test pilot.", "popularity": 120.0, "director": "Joseph Kosinski", "cast": "Tom Cruise Miles Teller Jennifer Connelly"},
    {"id": 42, "title": "The Batman", "genres": "Action Crime Drama Mystery Thriller", "vote_average": 7.9, "vote_count": 16000, "release_date": "2022-03-04", "overview": "In his second year of fighting crime, Batman uncovers corruption in Gotham City that connects to his own family while facing a serial killer known as the Riddler.", "popularity": 108.0, "director": "Matt Reeves", "cast": "Robert Pattinson Zoë Kravitz Jeffrey Wright"},
    {"id": 43, "title": "Oppenheimer", "genres": "Biography Drama History", "vote_average": 8.6, "vote_count": 20000, "release_date": "2023-07-21", "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.", "popularity": 125.0, "director": "Christopher Nolan", "cast": "Cillian Murphy Emily Blunt Matt Damon"},
    {"id": 44, "title": "Barbie", "genres": "Adventure Comedy Fantasy", "vote_average": 7.0, "vote_count": 18000, "release_date": "2023-07-21", "overview": "Barbie suffers a crisis that leads her to question her world and her existence. She and Ken are expelled from Barbieland and venture into the real world.", "popularity": 130.0, "director": "Greta Gerwig", "cast": "Margot Robbie Ryan Gosling America Ferrera"},
    {"id": 45, "title": "John Wick", "genres": "Action Crime Thriller", "vote_average": 7.4, "vote_count": 16000, "release_date": "2014-10-24", "overview": "An ex-hitman comes out of retirement to track down the gangsters that killed his dog, a gift from his recently deceased wife.", "popularity": 95.0, "director": "Chad Stahelski", "cast": "Keanu Reeves Michael Nyqvist Alfie Allen"},
    {"id": 46, "title": "The Prestige", "genres": "Drama Mystery Sci-Fi Thriller", "vote_average": 8.5, "vote_count": 14000, "release_date": "2006-10-20", "overview": "After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.", "popularity": 84.0, "director": "Christopher Nolan", "cast": "Christian Bale Hugh Jackman Scarlett Johansson"},
    {"id": 47, "title": "Memento", "genres": "Mystery Thriller", "vote_average": 8.4, "vote_count": 14000, "release_date": "2000-10-20", "overview": "A man with short-term memory loss attempts to track down his wife's murderer.", "popularity": 80.0, "director": "Christopher Nolan", "cast": "Guy Pearce Carrie-Anne Moss Joe Pantoliano"},
    {"id": 48, "title": "2001: A Space Odyssey", "genres": "Adventure Drama Science Fiction", "vote_average": 8.3, "vote_count": 12000, "release_date": "1968-04-03", "overview": "After discovering a mysterious artifact buried beneath the Lunar surface, mankind sets off on a quest to find its origins with help from intelligent supercomputer H.A.L. 9000.", "popularity": 75.0, "director": "Stanley Kubrick", "cast": "Keir Dullea Gary Lockwood William Sylvester"},
    {"id": 49, "title": "Apocalypse Now", "genres": "Drama War", "vote_average": 8.5, "vote_count": 11000, "release_date": "1979-08-15", "overview": "A U.S. Army officer serving in Vietnam is tasked with assassinating a renegade Special Forces Colonel who sees himself as a god.", "popularity": 74.0, "director": "Francis Ford Coppola", "cast": "Martin Sheen Marlon Brando Robert Duvall"},
    {"id": 50, "title": "Coco", "genres": "Animation Adventure Family Fantasy Music", "vote_average": 8.4, "vote_count": 16000, "release_date": "2017-10-27", "overview": "Aspiring musician Miguel, confronted with his family's ancestral ban on music, enters the Land of the Dead to find his great-great-grandfather.", "popularity": 91.0, "director": "Lee Unkrich", "cast": "Anthony Gonzalez Gael García Bernal Benjamin Bratt"},
]


def _safe_literal_eval(val):
    """Safely parse Python literals from string columns in CSV files."""
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return []


def _extract_genres(genres_val) -> str:
    """Convert genres column (list of dicts) to space-separated string."""
    if isinstance(genres_val, list):
        return " ".join(g.get("name", "") for g in genres_val)
    if isinstance(genres_val, str):
        parsed = _safe_literal_eval(genres_val)
        if isinstance(parsed, list):
            return " ".join(g.get("name", "") for g in parsed)
    return str(genres_val)


def _extract_cast(cast_val, top_n: int = 5) -> str:
    """Extract top-N cast names from cast column."""
    if isinstance(cast_val, list):
        return " ".join(c.get("name", "").replace(" ", "") for c in cast_val[:top_n])
    if isinstance(cast_val, str):
        parsed = _safe_literal_eval(cast_val)
        if isinstance(parsed, list):
            return " ".join(c.get("name", "").replace(" ", "") for c in parsed[:top_n])
    return ""


def _extract_director(crew_val) -> str:
    """Extract director name from crew column."""
    if isinstance(crew_val, list):
        for member in crew_val:
            if member.get("job") == "Director":
                return member.get("name", "").replace(" ", "")
    if isinstance(crew_val, str):
        parsed = _safe_literal_eval(crew_val)
        if isinstance(parsed, list):
            for member in parsed:
                if member.get("job") == "Director":
                    return member.get("name", "").replace(" ", "")
    return ""


def load_sample_dataset() -> pd.DataFrame:
    """Return the built-in sample dataset as a clean DataFrame."""
    df = pd.DataFrame(SAMPLE_MOVIES)
    df["release_year"] = df["release_date"].str[:4].astype(int, errors="ignore")
    df["genres_list"] = df["genres"].str.split()
    return df


def load_full_dataset() -> pd.DataFrame:
    """
    Try to load the full MovieLens/TMDB metadata dataset.
    Falls back to sample dataset if files are not found.

    Download instructions (optional, for richer dataset):
      kaggle datasets download -d rounakbanik/the-movies-dataset
      Unzip movies_metadata.csv and credits.csv into data/
    """
    if not METADATA_PATH.exists():
        logger.info("Full dataset not found — using built-in sample dataset.")
        return load_sample_dataset()

    try:
        logger.info("Loading full TMDB metadata dataset…")
        meta = pd.read_csv(METADATA_PATH, low_memory=False)

        # Drop malformed rows (vote_average column sometimes contains bad IDs)
        meta = meta[pd.to_numeric(meta["vote_average"], errors="coerce").notna()]

        # Parse columns
        meta["genres"] = meta["genres"].apply(_extract_genres)
        meta["vote_average"] = pd.to_numeric(meta["vote_average"], errors="coerce").fillna(0)
        meta["vote_count"] = pd.to_numeric(meta["vote_count"], errors="coerce").fillna(0)
        meta["popularity"] = pd.to_numeric(meta["popularity"], errors="coerce").fillna(0)
        meta["release_date"] = meta["release_date"].fillna("1900-01-01")
        meta["release_year"] = meta["release_date"].str[:4]
        meta["release_year"] = pd.to_numeric(meta["release_year"], errors="coerce").fillna(1900).astype(int)
        meta = meta[meta["vote_count"] >= 50].copy()  # remove movies with almost no votes
        meta = meta[meta["title"].notna()].copy()
        meta["overview"] = meta["overview"].fillna("")
        meta["id"] = pd.to_numeric(meta["id"], errors="coerce")
        meta = meta.dropna(subset=["id"])
        meta["id"] = meta["id"].astype(int)

        # Load credits if available
        if CREDITS_PATH.exists():
            credits = pd.read_csv(CREDITS_PATH)
            credits["id"] = pd.to_numeric(credits["id"], errors="coerce").dropna().astype(int)
            credits["cast"] = credits["cast"].apply(_extract_cast)
            credits["director"] = credits["crew"].apply(_extract_director)
            meta = meta.merge(credits[["id", "cast", "director"]], on="id", how="left")
            meta["cast"] = meta["cast"].fillna("")
            meta["director"] = meta["director"].fillna("")
        else:
            meta["cast"] = ""
            meta["director"] = ""

        meta["genres_list"] = meta["genres"].str.split()
        logger.info(f"Full dataset loaded: {len(meta)} movies.")
        return meta.reset_index(drop=True)

    except Exception as e:
        logger.warning(f"Failed to load full dataset ({e}). Falling back to sample.")
        return load_sample_dataset()


def get_all_genres(df: pd.DataFrame) -> list[str]:
    """Return sorted unique genres present in the dataset."""
    genres = set()
    for g_list in df["genres_list"].dropna():
        genres.update(g_list)
    return sorted(genres)


def filter_movies(
    df: pd.DataFrame,
    genres: list[str] | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_rating: float = 0.0,
) -> pd.DataFrame:
    """
    Apply sidebar filters to the movie DataFrame.

    Parameters
    ----------
    df         : Full movie DataFrame
    genres     : If provided, keep only movies containing at least one of these genres
    min_year   : Minimum release year
    max_year   : Maximum release year
    min_rating : Minimum vote_average
    """
    mask = df["vote_average"] >= min_rating

    if genres:
        genre_mask = df["genres_list"].apply(
            lambda g: any(genre in g for genre in genres) if isinstance(g, list) else False
        )
        mask &= genre_mask

    if min_year:
        mask &= df["release_year"] >= min_year
    if max_year:
        mask &= df["release_year"] <= max_year

    return df[mask].copy()

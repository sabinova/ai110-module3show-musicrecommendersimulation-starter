"""
Music Recommender — core scoring and recommendation logic.

This module provides two interfaces:
1. Functional (dict-based): load_songs, score_song, recommend_songs — used by main.py
2. OOP (class-based): Song, UserProfile, Recommender — used by tests

Optional Extensions implemented:
- Challenge 1: Advanced features (popularity, release_decade)
- Challenge 2: Multiple scoring modes (balanced, genre-first, mood-first, energy-focused)
- Challenge 3: Diversity penalty (limits same genre/artist in top results)
"""

import csv
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data Classes (OOP path — required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its attributes from the catalog."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Challenge 2: Scoring Mode Presets
# ---------------------------------------------------------------------------
# Each mode is a dict of weight multipliers applied to the base scores.

SCORING_MODES = {
    "balanced": {
        "genre": 2.0, "mood": 1.0, "energy": 1.0,
        "valence": 0.5, "danceability": 0.5, "acousticness": 0.3,
        "popularity": 0.3, "decade": 0.2,
    },
    "genre-first": {
        "genre": 3.0, "mood": 0.5, "energy": 0.5,
        "valence": 0.3, "danceability": 0.3, "acousticness": 0.2,
        "popularity": 0.2, "decade": 0.1,
    },
    "mood-first": {
        "genre": 0.5, "mood": 3.0, "energy": 1.0,
        "valence": 0.8, "danceability": 0.5, "acousticness": 0.3,
        "popularity": 0.2, "decade": 0.1,
    },
    "energy-focused": {
        "genre": 0.5, "mood": 0.5, "energy": 3.0,
        "valence": 0.5, "danceability": 1.0, "acousticness": 0.3,
        "popularity": 0.2, "decade": 0.1,
    },
}


# ---------------------------------------------------------------------------
# Shared Scoring Logic
# ---------------------------------------------------------------------------

def _score_genre(song_genre: str, user_genre: str, weight: float) -> Tuple[float, str]:
    """Award points if the song's genre matches the user's favorite."""
    if song_genre.lower() == user_genre.lower():
        return weight, f"genre match (+{weight:.2f})"
    return 0.0, ""


def _score_mood(song_mood: str, user_mood: str, weight: float) -> Tuple[float, str]:
    """Award points if the song's mood matches the user's favorite."""
    if song_mood.lower() == user_mood.lower():
        return weight, f"mood match (+{weight:.2f})"
    return 0.0, ""


def _score_energy(song_energy: float, user_energy: float, weight: float) -> Tuple[float, str]:
    """Award points based on closeness to the user's target energy."""
    pts = weight * (1.0 - abs(song_energy - user_energy))
    return pts, f"energy similarity (+{pts:.2f})"


def _score_valence(song_valence: float, weight: float, midpoint: float = 0.5) -> Tuple[float, str]:
    """Award points for valence closeness to a neutral midpoint."""
    pts = weight * (1.0 - abs(song_valence - midpoint))
    return pts, f"valence similarity (+{pts:.2f})"


def _score_danceability(song_dance: float, weight: float, midpoint: float = 0.5) -> Tuple[float, str]:
    """Award points for danceability closeness to a neutral midpoint."""
    pts = weight * (1.0 - abs(song_dance - midpoint))
    return pts, f"danceability similarity (+{pts:.2f})"


def _score_acousticness(song_acoustic: float, likes_acoustic: bool, weight: float) -> Tuple[float, str]:
    """Award bonus if the user likes acoustic and the song is acoustic."""
    if likes_acoustic and song_acoustic > 0.7:
        return weight, f"acoustic bonus (+{weight:.2f})"
    return 0.0, ""


def _score_popularity(song_popularity: int, weight: float) -> Tuple[float, str]:
    """Award points based on song popularity (0-100 normalized to 0-1)."""
    pts = weight * (song_popularity / 100.0)
    return pts, f"popularity boost (+{pts:.2f})"


def _score_decade(song_decade: int, weight: float, preferred_decade: int = 2020) -> Tuple[float, str]:
    """Award points for songs closer to a preferred era."""
    distance = abs(song_decade - preferred_decade) / 10.0
    pts = weight * max(0.0, 1.0 - distance * 0.25)
    return pts, f"era match (+{pts:.2f})"


def _compute_score(
    song_genre: str, song_mood: str, song_energy: float,
    song_valence: float, song_dance: float, song_acoustic: float,
    song_popularity: int, song_decade: int,
    user_genre: str, user_mood: str, user_energy: float,
    likes_acoustic: bool, mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """Run the full Algorithm Recipe and return (total_score, reasons_list)."""
    w = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    total = 0.0
    reasons: List[str] = []

    checks = [
        _score_genre(song_genre, user_genre, w["genre"]),
        _score_mood(song_mood, user_mood, w["mood"]),
        _score_energy(song_energy, user_energy, w["energy"]),
        _score_valence(song_valence, w["valence"]),
        _score_danceability(song_dance, w["danceability"]),
        _score_acousticness(song_acoustic, likes_acoustic, w["acousticness"]),
        _score_popularity(song_popularity, w["popularity"]),
        _score_decade(song_decade, w["decade"]),
    ]

    for pts, reason in checks:
        total += pts
        if reason:
            reasons.append(reason)

    return round(total, 2), reasons


# ---------------------------------------------------------------------------
# Challenge 3: Diversity Penalty
# ---------------------------------------------------------------------------

def _apply_diversity_penalty(
    scored: List[Tuple[Dict, float, str]],
    max_per_genre: int = 2,
    max_per_artist: int = 1,
    penalty: float = 1.5,
) -> List[Tuple[Dict, float, str]]:
    """Re-rank results so the top K doesn't over-represent one genre or artist."""
    genre_count: Dict[str, int] = {}
    artist_count: Dict[str, int] = {}
    adjusted: List[Tuple[Dict, float, str]] = []

    for song, score, explanation in scored:
        g = song["genre"].lower()
        a = song["artist"].lower()
        genre_count[g] = genre_count.get(g, 0) + 1
        artist_count[a] = artist_count.get(a, 0) + 1

        adj_score = score
        penalty_reasons = []

        if genre_count[g] > max_per_genre:
            adj_score -= penalty
            penalty_reasons.append(f"genre diversity penalty (-{penalty:.2f})")
        if artist_count[a] > max_per_artist:
            adj_score -= penalty
            penalty_reasons.append(f"artist diversity penalty (-{penalty:.2f})")

        if penalty_reasons:
            explanation = explanation + "; " + "; ".join(penalty_reasons)

        adjusted.append((song, round(adj_score, 2), explanation))

    adjusted.sort(key=lambda item: item[1], reverse=True)
    return adjusted


# ---------------------------------------------------------------------------
# Functional Path (dict-based — used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, csv_path)

    songs: List[Dict] = []
    with open(full_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            row["popularity"] = int(row.get("popularity", 50))
            row["release_decade"] = int(row.get("release_decade", 2020))
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, List[str]]:
    """Score a single song against user preferences using the Algorithm Recipe."""
    return _compute_score(
        song_genre=song["genre"], song_mood=song["mood"],
        song_energy=song["energy"], song_valence=song["valence"],
        song_dance=song["danceability"], song_acoustic=song["acousticness"],
        song_popularity=song.get("popularity", 50),
        song_decade=song.get("release_decade", 2020),
        user_genre=user_prefs.get("genre", ""),
        user_mood=user_prefs.get("mood", ""),
        user_energy=user_prefs.get("energy", 0.5),
        likes_acoustic=user_prefs.get("likes_acoustic", False),
        mode=mode,
    )


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5,
    mode: str = "balanced", diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, optionally apply diversity penalty, return the top k."""
    scored: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = "; ".join(reasons) if reasons else "no strong match"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)

    if diversity:
        scored = _apply_diversity_penalty(scored)

    return scored[:k]


# ---------------------------------------------------------------------------
# OOP Path (class-based — used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Return the numeric score for a single Song against a UserProfile."""
        score, _ = _compute_score(
            song_genre=song.genre, song_mood=song.mood,
            song_energy=song.energy, song_valence=song.valence,
            song_dance=song.danceability, song_acoustic=song.acousticness,
            song_popularity=song.popularity, song_decade=song.release_decade,
            user_genre=user.favorite_genre, user_mood=user.favorite_mood,
            user_energy=user.target_energy, likes_acoustic=user.likes_acoustic,
        )
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs sorted by score descending."""
        ranked = sorted(
            self.songs,
            key=lambda song: self._score_song(user, song),
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        _, reasons = _compute_score(
            song_genre=song.genre, song_mood=song.mood,
            song_energy=song.energy, song_valence=song.valence,
            song_dance=song.danceability, song_acoustic=song.acousticness,
            song_popularity=song.popularity, song_decade=song.release_decade,
            user_genre=user.favorite_genre, user_mood=user.favorite_mood,
            user_energy=user.target_energy, likes_acoustic=user.likes_acoustic,
        )
        return "; ".join(reasons) if reasons else "no strong match"
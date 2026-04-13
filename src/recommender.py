"""
Music Recommender — core scoring and recommendation logic.

This module provides two interfaces:
1. Functional (dict-based): load_songs, score_song, recommend_songs — used by main.py
2. OOP (class-based): Song, UserProfile, Recommender — used by tests
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


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Shared Scoring Logic
# ---------------------------------------------------------------------------
# Both the functional and OOP paths call these helpers so the Algorithm Recipe
# lives in exactly one place.  If you change a weight here, both paths update.

def _score_genre(song_genre: str, user_genre: str) -> Tuple[float, str]:
    """Award +2.0 points if the song's genre matches the user's favorite."""
    if song_genre.lower() == user_genre.lower():
        return 2.0, "genre match (+2.00)"
    return 0.0, ""


def _score_mood(song_mood: str, user_mood: str) -> Tuple[float, str]:
    """Award +1.0 point if the song's mood matches the user's favorite."""
    if song_mood.lower() == user_mood.lower():
        return 1.0, "mood match (+1.00)"
    return 0.0, ""


def _score_energy(song_energy: float, user_energy: float) -> Tuple[float, str]:
    """Award up to +1.0 point based on closeness to the user's target energy."""
    pts = 1.0 - abs(song_energy - user_energy)
    return pts, f"energy similarity (+{pts:.2f})"


def _score_valence(song_valence: float, midpoint: float = 0.5) -> Tuple[float, str]:
    """Award up to +0.5 points for valence closeness to a neutral midpoint."""
    pts = 0.5 * (1.0 - abs(song_valence - midpoint))
    return pts, f"valence similarity (+{pts:.2f})"


def _score_danceability(song_dance: float, midpoint: float = 0.5) -> Tuple[float, str]:
    """Award up to +0.5 points for danceability closeness to a neutral midpoint."""
    pts = 0.5 * (1.0 - abs(song_dance - midpoint))
    return pts, f"danceability similarity (+{pts:.2f})"


def _score_acousticness(song_acoustic: float, likes_acoustic: bool) -> Tuple[float, str]:
    """Award +0.3 bonus if the user likes acoustic and the song is acoustic."""
    if likes_acoustic and song_acoustic > 0.7:
        return 0.3, "acoustic bonus (+0.30)"
    return 0.0, ""


def _compute_score(
    song_genre: str,
    song_mood: str,
    song_energy: float,
    song_valence: float,
    song_dance: float,
    song_acoustic: float,
    user_genre: str,
    user_mood: str,
    user_energy: float,
    likes_acoustic: bool,
) -> Tuple[float, List[str]]:
    """
    Run the full Algorithm Recipe and return (total_score, reasons_list).

    This is the single source of truth for scoring.  Both the dict-based
    score_song() and the OOP Recommender call this function.
    """
    total = 0.0
    reasons: List[str] = []

    checks = [
        _score_genre(song_genre, user_genre),
        _score_mood(song_mood, user_mood),
        _score_energy(song_energy, user_energy),
        _score_valence(song_valence),
        _score_danceability(song_dance),
        _score_acousticness(song_acoustic, likes_acoustic),
    ]

    for pts, reason in checks:
        total += pts
        if reason:                       # skip empty reasons (no match)
            reasons.append(reason)

    return round(total, 2), reasons


# ---------------------------------------------------------------------------
# Functional Path (dict-based — used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries."""
    # Resolve path relative to project root (one level up from src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, csv_path)

    songs: List[Dict] = []
    with open(full_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields from strings to proper types
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences using the Algorithm Recipe."""
    return _compute_score(
        song_genre=song["genre"],
        song_mood=song["mood"],
        song_energy=song["energy"],
        song_valence=song["valence"],
        song_dance=song["danceability"],
        song_acoustic=song["acousticness"],
        user_genre=user_prefs.get("genre", ""),
        user_mood=user_prefs.get("mood", ""),
        user_energy=user_prefs.get("energy", 0.5),
        likes_acoustic=user_prefs.get("likes_acoustic", False),
    )


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort by score descending, and return the top k results."""
    scored: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong match"
        scored.append((song, score, explanation))

    # sorted() returns a new list — original stays unchanged
    scored.sort(key=lambda item: item[1], reverse=True)

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
            song_genre=song.genre,
            song_mood=song.mood,
            song_energy=song.energy,
            song_valence=song.valence,
            song_dance=song.danceability,
            song_acoustic=song.acousticness,
            user_genre=user.favorite_genre,
            user_mood=user.favorite_mood,
            user_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
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
            song_genre=song.genre,
            song_mood=song.mood,
            song_energy=song.energy,
            song_valence=song.valence,
            song_dance=song.danceability,
            song_acoustic=song.acousticness,
            user_genre=user.favorite_genre,
            user_mood=user.favorite_mood,
            user_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
        )
        return "; ".join(reasons) if reasons else "no strong match"
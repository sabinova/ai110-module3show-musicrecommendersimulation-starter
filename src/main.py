"""
Command line runner for the Music Recommender Simulation.

Demonstrates all optional extensions:
- Challenge 1: Advanced features (popularity, release_decade in scoring)
- Challenge 2: Multiple scoring modes (balanced, genre-first, mood-first, energy-focused)
- Challenge 3: Diversity penalty (diversity=True flag)
- Challenge 4: Visual summary table output
"""

from recommender import load_songs, recommend_songs, SCORING_MODES


# ---------------------------------------------------------------------------
# Challenge 4: Visual Summary Table
# ---------------------------------------------------------------------------

def print_table(profile_name: str, user_prefs: dict, songs: list,
                k: int = 5, mode: str = "balanced", diversity: bool = False) -> None:
    """Display recommendations as a formatted ASCII table."""
    recommendations = recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity)

    header = f"  Profile: {profile_name}  |  Mode: {mode}  |  Diversity: {'ON' if diversity else 'OFF'}"
    print(f"\n{'=' * 90}")
    print(header)
    print(f"  Prefs: {user_prefs}")
    print(f"{'=' * 90}")

    # Table header
    print(f"  {'#':<4} {'Title':<28} {'Artist':<18} {'Genre':<12} {'Score':>6}")
    print(f"  {'-'*4} {'-'*28} {'-'*18} {'-'*12} {'-'*6}")

    # Table rows
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        title = song['title'][:27]
        artist = song['artist'][:17]
        genre = song['genre'][:11]
        print(f"  {rank:<4} {title:<28} {artist:<18} {genre:<12} {score:>6.2f}")

    # Reasons detail below the table
    print(f"\n  Reasoning:")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank} {song['title']}: {explanation}")

    print(f"\n{'-' * 90}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_pop = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    user_lofi = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}
    user_rock = {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
    user_edge = {"genre": "classical", "mood": "energetic", "energy": 0.9, "likes_acoustic": True}

    # --- Core profiles (balanced mode, no diversity) ---
    print("\n" + "=" * 90)
    print("  PART 1: Core Profiles — Balanced Mode")
    print("=" * 90)

    print_table("Happy Pop Listener", user_pop, songs)
    print_table("Chill Lofi Studier", user_lofi, songs)
    print_table("Intense Rock Gym-Goer", user_rock, songs)
    print_table("Classical Energetic (Edge Case)", user_edge, songs)

    # --- Challenge 2: Compare scoring modes on one profile ---
    print("\n" + "=" * 90)
    print("  PART 2: Scoring Mode Comparison — Rock Gym-Goer Profile")
    print("=" * 90)

    for mode_name in SCORING_MODES:
        print_table("Rock Gym-Goer", user_rock, songs, mode=mode_name)

    # --- Challenge 3: Diversity penalty demo ---
    print("\n" + "=" * 90)
    print("  PART 3: Diversity Penalty — Lofi Profile")
    print("=" * 90)

    print_table("Lofi (No Diversity)", user_lofi, songs, diversity=False)
    print_table("Lofi (Diversity ON)", user_lofi, songs, diversity=True)


if __name__ == "__main__":
    main()
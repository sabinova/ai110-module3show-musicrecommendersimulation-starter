"""
Command line runner for the Music Recommender Simulation.

Loads the song catalog, applies user taste profiles, and prints
ranked recommendations with scores and explanations.
"""

from recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Display recommendations for a single user profile in a clean format."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print(f"{'=' * 60}")
    print(f"  Profile: {profile_name}")
    print(f"  Preferences: {user_prefs}")
    print(f"{'=' * 60}")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        print(f"       Why:   {explanation}")

    print(f"\n{'-' * 60}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")

    # --- Default profile (Phase 3 verification) ---
    print_recommendations(
        profile_name="Happy Pop Listener",
        user_prefs={"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        songs=songs,
    )


if __name__ == "__main__":
    main()
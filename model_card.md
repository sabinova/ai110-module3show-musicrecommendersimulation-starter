# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

This system suggests the top 5 songs from a small catalog of 20 tracks based on a user's preferred genre, mood, and energy level. It is built for classroom exploration to understand how content-based recommenders work. It is not designed for real users or production environments.

---

## 3. How the Model Works

The recommender compares each song in the catalog against a user's taste profile using a weighted scoring system. Genre match awards the most points (+2.0) since it is the strongest signal of musical preference. Mood match adds +1.0. Energy similarity is measured by how close the song's energy is to the user's target — the smaller the gap, the higher the score (up to +1.0). Valence and danceability each contribute up to +0.5 based on closeness to a neutral midpoint. If the user prefers acoustic music and the song has high acousticness, a +0.3 bonus is added.

Once every song has a score, the system sorts them from highest to lowest and returns the top 5 with explanations listing exactly which checks contributed points.

---

## 4. Data

The catalog contains 20 songs in `data/songs.csv` spanning 14 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, hip-hop, edm, classical, country, latin, metal, folk, funk) and 10 moods (happy, chill, intense, relaxed, moody, focused, romantic, energetic, melancholic, nostalgic, aggressive, sad). The original starter dataset had 10 songs; 10 were added to improve genre and mood diversity.

Each song has numerical features on a 0–1 scale (energy, valence, danceability, acousticness) plus tempo in BPM. The dataset is still small and does not represent the breadth of real musical taste — there is no reggae, blues, gospel, or K-pop, for example, and each genre has at most 3 songs.

---

## 5. Strengths

The system works well for users whose preferences align cleanly with songs in the catalog. The "Chill Lofi Studier" profile produced excellent results — the top 3 songs were all lofi tracks correctly sorted by mood and energy closeness, and the acoustic bonus helped surface Coffee Shop Stories (jazz) as a reasonable #5 pick.

The explanation system is a clear strength. Every recommendation comes with a breakdown of exactly why it was chosen, making the scoring transparent and easy to audit. You can look at a result and immediately understand which features drove the ranking.

---

## 6. Limitations and Bias

The system's biggest weakness is **genre dominance**. With genre worth 2.0 out of 5.3 possible points, a genre-matching song with terrible energy and mood scores can still outrank a perfect-vibe song from a different genre. In testing, Winter Sonata (classical/melancholic/energy 0.2) ranked #1 for a user wanting classical + energetic + energy 0.9 — a slow, sad piece recommended to someone who wanted high-energy music, purely because the genre matched.

**Exact-match categories miss related genres.** "Indie pop" does not match "pop," and "metal" does not match "rock," even though listeners of one often enjoy the other. Iron Descent (metal/aggressive/0.97) ranked only #5 for a rock gym-goer despite being an obvious real-world fit.

**The catalog is too small to avoid repetition.** With only 1–3 songs per genre, the system quickly runs out of good matches and starts recommending songs with no categorical connection at all.

**Valence and danceability use a fixed midpoint (0.5)** instead of user-specified targets, which penalizes songs at the extremes and favors "middle of the road" tracks.

---

## 7. Evaluation

Four user profiles were tested:

**Happy Pop Listener** (pop/happy/energy 0.8): Sunrise City ranked #1 with a score of 4.66 — a near-perfect match. Gym Hero ranked #2, losing exactly the mood match point. Results felt intuitive.

**Chill Lofi Studier** (lofi/chill/energy 0.4, likes acoustic): Top 3 were all lofi tracks, with Midnight Coding and Library Rain nearly tied. The acoustic bonus correctly elevated Coffee Shop Stories. This profile produced the most satisfying results.

**Intense Rock Gym-Goer** (rock/intense/energy 0.9): Storm Runner was a clear #1 at 4.90. The surprise was Iron Descent (metal/aggressive/0.97) at only #5 with 1.82 — it feels like a great gym song but gets zero categorical points because "metal" ≠ "rock."

**Classical Energetic Edge Case** (classical/energetic/energy 0.9, likes acoustic): This was the adversarial test. Winter Sonata (energy 0.2) ranked #1 despite being the opposite of what the user wanted energy-wise. Genre dominance overrode the energy mismatch completely.

**Weight experiment:** Halving genre (2.0 → 1.0) and doubling energy (1.0 → 2.0) fixed the edge case — Winter Sonata dropped from #1 to #5 and Block Party (hip-hop/energetic/0.85) rose to #1. This confirmed that the original weighting creates a filter bubble around genre.

---

## 8. Future Work

- **Genre similarity instead of exact match.** Treat "metal" and "rock" as related genres with a partial match score (e.g., +1.0 instead of +2.0 for related, +0.0 for unrelated). This would fix the Iron Descent problem.
- **User-specified valence and danceability targets** instead of the fixed 0.5 midpoint, so the system can distinguish between users who want high-energy dance music vs. high-energy headbanging music.
- **Diversity penalty** that prevents the top 5 from being all the same genre or artist, forcing the system to surface variety instead of repeating the closest matches.

---

## 9. Personal Reflection

The biggest learning moment for me was the Classical Energetic edge case. I expected the system to recommend high-energy music since the user wanted energy at 0.9, but instead it put Winter Sonata — a slow, melancholic classical piece — at #1 just because the genre matched. That one test made the concept of filter bubbles click for me in a way that reading about them never did. The system was technically doing exactly what I told it to do, but the result was clearly wrong. It showed me that the weights you choose aren't just numbers — they encode assumptions about what matters, and those assumptions can quietly steer the whole system in a bad direction.

Working with AI tools helped me move faster, especially for scaffolding the project structure and generating the expanded dataset. But I had to double-check things like file path handling — the initial code broke because the CSV path was relative to the working directory, not the project root. That was a good reminder that generated code can look correct and still fail in your specific setup.

What surprised me most is how simple the algorithm really is. It's just addition and sorting. There's no machine learning, no neural network — just a loop that adds up points and picks the highest scores. And yet when I ran the Chill Lofi profile and saw Midnight Coding and Library Rain at the top, it genuinely felt like a real recommendation. That gap between how simple the system is and how "smart" it feels is something I'll think about differently now when I use Spotify or YouTube.
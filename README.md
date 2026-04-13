# 🎵 Music Recommender Simulation

## Project Summary

This project is a content-based music recommender built in Python. Unlike collaborative filtering, which relies on behavior from many users to find patterns (like Spotify's "users who liked X also liked Y"), this system works purely by comparing song attributes against a single user's taste profile. Each song in the catalog has features like genre, mood, energy, and danceability. The user provides their preferences, and the system scores every song based on how closely it matches, then returns the top results with explanations for each recommendation. It is designed for classroom exploration, not real-world use.

---

## How The System Works

This recommender uses a content-based filtering approach. It takes a user's taste profile and compares it against every song in a small CSV catalog to find the best matches.
 
Each `Song` carries the following features: genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), and acousticness (0–1). Genre and mood are categorical — they either match the user's preference or they don't. The numerical features allow the system to measure closeness rather than requiring an exact match.
 
A `UserProfile` stores: favorite_genre, favorite_mood, target_energy, and likes_acoustic. These represent the user's ideal "vibe" that every song gets compared against.
 
The scoring logic (the "Algorithm Recipe") works like this for each song:
 
- **Genre match:** +2.0 points if the song's genre matches the user's favorite genre. Genre carries the most weight because it tends to be the strongest signal of musical preference — recommending rock to a pop listener is usually a bigger miss than getting the energy level slightly off.
- **Mood match:** +1.0 point if the song's mood matches the user's favorite mood. Mood matters, but less than genre. A user who wants "happy pop" would likely still enjoy "intense pop" more than "happy jazz."
- **Energy similarity:** Up to +1.0 point based on how close the song's energy is to the user's target. Calculated as `1.0 - abs(song_energy - target_energy)`. A song with energy 0.82 scores 0.98 against a target of 0.80, while a song at 0.30 only scores 0.50.
 
Once every song has a score, the system sorts them from highest to lowest and returns the top K results along with the reasons each song earned its points.
 
**Expected bias:** Because genre has the highest weight (2.0), the system will tend to favor songs in the user's preferred genre even when songs from other genres might better match their mood and energy preferences. This is a deliberate trade-off — genre acts as a strong filter, which could create a filter bubble over time.
 
Data flow: **Input** (User Preferences) → **Process** (Loop through every song, score it using the algorithm recipe) → **Output** (Top K ranked recommendations with explanations).

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


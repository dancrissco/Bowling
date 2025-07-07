# Bowling Simulator with AI Opponent

This is an interactive 3D bowling simulator built with **PyBullet** and **Tkinter** in Python. The game features realistic physics, visual effects, sound, and a competitive AI opponent.

## 🎮 Features

- Full 3D physics-based bowling environment
- Tkinter GUI for player control and scoring display
- Adjustable ball **position** and **angle** using sliders
- Realistic 5-pin bowling setup on a wooden-style lane
- Cinematic **camera fly-in** after each throw
- Dynamic **sound effect** when pins are knocked down
- Frame-by-frame play (5 frames total)
- Alternating turns between **player and AI opponent**
- AI aims toward strike zone with slight variations
- Live score tracking for both player and AI

---

## 📂 Files

- `bowling_sim_ai.py` – Main Python script
- `hit.wav` – Sound file for pin collision (place in same folder)
- `README.md` – This file

---

## 🛠 Requirements

Install dependencies using pip:

```bash
pip install pybullet numpy playsound
```

You must also have a `hit.wav` sound file in the same directory. You can use any short `.wav` sound (e.g. bowling pin hit, clap).

---

## 🚀 Running the Game

```bash
python bowling_sim_ai.py
```

Use the sliders to set your ball's X-position and launch angle. Click **"Throw Ball"** to play your turn. Watch the AI opponent follow you!

---

## 📸 Screenshots

> Coming soon: Add screenshots or gifs of the gameplay in action.

---

## 🤖 AI Behavior

The AI opponent simulates a skilled bowler:

- Aims for the 1-3 pin pocket
- Uses random offset within a small range to mimic human error

---

## 🧠 Educational Uses

This project is great for:

- Teaching physics simulation and computer vision
- Exploring camera control and UI integration
- Demonstrating beginner AI behavior in games
- Engaging STEM learners through interactive robotics concepts

---

## 📌 TODO / Roadmap

-

---

## 👤 Author

Created by [Your Name]. Inspired by engineering demos and robotics simulation projects.

---

## 📃 License

MIT License (or choose your preferred license)


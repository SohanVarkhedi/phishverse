# PHISHVERSE — Cybersecurity Awareness RPG

A **Pokémon Fire Red / Emerald-style** 2D top-down RPG built with **Python + Pygame**.

> Navigate the office. Resist phishing attacks. Protect your Cyber Score.

---

## 🕹️ How to Run

```bash
pip install pygame
python main.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `WASD` / `Arrow Keys` | Move player |
| `E` / `Enter` | Interact with object / Confirm dialog choice |
| `↑` / `↓` in dialog | Navigate choices |
| `ESC` | Pause menu |
| `Q` / `ESC` (Report) | Quit game |

---

## 🗺️ Map Layout

```
┌─────────────────────────────────────────┐
│             ENTRY / OUTSIDE             │
├─────────────────────────────────────────┤
│               RECEPTION                 │
├─────────────────┬───────────────────────┤
│   WORK AREA     │        HR ROOM        │
├─────────────────┼───────────────────────┤
│   CAFETERIA     │    MEETING ROOM       │
├─────────────────┴───────────────────────┤
│            IT SUPPORT DESK              │
└─────────────────────────────────────────┘
```

Player spawns at **Entry** (top) and walks south through the building.

---

## ⚠️ Cybersecurity Events

| # | Event | Location | Attack Type |
|---|-------|----------|-------------|
| 1 | Email Phishing (Password Reset) | Work Area — Computer | Urgency Manipulation |
| 2 | QR Code Phishing | Cafeteria — Poster | Reward Manipulation |
| 3 | USB Drop Attack | Entry — Floor | Curiosity Bait |
| 4 | HR Authority Message | HR Room — Computer | Authority Phishing |
| 5 | Voice Phishing (Vishing) | HR Room — Phone | Authority + Fear |
| 6 | CEO Fraud / BEC (BOSS) | Meeting Room | BEC Attack |

---

## 📊 Player Stats

| Stat | Description |
|------|-------------|
| `score` | Starts at 100; decreases on wrong choices |
| `urgency_bias` | Susceptibility to time-pressure attacks |
| `authority_bias` | Susceptibility to fake authority |
| `reward_bias` | Susceptibility to free-prize lures |
| `fear_bias` | Susceptibility to fear-based threats |

---

## 🏁 Ending

Complete all 6 events → **Cyber Resilience Report** is generated showing:
- Final Score
- Bias breakdown (animated bars)
- Risk Level: `LOW` / `MEDIUM` / `HIGH`
- Weakest Area
- Personalised Recommendation
- Cyber Awareness Certificate

---

## 📁 Project Structure

```
PHISHVERSE/
├── main.py           ← Game loop, state machine
├── constants.py      ← All config & colours
├── player.py         ← Tile movement, sprite
├── map.py            ← 40×33 office tile grid
├── tiles.py          ← Procedural pixel-art tile renderer
├── npc.py            ← NPC characters & dialogue
├── dialogue.py       ← Pokémon-style dialog box
├── events.py         ← Event definitions loader
├── event_manager.py  ← Event lifecycle orchestrator
├── risk_engine.py    ← Score tracking & risk assessment
├── ui.py             ← HUD, pause menu, title screen
├── report.py         ← Final Cyber Resilience Report
├── data/
│   └── events.json   ← All 6 event definitions (JSON)
└── requirements.txt
```

---

## 🔧 Technical Notes

- **No external assets required** — all tiles and sprites are procedurally drawn with `pygame` primitives
- **OOP architecture** — each system is a separate module
- **JSON-driven events** — add new events by editing `data/events.json`
- Tested with **Python 3.13 + pygame 2.6.1**

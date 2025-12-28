# 📌 Stick To It
A minimalist, sticky-note-style productivity timer that lives on your desktop, tracks task lifecycle states in a CSV, and nudges you every two hours to stay focused. It categorizes tasks into **Now** and **Later**, tracking the exact timestamp of every state change (Created → In Progress → Completed) directly into a local CSV file. Keep note of the tasks you want to work, you are working on and completed, at end of the year see what you have achieved.

## ✨ Features
* **Three-State Tracking:** Automatically logs dates for task creation, start, and completion.
* **Smart UI:** "Now" section stays expanded; "Later" stays collapsed until needed.
* **Automatic Reminders:** Pops up every 2 hours to keep you accountable.
* **Privacy First:** All data is stored in a simple `tasks.csv` on your machine.
* **No Admin Required:** Runs entirely in user-space.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.8+** must be installed on your system.

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/prasadkothavale/stick-to-it.git
   cd stick-to-it
   ```
2. **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv stick-to-it
    ```
- Windows: 
    ```bash
    source stick-to-it/Scripts/activate
    ```
- Mac/Linux:
    ```bash
    source stick-to-it/bin/activate
    ```

## 🖥️ Platform Setup
### Windows (Primary)

To make Stick To It start automatically without admin rights:

1. Create a shortcut of main.py (or the compiled .exe).
2. Press `⊞ Win` + `R`, type `shell:startup`, and hit `⏎ Enter`.
3. Paste the shortcut into this folder.

### macOS
1. Open System Settings > General > Login Items.
2. Add the Python script or your compiled app to the list.
    > Note: Ensure you grant "Accessibility" permissions if you want the app to stay "Always on Top."

### Linux
1. Create a `.desktop` file in `~/.config/autostart/`.
2. Add the execution path to your python environment and the script.

## 📊 Data Storage
Data is saved in `tasks.csv` with the following headers: `Index`, `Todo Item`, `Start Date`, `In Progress Date`, `Completed Date, Status`

## Project Structure
```
stick-to-it/
├── src/
│   ├── main.py        # UI and Logic
│   ├── database.py    # CSV handling
│   └── styles.qss     # Visual styling (CSS-like)
├── assets/            # Icons
├── requirements.txt
├── LICENSE
└── README.md
```
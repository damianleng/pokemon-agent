# AI Strategies for Simulated Pokémon Battles

Comparing AI decision-making strategies (random, heuristics, greedy, lookahead) in simulated Pokémon battles using [poke-env](https://github.com/hsahovic/poke-env) and a local Pokémon Showdown server.

## Requirements

- Python 3.14+
- Node.js (for the Showdown server)

---

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd pokemon
```

### 2. Set up the Pokémon Showdown server

```bash
git clone https://github.com/smogon/pokemon-showdown.git
cd pokemon-showdown
npm install
node pokemon-showdown start --no-security
```

Leave this running in its own terminal. The server runs on `http://localhost:8000`.

### 3. Set up the Python environment

In a new terminal, from the `pokemon/` directory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running

Make sure the Showdown server is running, then:

```bash
source venv/bin/activate
python3 main.py
```

This runs 100 battles per matchup across 6 pairings and prints a summary table to the console, saves `results.png`, and generates `analysis_report.pdf`.

---

## AI Strategies

| Strategy | Class | Description |
|---|---|---|
| **Random** | `TrackedRandomPlayer` | Selects moves uniformly at random |
| **Heuristics** | `TrackedHeuristicsPlayer` | poke-env's built-in `SimpleHeuristicsPlayer` |
| **Greedy** | `MaxDamagePlayer` | Picks the move with highest base power × type effectiveness |
| **Lookahead** | `LookaheadPlayer` | Expectimax search to depth 2; opponent moves averaged (chance node) |

### Matchups

- Random vs Heuristics
- Greedy vs Heuristics
- Greedy vs Random
- Lookahead vs Random
- Lookahead vs Greedy
- Lookahead vs Heuristics

---

## Metrics Tracked

Each player collects per-battle data via `MetricsMixin`:

- **Win rate** — with binomial test for statistical significance (`***` if p < 0.05)
- **Avg turns per battle**
- **Avg team HP on win**
- **Avg Pokémon fainted per battle**
- **Streak analysis** — longest win/loss streaks, average streak length
- **Move selection patterns** — offensive/defensive/status split, type effectiveness rates, switch frequency

---

## Output

| File | Description |
|---|---|
| `results.png` | 6-panel bar chart (win rate, avg turns, avg win HP, win/loss breakdown, avg fainted, legend) |
| `analysis_report.pdf` | Multi-page PDF with the chart, statistical significance summary, per-player detail, and strategic insights |

---

## Project Structure

```
pokemon/
├── main.py              # Battle runner and console output
├── players.py           # AI player classes (Random, Heuristics, Greedy, Lookahead)
├── metrics.py           # MetricsMixin and statistical analysis functions
├── visualize.py         # matplotlib chart generation → results.png
├── pdf_report.py        # PDF report generation → analysis_report.pdf
├── analysis_display.py  # Strategy insight extraction and console display helpers
├── requirements.txt     # Python dependencies
├── pokemon-showdown/    # Local Showdown server (git ignored)
└── venv/                # Python virtual environment (git ignored)
```

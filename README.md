# AI Strategies for Simulated Pokémon Battle

Comparing AI decision-making strategies (random, greedy, lookahead) in simulated Pokémon battles using [poke-env](https://github.com/hsahovic/poke-env) and a local Pokémon Showdown server.

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
python3 test_connection.py
```

---

## Project Structure

```
pokemon/
├── test_connection.py       # AI agents and battle simulation
├── pokemon-showdown/        # Local Showdown server (git ignored)
├── venv/                    # Python virtual environment (git ignored)
└── README.md
```

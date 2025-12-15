# Steam Games Dashboard (2004–2019)

Interactive data visualization dashboard exploring trends in Steam games from 2004–2019, including release volume, pricing, genre composition, and player review sentiment.

## Dashboard Preview

Open: `visuals/00_dashboard.html`

## Features

* **Games released per year** (interactive year-range brush)
* **Price distribution by year**
* **Genre composition over time** (Top 10 + Other)
* **Reviews vs. rating** (log-scaled review counts)
* **Genre market share** filtered by selected years

## Tech Stack

* Python
* Pandas
* Altair

## Project Structure

* `dashboard.py` — data cleaning + chart generation
* `visuals/00_dashboard.html` — exported interactive dashboard
* `steam_games.csv` — dataset (if included)

## Setup

### 1) Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

## Run

```bash
python dashboard.py
```

After running, open:

* `visuals/00_dashboard.html`

## Data Source

Steam games dataset (Kaggle).
If your dataset is not included in this repo, download it and place it as `steam_games.csv` in the project root.

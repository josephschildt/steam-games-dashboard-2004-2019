# Steam Games Dashboard (2004–2019)

An interactive data visualization dashboard exploring trends in Steam games from 2004–2019.
This project analyzes release volume, pricing behavior, genre composition, and player review patterns using Python and Altair.

## Dashboard Preview
<img width="1372" height="1276" alt="visualization (3)" src="https://github.com/user-attachments/assets/ad42ee29-884e-49eb-8507-053c460c8936" />


After running the project, open the generated dashboard here:

```
visuals/00_dashboard.html
```

## Key Features

* **Games released per year** with an interactive year-range brush
* **Price distribution by year**
* **Genre composition over time** (Top 10 genres + Other)
* **Reviews vs. rating** with log-scaled review counts
* **Genre market share** filtered by selected years

## Tech Stack

* Python 3.12+
* Pandas
* Altair
* KaggleHub
* NumPy

## Project Structure

```
steam-games-dashboard-2004-2019/
├── dashboard.py            # Data cleaning and chart generation
├── requirements.txt        # Python dependencies
├── visuals/
│   └── 00_dashboard.html   # Exported interactive dashboard
├── .gitignore
└── README.md
```

## Setup Instructions

### 1) Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

```bash
python dashboard.py
```

Once the script finishes, open:

```
visuals/00_dashboard.html
```

in your browser to view the dashboard.

## Dataset

This project uses the **Steam Games Dataset** from Kaggle.

**Source:**
[https://www.kaggle.com/datasets/trolukovich/steam-games-complete-dataset](https://www.kaggle.com/datasets/trolukovich/steam-games-complete-dataset)

Due to its large file size (~78 MB), the dataset is **not included** in this repository and is ignored via `.gitignore`.

### To run the project locally:

1. Download the dataset from Kaggle using the link above
2. Extract the file
3. Place it in the project root as:

```
steam_games.csv
```


## Notes

* The repository intentionally excludes large data files to follow GitHub best practices
* All visualizations are generated programmatically using Altair
* This project was designed to emphasize clarity, interactivity, and clean exploratory analysis

---

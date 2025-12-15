# Steam Dashboard 2004 - 2019, Joseph Schildt

import os
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path


# Setup and load data
# Make sure the visuals folder exists so Altair has somewhere to save the HTML
Path("visuals").mkdir(exist_ok = True)

# Try to grab the dataset from KaggleHub first, fall back to local CSV
try:
    import kagglehub

    data_path = kagglehub.dataset_download(
        "trolukovich/steam-games-complete-dataset"
    )
    csv_path = os.path.join(data_path, "steam_games.csv")
except Exception:
    csv_path = "steam_games.csv"

# Read in the main Steam games dataset
df = pd.read_csv(csv_path, encoding = "latin-1", low_memory = False, on_bad_lines = "skip")


# Fix encoding such as"The WitcherÂ® 3"
# Helper strips bad symbols
def strip_bad_chars(series):
    cleaned = []
    for v in series:
        if isinstance(v, str):
            cleaned.append(v.replace("Â", ""))  # drop Â
        else:
            cleaned.append(v)
    return cleaned


for col in ["name", "genre", "all_reviews"]:
    if col in df.columns:
        df[col] = strip_bad_chars(df[col])


# Basic cleaning

# Convert release date into an actual datetime
df["release_date"] = pd.to_datetime(df["release_date"], errors = "coerce")
# Extract just the year as a number
df["year"] = df["release_date"].dt.year

# Only keep relevant Steam years
df = df[df["year"].between(2004, 2019)]

# If the dataset has a "types" column, only keep games (apps) and drop DLC, tools, etc.
if "types" in df.columns:
    df = df[df["types"] == "app"]


# Price cleaning, turns to numeric price column in USD
def clean_price(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower().replace("$", "")
    # Handle free games and empty values
    if s in ("free", "", "0", "0.00"):
        return 0.0
    try:
        return float(s)
    except Exception:
        return np.nan

price_list = []
for v in df["original_price"]:
    price_list.append(clean_price(v))

# Store the cleaned price as a new numeric column
df["price"] = pd.to_numeric(price_list, errors = "coerce")


# Genre list, each game can have multiple genres separated by commas.
genre_lists = []
for g in df["genre"].fillna("Unknown"):
    g_str = str(g)
    genre_lists.append(g_str.split(","))
df["genre_list"] = genre_lists


# Reviews parsing (for bottom charts)
# all_reviews looks like:
# "Very Positive (12,345 reviews)"
# Desired format:
# sentiment = "Very Positive"
# review_count = 12345
sentiments = []
review_counts = []

for text in df["all_reviews"].astype(str):
    text = text.strip()
    if "(" in text and ")" in text:
        # Player rating text is everything before first "("
        before = text.split("(", 1)[0].strip()

        # Get inside the first "()" which has review counts
        start = text.find("(") + 1
        end = text.find(")", start)
        if end == -1:
            inside = ""
        else:
            inside = text[start:end]

        # Keep only digits and commas from inside "(12,345 reviews)"
        digits_only = ""
        for ch in inside:
            if ch.isdigit() or ch == ",":
                digits_only += ch

        # Rating label
        if before == "":
            sentiments.append(np.nan)
        else:
            sentiments.append(before)

        # Review count as a number
        if digits_only == "":
            review_counts.append(np.nan)
        else:
            try:
                review_counts.append(int(digits_only.replace(",", "")))
            except Exception:
                review_counts.append(np.nan)
    else:
        # Rows with no pattern, treated as missing
        sentiments.append(np.nan)
        review_counts.append(np.nan)

# Clean up commas/spaces at the end of random labels
clean_sentiments = []
for s in sentiments:
    if isinstance(s, str):
        clean_sentiments.append(s.rstrip(",").strip())
    else:
        clean_sentiments.append(s)

# Internal name is "sentiment" but I describe it as "Player Rating" in the chart
df["sentiment"] = clean_sentiments
df["review_count"] = review_counts

# Only keep rows that actually have reviews
rv = df[(df["review_count"].notna()) & (df["review_count"] > 0)].copy()


# Long genre table: Top 10 + "Other"
g_long = df.explode("genre_list")
g_long["genre_item"] = g_long["genre_list"].astype(str).str.strip()

# Count how often each genre shows up
genre_counts = g_long["genre_item"].value_counts()
# Keep top 10 genres, everything else goes into "Other"
top10_genres = list(genre_counts.head(10).index)

genre_top_list = []
for val in g_long["genre_item"]:
    if val in top10_genres:
        genre_top_list.append(val)
    else:
        genre_top_list.append("Other")

g_long["genre_top"] = genre_top_list


# Interactions: brush, legends, slider
# Brush selection on the timeline. Filtering all other charts by year range
brush = alt.selection_interval(encodings = ["x"])

# Legend selection on genres. Clicking a genre in the legend highlights it.
sel_genre = alt.selection_point(
    fields = ["genre_top"],
    bind = "legend",
    toggle = True,
    empty = "all",
)

# Legend selection for player rating categories
sel_rating = alt.selection_point(
    fields = ["sentiment"],
    bind = "legend",
    toggle = True,
    empty = "all",
)

# Slider to control the maximum price
CAP = 80 
price_slider = alt.param(
    name = "max_price",
    value = 60,  # default max price
    bind = alt.binding_range(
        min = 1,
        max = CAP,
        step = 1,
        name = "Max Price (USD)"
    ),
)

# Timeline chart
games_per_year = df.groupby("year").size().reset_index(name = "count")

# Main timeline line chart
timeline = (
    alt.Chart(games_per_year)
    .mark_line(point = True)
    .encode(
        x = alt.X("year:O", title = "Year"),
        y = alt.Y("count:Q", title = "Games Released"),
        tooltip = ["year", "count"],
    )
    .properties(
        title = "Games Released Per Year — drag to filter",
        width = 1000,
        height = 170,
    )
    .add_params(brush)
)


# Price Distribution

# Only keep rows within the CAP
price_filtered = df[
    (df["price"].notna()) & (df["price"] <= CAP)][["year", "price"]]

# Boxplot of price by year, filtered by both brush and slider
price_panel = (
    alt.Chart(price_filtered)
    .add_params(price_slider)
    .transform_filter(brush)
    .transform_filter("datum.price <= max_price")
    .mark_boxplot(size = 12, outliers = False)
    .encode(
        x = alt.X("year:O", title = "Year"),
        y = alt.Y(
            "price:Q",
            title = "Price (USD)",
            scale = alt.Scale(domain = [0, CAP]),
        ),
    )
    .properties(
        title = "Price Distribution (use slider to limit max price)",
        width = 480,
        height = 220,
    )
)


# Genre composition
genre_year = g_long.groupby(["year", "genre_top"]).size().reset_index(name="count")

# Stacked area chart showing the share of each genre over time
genre_area = (
    alt.Chart(genre_year)
    .mark_area()
    .encode(
        x = alt.X("year:O", title = "Year"),
        y = alt.Y("count:Q", stack = "normalize", title = "Share of Releases"),
        color = alt.Color(
            "genre_top:N",
            title = "Genre",
            scale = alt.Scale(scheme = "tableau10"),
        ),
        opacity = alt.condition(sel_genre, alt.value(1.0), alt.value(0.25)),
        tooltip = ["year", "genre_top", "count"],
    )
    .add_params(sel_genre)
    .transform_filter(brush)
    .properties(
        title = "Genre Composition (Top 10 + Other)",
        width = 480,
        height = 220,
    )
)


# Reviews / Player Rating vs Audience Scale scatter
# Scatterplot, year vs review count, colored by player rating.
reviews = (
    alt.Chart(rv)
    .add_params(sel_rating)
    .transform_filter(brush)
    .mark_circle(opacity = 0.75)
    .encode(
        x = alt.X("year:O", title = "Year"),
        y = alt.Y(
            "review_count:Q",
            title = "Review Count (log scale)",
            scale = alt.Scale(type = "log"),
        ),
        size = alt.Size(
            "review_count:Q",
            legend = None,
            scale = alt.Scale(range=[20, 180]),
        ),
        color = alt.condition(
            sel_rating,
            alt.Color(
                "sentiment:N",
                title = "Player Rating",
                scale = alt.Scale(scheme = "redyellowgreen"),
            ),
            alt.value("#dddddd"),
        ),
        tooltip = [
            "name",
            "year",
            alt.Tooltip("sentiment:N", title = "Player Rating"),
            "review_count",
        ],
    )
    .properties(
        title ="Player Rating / Audience Scale",
        width = 720,
        height = 260,
    )
)

# Genre market share pie, filtered by year brush
genre_pie = (
    alt.Chart(g_long[["year", "genre_top"]])
    .mark_arc(innerRadius = 40)
    .encode(
        theta = alt.Theta("count():Q", title = "Releases"),
        color = alt.Color(
            "genre_top:N",
            title = "Genre",
            scale = alt.Scale(scheme = "tableau10"),
        ),
        tooltip = [
            "genre_top:N",
            alt.Tooltip("count():Q", title = "Releases"),
        ],
    )
    .transform_filter(brush)
    .add_params(sel_genre)
    .properties(
        title = "Genre Market Share (filtered by years)",
        width = 280,
        height = 260,
    )
)


# Average price by genre, with price slider

# Drop Free to Play so it does not crash the average prices
avg_price_source = g_long[
    (g_long["genre_top"] != "Free to Play")
    & g_long["price"].notna()
    & (g_long["price"] <= CAP)
]

# Horizontal bar chart showing average price by genre
avg_price_genre = (
    alt.Chart(avg_price_source)
    .add_params(sel_genre, price_slider)
    .transform_filter(brush)
    .transform_filter("datum.price <= max_price")
    .mark_bar()
    .encode(
        x = alt.X(
            "mean(price):Q",
            title = "Average Price (USD)",
        ),
        y = alt.Y(
            "genre_top:N",
            title = "Genre",
            sort = "-x",
        ),
        color = alt.Color(
            "genre_top:N",
            title = "Genre",
            scale = alt.Scale(scheme = "tableau10"),
            legend = None,
        ),
        tooltip = [
            "genre_top:N",
            alt.Tooltip("mean(price):Q", title = "Avg Price", format = ".2f"),
            alt.Tooltip("count():Q", title = "Number of Games"),
        ],
    )
    .properties(
        title = "Average Price by Genre (filtered by years & slider)",
        width = 1000,
        height = 260,
    )
)


# Layout and save

# Middle row, price boxplot + genre stacked area
middle = (
    alt.hconcat(price_panel, genre_area)
    .resolve_scale(y = "independent", color = "independent")
)

# Bottom row, reviews scatter + genre pie chart
bottom = (
    alt.hconcat(reviews, genre_pie)
    .resolve_scale(color = "independent")
)

# Stack everything vertically into one tall dashboard
dashboard = (
    alt.vconcat(timeline, middle, bottom, avg_price_genre, spacing = 30)
    .configure_axis(
        labelFontSize = 11,
        titleFontSize = 12,
        gridColor = "#e0e0e0",
        gridOpacity = 0.6,
        domainColor = "#b0b0b0",
    )
    .configure_title(
        fontSize = 14,
        font = "Helvetica",
        anchor = "start",
    )
    .configure_legend(
        labelFontSize = 11,
        titleFontSize = 12,
        orient = "right",
    )
    # Treat each chart as a card
    .configure_view(
        fill="#ffffff",
        stroke="#e5e7eb",
        strokeWidth=1,
    )
)

out_path = "visuals/00_dashboard.html"
dashboard.save(out_path)
print("Saved:", out_path)


# Simple page styling, center and add cards
try:
    with open(out_path, "r", encoding = "utf-8") as f:
        html = f.read()

    style_block = """
<style>
body {
  margin: 0;
  padding: 24px;
  background-color: #f3f4f6; /* light gray page background */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
/* center the dashboard on the page */
.vega-embed {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
"""

    # Inject the style block into the <head> of the HTML Altair generated
    if "</head>" in html:
        html = html.replace("</head>", style_block + "\n</head>")
    else:
        html = style_block + html

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Styled page written to:", out_path)
except Exception as e:
    print("Warning: could not post-style HTML:", e)

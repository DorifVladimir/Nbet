import os
import requests
import pandas as pd

# --- Config ---
COMPETITIONS = {
    # England
    "Premier League": "E0",
    "Championship": "E1",
    "League One": "E2",
    "League Two": "E3",
    "Conference": "EC",
    # Scotland
    "Scottish Premiership": "SC0",
    "Scottish Div 1": "SC1",
    "Scottish Div 2": "SC2",
    # Germany
    "Bundesliga": "D1",
    "Bundesliga 2": "D2",
    # Italy
    "Serie A": "I1",
    "Serie B": "I2",
    # Spain
    "La Liga": "SP1",
    "Segunda Division": "SP2",
    # France
    "Ligue 1": "F1",
    "Ligue 2": "F2",
    # Netherlands
    "Eredivisie": "N1",
    # Belgium
    "Belgian Jupiler League": "B1",
    # Portugal
    "Portugal Liga I": "P1",
    # Turkey
    "Turkey Ligi 1": "T1",
    # Romania
    "Liga 1": "ROU"
}

SEASONS = ["2223", "2324", "2425"]
BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
DATA_DIR = "data"

# Link direct pentru România (fără sezoane)
ROMANIA_CSV_URL = "https://www.football-data.co.uk/new/ROU.csv"
ROMANIA_LOCAL_FILE = os.path.join(DATA_DIR, "Liga 1", "ROU.csv")

# Creăm directoarele dacă nu există
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def download_csvs():
    for league, code in COMPETITIONS.items():
        league_dir = os.path.join(DATA_DIR, league)
        if not os.path.exists(league_dir):
            os.makedirs(league_dir)

        # România: download direct
        if league == "Liga 1":
            if not os.path.exists(ROMANIA_LOCAL_FILE):
                print(f"Descarc {ROMANIA_CSV_URL}")
                r = requests.get(ROMANIA_CSV_URL)
                if r.status_code == 200:
                    with open(ROMANIA_LOCAL_FILE, "wb") as f:
                        f.write(r.content)
                    print(f"Salvat: {ROMANIA_LOCAL_FILE}")
                else:
                    print(f"Nu am putut descarca {ROMANIA_CSV_URL}")
            else:
                print(f"CSV deja exista: {ROMANIA_LOCAL_FILE}")
            continue  # nu mai iterăm peste SEASONS

        # Celelalte ligi
        for season in SEASONS:
            url = BASE_URL.format(season=season, league=code)
            local_path = os.path.join(league_dir, f"{code}_{season}.csv")
            if not os.path.exists(local_path):
                print(f"Descarc {url}")
                r = requests.get(url)
                if r.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    print(f"Salvat: {local_path}")
                else:
                    print(f"Nu am putut descarca {url}")
            else:
                print(f"CSV deja exista: {local_path}")


def load_csvs():
    dfs = []
    for league, code in COMPETITIONS.items():
        league_dir = os.path.join(DATA_DIR, league)
        if league == "Liga 1":
            path = ROMANIA_LOCAL_FILE
            if os.path.exists(path):
                df = pd.read_csv(path)
                df['League'] = league
                dfs.append(df)
        else:
            for season in SEASONS:
                path = os.path.join(league_dir, f"{code}_{season}.csv")
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    df['League'] = league
                    dfs.append(df)

    if not dfs:
        print("Nu am găsit niciun CSV de încărcat.")
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    print(f"CSV încărcat: {len(combined)} meciuri combinate")
    return combined

#
# if __name__ == "__main__":
#     download_csvs()
#     df_combined = load_csvs()
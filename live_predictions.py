import os
import pandas as pd
from scipy.stats import poisson
from rapidfuzz import process
from prepare_history_data import load_csvs
from datetime import datetime

LOG_FILE = "prediction_log.csv"

# --- Parametri ---
RECENT_MATCHES = 5
ALPHA = 0.2  # ajustare lambda pe baza datelor live
MAX_GOALS = 10  # pentru calcul 1X2
OU_LINES = [0.75, 1, 1.25, 1.75, 2, 2.25, 2.75, 3, 3.25, 3.75]

# --- Funcții pentru calcul probabilități ---
def calculate_lambdas(df, home_team, away_team, recent_matches=RECENT_MATCHES):
    home_df = df[df['HomeTeam'] == home_team].tail(recent_matches)
    away_df = df[df['AwayTeam'] == away_team].tail(recent_matches)

    lambda_home = home_df['FTHG'].mean() if not home_df.empty else 1.2
    lambda_away = away_df['FTAG'].mean() if not away_df.empty else 1.0

    # ajustări pe baza avantajului acasă/deplasare
    home_adv = lambda_home - df[df['HomeTeam'] == home_team]['FTAG'].mean()
    away_disadv = lambda_away - df[df['AwayTeam'] == away_team]['FTHG'].mean()
    lambda_home += home_adv * 0.1
    lambda_away += away_disadv * 0.1

    return lambda_home, lambda_away

def poisson_over_prob(lambda_total, current_goals, k):
    needed = max(0, k - current_goals + 1)
    prob = 1 - poisson.cdf(needed - 1, lambda_total)
    return round(prob * 100, 1)

def calculate_1X2(lambda_home, lambda_away):
    prob_home, prob_draw, prob_away = 0.0, 0.0, 0.0
    for h in range(MAX_GOALS):
        for a in range(MAX_GOALS):
            p = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
            if h > a:
                prob_home += p
            elif h == a:
                prob_draw += p
            else:
                prob_away += p
    total = prob_home + prob_draw + prob_away
    return {
        'Home Win': round(prob_home / total * 100, 1),
        'Draw': round(prob_draw / total * 100, 1),
        'Away Win': round(prob_away / total * 100, 1),
        'CI ±': 5
    }

def calculate_over_under(lambda_home, lambda_away, current_goals=0):
    total_lambda = lambda_home + lambda_away
    ou_probs = {}
    for line in OU_LINES:
        over_prob = poisson_over_prob(total_lambda, current_goals, line)
        under_prob = 100 - over_prob  # sau 1 - over_prob dacă folosești 0-1
        ou_probs[line] = {'over': over_prob, 'under': under_prob}
    return ou_probs

def update_lambdas(lambda_home, lambda_away,
                   yellow_cards_home=0, yellow_cards_away=0,
                   corners_home=0, corners_away=0,
                   possession_home=50, possession_away=50,
                   shots_on_target_home=0, shots_on_target_away=0,
                   free_kicks_home=0, free_kicks_away=0,
                   alpha=ALPHA):
    """
    Ajustează lambda pe baza datelor live
    """
    lambda_home_new = lambda_home * (1 - 0.05 * yellow_cards_home + 0.02 * corners_home)
    lambda_away_new = lambda_away * (1 - 0.05 * yellow_cards_away + 0.02 * corners_away)

    lambda_home_new *= 1 + (possession_home - 50) / 100 * alpha
    lambda_away_new *= 1 + (possession_away - 50) / 100 * alpha

    lambda_home_new *= 1 + shots_on_target_home * 0.03 + free_kicks_home * 0.01
    lambda_away_new *= 1 + shots_on_target_away * 0.03 + free_kicks_away * 0.01

    return lambda_home_new, lambda_away_new

# --- Fuzzy matching pentru nume echipe ---
# def find_team_name(team_input, df):
#     all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
#     match, score = process.extractOne(team_input, all_teams)
#     if score < 70:
#         raise ValueError(f"Echipa '{team_input}' nu a fost găsită cu încredere suficientă.")
#     return match

def find_team_name(team_input, df, min_score=70):
    # eliminăm NaN și forțăm conversia în string
    all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).dropna().astype(str).unique().tolist()

    # forțăm și inputul să fie string
    if not isinstance(team_input, str):
        team_input = str(team_input)

    # dacă lista e goală, return None
    if not all_teams:
        print("Lista echipelor este goală, nu pot face fuzzy match.")
        return None

    result = process.extractOne(team_input, all_teams)

    if result is None:
        print(f"Nu am găsit niciun match pentru '{team_input}'")
        return None

    match, score, _ = result
    if score < min_score:
        print(f" Match slab pentru '{team_input}' → '{match}' (score={score})")
        return None

    return match

# --- Logging ---
def log_prediction(home_team, away_team, score_home, score_away, probs_1X2, probs_ou):
    row = {
        'Timestamp': datetime.now(),
        'HomeTeam': home_team,
        'AwayTeam': away_team,
        'ScoreHome': score_home,
        'ScoreAway': score_away,
        'Prob_HomeWin': probs_1X2['Home Win'],
        'Prob_Draw': probs_1X2['Draw'],
        'Prob_AwayWin': probs_1X2['Away Win']
    }
    row.update({f"OU_{k}": v for k, v in probs_ou.items()})
    file_exists = os.path.isfile(LOG_FILE)
    df_log = pd.DataFrame([row])
    if file_exists:
        df_log.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df_log.to_csv(LOG_FILE, mode='w', header=True, index=False)

# --- Funcții principale ---
def generate_league_predictions(df_league):
    """
    Generează predicții inițiale pentru toate meciurile dintr-o ligă
    """
    predictions = {}
    for idx, row in df_league.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        lambda_home, lambda_away = calculate_lambdas(df_league, home_team, away_team)
        probs_1X2 = calculate_1X2(lambda_home, lambda_away)
        probs_ou = calculate_over_under(lambda_home, lambda_away)
        predictions[(home_team, away_team)] = {
            'lambda_home': lambda_home,
            'lambda_away': lambda_away,
            'probs_1X2': probs_1X2,
            'probs_ou': probs_ou
        }
    return predictions

def update_match_live(predictions_dict, home_team_input, away_team_input,
                      score_home=0, score_away=0,
                      yellow_cards_home=0, yellow_cards_away=0,
                      corners_home=0, corners_away=0,
                      possession_home=50, possession_away=50,
                      shots_on_target_home=0, shots_on_target_away=0,
                      free_kicks_home=0, free_kicks_away=0):
    """
    Ajustează predicția unui meci existent folosind date live.
    Dacă nu se găsește echipa/meciul, returnează None.
    """

    df_keys = pd.DataFrame([{'HomeTeam': k[0], 'AwayTeam': k[1]} for k in predictions_dict.keys()])

    home_team = find_team_name(home_team_input, df_keys)
    away_team = find_team_name(away_team_input, df_keys)

    if not home_team or not away_team:
        print(f"[WARN] Echipele '{home_team_input}' vs '{away_team_input}' nu au fost găsite în predicții.")
        return None

    key = (home_team, away_team)
    if key not in predictions_dict:
        print(f"[WARN] Meciul {home_team} vs {away_team} nu există în predicții.")
        return None

    data = predictions_dict[key]

    lambda_home, lambda_away = update_lambdas(
        data['lambda_home'], data['lambda_away'],
        yellow_cards_home, yellow_cards_away,
        corners_home, corners_away,
        possession_home, possession_away,
        shots_on_target_home, shots_on_target_away,
        free_kicks_home, free_kicks_away
    )

    probs_1X2 = calculate_1X2(lambda_home, lambda_away)
    probs_ou = calculate_over_under(lambda_home, lambda_away, score_home + score_away)

    predictions_dict[key].update({
        'lambda_home': lambda_home,
        'lambda_away': lambda_away,
        'probs_1X2': probs_1X2,
        'probs_ou': probs_ou
    })

    log_prediction(home_team, away_team, score_home, score_away, probs_1X2, probs_ou)
    return predictions_dict[key]

# --- Script principal ---
# if __name__ == "__main__":
#     df_combined = load_csvs()
#     # Generăm predicții pentru toate ligile
#     leagues = df_combined['League'].unique()
#     all_predictions = {}
#     for league in leagues:
#         df_league = df_combined[df_combined['League'] == league]
#         preds = generate_league_predictions(df_league)
#         all_predictions.update(preds)
#
#     print(all_predictions)
#     # Exemplu: actualizare predicție live pentru un meci
#     result = update_match_live(
#         all_predictions,
#         "U Craiova", "FCSB",
#         score_home=1, score_away=0,
#         yellow_cards_home=1, yellow_cards_away=0,
#         corners_home=2, corners_away=1,
#         possession_home=55, possession_away=45,
#         shots_on_target_home=3, shots_on_target_away=2,
#         free_kicks_home=1, free_kicks_away=0
#     )
#     print(f"Predicție actualizată live: {result}")
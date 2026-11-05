# Football Live Betting Bot

A Windows desktop app that estimates over/under probabilities for live football matches and places bets through a browser. It builds a Poisson goal model from historical results, adjusts it with live match statistics, and bets when the model is confident and the odds fall in a set range.

> **Warning:** this software logs in to a real betting account and places real-money bets. It is an experiment, not a profitable system, and you can lose money. Check that automated betting is allowed by your bookmaker's terms and your local law, and only stake what you can afford to lose.

## How it works

1. **Load history.** Downloads match results for 21 leagues from [football-data.co.uk](https://www.football-data.co.uk/). Files already in `data/` are not downloaded again.
2. **Estimate expected goals.** For each home/away pairing in the data, it averages the home team's last 5 home games and the away team's last 5 away games.
3. **Calculate probabilities.** A Poisson distribution gives the probabilities for home win, draw, away win, and over/under lines from 0.75 to 3.75.
4. **Find live matches.** It reads the live match list, skips youth and women's games, and matches team names to the model by fuzzy comparison.
5. **Update from live stats.** The score, cards, corners, possession, shots on target and free kicks adjust the expected goals.
6. **Place a bet.** It bets a line when the model gives it at least 70% and the odds are between 1.70 and 2.20, and each prediction is used only once per match.

## Requirements

- Windows with Microsoft Edge
- Python 3.10 or newer (developed on 3.14)
- A betting site account, plus the optional statistics site and predictions API accounts

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install selenium pandas scipy rapidfuzz fuzzywuzzy python-dotenv customtkinter requests
Copy-Item .env.example .env
```

Then fill in `.env`:

| Setting | Purpose |
|---|---|
| `SITE_A_URL` | Betting site used by the app |
| `SITE_B_URL`, `SITE_B_UI_PREFIX` | Second, older site integration (`SiteB` class) |
| `STATS_SITE_URL`, `STATS_USERNAME`, `STATS_PASSWORD` | Statistics site login |
| `PREDICTIONS_API_HOST`, `PREDICTIONS_API_PATH`, `PREDICTIONS_API_KEY` | Predictions API, used by `SiteB` |

The site automation depends on each site's page layout, so it is written for specific sites and will need changes for any others.

## Usage

```powershell
python GUI.py
```

Enter your betting account username and password, then press **Start Betting**. The app opens Edge and keeps running until you press **Stop Betting**. The password is kept in memory only and is not saved to disk.

## Project structure

| File | Purpose |
|---|---|
| `GUI.py` | Desktop window and start/stop controls |
| `functii.py` | Browser automation, match selection and bet placement |
| `live_predictions.py` | Poisson model and live adjustments |
| `prepare_history_data.py` | Downloads and loads historical data |
| `data/` | Historical match results by league |
| `main.py` | Separate tool that analyzes Samsung Secure Folder backups; not part of the bot |

The app writes these local files, which are not committed:

| File | Contents |
|---|---|
| `prediction_log.csv` | Each live prediction update |
| `used_predictions.csv` | Bets placed |
| `meciuri_fara_predictii.log` | Live matches with no match in the model |

## Known limitations

- **Match minute is ignored.** Probabilities use full-match expected goals even late in a game, which overstates the chance of more goals.
- **Live adjustments stack up.** Revisiting a match applies its statistics again.
- **Opponent strength is ignored.** Each team's expected goals come only from its own recent games.
- **Coverage is limited.** Only home/away pairings found in the data can be matched, so new teams and pairings are skipped.
- **Historical data is not refreshed.** It ends with the 2024/25 season unless you update it.
- **Running past 12:00 may stop matching.** The midday reset adds entries in a different format to the predictions, which can break match lookup.
- **Stake settings are not used.** The stake is a fixed random amount of 7 to 10, and the Min, Max and max balance fields have no effect.
- **Lines 1.5 and 2.5 are not bet.** The model does not calculate them.
- **Results are not tracked.** Bets are logged, but wins and losses are not, so performance cannot be measured yet.

## License

[MIT](LICENSE)

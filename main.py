import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from nba_schedule import NBASchedule

API_KEY_FILE = 'apikey.txt'
FLOPPING_COUNTS_FILE = 'flopping_counts.json'
PROCESSED_GAMES_FILE = 'processed_games.json'
SCRAPING_URL = "https://www.spotrac.com/nba/fines-suspensions/fines/flopping/#player"


def read_api_key(filepath):
    with open(filepath, 'r') as file:
        return file.readline().strip()

# API call for play-by-play log based on game ID (match ID)
def fetch_play_by_play_data(game_id, api_key):
    base_url = 'https://api.sportradar.us/nba/trial/v8/en/games/{game_id}/pbp.json'
    full_url = base_url.format(game_id=game_id) + f"?api_key={api_key}"
    response = requests.get(full_url)

    if response.status_code == 200:
        data = response.json()
        if 'periods' not in data:
            print(f"Unexpected response structure for game {game_id}: {data}")
        return data
    else:
        print(f"Error fetching data for game {game_id}: {response.status_code}")
        return None

# Extract player names
def extract_flopping_fouls(periods_data):
    flopping_players = []

    for period in periods_data:
        if 'events' in period:
            for event in period['events']:
                if 'description' in event and 'technical foul (Flopping)' in event['description']:
                    player_name = event['description'].split(" technical foul (Flopping)")[0]
                    flopping_players.append(player_name)
    
    return flopping_players


def load_existing_data(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {} 

def load_processed_games(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return set(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Save processed games to a JSON file
def save_processed_games(processed_games, filepath):
    with open(filepath, 'w') as file:
        json.dump(list(processed_games), file, indent=4)

def mark_as_processed(game_id, processed_games):
    processed_games.add(game_id)

def save_data(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def integrate_scraped_data(scraped_data, flopping_counts):
    for entry in scraped_data:
        player_name = entry['player']
        foul_date = entry['date']
        # If the player is already in the flopping counts, update the date if the scraped date is more recent
        if player_name in flopping_counts:
            existing_date = flopping_counts[player_name].get('date')
            if not existing_date or datetime.strptime(foul_date, "%m/%d/%Y") > datetime.strptime(existing_date, "%m/%d/%Y"):
                flopping_counts[player_name]['date'] = foul_date
        # If the player is not in the counts, add them with a count of 1
        else:
            flopping_counts[player_name] = {'count': 1, 'date': foul_date}


def scrape_flopping_fouls():
    response = requests.get(SCRAPING_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find(id='main')
    rows = table.find_all('tr')[1:]

    scraped_data = []
    for row in rows:
        cols = row.find_all('td')
        if cols and len(cols) > 3:
            player_name = cols[0].get_text(strip=True)
            date_text = cols[3].get_text(strip=True)
            scraped_data.append({"player": player_name, "date": date_text})
    return scraped_data

def main():
    nba_schedule = NBASchedule()
    game_ids = nba_schedule.extract_game_ids()

    api_key = read_api_key('apikey.txt')
    flopping_counts = load_existing_data('flopping_counts.json')
    processed_games = load_processed_games('processed_games.json')

    scraped_data = scrape_flopping_fouls()

    for date, ids in game_ids.items():
        for game_id in ids:
            if game_id not in processed_games:
                play_by_play_data = fetch_play_by_play_data(game_id, api_key)
                if play_by_play_data and 'periods' in play_by_play_data:
                    periods_data = play_by_play_data["periods"]
                    flopping_fouls = extract_flopping_fouls(periods_data)
                    for player in flopping_fouls:
                        flopping_counts[player] = flopping_counts.get(player, 0) + 1
                else:
                    print(f"No 'periods' data for game {game_id}")
                processed_games.add(game_id)
                time.sleep(1.5)  # Delay due to API rate limit

    integrate_scraped_data(scraped_data, flopping_counts)

    save_data(flopping_counts, 'flopping_counts.json')
    save_processed_games(processed_games, 'processed_games.json')

if __name__ == "__main__":
    main()

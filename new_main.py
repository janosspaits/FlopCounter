import requests
import json
import time
from nba_schedule import NBASchedule

# Read API key from file
def read_api_key(filepath):
    with open(filepath, 'r') as file:
        return file.readline().strip()

# API call for play-by-play log based on game ID (match ID)
def fetch_play_by_play_data(game_id, api_key):
    base_url = 'https://api.sportradar.us/nba/trial/v8/en/games/{game_id}/pbp.json'
    full_url = base_url.format(game_id=game_id) + f"?api_key={api_key}"
    response = requests.get(full_url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for game {game_id}: {response.status_code}")
        return None

# Extract player names who committed technical fouls for flopping
def extract_flopping_fouls(periods_data):
    flopping_players = []

    for period in periods_data:
        if 'events' in period:
            for event in period['events']:
                if 'description' in event and 'technical foul (Flopping)' in event['description']:
                    player_name = event['description'].split(" technical foul (Flopping)")[0]
                    flopping_players.append(player_name)
    
    return flopping_players

# Load existing data
def load_existing_data(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return an empty dictionary if file doesn't exist or is empty

# Check if a game has already been processed
def is_already_processed(game_id, processed_games):
    return game_id in processed_games

# Mark a game as processed
def mark_as_processed(game_id, processed_games):
    processed_games.add(game_id)

# Save data to a JSON file
def save_data(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    nba_schedule = NBASchedule()
    game_ids = nba_schedule.extract_game_ids()

    api_key = read_api_key('apikey.txt')
    flopping_counts = load_existing_data('flopping_counts.json')
    processed_games = set(flopping_counts.keys())  # Assuming game IDs are keys

    for date, ids in game_ids.items():
        for game_id in ids:
            if not is_already_processed(game_id, processed_games):
                play_by_play_data = fetch_play_by_play_data(game_id, api_key)
                if play_by_play_data:
                    periods_data = play_by_play_data["periods"]
                    flopping_fouls = extract_flopping_fouls(periods_data)
                    for player in flopping_fouls:
                        flopping_counts[player] = flopping_counts.get(player, 0) + 1

                time.sleep(1.5)  # Delay due to API rate limit
                mark_as_processed(game_id, processed_games)

    save_data(flopping_counts, 'flopping_counts.json')

if __name__ == "__main__":
    main()
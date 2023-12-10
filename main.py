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
        data = response.json()
        if 'periods' not in data:
            print(f"Unexpected response structure for game {game_id}: {data}")
        return data
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

def load_processed_games(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return set(data)  # Assuming the file contains a list of game IDs
    except (FileNotFoundError, json.JSONDecodeError):
        return set()  # Return an empty set if file doesn't exist or is empty

# Save processed games to a JSON file
def save_processed_games(processed_games, filepath):
    with open(filepath, 'w') as file:
        json.dump(list(processed_games), file, indent=4)  # Convert set to list for JSON serialization

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
    processed_games = load_processed_games('processed_games.json')  # Load the set of processed game IDs

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
                processed_games.add(game_id)  # Directly add to processed_games set
                time.sleep(1.5)  # Delay due to API rate limit

    save_data(flopping_counts, 'flopping_counts.json')
    save_processed_games(processed_games, 'processed_games.json')  # Save the updated set of processed game IDs

if __name__ == "__main__":
    main()

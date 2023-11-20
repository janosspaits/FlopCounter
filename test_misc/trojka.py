from nba_schedule import NBASchedule
import requests
import json
import time

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

# Extract player names who made three-point shots
def extract_three_point_shots(periods_data):
    three_point_shooters = []

    for period in periods_data:
        if 'events' in period:
            for event in period['events']:
                # Check if the description contains a successful three point shot
                if 'description' in event and 'makes three point' in event['description']:
                    # Extract the player's name from the description
                    player_name = event['description'].split(" makes three point")[0].strip()
                    three_point_shooters.append(player_name)
    
    return three_point_shooters

def main():
    nba_schedule = NBASchedule()
    game_ids = nba_schedule.extract_game_ids()

    api_key = read_api_key('apikey.txt')
    three_point_counts = {}

    # Iterate through every match retrieved from the NBA schedule json
    for date, ids in game_ids.items():
        for game_id in ids:
            play_by_play_data = fetch_play_by_play_data(game_id, api_key)
            if play_by_play_data:
                periods_data = play_by_play_data["periods"]
                three_point_shots = extract_three_point_shots(periods_data)
                for player in three_point_shots:
                    three_point_counts[player] = three_point_counts.get(player, 0) + 1

            time.sleep(1.2)  # Delay due to API rate limit

    # Print the results to console
    for player, count in three_point_counts.items():
        print(f"{player}: {count} three-point shot(s) made")

    # Save to JSON file
    with open('three_point_counts.json', 'w') as file:
        json.dump(three_point_counts, file, indent=4)

if __name__ == "__main__":
    main()

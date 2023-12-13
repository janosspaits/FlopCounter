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
    print(f"Fetching data for game ID: {game_id}")

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

# Checks the play-by-play data for the Flopping foul string
def extract_flopping_fouls(periods_data, game_date):
    flopping_players = []
    formatted_game_date = datetime.strptime(game_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    for period in periods_data:
        if 'events' in period:
            for event in period['events']:
                if 'description' in event and 'technical foul (Flopping)' in event['description']:
                    player_name = event['description'].split(" technical foul (Flopping)")[0]
                    flopping_players.append({"player": player_name, "date": formatted_game_date})
    
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

        if player_name in flopping_counts:
            existing_entry = flopping_counts[player_name]

            # If the existing entry is an integer, convert it to the expected dictionary format
            if isinstance(existing_entry, int):
                flopping_counts[player_name] = {
                    'count': existing_entry,  # existing count
                    'dates': [foul_date]     # start a new list with the current date
                }
            else:
                # Add the date to the list of dates and increment the count
                existing_entry['dates'].append(foul_date)
                existing_entry['count'] += 1
        else:
            # Initialize a new entry for the player
            flopping_counts[player_name] = {
                'count': 1,
                'dates': [foul_date]
            }


def scrape_flopping_fouls(cutoff_date_str=None):
    response = requests.get(SCRAPING_URL)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table', class_='datatable')
    if not table:
        print("Couldn't find the table with class='datatable'.")
        return []

    rows = table.find_all('tr')[1:]  # Skip the header row
    if not rows:
        print("No rows found in the table.")
        return []

    # Use current date as default if cutoff_date_str is None
    cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d").date() if cutoff_date_str else datetime.now().date()
    scraped_data = []

    for row in rows:
        cols = row.find_all('td')
        if not cols or len(cols) < 6:
            print("Row doesn't have enough columns.")
            continue

        player_name_element = cols[0].find('a')
        if not player_name_element:
            print("Player name element not found in the row.")
            continue

        player_name = player_name_element.get_text(strip=True)

        date_text = cols[5].get_text(strip=True)  # Date is in the last column
        try:
            date_of_foul = datetime.strptime(date_text, "%m/%d/%Y").date()
        except ValueError:
            print(f"Invalid date format: {date_text}")
            continue

        if date_of_foul <= cutoff_date:
            scraped_data.append({"player": player_name, "date": date_text})
        else:
            print(f"Date {date_text} is after the cutoff date.")

    print(f"Total entries scraped: {len(scraped_data)}")
    return scraped_data



def main():
    nba_schedule = NBASchedule()
    cutoff_date = None  # Set a cutoff date for testing
    game_ids = nba_schedule.extract_game_ids(cutoff_date)

    api_key = read_api_key(API_KEY_FILE)
    flopping_counts = load_existing_data(FLOPPING_COUNTS_FILE)
    processed_games = load_processed_games(PROCESSED_GAMES_FILE)

    scraped_data = scrape_flopping_fouls(cutoff_date)

    for date, ids in game_ids.items():
        for game_id in ids:
            if game_id not in processed_games:
                play_by_play_data = fetch_play_by_play_data(game_id, api_key)
                if play_by_play_data and 'periods' in play_by_play_data:
                    periods_data = play_by_play_data["periods"]
                    flopping_fouls = extract_flopping_fouls(periods_data, date)
                    for foul in flopping_fouls:
                        player = foul["player"]
                        date_of_foul = foul["date"]
                        if player in flopping_counts:
                            if isinstance(flopping_counts[player], dict):
                                flopping_counts[player]['dates'].append(date_of_foul)
                                flopping_counts[player]['count'] += 1
                            else:
                                flopping_counts[player] = {
                                    'count': flopping_counts[player] + 1,
                                    'dates': [date_of_foul]
                                }
                        else:
                            flopping_counts[player] = {
                                'count': 1,
                                'dates': [date_of_foul]
                            }
                processed_games.add(game_id)
                time.sleep(1.5)  # Delay due to API rate limit

    integrate_scraped_data(scraped_data, flopping_counts)

    save_data(flopping_counts, FLOPPING_COUNTS_FILE)
    save_processed_games(processed_games, PROCESSED_GAMES_FILE)

if __name__ == "__main__":
    main()


import requests
import json
import time
from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from datetime import datetime
from bs4 import BeautifulSoup
from nba_schedule import NBASchedule

API_KEY_FILE = "apikey.txt"
FLOPPING_COUNTS_FILE = "flopping_counts.json"
PROCESSED_GAMES_FILE = "processed_games.json"
SCRAPING_URL = "https://www.spotrac.com/nba/fines-suspensions/fines/flopping/#player"


def read_api_key(filepath: str) -> str:
    """
    Reads an API key from a file.

    Parameters:
    - filepath (str): The path to the file containing the API key.

    Returns:
    - The API key as a string.
    """
    with open(filepath, "r") as file:
        return file.readline().strip()


def fetch_play_by_play_data(game_id: str, api_key: str) -> dict:
    """
    A function to fetch play-by-play data for a given game ID using the Sportradar API.

    Parameters:
    - game_id (str): The ID of the game for which to fetch data.
    - api_key (str): The API key for accessing the Sportradar API.

    Returns:
    - dict: The play-by-play data for the specified game ID, or None if an error occurs.
    """
    print(f"Fetching data for game ID: {game_id}")

    base_url = "https://api.sportradar.us/nba/trial/v8/en/games/{game_id}/pbp.json"
    full_url = base_url.format(game_id=game_id) + f"?api_key={api_key}"

    headers = {"accept": "application/json"}

    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        is_scheduled = data.get("status") == "scheduled"
        return data, is_scheduled
    else:
        print(f"Error fetching data for game {game_id}: {response.status_code}")
        return None, False


# Checks the play-by-play data for the Flopping foul string
def extract_flopping_fouls(periods_data: list, game_date: str) -> list:
    """
    Extracts players who committed a flopping foul from the provided periods data for a specific game date.

    Parameters:
    - periods_data (list): A list of period data containing information about events during the game.
    - game_date (str): The date of the game in the format "%Y-%m-%d".

    Returns:
    - list: A list of dictionaries containing player names who committed a flopping foul and the formatted game date.
    """
    flopping_players = []
    formatted_game_date = datetime.strptime(game_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    for period in periods_data:
        if "events" in period:
            for event in period["events"]:
                if "description" in event and "technical foul (Flopping)" in event["description"]:
                    player_name = event["description"].split(" technical foul (Flopping)")[0]
                    flopping_players.append(
                        {
                            "player": player_name,
                            "date": formatted_game_date,
                        }
                    )

    return flopping_players


def load_existing_data(
    filepath: str,
) -> dict:
    """
    Load existing data from the given file path and return it as a dictionary.

    Args:
    - filepath (str): The file path to load the data from.

    Returns:
    - dict: The loaded data as a dictionary, or an empty dictionary if the file is not found or the data cannot be decoded as JSON.
    """
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            return data
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {}


def load_processed_games(
    filepath: str,
) -> set:
    """
    A function that loads processed games from a file.

    Parameters:
    - filepath: a string representing the file path to load the processed games from

    Returns:
    - a set containing the processed games, or an empty set if the file is not found or cannot be decoded
    """
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            return set(data)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return set()


def save_processed_games(processed_games: set, filepath: str) -> None:
    """
    Save the processed games to a file.

    Parameters:
    - processed_games (set): The set of processed games to be saved.
    - filepath (str): The file path where the processed games will be saved.
    """
    with open(filepath, "w") as file:
        json.dump(
            list(processed_games),
            file,
            indent=4,
        )


def mark_as_processed(game_id: str, processed_games: set) -> None:
    """
    Add the given game ID to the set of processed games.

    Parameters:
    - game_id (str): The ID of the game to mark as processed.
    - processed_games (set): A set of game IDs that have already been processed.

    Returns:
    - None
    """
    processed_games.add(game_id)


def save_data(data: dict, filepath: str) -> None:
    """
    Save the data to a JSON file.

    Parameters:
    - data (dict): The data to be saved.
    - filepath (str): The file path where the data will be saved.

    Returns:
    - None
    """
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def integrate_scraped_data(
    scraped_data: List[Dict[str, Union[str, int]]],
    flopping_counts: Dict[str, Dict[str, Union[int, List[str]]]],
) -> None:
    """
    Integrate the scraped data into the existing flopping counts data structure.

    The scraped_data is a list of dictionaries with the following keys:
    - player: the player's name
    - date: the date of the foul
    - count: the number of times the player has been called for a foul that season

    The flopping_counts is a dictionary keyed by player name, with values that are
    either an integer (the number of times the player has been called for a foul)
    or a dictionary with the following keys:
    - count: the number of times the player has been called for a foul
    - dates: a list of dates when the player committed a foul

    This function updates the flopping_counts dictionary to reflect the new
    information from the scraped_data.

    Args:
        scraped_data: The data scraped from the website.
        flopping_counts: The existing data structure containing flopping counts.

    Returns:
        None
    """
    for entry in scraped_data:
        player_name = entry["player"]
        foul_date = entry["date"]

        if player_name in flopping_counts:
            existing_entry = flopping_counts[player_name]

            # Ensure the existing entry is in the expected dictionary format
            if isinstance(existing_entry, int):
                existing_entry = {
                    "count": existing_entry,
                    "dates": [],
                }

            # Add the date only if it's not already in the list, then increment the count
            if foul_date not in existing_entry.get("dates", []):
                existing_entry.setdefault("dates", []).append(foul_date)
                existing_entry["count"] = len(existing_entry["dates"])

            flopping_counts[player_name] = existing_entry
        else:
            # Initialize a new entry for the player
            flopping_counts[player_name] = {
                "count": 1,
                "dates": [foul_date],
            }


def scrape_flopping_fouls(
    cutoff_date_str: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Scrape the flopping fouls from the website.

    Args:
        cutoff_date_str: The cutoff date for the flopping fouls. If None, use the current date.

    Returns:
        A list of dictionaries with the following keys:
        - player: The player's name
        - date: The date of the foul
    """
    response = requests.get(SCRAPING_URL)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="datatable")
    if not table:
        print("Couldn't find the table with class='datatable'.")
        return []

    rows = table.find_all("tr")[1:]  # Skip the header row
    if not rows:
        print("No rows found in the table.")
        return []

    # Use current date as default if cutoff_date_str is None
    cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d").date() if cutoff_date_str else datetime.now().date()
    scraped_data = []

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 6:
            print("Row doesn't have enough columns.")
            continue

        player_name_element = cols[0].find("a")
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
            scraped_data.append(
                {
                    "player": player_name,
                    "date": date_text,
                }
            )
        else:
            print(f"Date {date_text} is after the cutoff date.")

    print(f"Total entries scraped: {len(scraped_data)}")
    return scraped_data


def sort_flopping_counts_descending(
    filepath: str,
) -> None:
    """
    Sorts the counts of items in the given JSON file in descending order and saves the result back to the same file.

    Args:
        filepath (str): The path to the JSON file to be sorted.

    Returns:
        None
    """
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return

    items = list(data.items())
    sorted_items = sorted(
        items,
        key=lambda x: (x[1]["count"] if isinstance(x[1], dict) else x[1]),
        reverse=True,
    )

    with open(filepath, "w") as file:
        file.write("{\n")
        for i, (
            player,
            details,
        ) in enumerate(sorted_items):
            json_string = f'"{player}": {json.dumps(details)}'
            if i < len(sorted_items) - 1:
                json_string += ","
            file.write(json_string + "\n")
        file.write("}\n")

    print("Flopping counts sorted and saved.")


def main():
    """
    Main function that runs the program.
    """
    nba_schedule = NBASchedule()
    cutoff_date = None  # Set a cutoff date for testing
    game_ids = nba_schedule.extract_game_ids(cutoff_date)

    api_key = read_api_key(API_KEY_FILE)
    flopping_counts = load_existing_data(FLOPPING_COUNTS_FILE)
    processed_games = load_processed_games(PROCESSED_GAMES_FILE)

    scraped_data = scrape_flopping_fouls(cutoff_date)

    api_call_counter = 0

    try:
        for date, ids in game_ids.items():
            for game_id in ids:
                if game_id not in processed_games:
                    (play_by_play_data, is_scheduled) = fetch_play_by_play_data(game_id, api_key)
                    api_call_counter += 1
                    print(f"API calls made: {api_call_counter}")
                    if play_by_play_data and "periods" in play_by_play_data and not is_scheduled:
                        periods_data = play_by_play_data["periods"]
                        flopping_fouls = extract_flopping_fouls(periods_data, date)
                        for foul in flopping_fouls:
                            player = foul["player"]
                            date_of_foul = foul["date"]
                            if player in flopping_counts:
                                if isinstance(flopping_counts[player], dict):
                                    flopping_counts[player]["dates"].append(date_of_foul)
                                    flopping_counts[player]["count"] += 1
                                else:
                                    flopping_counts[player] = {
                                        "count": flopping_counts[player] + 1,
                                        "dates": [date_of_foul],
                                    }
                            else:
                                flopping_counts[player] = {
                                    "count": 1,
                                    "dates": [date_of_foul],
                                }
                        processed_games.add(game_id)
                    else:
                        print(f"Game {game_id} is scheduled or data incomplete. Skipping.")
                    time.sleep(1.5)  # Delay due to API rate limit

        integrate_scraped_data(scraped_data, flopping_counts)

    except KeyboardInterrupt:
        print("Interrupted! Saving progress before exiting...")

    finally:
        # These lines will run whether the script is interrupted or completes normally
        save_data(flopping_counts, FLOPPING_COUNTS_FILE)

        save_processed_games(processed_games, PROCESSED_GAMES_FILE)

        sort_flopping_counts_descending(FLOPPING_COUNTS_FILE)

        print("Progress saved successfully.")


if __name__ == "__main__":
    main()

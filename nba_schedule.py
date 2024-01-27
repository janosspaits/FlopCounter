import json
import datetime
import requests


class NBASchedule:
    def __init__(self):
        self.schedule_file_path = "nba_schedule.json"  # Hardcoded file path
        self.schedule_data = self.load_schedule()

    def load_schedule(self):
        """Load the NBA schedule JSON data from the file."""
        with open(self.schedule_file_path, "r") as file:
            return json.load(file)

    def extract_game_ids(self, cutoff_date=None):
        """Extract game IDs with their dates up until the specified cutoff date or current day."""
        today = datetime.date.today().isoformat()
        cutoff = cutoff_date if cutoff_date else today
        game_ids_by_date = {}

        if "games" in self.schedule_data:
            for game in self.schedule_data["games"]:
                game_date = game["scheduled"].split("T")[0]  # Extract the date part
                if game_date <= cutoff:
                    if game_date not in game_ids_by_date:
                        game_ids_by_date[game_date] = []
                    game_ids_by_date[game_date].append(game["id"])

        return game_ids_by_date


def fetch_nba_schedule(api_key):
    url = f"https://api.sportradar.us/nba/trial/v8/en/games/2023/REG/schedule.json?api_key={api_key}"

    # Make the request
    response = requests.get(url)

    if response.status_code == 200:
        # Save the response data in a JSON file with pretty formatting
        with open("nba_schedule.json", "w") as file:
            json.dump(response.json(), file, indent=4)
        print("Schedule saved successfully.")
    else:
        print(f"Error: {response.status_code}")


def read_api_key(filepath):
    with open(filepath, "r") as file:
        return file.readline().strip()


# Uncomment and call to fetch_nba_schedule:

if __name__ == "__main__":
    api_key = read_api_key("apikey.txt")
    fetch_nba_schedule(api_key)

##########################################################################################################

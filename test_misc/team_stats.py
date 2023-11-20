import requests
import csv
import time

# Sample call:
# https://api.sportradar.com/nba/trial/v8/en/seasons/2023/REG/teams/583eccfa-fb46-11e1-82cb-f4ce4684ea4c/statistics.json?api_key=788u3xku2bs4v37sukxcbbpy

team_ids_dict = {
    "Atlanta Hawks": "583ecb8f-fb46-11e1-82cb-f4ce4684ea4c",
    "Boston Celtics": "583eccfa-fb46-11e1-82cb-f4ce4684ea4c",
    "Brooklyn Nets": "583ec9d6-fb46-11e1-82cb-f4ce4684ea4c",
    "Charlotte Hornets": "583ec97e-fb46-11e1-82cb-f4ce4684ea4c",
    "Chicago Bulls": "583ec5fd-fb46-11e1-82cb-f4ce4684ea4c",
    "Cleveland Cavaliers": "583ec773-fb46-11e1-82cb-f4ce4684ea4c",
    "Dallas Mavericks": "583ecf50-fb46-11e1-82cb-f4ce4684ea4c",
    "Denver Nuggets": "583ed102-fb46-11e1-82cb-f4ce4684ea4c",
    "Detroit Pistons": "583ec928-fb46-11e1-82cb-f4ce4684ea4c",
    "Golden State Warriors": "583ec825-fb46-11e1-82cb-f4ce4684ea4c",
    "Houston Rockets": "583ecb3a-fb46-11e1-82cb-f4ce4684ea4c",
    "Indiana Pacers": "583ec7cd-fb46-11e1-82cb-f4ce4684ea4c",
    "Los Angeles Clippers": "583ecdfb-fb46-11e1-82cb-f4ce4684ea4c",
    "Los Angeles Lakers": "583ecae2-fb46-11e1-82cb-f4ce4684ea4c",
    "Memphis Grizzlies": "583eca88-fb46-11e1-82cb-f4ce4684ea4c",
    "Miami Heat": "583ecea6-fb46-11e1-82cb-f4ce4684ea4c",
    "Milwaukee Bucks": "583ecefd-fb46-11e1-82cb-f4ce4684ea4c",
    "Minnesota Timberwolves": "583eca2f-fb46-11e1-82cb-f4ce4684ea4c",
    "New Orleans Pelicans": "583ecc9a-fb46-11e1-82cb-f4ce4684ea4c",
    "New York Knicks": "583ec70e-fb46-11e1-82cb-f4ce4684ea4c",
    "Oklahoma City Thunder": "583ecfff-fb46-11e1-82cb-f4ce4684ea4c",
    "Orlando Magic": "583ed157-fb46-11e1-82cb-f4ce4684ea4c",
    "Philadelphia 76ers": "583ec87d-fb46-11e1-82cb-f4ce4684ea4c",
    "Phoenix Suns": "583ecfa8-fb46-11e1-82cb-f4ce4684ea4c",
    "Portland Trail Blazers": "583ed056-fb46-11e1-82cb-f4ce4684ea4c",
    "Sacramento Kings": "583ed0ac-fb46-11e1-82cb-f4ce4684ea4c",
    "San Antonio Spurs": "583ecd4f-fb46-11e1-82cb-f4ce4684ea4c",
    "Toronto Raptors": "583ecda6-fb46-11e1-82cb-f4ce4684ea4c",
    "Utah Jazz": "583ece50-fb46-11e1-82cb-f4ce4684ea4c",
    "Washington Wizards": "583ec8d4-fb46-11e1-82cb-f4ce4684ea4c"
}


# Function to read the API key from a file
def read_api_key(filepath):
    with open(filepath, 'r') as file:
        return file.readline().strip()

# Function to fetch seasonal data for a given team
def fetch_seasonal_data(team_name, team_id, api_key):
    base_url = f'https://api.sportradar.com/nba/trial/v8/en/seasons/2023/REG/teams/{team_id}/statistics.json?api_key={api_key}'
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        totals = data.get('own_record', {}).get('total', {})
        selected_data = {key: totals.get(key) for key in ['games_played', 'field_goals_made', 'field_goals_att', 
                                                          'two_points_made', 'two_points_att', 'three_points_made', 
                                                          'three_points_att', 'free_throws_made', 'total_rebounds', 
                                                          'assists', 'total_turnovers', 'steals', 'blocks']}
        return team_name, selected_data
    else:
        print(f"Error fetching data for {team_name}: {response.status_code}")
        return team_name, None

# Main script
api_key = read_api_key('apikey.txt')

# CSV file setup
with open('team_selected_totals.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    headers = ['Team', 'Games Played', 'Field Goals Made', 'Field Goals Attempted', 'Two Points Made', 
               'Two Points Attempted', 'Three Points Made', 'Three Points Attempted', 'Free Throws Made', 
               'Total Rebounds', 'Assists', 'Total Turnovers', 'Steals', 'Blocks']
    writer.writerow(headers)

    for team_name, team_id in team_ids_dict.items():
        team_data = fetch_seasonal_data(team_name, team_id, api_key)
        if team_data[1]:
            # Write the data row
            writer.writerow([team_data[0]] + list(team_data[1].values()))
            print(f"Data written for {team_name}")
        else:
            print(f"No data for {team_name}")

        # Sleep for 1.5 seconds to adhere to the API rate limit
        time.sleep(1.5)

print("Data fetching and CSV writing complete.")
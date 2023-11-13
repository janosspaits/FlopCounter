import requests
import json

# API call
url = "https://api.sportradar.us/nba/trial/v7/en/games/2023/REG/schedule.json?api_key=gdphf556ghttwjujt6mfmjkq"

# Make the request
response = requests.get(url)

if response.status_code == 200:
    # Save the response data in a JSON file with pretty formatting
    with open('nba_schedule.json', 'w') as file:
        json.dump(response.json(), file, indent=4)
    print("Schedule saved successfully.")
else:
    print(f"Error: {response.status_code}")
# FlopCounter

## Description

This is the only source on the planet where you can check the exact number of flopping technical fouls committed in the NBA for the 2023/2024 season.

This Python application is designed to analyze play-by-play data from NBA games to identify instances of technical fouls for flopping. It utilizes data from the SportRadar API to fetch detailed game events and processes this data to extract and report players who have committed flopping technical fouls.

## Features
Fetches play-by-play data for NBA games using the Sportradar API.
Scrapes Spotrac for the same data.
Identifies and counts instances of flopping technical fouls committed by players.
Stores and displays the list of players who have committed flopping fouls, including the count of occurrences.

## Data Source
The application retrieves data from the SportRadar NBA API. This includes game schedules, play-by-play event descriptions, and specific game-related data. (https://developer.sportradar.com/docs/read/basketball/NBA_v8)
It also retrieves data from Spotrac: https://www.spotrac.com/nba/fines-suspensions/fines/flopping/#player
These two sources oddly complement each other, as Spotrac only track the flopping fines given as post-game decisions, whilst the API only tracks flopping technical fouls called live in game.

## Disclaimer
### Usage Disclaimer
This application is intended for educational and research purposes only. Users are responsible for complying with Sportradar's terms of service, including any limitations on data usage. The developer of this application assumes no responsibility for any misuse of data or violations of Sportradar's terms.

### Commercial Use
This application, and any data retrieved through it, must not be used for commercial purposes. The Sportradar API is subject to its own terms of service, which must be adhered to at all times.

## Installation and Setup
- Ensure Python 3.x is installed on your system.
- Highly recommend reopening the project in a docker container (using the devcontainer.json file) as this will automatically install the packages needed.
- Install/import required Python packages: requests, json, time (pip install -r requirements.txt)
- Obtain an API key from SportRadar: https://developer.sportradar.com
- Save the API key to a file in the project directory called apikey.txt (this file should be git ignored for privacy)

## Usage
- To get the most up-to-date NBA Schedule JSON file, uncomment the function in nba_shedule.py and run the file. This should overwrite any existing nba_shedule.json files.
- Run main.py
- The application will print to console and also save the results into a dictionary called 'flopping_counts.json'
- Please be aware that due to API limitations, parsing through every match takes some time. The app is currently set to wait 1.5 seconds between each API call (the limit is 1/s on a free Trial account)
- Please be aware that the free Trial API key has a limitation of 1000 calls per month. This means by the end of the season this app would inevitably break, as an NBA season consists of 1230 matches.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is open-sourced under the [MIT License](LICENSE).

## Developed by

Janos Spaits

https://github.com/janosspaits

2023

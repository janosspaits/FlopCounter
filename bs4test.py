import requests
from datetime import datetime
from bs4 import BeautifulSoup

SCRAPING_URL = "https://www.spotrac.com/nba/fines-suspensions/fines/flopping/#player"

def scrape_flopping_fouls(cutoff_date_str="2023-11-13"):
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

    cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d").date()
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

print(scrape_flopping_fouls(cutoff_date_str="2023-12-10"))

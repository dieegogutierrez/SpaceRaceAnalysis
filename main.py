import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date

URL = "https://nextspaceflight.com/launches/past/?search="

response = requests.get(URL)
data = response.text

soup = BeautifulSoup(data, "html.parser")

last_page_soup = soup.select_one('.mdc-button--raised:-soup-contains("last")')
last_page = int(last_page_soup.get('onclick').split('=')[2].split('&')[0])

final_data = []

for page_num in range(1, last_page+1):
    response = requests.get(f"https://nextspaceflight.com/launches/past/?page={page_num}&search=")
    data = response.text
    soup = BeautifulSoup(data, "html.parser")
    details_soup = soup.select('h5')
    datetime_and_location_soup = soup.select('.mdl-card__supporting-text')
    mission_details_link_soup = soup.select('.mdc-button:-soup-contains("Details")')

    for i in range(len(mission_details_link_soup)):
        details_url = mission_details_link_soup[i].get('onclick').split("'")[1].strip("'")
        response = requests.get(f"https://nextspaceflight.com{details_url}")
        data = response.text
        soup = BeautifulSoup(data, "html.parser")
        mission_status = soup.select_one('h6')
        organization = soup.select_one('.a:first-child .mdl-cell:first-child')
        status = soup.select_one('.a:first-child .mdl-cell:nth-of-type(2)')
        datetime_and_location_split = datetime_and_location_soup[i].get_text(strip=True, separator="#").split('#')
        price = soup.select_one('.a:first-child .mdl-cell:nth-of-type(3)')
        if "$" in price.get_text():
            try:
                price_value = float(price.get_text(strip=True).split('$')[1].split(' ')[0])
            except ValueError:
                price_value = ""
        else:
            price_value = ""

        record = {
            "Organization": organization.get_text(strip=True),
            "Location": datetime_and_location_split[1],
            "Datetime": datetime_and_location_split[0],
            "Details": details_soup[i].get_text(strip=True),
            "Status": status.get_text(strip=True).split(': ')[1],
            "Price": price_value,
            "Mission_status": mission_status.get_text(strip=True)
        }
        final_data.append(record)

pd.DataFrame(final_data).to_csv(f"mission_launches_updated_{date.today()}.csv")
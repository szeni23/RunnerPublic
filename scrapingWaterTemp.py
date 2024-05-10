import os

import requests
from bs4 import BeautifulSoup
import re
import csv


def fetch_temperature_info(url):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        target_container = soup.find('div', id="Par_imagetext_892340585_")
        if not target_container:
            return "Target container with specified ID not found"

        paragraphs = target_container.select(
            "div.row.id-bild-text.no-shadow.bild-rechts-text-links div.col-md-12 div.row div.col-xs-12 p")

        if len(paragraphs) < 2:
            return "Not enough <p> elements to find the temperature information"

        date_text = paragraphs[0].text
        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', date_text)
        if not date_match:
            return "Date not found in the expected format"
        date = date_match.group(0)

        temp_text = paragraphs[1].text
        temp_match = re.search(r'(\d+)\s*°', temp_text)
        if not temp_match:
            return "Temperature not found in the expected format"
        temperature = temp_match.group(1)

        print(f"Date: {date}, Temperature: {temperature}°C")

        write_header = not os.path.exists('temperature_data.csv')

        with open('temperature_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(['Date', 'Temp'])
            writer.writerow([date, temperature])

        return f"Data saved: Date - {date}, Temperature - {temperature}°C"

    except requests.RequestException as e:
        return f"An error occurred: {e}"


url = "https://www.sport.stadt.sg.ch/news/stsg_sport/2024/05/freibaeder--tagesaktuelle-oeffnungszeiten-und-temperaturen.html"
result = fetch_temperature_info(url)
print(result)

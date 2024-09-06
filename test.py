import requests
import json
from datetime import datetime, timedelta
from alerts_updates.alerts_refactor import process_alerts
import threading

saved_alerts = []


def find_category_above_15(url):
    print(f"Fetching data from {url}")
    # Fetch the data
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    data = response.json()

    # Look for a category above 15 in reverse order (most recent first)
    fixed_record = process_alerts(data)
    keep_records = []

    for record in fixed_record:
        for alert in record["alerts"]:
            if alert["matrix_id"] not in saved_alerts:
                keep_records.append(record)
                saved_alerts.append(alert["matrix_id"])
                break

    if len(keep_records) != 0:
        # append to file
        with open('alerts.json', 'a') as f:
            json.dump(keep_records, f, ensure_ascii=False, indent=4)


def generate_urls(base_url, end_date):
    date_format = "%d.%m.%Y"
    start_date = end_date - timedelta(days=1)  # Start by looking back 1 day
    urls = []

    while start_date > datetime.strptime("01.01.2020", date_format):
        # Format the date range for the URL
        date_range = f"fromDate={start_date.strftime(date_format)}&toDate={end_date.strftime(date_format)}"
        # Construct the URL
        url = f"{base_url}?lang=he&{date_range}&mode=0"
        # Update dates for next iteration
        end_date = start_date
        start_date -= timedelta(days=1)
        thread = threading.Thread(target=find_category_above_15, args=(url,))
        thread.start()


if __name__ == '__main__':

    base_url = "https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx"
    end_date = datetime.strptime("27.10.2023", "%d.%m.%Y")
    generate_urls(base_url, end_date)
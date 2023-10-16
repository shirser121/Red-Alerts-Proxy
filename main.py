from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json

import requests
import threading
import time
import os
import logging

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

API_URL = os.environ.get("API_URL", 'https://api.tzevaadom.co.il/alerts-history/')
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 2))
jsonData = []

logging.basicConfig(level=logging.INFO)


def update_data():
    global jsonData
    while True:
        try:
            response = requests.get(API_URL)
            response.raise_for_status()  # raises exception when not a 2xx response
            content = response.content.decode('utf-8')
            jsonData = json.loads(content)
        except Exception as e:
            logging.error(f'Error fetching data: {e}')
        time.sleep(UPDATE_INTERVAL)


@app.route('/')
def home():
    city = request.args.get('city')
    since_id = request.args.get('since_id', type=int)
    since_date = request.args.get('since_date', type=int)

    results = jsonData

    if city:
        filtered_results = []

        for record in results:
            matching_alerts = []
            for alert in record['alerts']:
                for city_sub in alert['cities']:
                    if city in city_sub:
                        matching_alerts.append(alert)
                        break
            if matching_alerts:
                new_record = record.copy()
                new_record['alerts'] = matching_alerts
                filtered_results.append(new_record)

        results = filtered_results

    if since_id:
        results = [record for record in results if record['id'] > since_id]

    if since_date:
        results = [record for record in results if any(alert['time'] > since_date for alert in record['alerts'])]

    response_data = json.dumps(results, ensure_ascii=False)
    return app.response_class(response_data, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    update_thread = threading.Thread(target=update_data)
    update_thread.start()
    app.run(host="0.0.0.0", port=3007)

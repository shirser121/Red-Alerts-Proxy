import json
import time
from flask import request, jsonify

from red_alerts.shared import redis_client
from red_alerts.logger import logger

STALE_THRESHOLD = 60  # seconds


def init_routes(app):
    @app.route('/')
    def home():
        cities = request.args.get('cities')
        since_id = request.args.get('since_id', type=int)
        since_date = request.args.get('since_date', type=int)

        try:
            results = json.loads(redis_client.get('alerts_data') or '[]')
        except Exception as e:
            return jsonify({"error": "Failed to fetch data from Redis", "details": str(e)}), 500

        last_updated = redis_client.get('alerts_last_updated')
        if last_updated is None:
            logger.warning("No data has been fetched yet by the worker.")
        else:
            age = time.time() - float(last_updated)
            if age > STALE_THRESHOLD:
                logger.warning(f"Data is stale: last updated {age:.0f}s ago.")

        if cities:
            cities = cities.split(',')
            filtered_results = []

            for record in results:
                matching_alerts = []
                for alert in record['alerts']:
                    for city_sub in alert['cities']:
                        if any(city in city_sub for city in cities):
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

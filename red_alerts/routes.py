import json
from flask import request, jsonify
from red_alerts.shared import redis_client
from red_alerts.logger import logger  # Assuming logger is available for logging


def init_routes(app):
    @app.route('/')
    def home():
        # Extract query parameters
        cities = request.args.get('cities')
        since_id = request.args.get('since_id', type=int)
        since_date = request.args.get('since_date', type=int)

        try:
            # Fetch alert data from Redis, default to empty list if not found
            results = json.loads(redis_client.get('alerts_data') or '[]')
        except Exception as e:
            logger.error(f"Error fetching data from Redis: {e}")
            return jsonify({"error": "Failed to fetch data from Redis", "details": str(e)}), 500

        # Filter by cities if provided
        if cities:
            cities = cities.split(',')
            filtered_results = []

            for record in results:
                matching_alerts = []
                for alert in record['alerts']:
                    # Check if any of the cities in the alert match the provided cities
                    for city_sub in alert['cities']:
                        if any(city in city_sub for city in cities):  # Could change to exact match if required
                            matching_alerts.append(alert)
                            break  # Stop checking after the first match

                if matching_alerts:
                    # Only include the record if there are matching alerts
                    new_record = record.copy()
                    new_record['alerts'] = matching_alerts
                    filtered_results.append(new_record)

            results = filtered_results

        # Filter by since_id if provided
        if since_id is not None:
            results = [record for record in results if record.get('id', 0) > since_id]

        # Filter by since_date if provided
        if since_date is not None:
            results = [
                record for record in results
                if any(alert.get('time', 0) > since_date for alert in record['alerts'])
            ]

        # Respond with filtered results
        response_data = json.dumps(results, ensure_ascii=False)
        return app.response_class(response_data, content_type="application/json; charset=utf-8")

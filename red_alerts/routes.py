import json
from flask import request, jsonify

from red_alerts.shared import redis_client


def init_routes(app):
    @app.route('/')
    def home():
        city = request.args.get('city')
        since_id = request.args.get('since_id', type=int)
        since_date = request.args.get('since_date', type=int)

        try:
            results = json.loads(redis_client.get('alerts_data') or '[]')
        except Exception as e:
            # You can log the error if needed
            return jsonify({"error": "Failed to fetch data from Redis", "details": str(e)}), 500

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

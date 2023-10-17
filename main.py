from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import json

from logger import logger
from shared import redis_client
from tasks import celery, update_data

app = Flask(__name__)
limiter = Limiter(
    app,
    storage_uri="redis://redis:6379/1"
)
limiter.init_app(app)


def make_celery(app):
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@app.route('/')
def home():
    city = request.args.get('city')
    since_id = request.args.get('since_id', type=int)
    since_date = request.args.get('since_date', type=int)

    results = json.loads(redis_client.get('alerts_data') or '[]')

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
    app.run(host="0.0.0.0", port=3007)

from collections import defaultdict
import datetime
import pytz
import json

ISRAEL_TZ = pytz.timezone('Israel')
UTC_TZ = pytz.utc
THREAT_CATEGORY_THRESHOLD = 15

# Read from newKeys.json
with open('./alerts_updates/newKeys.json') as f:
    newKeys = json.load(f)


class AlertGroup:
    def __init__(self):
        self.cities = []
        self.threat = 0
        self.isDrill = False
        self.matrix_id = 0
        self.rid = 0
        self.time = 0
        self.description = ''

    def to_dict(self):
        return {
            'cities': self.cities,
            'threat': self.threat,
            'isDrill': self.isDrill,
            'matrix_id': self.matrix_id,
            'rid': self.rid,
            'time': self.time,
            'description': self.description
        }


def convert_to_list_format(grouped_alerts):
    final_list = []

    for timestamp_prefix, alerts in grouped_alerts.items():
        final_list.append({
            'id': int(timestamp_prefix),
            'alerts': alerts
        })

    return final_list


def group_alerts_by_prefix_timestamp(alerts):
    grouped_alerts = defaultdict(list)

    for key, value in alerts.items():
        value = value.to_dict()
        timestamp_prefix = value["time"] // 1000
        grouped_alerts[timestamp_prefix].append(value)

    return grouped_alerts


def parse_alert(alert):
    """Parse a single alert, returning a UTC timestamp and the alert data."""
    naive_dt = datetime.datetime.fromisoformat(f"{alert['alertDate'].split('T')[0]}T{alert['time']}")
    aware_dt = ISRAEL_TZ.localize(naive_dt)
    utc_dt = aware_dt.astimezone(UTC_TZ)
    timestamp = int(utc_dt.timestamp())
    return timestamp, alert['data'], alert['category'], alert['matrix_id'], alert['rid'], alert["category_desc"]


def group_alerts(alerts):
    """Group alerts by timestamp."""
    grouped_alerts = defaultdict(AlertGroup)

    for alert in alerts:
        timestamp, data, category, matrix_id, rid, description = parse_alert(alert)
        grouped_alerts[timestamp].cities.append(data)
        grouped_alerts[timestamp].threat = newKeys[str(matrix_id)]["id"]
        grouped_alerts[timestamp].isDrill = newKeys[str(matrix_id)]["isDrill"]
        grouped_alerts[timestamp].rid = rid
        grouped_alerts[timestamp].matrix_id = matrix_id
        grouped_alerts[timestamp].time = timestamp
        grouped_alerts[timestamp].description = f"{newKeys[str(matrix_id)]['he']} = {description}"

    return grouped_alerts


def process_alerts(alerts):
    """Process a list of alerts, returning a list of new alert dictionaries."""
    grouped_alerts = group_alerts(alerts)
    grouped_alerts = group_alerts_by_prefix_timestamp(grouped_alerts)
    grouped_alerts = convert_to_list_format(grouped_alerts)
    return grouped_alerts


if __name__ == '__main__':
    import requests
    response = requests.get('https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1')
    input_json = response.json()
    print(json.dumps(process_alerts(input_json), indent=4, ensure_ascii=False))

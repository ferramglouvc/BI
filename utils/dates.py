from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_data_date():
    now = datetime.now(ZoneInfo("America/Cancun"))

    if now.hour < 11:
        return now.date() - timedelta(days=2)

    return now.date() - timedelta(days=1)

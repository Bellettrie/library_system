from datetime import datetime

from config.models import LendingSettings
from lendings.procedures.get_fine_days import get_fine_days


def get_total_fine_for_lending(lending, current_date: datetime.date):
    lending_settings = LendingSettings.get_for(lending.item, lending.member)

    return min(lending_settings.max_fine, lending_settings.fine_amount * get_fine_days(lending, current_date))

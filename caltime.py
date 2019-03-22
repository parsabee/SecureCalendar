# Time functions for secure calendar.

import arrow


def today_ymd():
    """
    Function for getting today's year, month, and day.
    For setting start state of the calendar.
    Returns three ints.
    """
    today = arrow.now()
    return today.year, today.month, today.day


def days(month, year):
    """
    Function that returns the day of the week on which a given month starts,
    as well as the number of days in that month.
    Params: month and year are ints.
    Returns: first_day and days_in_month are its.
    """
    # day_map = {"Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4,
    #            "Thursday": 5, "Friday": 6, "Saturday": 7}
    date_str = "{:04d}-{:02d}-01T00:00:00+00:00".format(year, month)
    date = arrow.get(date_str)
    first_day = date.format('dddd')  # Get the string name of the first day of the month.
    days_in_month = date.shift(months=+1, days=-1).day  # The day of the last day of the month.
    # day_map[first_day]
    return first_day, days_in_month

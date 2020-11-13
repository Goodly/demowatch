import datetime

def day_from_date(date_string):
    """
    Gets the day of the week of a given date.
    str date_string: date to convert
    str return: day of the week represented by date_string
    """
    return day_index(datetime.datetime.strptime(date_string, '%Y-%m-%d').strftime('%A'))

def event_day(text):
    """
    Gets the day of the week mentioned in a text.
    str text: article to get date of
    str return: index of day of event or None
    """
    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        if day in text:
            return day_index(day)

def day_index(day):
    """
    Gets the index of the day of the week: day_index("Sunday") = 0.
    str day: name of day of the week
    int return: index corresponding to day of the week
    """
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return None or days.index(day)

def date_diff(date, diff):
    """
    Gets the date some number of days before a given date.
    str date: starting date
    int diff: number of days to go back
    str return: the date diff days before param date
    """
    pass
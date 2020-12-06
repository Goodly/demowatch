import datetime
import gzip
import shutil

def convert_gzip(path):
    """
    Converts files at path folder to JSONs.
    str path: path to folder to convert
    """
    with gzip.open(path, 'rb') as f_in:
        with open(path[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def flatten_tuas(tua_dict):
    """
    Flattens nested dictionary of TUAs.
    dict tua_dict: dictionary to flatten
    """
    new_dict = {}
    for tua_type in tua_dict:
        tua_group = tua_dict[tua_type]
        tua_list = []
        for k in tua_group:
            tua_list += tua_group[k]
        new_dict[tua_type] = tua_list
    return new_dict

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
    d1 = ["", len(text)]
    d2 = ["", len(text)]
    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        if day in text:
            index = text.find(day)
            if index < d2[1]:
                if index < d1[1]:
                    d2 = d1
                    d1 = [day, text.find(day)]
                else:
                    d2 = [day, text.find(day)]
    return day_index(d2[0] or d1[0])

def day_index(day):
    """
    Gets the index of the day of the week: day_index("Sunday") = 0.
    str day: name of day of the week
    int return: index corresponding to day of the week
    """
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if day in days:
        return days.index(day)

def date_diff(date, diff):
    """
    Gets the date some number of days before a given date.
    str date: starting date
    int diff: number of days to go back
    str return: the date diff days before param date
    """
    event_date = datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=diff)
    return event_date.strftime('%Y-%m-%d')

def date_format(date):
    """
    Reformats a given date string.
    str date: date string to alter
    """
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
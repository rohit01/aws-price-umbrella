import datetime
import calendar
import re


def validate_email(email, email_regex_csv):
    regex_list = [e.strip() for e in email_regex_csv.split(',')]
    for user_regex in regex_list:
        ## Only * is allowed in user email regex
        match_regex = re.escape(user_regex)
        match_regex = "^%s$" % match_regex.replace('\\*', '.*')
        if re.match(match_regex, email):
            return True
    return False


def convert_none_into_blank_values(details):
    for k, v in details.items():
        if v == None:
            details[k] = ''
    return details


def pretty_date(time_object=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.datetime.now()
    if type(time_object) is int:
        diff = now - datetime.datetime.fromtimestamp(time_object)
    elif isinstance(time_object, datetime.datetime):
        diff = now - time_object
    elif not time_object:
        return ''
    second_diff = diff.seconds
    day_diff = diff.days
    if day_diff < 0:
        return ''
    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def get_current_month_day_count():
    now = datetime.datetime.now()
    return calendar.monthrange(now.year, now.month)[1]


def get_current_month_and_year():
    now = datetime.datetime.now()
    return now.strftime("%B"), now.year

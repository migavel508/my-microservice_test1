from datetime import datetime

def get_current_month():
    """
    Function to get the current month number.
    Returns:
        int: Current month as an integer
    """
    return datetime.now().month

def get_current_year():
    """
    Function to get the current year number.
    Returns:
        int: Current year as an integer
    """
    return datetime.now().year

def is_leap_year(year):
    """
    Function to check if a year is a leap year or not.
    Args:
        year (int): Year to check
    Returns:
        bool: True if leap year, False otherwise
    """
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True
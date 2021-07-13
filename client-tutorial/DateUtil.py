from datetime import date, datetime


def calculate_age(born:datetime.date) -> int:
    """
    calculate the age of a patient based on the supplied dob. This of course does not take account time zones (like the person
    was born in singapore and is now in New York which crosses the international date line... (it';'s a demo)
    :param born:
    :type born:
    :return: age in years
    :rtype: int
    """
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

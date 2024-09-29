from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def total_run_hour_in_hours(td):
    """Converts a timedelta object to hours with decimal minutes."""
    if isinstance(td, timedelta):
        total_seconds = td.total_seconds()
        hours = total_seconds / 3600  # Convert total seconds to hours
        return f"{hours:.2f}"  # Return hours with 2 decimal places
    return ''


@register.filter
def divide_by(value, divisor):
    try:
        return value / divisor
    except (TypeError, ZeroDivisionError):
        return value


@register.filter
def format_currency(value):
    if value is not None:
        # Convert the value to a float and format it as a string with thousand separators
        return "{:,.2f}".format(value)
    else:
        return ""


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)




@register.filter
def get_all_fields(obj):
    """
    Returns a list of all field names of the given object.
    """
    return [field.name for field in obj._meta.get_fields()]


@register.filter
def calculate_faulty_percentage(faulty_count, total_count):
    if total_count > 0:
        return (faulty_count / total_count) * 100
    return 0



@register.filter
def subtract_with_multiplier(value, arg):
    return (value*2.4) - (arg * 2.4)

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    try:
        return value + arg
    except TypeError:
        return ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)




@register.filter
def get_region(regions, region_name):
    return regions.get(region_name, {}).get('TT', 0)  # Default to 0 if not found

@register.filter
def get_region_pgrh(regions, region_name):
    return regions.get(region_name, {}).get('PGRH', 0)  # Default to 0 if not found

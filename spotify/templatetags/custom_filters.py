from django import template
from datetime import datetime
import re


register = template.Library()

@register.filter
def milliseconds_to_minutes_seconds(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


KEY_MAP = {
    -1: "No Key",
    0: "C",
    1: "C♯/D♭",
    2: "D",
    3: "D♯/E♭",
    4: "E",
    5: "F",
    6: "F♯/G♭",
    7: "G",
    8: "G♯/A♭",
    9: "A",
    10: "A♯/B♭",
    11: "B"
}

@register.filter(name='key_to_pitch')
def key_to_pitch(value):
    return KEY_MAP.get(value, "No Key")

MODALITY_MAP = {
    -1: "No modality",
    0: "Minor",
    1: "Major"
}

@register.filter(name='mode_to_modality')
def mode_to_modality(value):
    return MODALITY_MAP.get(value, "No modality")

@register.filter
def format_to_year(value):
    # Check if the value is a string and try to parse it to a datetime object
    if isinstance(value, str):
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value  # If parsing fails, return the original value
    elif isinstance(value, datetime):
        date_obj = value
    else:
        return value  # If it's neither a string nor a datetime, return the original value
    
    # Return the formatted date
    return date_obj.strftime("%Y")

@register.filter
def format_to_date(value):
    # Check if the value is a string and try to parse it to a datetime object
    if isinstance(value, str):
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value  # If parsing fails, return the original value
    elif isinstance(value, datetime):
        date_obj = value
    else:
        return value  # If it's neither a string nor a datetime, return the original value
    
    # Return the formatted date
    return date_obj.strftime("%d %B %Y")


@register.filter
def seconds_to_time(value):
    """Converts seconds to 'HH:MM:SS' or 'MM:SS' format."""
    try:
        total_seconds = int(value)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes}:{seconds:02}"
    except ValueError:
        return value
    
@register.filter
def format_date(value):
    """Converts an ISO 8601 date string to a 'DD MMM YYYY' format."""
    try:
        date = datetime.fromisoformat(value)
        return date.strftime("%d %b %Y")
    except ValueError:
        return value

@register.filter
def comma_separated(value):
    """Converts a number into a comma-separated string and removes any non-numeric characters."""
    try:
        # Extract only numeric characters from the value
        numeric_value = re.sub(r'\D', '', value)
        # Convert the numeric string to an integer and format with commas
        int_value = int(numeric_value)
        string_with_commas = f"{int_value:,}"
        return string_with_commas
    except (ValueError, TypeError):
        return value  # Return the original value if it's not a valid integer
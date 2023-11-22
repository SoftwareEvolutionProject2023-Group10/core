"""Module for mapping weather conditions to RGB color values.

RGB color values are used to set the color of lights to reflect the current weather.
"""
WEATHER_TO_COLOR_MAP = {
    "clear-night": (25, 25, 112),  # Midnight Blue
    "cloudy": (169, 169, 169),  # Dark Gray
    "exceptional": (255, 215, 0),  # Gold
    "fog": (105, 105, 105),  # Dim Gray
    "hail": (135, 206, 250),  # Sky Blue
    "lightning": (255, 255, 0),  # Yellow
    "lightning-rainy": (0, 0, 139),  # Dark Blue
    "partlycloudy": (250, 250, 210),  # Light Yellow
    "pouring": (70, 130, 180),  # Steel Blue
    "rainy": (30, 144, 255),  # Blue
    "snowy": (255, 250, 250),  # Snow
    "snowy-rainy": (176, 224, 230),  # Powder Blue
    "sunny": (255, 255, 0),  # Bright Yellow
    "windy": (152, 251, 152),  # Pale Green
    "windy-variant": (102, 205, 170),  # Medium Aquamarine
}


def get_color_for_weather_state(weather_state):
    """Return the RGB color value for a given weather state."""
    return WEATHER_TO_COLOR_MAP.get(weather_state, (255, 255, 255))  # Default to white

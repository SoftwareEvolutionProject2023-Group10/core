"""Module for mapping weather conditions to RGB color values.

RGB color values are used to set the color of lights to reflect the current weather.
"""
import colorsys

WEATHER_TO_COLOR_MAP = {
    "clear-night": (0, 0, 128),  # Midnight Blue
    "cloudy": (0, 128, 128),  # Dark Gray
    "exceptional": (255, 0, 0),  # Gold
    "fog": (0, 128, 128),  # Dim Gray
    "hail": (0, 0, 255),  # Sky Blue
    "lightning": (255, 255, 0),  # Yellow
    "lightning-rainy": (0, 128, 128),  # Dark Blue
    "partlycloudy": (255, 255, 0),  # Light Yellow
    "pouring": (0, 0, 255),  # Steel Blue
    "rainy": (30, 144, 255),  # Blue
    "snowy": (255, 250, 250),  # Snow
    "snowy-rainy": (0, 0, 255),  # Powder Blue
    "sunny": (255, 255, 0),  # Bright Yellow
    "windy": (255, 69, 0),  # Pale Green
    "windy-variant": (255, 69, 0),  # Medium Aquamarine
}


def rgb_to_hs(rgb):
    """RGB to HS converter."""
    r, g, b = (x / 255.0 for x in rgb)
    h, s, _ = colorsys.rgb_to_hsv(r, g, b)
    return int(h * 360), int(s * 100)


def get_color_for_weather_state(weather_state):
    """Return the RGB color value for a given weather state."""
    return rgb_to_hs(
        WEATHER_TO_COLOR_MAP.get(weather_state, (255, 255, 255))
    )  # Default to white


def calculate_brightness(temperature) -> int:
    """Define the brightness base of temperature in the range of 0-100."""
    if temperature is None:
        return 255

    min_temp = -20  # Minimum temperature
    max_temp = 40  # Maximum temperature

    # Normalize the temperature within the range
    normalized_temp = 1 - (temperature - min_temp) / (max_temp - min_temp)

    brightness = normalized_temp * 255

    # 0 to 100
    brightness = max(0, min(brightness, 255))

    return int(brightness)

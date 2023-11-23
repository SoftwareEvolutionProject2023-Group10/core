"""Constants for this integration."""
import colorsys

DOMAIN = "weather_light_switch"

ATTR_SIM_LIGHT_ENTITY = "light.simulated_light"
ATTR_SMHI_WEATHER = "weather.smhi_weather"
# Weather conditions as constants
CLEAR_NIGHT = "clear-night"
CLOUDY = "cloudy"
EXCEPTIONAL = "exceptional"
FOG = "fog"
HAIL = "hail"
LIGHTNING = "lightning"
LIGHTNING_RAINY = "lightning-rainy"
PARTLY_CLOUDY = "partlycloudy"
POURING = "pouring"
RAINY = "rainy"
SNOWY = "snowy"
SNOWY_RAINY = "snowy-rainy"
SUNNY = "sunny"
WINDY = "windy"
WINDY_VARIANT = "windy-variant"
OFF = "OFF"

# RGB colors as constants
NAVY_BLUE = (0, 0, 128)
DARK_GRAY = (169, 169, 169)
RED = (255, 0, 0)
SILVER = (192, 192, 192)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TEAL = (0, 128, 128)
SNOW = (255, 250, 250)
RED_ORANGE = (255, 69, 0)
BLACK = (100, 100, 100)
GRAY = (128, 128, 128)
OFF_LIGHT = (68, 115, 158)


def rgb_to_hs(rgb):
    """RGB to HS converter."""
    r, g, b = (x / 255.0 for x in rgb)
    h, s, _ = colorsys.rgb_to_hsv(r, g, b)
    return int(h * 360), int(s * 100)


# Color map with HS values directly
COLOR_MAP = {
    CLEAR_NIGHT: rgb_to_hs(NAVY_BLUE),
    CLOUDY: rgb_to_hs(TEAL),
    EXCEPTIONAL: rgb_to_hs(RED),
    FOG: rgb_to_hs(TEAL),
    HAIL: rgb_to_hs(BLUE),
    LIGHTNING: rgb_to_hs(YELLOW),
    LIGHTNING_RAINY: rgb_to_hs(TEAL),
    PARTLY_CLOUDY: rgb_to_hs(YELLOW),
    POURING: rgb_to_hs(BLUE),
    RAINY: rgb_to_hs(BLUE),
    SNOWY: rgb_to_hs(SNOW),
    SNOWY_RAINY: rgb_to_hs(BLUE),
    SUNNY: rgb_to_hs(YELLOW),
    WINDY: rgb_to_hs(RED_ORANGE),
    WINDY_VARIANT: rgb_to_hs(RED_ORANGE),
    OFF: rgb_to_hs(OFF_LIGHT),
}

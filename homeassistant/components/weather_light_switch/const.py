"""Constants for this integration."""

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
BLACK = (10, 0, 0)
GRAY = (128, 128, 128)

COLOR_MAP = {
    CLEAR_NIGHT: NAVY_BLUE,  # Navy Blue
    CLOUDY: DARK_GRAY,  # Dark Gray
    EXCEPTIONAL: RED,  # Red
    FOG: SILVER,  # Silver
    HAIL: BLUE,  # Blue
    LIGHTNING: YELLOW,  # Yellow
    LIGHTNING_RAINY: TEAL,  # Teal
    PARTLY_CLOUDY: YELLOW,  # Yellow
    POURING: BLUE,  # Blue
    RAINY: BLUE,  # Blue
    SNOWY: SNOW,  # Snow
    SNOWY_RAINY: BLUE,  # Blue
    SUNNY: YELLOW,  # Yellow
    WINDY: RED_ORANGE,  # Red-Orange
    WINDY_VARIANT: RED_ORANGE,  # Red-Orange
    OFF: GRAY,
}

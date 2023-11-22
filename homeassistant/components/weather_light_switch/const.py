"""Constants for this integration."""

DOMAIN = "weather_light_switch"
DEFAULT_TEMP = 20
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
MIDNIGHT_BLUE = (25, 25, 112)
DARK_GRAY = (169, 169, 169)
GOLD = (255, 215, 0)
SILVER = (105, 105, 105)
SKY_BLUE = (135, 206, 250)
YELLOW = (255, 255, 2)
DARK_BLUE = (0, 0, 139)
LIGHT_YELLOW = (250, 250, 210)
STEEL_BLUE = (70, 130, 180)
BLUE = (30, 144, 255)
SNOW = (250, 250, 250)
POWDER_BLUE = (176, 224, 230)
BRIGHT_YELLOW = (255, 255, 0)
PALE_GREEN = (152, 251, 152)
RED_ORANGE = (255, 69, 0)
BLACK = (0, 0, 0)
OFF_LIGHT = (68, 115, 158)

COLOR_MAP = {
    CLEAR_NIGHT: MIDNIGHT_BLUE,  # Midnight_Blue
    CLOUDY: DARK_GRAY,  # Dark_Gray
    EXCEPTIONAL: GOLD,  # Gold
    FOG: SILVER,  # Silver
    HAIL: SKY_BLUE,  # Sky_Blue
    LIGHTNING: YELLOW,  # Yellow
    LIGHTNING_RAINY: DARK_BLUE,  # Dark_Blue
    PARTLY_CLOUDY: LIGHT_YELLOW,  # Light_Yellow
    POURING: STEEL_BLUE,  # Steel_Blue
    RAINY: BLUE,  # Blue
    SNOWY: SNOW,  # Snow
    SNOWY_RAINY: POWDER_BLUE,  # Powder_Blue
    SUNNY: BRIGHT_YELLOW,  # Bright_Yellow
    WINDY: PALE_GREEN,  # Pale_Green
    WINDY_VARIANT: RED_ORANGE,  # Red_Orange
    OFF: BLACK,
}

import json

import httpx

from oterm.config import envConfig
from oterm.tools import Parameters, Property, Tool, ToolFunction

WeatherTool = Tool(
    type="function",
    function=ToolFunction(
        name="get_weather_info",
        description="Function to return the current weather for the given location in Standard Units.",
        parameters=Parameters(
            type="object",
            properties={
                "latitude": Property(
                    type="float", description="The latitude of the location."
                ),
                "longitude": Property(
                    type="float", description="The longitude of the location."
                ),
            },
            required=["latitude", "longitude"],
        ),
    ),
)


def get_current_weather(latitude: float, longitude: float) -> str:
    try:
        api_key = envConfig.OPEN_WEATHER_MAP_API_KEY
        if not api_key:
            raise Exception("OpenWeatherMap API key not found")

        response = httpx.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
        )

        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            return json.dumps(
                {"error": f"{response.status_code}: {response.reason_phrase}"}
            )
    except Exception as e:
        return json.dumps({"error": str(e)})

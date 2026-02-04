import os
from typing import Any, Dict

import requests


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def _request_with_retries(url: str, params: Dict[str, str]) -> requests.Response:
    last_exc: Exception | None = None
    for _ in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response
            if response.status_code in {400, 401, 404}:
                return response
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError("request failed without exception")


def fetch_current_weather(city: str, units: str = "metric") -> Dict[str, Any]:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY not set"}
    params = {"q": city, "appid": api_key, "units": units}
    response = _request_with_retries(OPENWEATHER_URL, params)
    if response.status_code != 200:
        return {"error": f"OpenWeather returned {response.status_code}", "details": response.text}
    data = response.json()
    main = data.get("main", {})
    weather_list = data.get("weather", [])
    description = weather_list[0].get("description") if weather_list else None
    return {
        "city": data.get("name"),
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "conditions": description,
        "units": units,
    }

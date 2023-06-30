import os
import requests
import sys


def getWeatherData(*, city:str, days:int=8, alerts:str='yes', aqi:str='no', api_key:str) -> dict:
    """Fetches weather data from api.weatherapi.com for (no. of days=)days and returns it as a dictionary"""
    try:
        weather_url = f'https://api.weatherapi.com/v1/forecast.json?q={city}&days={days}&alerts={alerts}&aqi={aqi}&key={api_key}'
        weather_data = requests.get(weather_url)
        weather_data: dict = weather_data.json()
    except Exception as e:
        print('Error fetching data from weatherapi.com:', e)
        sys.exit(1)
    
    return weather_data


def getCurrentWeather(weather_data:dict) -> dict:
    """Returns the current weather"""
    REQ_KEYS = ('temp_c', 'feelslike_c', 'humidity', 'precip_mm', 'condition', 'wind_kph', 'last_updated')
    current_weather = {key:weather_data['current'][key] for key in REQ_KEYS}
    return current_weather


def getWeeklyWeatherAndAlerts(weather_data:dict, work_hours:tuple, alert_mode:int=2) -> tuple[list[dict]]:
    """Returns weather data and rainfall alerts (based on the alert mode) for the workdays"""
    # alert_mode can be 0, 1, 2 or 3
    ALERT_MODES = ('Patchy rain', 'Light rain', 'Moderate rain', 'Heavy rain')
    REQ_KEYS = ('maxtemp_c', 'mintemp_c', 'avgtemp_c', 'avghumidity', 'totalprecip_mm', 'daily_chance_of_rain', 'condition')

    location:str = f"{weather_data['location']['name']}, {weather_data['location']['region']}, {weather_data['location']['country']}"
    
    weekly_weather: list = []
    weekly_alerts: list = []
    for day in weather_data['forecast']['forecastday']:
        daily_weather:dict = {'location':location, 'date':day['date']}
        daily_weather.update({key:day['day'][key] for key in REQ_KEYS})
        daily_weather['condition'] = daily_weather['condition']['text']
        weekly_weather.append(daily_weather)
        
        # Check if chances of rain in work hours
        for hour in day['hour'][work_hours[0]:work_hours[1]+1]:
            for condition in ALERT_MODES[alert_mode:]:
                if condition in hour['condition']['text']:
                    weekly_alerts.append({
                    'location': location, 'day': day['date'], 'time':hour['time'][-5:], 
                    'condition':hour['condition']['text'], 'precip_mm':hour['precip_mm'],
                    'chance_of_rain':hour['chance_of_rain']
                    })
    
    return weekly_weather, weekly_alerts


if __name__=='__main__':
    city: str = input('Enter the name of the city:').strip()
    work_hours_str: str = input('Enter work hrs in 24hr format separated by , as start,end:')
    work_hours: tuple = tuple(int(i) for i in work_hours_str.strip().split(','))

    API_KEY = os.environ.get('API_KEY')
    
    weather_data = getWeatherData(city=city, api_key=API_KEY)
    _, weekly_alerts = getWeeklyWeatherAndAlerts(weather_data, work_hours, alert_mode=1)
    print(weekly_alerts)

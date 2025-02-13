import streamlit as st
import requests
import os
import pandas as pd

# Function to fetch weather data
def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY", "3c1d901aba98438bacb44730251302")  # Store API key in an environment variable
    base_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3&aqi=no&alerts=no"

    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise HTTP errors if any
        data = response.json()

        if "error" in data:
            return None, data["error"]["message"]

        weather_info = {
            "City": data["location"]["name"],
            "Country": data["location"]["country"],
            "Temperature": f"{data['current']['temp_c']}°C",
            "Feels Like": f"{data['current']['feelslike_c']}°C",
            "Humidity": f"{data['current']['humidity']}%",
            "Pressure": f"{data['current']['pressure_mb']} hPa",
            "Wind Speed": f"{data['current']['wind_kph']} kph",
            "Condition": data["current"]["condition"]["text"],
            "Icon": data["current"]["condition"]["icon"],
            "UV Index": data["current"]["uv"],
            "Visibility": f"{data['current']['vis_km']} km",
            "Forecast": data["forecast"]["forecastday"]
        }

        return weather_info, None

    except requests.exceptions.RequestException as e:
        return None, f"API request failed: {e}"

# Streamlit UI
def main():
    st.set_page_config(page_title="Weather App", layout="wide")

    st.sidebar.title("🌤 Real-Time Weather App")
    st.sidebar.write("Enter a city name to get up-to-date weather information.")

    city_name = st.sidebar.text_input("City Name", "Mumbai")

    if st.sidebar.button("Get Weather"):
        weather, error = get_weather(city_name)

        if error:
            st.sidebar.error(f"Error: {error}")
        else:
            st.title(f"Weather in {weather['City']}, {weather['Country']}")
            st.image(f"http:{weather['Icon']}", width=100)
            st.write(f"**Condition:** {weather['Condition']}")

            tab1, tab2, tab3 = st.tabs(["🌡 Current Weather", "📊 Forecast", "📈 Trends"])

            with tab1:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.metric("Temperature", weather["Temperature"])
                    st.metric("Feels Like", weather["Feels Like"])
                    st.metric("Humidity", weather["Humidity"])
                    st.metric("Pressure", weather["Pressure"])
                    st.metric("Wind Speed", weather["Wind Speed"])
                    st.metric("UV Index", weather["UV Index"])
                    st.metric("Visibility", weather["Visibility"])

                with col2:
                    st.image(f"http:{weather['Icon']}", width=80)

            with tab2:
                for day in weather["Forecast"]:
                    st.subheader(f"Forecast for {day['date']}")
                    st.image(f"http:{day['day']['condition']['icon']}", width=80)
                    st.write(f"**Condition:** {day['day']['condition']['text']}")
                    st.metric("Max Temperature", f"{day['day']['maxtemp_c']}°C")
                    st.metric("Min Temperature", f"{day['day']['mintemp_c']}°C")
                    st.metric("Average Humidity", f"{day['day']['avghumidity']}%")
                    st.metric("Total Precipitation", f"{day['day']['totalprecip_mm']} mm")

            with tab3:
                dates = [day['date'] for day in weather["Forecast"]]
                max_temps = [day['day']['maxtemp_c'] for day in weather["Forecast"]]
                min_temps = [day['day']['mintemp_c'] for day in weather["Forecast"]]

                df = pd.DataFrame({
                    "Date": dates,
                    "Max Temperature (°C)": max_temps,
                    "Min Temperature (°C)": min_temps
                })

                st.line_chart(df.set_index("Date"))

if __name__ == "__main__":
    main()
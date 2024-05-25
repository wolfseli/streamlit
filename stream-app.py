import numpy as np
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NASA Asteroid Data", page_icon="🌠")

st.title("NASA Asteroid Data")

st.write("This is a simple Streamlit app that shows the data of asteroids that have come close to Earth this month.")

# Set the API endpoint URL
url = "https://api.nasa.gov/neo/rest/v1/feed"

# Set the parameters for the API request
api_key = "96ycipvaBH52byeolyOAQPaaoEJCmLGZpzmWVwLG"
start_date = "2024-05-01"

# Initialize an empty list to store asteroid data
asteroid_data = []

# Calculate the number of days in the month
num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1

# Function to get asteroid data
@st.cache_data
def get_asteroid_data(url, api_key, start_date, num_days):
    asteroid_data = []
    for i in range(num_days):
        # Calculate the current date
        current_date = pd.to_datetime(start_date) + pd.DateOffset(days=i)
        
        # Convert the date to string format
        current_date_str = current_date.strftime('%Y-%m-%d')
        
        # Build the API request URL for the current date
        request_url = f"{url}?start_date={current_date_str}&end_date={current_date_str}&api_key={api_key}"
        
        # Send the API request and get the response
        response = requests.get(request_url)
        
        # Convert the response to JSON format
        json_data = response.json()
        
        # Extract the asteroid data from the JSON response
        for date in json_data["near_earth_objects"]:
            for asteroid in json_data["near_earth_objects"][date]:
                asteroid_data.append({
                    "name": asteroid["name"],
                    "diameter": asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"],
                    "velocity": asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"],
                    "distance": asteroid["close_approach_data"][0]["miss_distance"]["kilometers"],
                    "Date": date,
                    "is_potentially_hazardous": asteroid["is_potentially_hazardous_asteroid"]
                })
    return asteroid_data

# Get the asteroid data
asteroid_data = get_asteroid_data(url, api_key, start_date, num_days)

# Convert the asteroid data to a Pandas dataframe
asteroid_df = pd.DataFrame(asteroid_data)

# Add radio button to filter potentially hazardous asteroids
hazardous = st.radio("Filter potentially hazardous asteroids:", ["Yes", "No", "All"])

if hazardous == "Yes":
    asteroid_df = asteroid_df[asteroid_df["is_potentially_hazardous"]]
elif hazardous == "No":
    asteroid_df = asteroid_df[~asteroid_df["is_potentially_hazardous"]]

# Display the asteroid data
st.write("Asteroid Data for this month:")
st.write(asteroid_df)

# Show a plot of the number of asteroids by date
st.write("Number of asteroids by date:")
date_counts = asteroid_df["Date"].value_counts().sort_index()
st.bar_chart(date_counts)

# make bins for the diameter of the asteroids. The bins are 0-100, 100-200, 200-300, 300-400, 400-500, 500-600, 600-700, 700-800, 800-900, 900-1000, over 1000
# count the number of asteroids in each bin an show a bar chart
bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, np.inf]
labels = ['0-100', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700', '700-800', '800-900', '900-1000', 'over 1000']
asteroid_df['diameter_bin'] = pd.cut(asteroid_df['diameter'], bins=bins, labels=labels, right=False)
diameter_counts = asteroid_df['diameter_bin'].value_counts().sort_index()
st.write("Number of asteroids by diameter:")
st.bar_chart(diameter_counts)

# streamlit run stream-app.py
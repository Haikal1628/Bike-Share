import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set the style for seaborn
sns.set(style='darkgrid')

# Function to calculate total counts by hour
def calculate_hourly_counts(hour_data):
    hourly_count = hour_data.groupby(by="hours").agg({"count_cr": ["sum"]})
    return hourly_count

# Function to filter data for a specific year
def filter_days_data(day_data):
    filtered_data = day_data.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')
    return filtered_data

# Function to sum registered users per day
def sum_registered_users(day_data):
    registered_data = day_data.groupby(by="dteday").agg({"registered": "sum"})
    registered_data = registered_data.reset_index()
    registered_data.rename(columns={"registered": "register_sum"}, inplace=True)
    return registered_data

# Function to sum casual users per day
def sum_casual_users(day_data):
    casual_data = day_data.groupby(by="dteday").agg({"casual": ["sum"]})
    casual_data = casual_data.reset_index()
    casual_data.rename(columns={"casual": "casual_sum"}, inplace=True)
    return casual_data

# Function to get ordered item counts by hour
def get_order_count_by_hour(hour_data):
    ordered_counts = hour_data.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return ordered_counts

# Function to aggregate seasonal data
def aggregate_season_data(day_data): 
    seasonal_counts = day_data.groupby(by="season").count_cr.sum().reset_index() 
    return seasonal_counts

# Load the datasets
day_data = pd.read_csv("day_clean.csv")
hour_data = pd.read_csv("hour_clean.csv")

# Define the date column
date_columns = ["dteday"]
day_data.sort_values(by="dteday", inplace=True)
day_data.reset_index(drop=True, inplace=True)   

hour_data.sort_values(by="dteday", inplace=True)
hour_data.reset_index(drop=True, inplace=True)

# Convert date columns to datetime
for column in date_columns:
    day_data[column] = pd.to_datetime(day_data[column])
    hour_data[column] = pd.to_datetime(hour_data[column])

# Get the date range for filtering
start_date_days = day_data["dteday"].min()
end_date_days = day_data["dteday"].max()
start_date_hours = hour_data["dteday"].min()
end_date_hours = hour_data["dteday"].max()

# Streamlit sidebar configuration
with st.sidebar:
    # Add a company logo
    st.image("bikephoto.png")
    
    # Date input for filtering data
    start_date, end_date = st.date_input(
        label='Select Date Range',
        min_value=start_date_days,
        max_value=end_date_days,
        value=[start_date_days, end_date_days]
    )
  
# Filter datasets based on the selected date range
filtered_day_data = day_data[(day_data["dteday"] >= str(start_date)) & 
                              (day_data["dteday"] <= str(end_date))]

filtered_hour_data = hour_data[(hour_data["dteday"] >= str(start_date)) & 
                                (hour_data["dteday"] <= str(end_date))]

# Perform data calculations
hourly_counts_df = calculate_hourly_counts(filtered_hour_data)
filtered_data_2011 = filter_days_data(filtered_day_data)
registered_users_df = sum_registered_users(filtered_day_data)
casual_users_df = sum_casual_users(filtered_day_data)
order_counts_by_hour_df = get_order_count_by_hour(filtered_hour_data)
seasonal_counts_df = aggregate_season_data(filtered_hour_data)

# Create a dashboard with various visualizations
st.header('Bike Sharing Dashboard')

st.subheader('Daily Bike Sharing Metrics')
col1, col2, col3 = st.columns(3)

with col1:
    total_registered = registered_users_df.register_sum.sum()
    st.metric("Total Registered Users", value=total_registered)

with col2:
    total_casual = casual_users_df.casual_sum.sum()
    st.metric("Total Casual Users", value=total_casual)
    
with col3:
    total_bike_shares = filtered_data_2011.count_cr.sum()
    st.metric("Total Bike Shares", value=total_bike_shares)

st.subheader("Company Performance Over the Years")

# Plotting company performance
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    day_data["dteday"],
    day_data["count_cr"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Analyzing which season has the highest bike rentals
st.subheader("Which Season Has the Most Rentals?")

color_palette = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9"]
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
        y="count_cr", 
        x="season",
        data=seasonal_counts_df.sort_values(by="season", ascending=False),
        palette=color_palette,
        ax=ax
    )
ax.set_title("Seasonal Bike Rental Counts", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

# Analyzing peak and off-peak hours for bike rentals
st.subheader("What Are the Peak and Off-Peak Rental Hours?")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(x="hours", y="count_cr", data=order_counts_by_hour_df.head(5), palette=["#D3D3D3", "#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Peak Rental Hours", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="hours", y="count_cr", data=order_counts_by_hour_df.sort_values(by="hours", ascending=True).head(5), palette=["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#90CAF9"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)", fontsize=30)
ax[1].set_title("Off-Peak Rental Hours", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and clean the data
def load_data():
    file = 'aircrahesFullDataUpdated_2024.csv'
    df = pd.read_csv(file)

    # Data Cleaning
    # Replace '-' with NaN in 'Country/Region'
    df['Country/Region'] = df['Country/Region'].replace('-', pd.NA)

    # Fill missing values in 'Country/Region' and 'Operator' with 'Unknown'
    df['Country/Region'] = df['Country/Region'].fillna('Unknown')
    df['Operator'] = df['Operator'].fillna('Unknown')

    # Trim and Clean Text Fields
    df['Country/Region'] = df['Country/Region'].str.strip().str.title()
    df['Aircraft Manufacturer'] = df['Aircraft Manufacturer'].str.strip().str.title()
    df['Aircraft'] = df['Aircraft'].str.strip()
    df['Location'] = df['Location'].str.strip()
    df['Operator'] = df['Operator'].str.strip()

    # Convert 'Quarter' and 'Month' to categorical data types
    df['Quarter'] = pd.Categorical(df['Quarter'], categories=['Qtr 1', 'Qtr 2', 'Qtr 3', 'Qtr 4'])
    df['Month'] = pd.Categorical(df['Month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'])

    # Handling Outliers
    Q1_ground = df['Ground'].quantile(0.25)
    Q3_ground = df['Ground'].quantile(0.75)
    IQR_ground = Q3_ground - Q1_ground

    Q1_fatalities = df['Fatalities (air)'].quantile(0.25)
    Q3_fatalities = df['Fatalities (air)'].quantile(0.75)
    IQR_fatalities = Q3_fatalities - Q1_fatalities

    lower_bound_ground = Q1_ground - 1.5 * IQR_ground
    upper_bound_ground = Q3_ground + 1.5 * IQR_ground

    lower_bound_fatalities = Q1_fatalities - 1.5 * IQR_fatalities
    upper_bound_fatalities = Q3_fatalities + 1.5 * IQR_fatalities

    df['Ground'] = df['Ground'].clip(lower=lower_bound_ground, upper=upper_bound_ground)
    df['Fatalities (air)'] = df['Fatalities (air)'].clip(lower=lower_bound_fatalities, upper=upper_bound_fatalities)

    # Remove Duplicates
    df.drop_duplicates(inplace=True)

    return df

# Load data
df = load_data()

# Title of the app
st.title('Aircraft Crashes Data Explorer')

# Sidebar filters
st.sidebar.header('Filter the data')

# Filter by Year
years = st.sidebar.multiselect('Select Year(s)', options=df['Year'].unique(), default=df['Year'].unique())

# Filter the dataframe based on the selected years
filtered_df = df[df['Year'].isin(years)]

# 1. Crashes Over Time
st.header('Crashes Over Time')
crashes_per_year = filtered_df.groupby('Year').size()
plt.figure(figsize=(10, 6))
plt.plot(crashes_per_year.index, crashes_per_year.values, marker='o', linestyle='-', color='b')
plt.title('Number of Crashes per Year')
plt.xlabel('Year')
plt.ylabel('Number of Crashes')
st.pyplot(plt)

# 2. Geographic Distribution
st.header('Geographic Distribution of Crashes')

if 'Latitude' in df.columns and 'Longitude' in df.columns:
    st.map(filtered_df[['Latitude', 'Longitude']].dropna())
else:
    st.write("Latitude and Longitude data is not available in the dataset.")
    crashes_by_region = filtered_df['Country/Region'].value_counts()
    plt.figure(figsize=(10, 6))
    crashes_by_region.head(10).plot(kind='bar', color='skyblue')
    plt.title('Top 10 Regions by Number of Crashes')
    plt.xlabel('Country/Region')
    plt.ylabel('Number of Crashes')
    st.pyplot(plt)
    
# 3. Fatalities vs. Aboard
st.header('Fatalities vs. Number of People Aboard')
plt.figure(figsize=(10, 6))
plt.scatter(filtered_df['Aboard'], filtered_df['Fatalities (air)'], alpha=0.7)
plt.title('Fatalities vs. Number of People Aboard')
plt.xlabel('Number of People Aboard')
plt.ylabel('Fatalities')
st.pyplot(plt)

# 4. Top Aircraft Manufacturers
st.header('Top 10 Aircraft Manufacturers Involved in Crashes')
top_manufacturers = filtered_df['Aircraft Manufacturer'].value_counts().head(10)
plt.figure(figsize=(10, 6))
top_manufacturers.plot(kind='bar', color='orange')
plt.title('Top 10 Aircraft Manufacturers Involved in Crashes')
plt.xlabel('Aircraft Manufacturer')
plt.ylabel('Number of Crashes')
st.pyplot(plt)

# 5. Fatalities Over Time
st.header('Fatalities Over Time')
fatalities_per_year = filtered_df.groupby('Year')['Fatalities (air)'].sum()
plt.figure(figsize=(10, 6))
plt.plot(fatalities_per_year.index, fatalities_per_year.values, marker='o', linestyle='-', color='r')
plt.title('Total Fatalities per Year')
plt.xlabel('Year')
plt.ylabel('Total Fatalities')
st.pyplot(plt)

# Option to download the filtered data
st.header('Download the filtered data')
st.write("You can download the filtered dataset as a CSV file.")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(label="Download CSV", data=csv, file_name='filtered_aircrashes_data.csv', mime='text/csv')
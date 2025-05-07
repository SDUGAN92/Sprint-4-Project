import streamlit as st
import pandas as pd
import plotly_express as px

# Read the CSV file
df = pd.read_csv("vehicles_us (1).csv")

# Display the column names
st.subheader("Column Names:")
st.write(df.columns.tolist())

# Display title
st.title("Vehicle Data Analysis")

# Display the first few rows of the dataframe
st.dataframe(df.head())

st.subheader("Checking 'price' column:")
st.write(f"Data type of 'price': {df['price'].dtype}")
st.write(f"Number of non-null values in 'price': {df['price'].count()}")
st.write(f"First 10 values of 'price': {df['price'].head(10).tolist()}")

# Create a histogram of vehicle prices
fig_price = px.histogram(df, x='price', title='Distribution of Vehicle Prices')

# Display the histogram in the Streamlit app
st.plotly_chart(fig_price)

st.header('Vehicle types by model')
# create a plotly histogram figure
fig_type_manufacturer = px.histogram(df, x='model', color='type', title='Distribution of Vehicle Types by Model')
# display the figure with streamlit
st.plotly_chart(fig_type_manufacturer)

st.header('Histogram of condition vs. model_year')
# create a plotly histogram figure
fig_condition_year = px.histogram(df, x='model_year', color='condition', title='Distribution of Condition by Model Year')
# display the figure with streamlit
st.plotly_chart(fig_condition_year)

st.header('Compare price distribution between manufacturers')

# Get unique manufacturer names from the 'model' column
manufacturers = df['model'].str.split(' ', expand=True)[0].unique()
manufacturers.sort()

# Allow the user to select the first manufacturer
manufacturer1 = st.selectbox('Select the first manufacturer:', manufacturers)

# Allow the user to select the second manufacturer
manufacturer2 = st.selectbox('Select the second manufacturer:', manufacturers)

# Filter the DataFrame based on user selections
filtered_df = df[df['model'].str.split(' ', expand=True)[0].isin([manufacturer1, manufacturer2])]

if not filtered_df.empty:
    # Create a box plot to compare price distribution
    fig_price_comparison = px.box(filtered_df, x=filtered_df['model'].str.split(' ', expand=True)[0], y='price', color=filtered_df['model'].str.split(' ', expand=True)[0],
                                 title=f'Price Distribution Comparison: {manufacturer1} vs {manufacturer2}')
    st.plotly_chart(fig_price_comparison)
else:
    st.warning("No data available for the selected manufacturers.")
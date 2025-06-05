#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title('Vehicle Advertisement Listings - US')

# Read data from csv file
try:
    df = pd.read_csv('./vehicles_us_cleaned.csv')
except FileNotFoundError:
    st.error("Error: 'vehicles_us_cleaned.csv' not found. Please ensure the file is in the correct directory.")
    st.stop()

# Display data
st.write(df)

# --- Data Cleaning ---
df_clean = df.copy()

# Clean 'manufacturer' column
df_clean['manufacturer'] = df_clean['manufacturer'].fillna('Unknown').astype(str)

# Clean 'price' column
df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
df_clean['price'] = df_clean['price'].fillna(0)


# Histogram of vehicle types by manufacturer
st.subheader('Histogram of the types of vehicles by manufacturer')
fig_types = px.histogram(df_clean, x='manufacturer', color='type', title='Vehicle Types by Manufacturer')
st.plotly_chart(fig_types)


# Price distribution between manufacturers
st.subheader('Histogram of price distribution between manufacturers')

# Dropdown for selecting manufacturers
all_manufacturers = df_clean['manufacturer'].unique().tolist()
default_index1 = 1 if len(all_manufacturers) > 1 else 0
default_index2 = 2 if len(all_manufacturers) > 2 else (1 if len(all_manufacturers) > 1 else 0)

manufacturer1 = st.selectbox('Manufacturer 1', all_manufacturers, index=default_index1)
manufacturer2 = st.selectbox('Manufacturer 2', all_manufacturers, index=default_index2)

# Normalized histogram checkbox
normalized = st.checkbox('Normalized')

# Determine histnorm value
histnorm_val = 'percent' if normalized else None

# Filter data for selected manufacturers
if manufacturer1 and manufacturer2:
    manufacturers_to_plot = [manufacturer1, manufacturer2]
    filtered_df = df_clean[df_clean['manufacturer'].isin(manufacturers_to_plot)].copy()
else:
    st.warning("Please select two manufacturers to plot.")
    filtered_df = pd.DataFrame()

# Create histogram
if filtered_df.empty:
    st.info("No data available for the selected manufacturers. Showing an empty plot.")
    fig_price = go.Figure()
else:
    fig_price = px.histogram(
        data_frame=filtered_df,
        x='price',
        color='manufacturer',
        histnorm=histnorm_val,
        opacity=0.75,
        barmode='overlay',
        title=f'Price Distribution: {manufacturer1} vs {manufacturer2}'
    )

    # Apply axis titles
    fig_price.update_xaxes(title_text='Price')
    fig_price.update_yaxes(title_text='Count' if histnorm_val is None else 'Percentage')

st.plotly_chart(fig_price)


# Scatter plot matrix
st.subheader('Scatter plot matrix')

# Dropdowns for plot dimensions and color
numerical_cols = df_clean.select_dtypes(include=['number']).columns.tolist()
categorical_cols = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()
all_plot_cols = numerical_cols + categorical_cols

x_axis_index = 0 if len(all_plot_cols) > 0 else 0
y_axis_index = 1 if len(all_plot_cols) > 1 else 0
color_index = 2 if len(all_plot_cols) > 2 else 0

x_axis = st.selectbox('X axis', all_plot_cols, index=x_axis_index)
y_axis = st.selectbox('Y axis', all_plot_cols, index=y_axis_index)
color = st.selectbox('Color', all_plot_cols, index=color_index)

# Subheader for scatter plot matrix
st.subheader(f'Scatter plot matrix of {x_axis} and {y_axis} by {color}')

# Create scatter plot matrix
if x_axis and y_axis and color and x_axis in df_clean.columns and y_axis in df_clean.columns and color in df_clean.columns:
    fig_scatter = px.scatter_matrix(df_clean, dimensions=[x_axis, y_axis], color=color, title=f'Scatter Plot Matrix: {x_axis} vs {y_axis} by {color}')
    st.plotly_chart(fig_scatter)
else:
    st.warning("Please select valid columns for the scatter plot matrix.")

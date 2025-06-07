import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Functions for code organization ---

@st.cache_data # Cache data loading and cleaning for performance
def load_and_clean_data(file_path): # CORRECTED: Changed from a string literal to a parameter name 'file_path'
    """Loads and cleans vehicle data from a CSV file."""
    try:
        # The file path is used here to read the CSV
        df = pd.read_csv(file_path) # Uses the 'file_path' argument
    except FileNotFoundError:
        st.error(f"Error: '{file_path}' not found. Ensure the file is in the correct directory.") # Uses 'file_path' in error message
        st.stop()

    df_clean = df.copy()

    # --- Data Cleaning and Missing Value Imputation ---

    # Handle 'is_4wd': Fill NaNs with 0, convert to boolean.
    df_clean['is_4wd'] = df_clean['is_4wd'].fillna(0).astype(bool)

    # Handle 'paint_color': Fill NaNs with 'unknown'.
    df_clean['paint_color'] = df_clean['paint_color'].fillna('unknown')

    # Handle 'manufacturer': Fill NaNs with 'Unknown', ensure string type.
    df_clean['manufacturer'] = df_clean['manufacturer'].fillna('Unknown').astype(str)

    # Handle 'price': Convert to numeric, fill NaNs with 0.
    df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
    df_clean['price'] = df_clean['price'].fillna(0)

    # Handle 'cylinders': Fill NaNs using median grouped by 'type', then overall median.
    df_clean['cylinders'] = pd.to_numeric(df_clean['cylinders'], errors='coerce')
    df_clean['cylinders'] = df_clean.groupby('type')['cylinders'].transform(lambda x: x.fillna(x.median()))
    df_clean['cylinders'] = df_clean['cylinders'].fillna(df_clean['cylinders'].median()).astype(int)

    # Handle 'model_year': Fill NaNs using median grouped by 'type', then overall median.
    df_clean['model_year'] = pd.to_numeric(df_clean['model_year'], errors='coerce')
    df_clean['model_year'] = df_clean.groupby('type')['model_year'].transform(lambda x: x.fillna(x.median()))
    df_clean['model_year'] = df_clean['model_year'].fillna(df_clean['model_year'].median()).astype(int)

    # Handle 'odometer': Fill NaNs using median grouped by 'model_year' and 'condition', then overall median.
    df_clean['condition'] = df_clean['condition'].fillna('unknown_condition')
    df_clean['odometer'] = pd.to_numeric(df_clean['odometer'], errors='coerce')
    df_clean['odometer'] = df_clean.groupby(['model_year', 'condition'])['odometer'].transform(lambda x: x.fillna(x.median()))
    df_clean['odometer'] = df_clean['odometer'].fillna(df_clean['odometer'].median()).astype(int) 
    
    return df_clean

def display_vehicle_types_histogram(df_data):
    """Displays a histogram of vehicle types by manufacturer."""
    st.subheader('Vehicle Types by Manufacturer')
    fig_types = px.histogram(df_data, x='manufacturer', color='type', title='Distribution of Vehicle Types by Manufacturer')
    st.plotly_chart(fig_types)

def display_price_distribution_histogram(df_data):
    """Displays a histogram of price distribution between selected manufacturers."""
    st.subheader('Price Distribution Comparison Between Manufacturers')

    all_manufacturers = df_data['manufacturer'].unique().tolist()
    default_index1 = min(1, len(all_manufacturers) - 1) if len(all_manufacturers) > 0 else 0
    default_index2 = min(2, len(all_manufacturers) - 1) if len(all_manufacturers) > 1 else (min(1, len(all_manufacturers) - 1) if len(all_manufacturers) > 0 else 0)

    col1, col2 = st.columns(2)
    with col1:
        manufacturer1 = st.selectbox('Select Manufacturer 1', all_manufacturers, index=default_index1)
    with col2:
        manufacturer2 = st.selectbox('Select Manufacturer 2', all_manufacturers, index=default_index2)

    normalized = st.checkbox('Show Normalized Distribution (Percentage)')

    histnorm_val = 'percent' if normalized else None

    if manufacturer1 and manufacturer2 and manufacturer1 != manufacturer2:
        manufacturers_to_plot = [manufacturer1, manufacturer2]
        filtered_df_manufacturers = df_data[df_data['manufacturer'].isin(manufacturers_to_plot)].copy()
    else:
        st.warning("Please select two *different* manufacturers to compare price distributions.")
        filtered_df_manufacturers = pd.DataFrame()

    if filtered_df_manufacturers.empty:
        st.info("No data available for the selected manufacturers comparison.")
        fig_price = go.Figure()
    else:
        fig_price = px.histogram(
            data_frame=filtered_df_manufacturers,
            x='price',
            color='manufacturer',
            histnorm=histnorm_val,
            opacity=0.75,
            barmode='overlay',
            title=f'Price Distribution: {manufacturer1} vs {manufacturer2}'
        )
        fig_price.update_xaxes(title_text='Price')
        fig_price.update_yaxes(title_text='Count' if histnorm_val is None else 'Percentage')

    st.plotly_chart(fig_price)

def display_custom_scatter_plot(df_data):
    """Displays a custom scatter plot based on user selections."""
    st.subheader('Custom Scatter Plot')

    numerical_cols = df_data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df_data.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    all_plot_cols = numerical_cols + categorical_cols

    x_default_idx = all_plot_cols.index('odometer') if 'odometer' in all_plot_cols else (min(0, len(all_plot_cols) - 1) if len(all_plot_cols) > 0 else 0)
    y_default_idx = all_plot_cols.index('price') if 'price' in all_plot_cols else (min(1, len(all_plot_cols) - 1) if len(all_plot_cols) > 1 else 0)
    color_default_idx = all_plot_cols.index('type') if 'type' in all_plot_cols else (min(2, len(all_plot_cols) - 1) if len(all_plot_cols) > 2 else 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox('Select X-axis', all_plot_cols, index=x_default_idx)
    with col2:
        y_axis = st.selectbox('Select Y-axis', all_plot_cols, index=y_default_idx)
    with col3:
        color = st.selectbox('Color by', all_plot_cols, index=color_default_idx)

    st.subheader(f'{x_axis.replace("_", " ").title()} vs. {y_axis.replace("_", " ").title()} (Colored by {color.replace("_", " ").title()})')

    if x_axis and y_axis and color and x_axis in df_data.columns and y_axis in df_data.columns and color in df_data.columns:
        fig_scatter = px.scatter(df_data, x=x_axis, y=y_axis, color=color, 
                                 title=f'Scatter Plot: {x_axis.replace("_", " ").title()} vs. {y_axis.replace("_", " ").title()}')
        st.plotly_chart(fig_scatter)
    else:
        st.warning("Please select valid columns for the scatter plot.")


# --- Main Streamlit Application Layout ---

st.title('Vehicle Advertisement Listings - US')

# Load and clean data (cached for performance)
df_cleaned = load_and_clean_data('./vehicles_us_cleaned.csv')

st.write("---")

# --- Price Filtering with Slider ---
st.header("Explore Listings by Price")
min_price_overall, max_price_overall = int(df_cleaned['price'].min()), int(df_cleaned['price'].max())
price_range = st.slider(
    "Adjust price range",
    min_value=min_price_overall,
    max_value=max_price_overall,
    value=(min_price_overall, max_price_overall),
    help="Drag handles to select your desired min/max price."
)

df_filtered_by_price = df_cleaned[(df_cleaned['price'] >= price_range[0]) & (df_cleaned['price'] <= price_range[1])]

if df_filtered_by_price.empty:
    st.warning("No vehicle listings match the selected price range. Broaden your selection.")
else:
    st.info(f"Displaying data for **{len(df_filtered_by_price)}** vehicles within the selected price range.")
    st.write("---")

    # --- Display Plots using filtered data ---
    display_vehicle_types_histogram(df_filtered_by_price)
    st.write("---")
    display_price_distribution_histogram(df_filtered_by_price)
    st.write("---")
    display_custom_scatter_plot(df_filtered_by_price)

    st.write("---")
    # --- Show Raw Data Checkbox and Slider ---
    st.header("View Raw Data")
    if st.checkbox("Show raw data table"):
        max_rows_to_display = len(df_filtered_by_price)
        if max_rows_to_display > 0:
            n_rows = st.slider("Number of rows to display", 
                                min_value=5, 
                                max_value=max_rows_to_display, 
                                value=min(10, max_rows_to_display),
                                step=5,
                                help="Select how many rows of filtered data to see.")
            st.dataframe(df_filtered_by_price.head(n_rows))
            st.write(f"Displaying **{min(n_rows, max_rows_to_display)}** of **{max_rows_to_display}** filtered entries.")
        else:
            st.info("No data available to display based on current filters.")


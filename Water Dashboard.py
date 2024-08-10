import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_excel('data/NonRevenue Water Data(1).xlsx')
    data['Time'] = pd.to_datetime(data['Time'])
    # Drop unnamed columns and the 'Anomalous' column
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    if 'Anomalous' in data.columns:
        data = data.drop(columns=['Anomalous'])
    return data

data = load_data()

# Extract year, month, and day from 'Time' and add them as separate columns
data['Year'] = data['Time'].dt.year
data['Month'] = data['Time'].dt.month
data['Day'] = data['Time'].dt.day

# Sidebar filters
st.sidebar.header("Filter Data")

def multi_select_with_all(label, options, default=None):
    st.sidebar.write(label)
    all_selected = st.sidebar.checkbox(f"Select All {label}", value=False)
    if all_selected:
        selected = options
    else:
        selected = st.sidebar.multiselect(f"Select {label}", options, default=default)
    return selected

# Get unique values for filters
unique_ids = data['User_ID'].unique()
unique_area_codes = data['Area_Code'].unique()
unique_device_ids = data['Device_ID'].unique()
unique_is_at_home = data['Water_Usage'].unique()
unique_years = data['Year'].unique()
unique_months = data['Month'].unique()
unique_days = data['Day'].unique()

# Filter options with select all functionality
selected_id = multi_select_with_all("User ID", unique_ids)
selected_area_code = multi_select_with_all("Area Code", unique_area_codes)
selected_device_id = multi_select_with_all("Device ID", unique_device_ids)
selected_is_at_home = multi_select_with_all("Water Usage", unique_is_at_home)
selected_year = multi_select_with_all("Year", unique_years)
selected_month = multi_select_with_all("Month", unique_months)
selected_day = multi_select_with_all("Day", unique_days)

# Filter data based on selections
filtered_data = data.copy()

if len(selected_id) > 0:
    filtered_data = filtered_data[filtered_data['User_ID'].isin(selected_id)]
if len(selected_area_code) > 0:
    filtered_data = filtered_data[filtered_data['Area_Code'].isin(selected_area_code)]
if len(selected_device_id) > 0:
    filtered_data = filtered_data[filtered_data['Device_ID'].isin(selected_device_id)]
if len(selected_is_at_home) > 0:
    filtered_data = filtered_data[filtered_data['Water_Usage'].isin(selected_is_at_home)]
if len(selected_year) > 0:
    filtered_data = filtered_data[filtered_data['Year'].isin(selected_year)]
if len(selected_month) > 0:
    filtered_data = filtered_data[filtered_data['Month'].isin(selected_month)]
if len(selected_day) > 0:
    filtered_data = filtered_data[filtered_data['Day'].isin(selected_day)]

# Display filtered data
st.title("Water Consumption Analysis Dashboard")
st.write(f"Showing {filtered_data.shape[0]} rows of filtered data.")
st.dataframe(filtered_data)

# Water Distribution Visualization
st.header("Water Distribution Visualization")

water_level = 60  # Current water level (0-100)

fig = go.Figure()

# Add water tank (rectangle)
fig.add_shape(
    type="rect",
    x0=1, y0=120, x1=3, y1=220,  # Tank dimensions
    line=dict(color="blue", width=3),
    fillcolor="lightblue",
)

# Add water level (filled area)
fig.add_shape(
    type="rect",
    x0=1, y0=120, x1=3, y1=120 + water_level,  # Current water level
    line=dict(color="blue", width=0),  # No border
    fillcolor="blue",
)

# Define alert levels with colors
alert_colors = {
    25: "green",
    50: "yellow",
    75: "orange",
    100: "red"
}

# Add alert lines inside the tank
for level, color in alert_colors.items():
    fig.add_shape(
        type="line",
        x0=1, y0=120 + level, x1=3, y1=120 + level,
        line=dict(color=color, width=2, dash="dash"),
    )
    fig.add_annotation(
        x=3.2,
        y=120 + level,
        text=f"{level}% Alert",
        showarrow=False,
        font=dict(color=color)
    )

# Add pipelines (lines extending from the bottom of the tank)
fig.add_shape(
    type="line",
    x0=2, y0=120, x1=2, y1=80,
    line=dict(color="gray", width=3)
)
fig.add_shape(
    type="line",
    x0=2, y0=80, x1=1, y1=60,
    line=dict(color="gray", width=3)
)
fig.add_shape(
    type="line",
    x0=2, y0=80, x1=3, y1=60,
    line=dict(color="gray", width=3)
)

# Add text annotations for the pipelines, areas, and devices
fig.add_annotation(
    x=0.5, y=60, text="Area 1\nDevice 1", showarrow=False, font=dict(color="black")
)
fig.add_annotation(
    x=3.5, y=60, text="Area 2\nDevice 2", showarrow=False, font=dict(color="black")
)

# Add water distribution to users (lines extending to users)
for i in range(5):
    fig.add_shape(
        type="line",
        x0=1, y0=60, x1=0.5, y1=50 - i * 10,
        line=dict(color="gray", width=2)
    )
    fig.add_annotation(
        x=0.3, y=50 - i * 10, text=f"User {i + 1}", showarrow=False, font=dict(color="purple")
    )

for i in range(5, 10):
    fig.add_shape(
        type="line",
        x0=3, y0=60, x1=3.5, y1=50 - (i - 5) * 10,
        line=dict(color="gray", width=2)
    )
    fig.add_annotation(
        x=3.7, y=50 - (i - 5) * 10, text=f"User {i + 1}", showarrow=False, font=dict(color="purple")
    )

fig.update_layout(
    title="Water Tank Level with Distribution to Areas, Devices, and Users",
    xaxis=dict(visible=False),
    yaxis=dict(title="Water Level (%)", range=[0, 250], showgrid=False),
    width=600, height=600,
    template="plotly_white"
)

st.plotly_chart(fig)

# Time Series Analysis with Trend Line
st.header("Time Series Analysis with Trend Line")
monthly_trend = filtered_data.groupby(['Year', 'Month'])['Monthly_Water_Consumption'].sum().reset_index()
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=monthly_trend['Month'], y=monthly_trend['Monthly_Water_Consumption'], mode='lines+markers', name='Monthly Consumption'))
fig_trend.add_trace(go.Scatter(x=monthly_trend['Month'], y=monthly_trend['Monthly_Water_Consumption'].rolling(window=12).mean(), mode='lines', name='Trend Line', line=dict(color='red', width=2)))
fig_trend.update_layout(title='Monthly Water Consumption Trend with Trend Line',
                        xaxis_title='Month',
                        yaxis_title='Monthly Water Consumption (L)')
st.plotly_chart(fig_trend)

# Box Plot for Distribution Analysis
st.header("Box Plot for Distribution Analysis")
fig_box = px.box(filtered_data, x='Water_Usage', y='Daily_Water_Consumption', title='Box Plot of Daily Water Consumption by Usage Type')
st.plotly_chart(fig_box)

# Heatmap for Correlation Analysis
st.header("Heatmap for Correlation Analysis")
corr_matrix = filtered_data[['Hourly_Water_Consumption', 'Daily_Water_Consumption', 'Monthly_Water_Consumption', 'Yearly_Water_Consumption']].corr()
fig_heatmap = px.imshow(corr_matrix, text_auto=True, title='Correlation Heatmap')
st.plotly_chart(fig_heatmap)

# Violin Plot for Distribution Comparison
st.header("Violin Plot for Distribution Comparison")
fig_violin = px.violin(filtered_data, y='Daily_Water_Consumption', x='Water_Usage', box=True, points="all", title='Violin Plot of Daily Water Consumption by Usage Type')
st.plotly_chart(fig_violin)

# Stacked Bar Chart for Monthly Consumption Breakdown
st.header("Stacked Bar Chart for Monthly Consumption Breakdown")
monthly_breakdown = filtered_data.groupby(['Month', 'Area_Code'])['Monthly_Water_Consumption'].sum().reset_index()
fig_stacked_bar = px.bar(monthly_breakdown, x='Month', y='Monthly_Water_Consumption', color='Area_Code', title='Monthly Water Consumption Breakdown by Area Code', text='Monthly_Water_Consumption')
st.plotly_chart(fig_stacked_bar)

# Scatter Plot for User Consumption
st.header("Scatter Plot for User Consumption")
fig_scatter = px.scatter(filtered_data, x='User_ID', y='Monthly_Water_Consumption', color='Area_Code', title='Scatter Plot of Monthly Water Consumption by User ID and Area Code', size='Monthly_Water_Consumption', hover_data=['Device_ID'])
st.plotly_chart(fig_scatter)

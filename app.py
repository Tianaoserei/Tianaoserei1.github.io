import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Community Health Ranking", page_icon=":hospital:", layout="wide")

# Custom CSS for background and sidebar
st.markdown(
    """
    <style>
    .stApp {
        background-color: #87CEEB; /* Sky Blue Background */
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load consolidated data
@st.cache_data
def load_data():
    file_path = 'C:/Users/HP/Downloads/CHR_All.xlsx'
    data = pd.ExcelFile(file_path)
    consolidated_data = []
    for sheet_name in data.sheet_names:
        year = int(sheet_name.split('_')[0])
        sheet_data = data.parse(sheet_name)
        sheet_data['Year'] = year
        consolidated_data.append(sheet_data)
    return pd.concat(consolidated_data, ignore_index=True)

data = load_data()

# Sidebar
st.sidebar.title("Filters")
st.sidebar.subheader("Customize your view")

# Year selection
years = sorted(data["Year"].unique())
selected_year = st.sidebar.selectbox("Select Year to Visualize", years)

# Filter data by year
filtered_data = data[data["Year"] == selected_year]

# State selection
st.sidebar.subheader("State Filter")
states = filtered_data["state_abbreviation"].dropna().unique()
selected_states = st.sidebar.multiselect("Select States", options=states, default=states)  # Default to all states

# Name selection (unselected by default)
st.sidebar.subheader("Name Filter")
names = filtered_data["name"].dropna().unique()
selected_names = st.sidebar.multiselect("Select Name Attributes", options=names, default=[])

# Attribute selection
st.sidebar.subheader("Attributes")
available_columns = filtered_data.columns[3:]  # Adjust based on your dataset
selected_attributes = st.sidebar.multiselect("Select Attributes to Filter", available_columns, default=[])

# Apply filters
if selected_states:
    filtered_data = filtered_data[filtered_data["state_abbreviation"].isin(selected_states)]
if selected_names:
    filtered_data = filtered_data[filtered_data["name"].isin(selected_names)]

# Main layout
st.title("Community Health Ranking Dashboard")
st.markdown(f"### Visualizing health data for **{selected_year}**")

if filtered_data.empty:
    st.warning("No data available. Please adjust your filters.")
else:
    st.success(f"Data available for {len(filtered_data)} records.")

# Key Metrics Section
if not filtered_data.empty and selected_attributes:
    st.subheader("Key Metrics")
    metric_cols = st.columns(len(selected_attributes))
    for col, attribute in zip(metric_cols, selected_attributes):
        avg_value = filtered_data[attribute].mean()
        max_value = filtered_data[attribute].max()
        col.metric(label=f"Average {attribute}", value=f"{avg_value:.2f}")
        col.metric(label=f"Max {attribute}", value=f"{max_value:.2f}")

# Chart Selection Section
st.subheader("Create Your Visualization")
if not selected_attributes:
    st.warning("Please select at least one attribute to visualize.")
else:
    chart_type = st.selectbox("Choose Chart Type", ["Bar Chart", "Pie Chart", "Histogram", "Line Chart", "Scatter Plot", "Percentile Chart"])

    if chart_type == "Bar Chart":
        for attribute in selected_attributes:
            fig = px.bar(
                filtered_data,
                x="name",
                y=attribute,
                color="state_abbreviation",
                title=f"Bar Chart of {attribute}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        for attribute in selected_attributes:
            grouped_data = filtered_data.groupby("state_abbreviation")[attribute].mean().reset_index()
            fig = px.pie(
                grouped_data,
                names="state_abbreviation",
                values=attribute,
                title=f"Pie Chart of {attribute}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Histogram":
        for attribute in selected_attributes:
            fig = px.histogram(
                filtered_data,
                x=attribute,
                nbins=15,
                title=f"Histogram of {attribute}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line Chart":
        for attribute in selected_attributes:
            fig = px.line(
                filtered_data,
                x="name",
                y=attribute,
                color="state_abbreviation",
                title=f"Line Chart of {attribute}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot":
        for attribute in selected_attributes:
            fig = px.scatter(
                filtered_data,
                x="name",
                y=attribute,
                color="state_abbreviation",
                size=attribute,
                title=f"Scatter Plot of {attribute}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Percentile Chart":
        for attribute in selected_attributes:
            # Calculate percentiles
            filtered_data["percentile"] = filtered_data[attribute].rank(pct=True) * 100
            fig = px.bar(
                filtered_data,
                x="name",
                y="percentile",
                color="state_abbreviation",
                title=f"Percentile Chart for {attribute}",
                labels={"percentile": "Percentile (%)"}
            )
            st.plotly_chart(fig, use_container_width=True)

# Expandable Data View
with st.expander("View Raw Data"):
    st.dataframe(filtered_data)



import streamlit as st
import pandas as pd
import plotly.express as px

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Travel Pattern Analysis Dashboard",
    page_icon=":airplane:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"

# Function to switch pages
def switch_page(page: str):
    st.session_state.current_page = page

# Load the cleaned dataset
@st.cache_data
def load_data():
    file_path = 'Travel details dataset.csv'  # Adjust if file path changes
    data = pd.read_csv(file_path)
    data['Start date'] = pd.to_datetime(data['Start date'])
    data['End date'] = pd.to_datetime(data['End date'])
    data['Duration (days)'] = (data['End date'] - data['Start date']).dt.days
    data['Accommodation cost'] = pd.to_numeric(data['Accommodation cost'], errors='coerce').fillna(0)
    data['Transportation cost'] = pd.to_numeric(data['Transportation cost'], errors='coerce').fillna(0)
    return data

# Load data
data = load_data()

# Sidebar navigation with session state
st.sidebar.title("Navigation")
if st.sidebar.button("Overview"):
    switch_page("Overview")
if st.sidebar.button("Trends"):
    switch_page("Trends")
if st.sidebar.button("Where to Visit"):
    switch_page("Where to Visit")
if st.sidebar.button("What to Avoid"):
    switch_page("What to Avoid")

# Sidebar filters with "All" options
st.sidebar.title("Filters")

# Normalize Transportation Types
def normalize_transportation_types(data):
    transport_mapping = {
        "Airplane": "Airplane",
        "Flight": "Airplane",
        "Plane": "Airplane",
        "Car": "Car",
        "Car rental": "Car",
        "Bus": "Bus",
        "Train": "Train",
        "Ferry": "Ferry",
        "Subway": "Subway"
    }
    data["Transportation type"] = data["Transportation type"].replace(transport_mapping)
    return data

# Apply normalization
data = normalize_transportation_types(data)

# Year Range Filter
year_filter = st.sidebar.slider(
    "Year Range", 
    min_value=2023, 
    max_value=int(data['Start date'].dt.year.max()), 
    value=(2023, int(data['Start date'].dt.year.max()))
)

# Destination Filter (Dropdown with All option)
destination_options = ["All"] + list(data['Destination'].unique())
destination_filter = st.sidebar.selectbox(
    "Select a Destination", 
    options=destination_options
)

# Transportation Type Filter (Dropdown with All option)
transportation_options = ["All"] + list(data['Transportation type'].unique())
transportation_filter = st.sidebar.multiselect(
    "Select Transportation Type", 
    options=transportation_options, 
    default=["All"]
)

# Apply filters
filtered_data = data[
    (data['Start date'].dt.year >= year_filter[0]) & 
    (data['Start date'].dt.year <= year_filter[1]) & 
    ((data['Destination'] == destination_filter) | (destination_filter == "All")) & 
    ((data['Transportation type'].isin(transportation_filter)) | ("All" in transportation_filter))
]

# Pages
if st.session_state.current_page == "Overview":
    # Add a title for the final project
    st.title("Exploring Travel Patterns: Unveiling Trends, Costs, and Destinations")
    st.write("Travel Analytics involve the study of travel trends, patterns, and behaviors to better understand the dynamics of the industry. By analyzing data on destinations, traveler preferences, costs, and transportation choices, tourism analytics provides valuable insights for travelers, businesses, and policymakers.")
    
    # Add key metrics and visualizations
    st.write("### Key Metrics")
    # Compute the most traveled destination and most used mode of transportation
    most_traveled_destination = filtered_data['Destination'].mode()[0] if not filtered_data.empty else "No Data"
    most_used_transportation = filtered_data['Transportation type'].mode()[0] if not filtered_data.empty else "No Data"

    # Display the metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Most Traveled Destination", most_traveled_destination)
    col2.metric("Most Used Transportation", most_used_transportation)
    col3.metric("Avg. Accommodation Cost", f"${filtered_data['Accommodation cost'].mean():.2f}" if not filtered_data.empty else "No Data")
    col4.metric("Avg. Transportation Cost", f"${filtered_data['Transportation cost'].mean():.2f}" if not filtered_data.empty else "No Data")
    
    # Add a subheading for "What is the Purpose?"
    st.subheader("What is the Purpose?")
    st.write("""
        The purpose of this dashboard is to provide key insights into  travel trends and patterns. 
        It helps users analyze destinations, costs, and traveler behaviors to make informed decisions 
        about their next trips or understand the tourism industry better.
    """)

    # Add a subheading for "How Does This Work?"
    st.subheader("How Does This Work?")
    st.write("""
        This dashboard uses a dataset of travel details to present key metrics, visualizations, 
        and trends. Users can interact with filters to customize their view by year, destination, 
        traveler nationality, and other factors. Insights are presented across multiple pages, 
        each focusing on different aspects of travel analytics.
    """)
    

elif st.session_state.current_page == "Trends":
    st.title("Trends")
    st.write("### Monthly Travel Trends")

    # Prepare monthly trends data
    filtered_data['Month'] = filtered_data['Start date'].dt.to_period('M')
    monthly_trends = filtered_data.groupby('Month').size().reset_index(name='Counts')

    # Convert 'Month' to string for Plotly compatibility
    monthly_trends['Month'] = monthly_trends['Month'].astype(str)

    # Create a labeled line chart using Plotly Express
    fig = px.line(
        monthly_trends,
        x='Month',
        y='Counts',
        labels={'Month': 'Month', 'Counts': 'Number of Trips'},
        title="Monthly Travel Trends",
        color_discrete_sequence=["#FF6347"] 
    )

    # Update layout for axis labels
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Trips",
        title_x=0.5  # Center the title
    )

    # Display the chart
    st.plotly_chart(fig)

    
    st.write("### Transportation Trends")
    transport_trends = filtered_data['Transportation type'].value_counts().reset_index()
    transport_trends.columns = ["Transportation Type", "Count"]
    fig = px.bar(
        transport_trends,
        x="Transportation Type",
        y="Count",
        labels={"Transportation Type": "Mode of Transport", "Count": "Usage Count"},
        title="Transportation Usage Trends",
        color="Transportation Type",
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

elif st.session_state.current_page == "Where to Visit":
    st.title("Where to Visit")
    st.write("### Top Affordable Destinations")

    # Ensure numeric conversion for costs
    filtered_data['Accommodation cost'] = pd.to_numeric(filtered_data['Accommodation cost'], errors='coerce').fillna(0)
    filtered_data['Transportation cost'] = pd.to_numeric(filtered_data['Transportation cost'], errors='coerce').fillna(0)

    # Calculate Total Cost
    filtered_data['Total Cost'] = filtered_data['Accommodation cost'] + filtered_data['Transportation cost']


    # Group by Destination and calculate the average total cost (only include rows with Total Cost > 0)
    affordable_destinations = (
        filtered_data[filtered_data['Total Cost'] > 0]  # Exclude rows with zero or missing Total Cost
        .groupby('Destination')['Total Cost']
        .mean()
        .sort_values()
        .reset_index()
    )

    # Ensure the grouped data has valid rows before plotting
    if affordable_destinations.empty:
        st.warning("No valid data available for affordable destinations. Please adjust the filters.")
    else:
        # Plot the chart
        fig = px.bar(
            affordable_destinations.head(10),  # Show top 10 destinations
            x='Destination',
            y='Total Cost',
            labels={'Destination': 'Destination', 'Total Cost': 'Average Cost ($)'},
            title="Top 10 Most Affordable Destinations",
            color_discrete_sequence=["#4CAF50"]  # Add a color palette
        )
        fig.update_layout(xaxis_title="Destination", yaxis_title="Average Cost ($)")
        st.plotly_chart(fig)

    # Filter out rows with zero values for Total Cost or Duration (days)
    filtered_non_zero_data = filtered_data[
        (filtered_data['Total Cost'] > 0) & 
    (filtered_data['Duration (days)'] > 0)
    ]
    # Cost vs Duration 
    st.write("### Cost vs Duration")
    fig = px.scatter(
        filtered_non_zero_data,
        x="Duration (days)",
        y="Total Cost",
        color="Destination",
        hover_data={'Total Cost': ':.2f', 'Traveler nationality': True},
        title="Cost vs Duration",
        labels={"Duration (days)": "Trip Duration (Days)", "Total Cost": "Total Travel Cost ($)"}
    )
    st.plotly_chart(fig)


    # Map Visualization for Travel Costs
    st.write("### Travel Costs by Country")
    fig = px.choropleth(
        filtered_data,
        locations="Destination",  # Match destinations to geographic locations
        locationmode="country names",
        color="Total Cost",
        hover_name="Destination",
        title="Travel Costs by Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={"Total Cost": "Total Cost ($)"}
    )
    fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Total Cost: $%{z:,.2f}')
    st.plotly_chart(fig)

# In the "What to Avoid" section:
elif st.session_state.current_page == "What to Avoid":
    st.title("What to Avoid")
    
    # Least Popular Destinations
    st.write("### Least Popular Destinations")
    least_visited = filtered_data['Destination'].value_counts().tail(10).reset_index()
    least_visited.columns = ["Destination", "Count"]
    fig = px.bar(
        least_visited,
        x="Destination",
        y="Count",
        labels={"Destination": "Destination", "Count": "Visits"},
        title="Least Popular Destinations",
        color="Destination",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

    # High-Cost Transportation
    st.write("### High-Cost Transportation")
    high_cost_transport = (
        filtered_data.groupby('Transportation type')['Transportation cost']
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.bar(
        high_cost_transport,
        x="Transportation type",
        y="Transportation cost",
        labels={"Transportation type": "Transportation Type", "Transportation cost": "Average Cost ($)"},
        title="High-Cost Transportation",
        color="Transportation type",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

# Footer
st.sidebar.markdown("---")
st.sidebar.write("App created using Streamlit")




# Import pandas to read and work with the CSV dataset
import pandas as pd

# Import Dash components for building the web application
from dash import Dash, dcc, html, Input, Output

# Import Plotly Express to create interactive charts
import plotly.express as px


# Read the cleaned crime dataset
df = pd.read_csv("cleaned_crime_data.csv")


# Remove rows with missing important values to avoid chart errors
df = df.dropna(subset=["AREA_NAME", "Year_Occ", "Crm_Cd_Desc", "Vict_Age"])


# Create the Dash application
app = Dash(__name__)


# Required for online deployment on Render / PythonAnywhere
server = app.server


# Create the layout/design of the dashboard page
app.layout = html.Div(
    style={
        "backgroundColor": "#D9D9D9",
        "padding": "25px",
        "fontFamily": "Arial"
    },
    children=[

        # Main dashboard title
        html.H1(
            "LA Crime Interactive Dashboard",
            style={
                "textAlign": "center",
                "color": "#2B2B2B"
            }
        ),

        # Dropdown label
        html.Label(
            "Select Area:",
            style={
                "fontWeight": "bold",
                "color": "#333333"
            }
        ),

        # Dropdown used to filter all charts by area
        dcc.Dropdown(
            options=[
                {"label": area, "value": area}
                for area in sorted(df["AREA_NAME"].unique())
            ],
            value=sorted(df["AREA_NAME"].unique())[0],
            id="area-dropdown",
            clearable=False,
            style={
                "width": "50%",
                "marginBottom": "25px"
            }
        ),

        # First interactive chart: yearly crime trend
        dcc.Graph(id="year-chart"),

        # Second interactive chart: top crime types
        dcc.Graph(id="crime-chart"),

        # Third interactive chart: victim age distribution
        dcc.Graph(id="age-chart"),

        # Fourth interactive chart: animated chart by year
        dcc.Graph(id="animated-chart")
    ]
)


# Callback connects the dropdown to all charts
# When the selected area changes, all four charts update automatically
@app.callback(
    [
        Output("year-chart", "figure"),
        Output("crime-chart", "figure"),
        Output("age-chart", "figure"),
        Output("animated-chart", "figure")
    ],
    [
        Input("area-dropdown", "value")
    ]
)
def update_charts(selected_area):

    # Filter dataset based on selected area from dropdown
    filtered = df[df["AREA_NAME"] == selected_area]

    # -------------------------------
    # Chart 1: Line chart
    # Shows number of crimes by year
    # -------------------------------
    yearly = (
        filtered
        .groupby("Year_Occ")
        .size()
        .reset_index(name="Crime Count")
    )

    fig1 = px.line(
        yearly,
        x="Year_Occ",
        y="Crime Count",
        markers=True,
        title=f"Yearly Crime Trends in {selected_area}",
        hover_data=["Crime Count"]
    )

    # -------------------------------
    # Chart 2: Horizontal bar chart
    # Shows top 10 crime types
    # -------------------------------
    top_crimes = (
        filtered["Crm_Cd_Desc"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_crimes.columns = ["Crime Type", "Crime Count"]

    fig2 = px.bar(
        top_crimes,
        x="Crime Count",
        y="Crime Type",
        orientation="h",
        title=f"Top 10 Crime Types in {selected_area}",
        hover_data=["Crime Count"]
    )

    # -------------------------------
    # Chart 3: Histogram
    # Shows victim age distribution
    # -------------------------------
    fig3 = px.histogram(
        filtered,
        x="Vict_Age",
        nbins=30,
        title=f"Victim Age Distribution in {selected_area}",
        labels={"Vict_Age": "Victim Age"},
        hover_data=["Vict_Age"]
    )

    # -------------------------------
    # Chart 4: Animated bar chart
    # Shows crime type changes over years
    # This satisfies animated Plotly figure requirement
    # -------------------------------
    animated_data = (
        filtered
        .groupby(["Year_Occ", "Crm_Cd_Desc"])
        .size()
        .reset_index(name="Crime Count")
    )

    # Keep only top crime types to avoid overcrowding
    top_animated_crimes = (
        filtered["Crm_Cd_Desc"]
        .value_counts()
        .head(5)
        .index
    )

    animated_data = animated_data[
        animated_data["Crm_Cd_Desc"].isin(top_animated_crimes)
    ]

    fig4 = px.bar(
        animated_data,
        x="Crm_Cd_Desc",
        y="Crime Count",
        color="Crm_Cd_Desc",
        animation_frame="Year_Occ",
        title=f"Animated Crime Type Changes Over Time in {selected_area}",
        labels={
            "Crm_Cd_Desc": "Crime Type",
            "Crime Count": "Crime Count",
            "Year_Occ": "Year"
        },
        hover_data=["Crime Count"]
    )

    # Improve chart layout for readability
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(
            plot_bgcolor="#F2F2F2",
            paper_bgcolor="#F2F2F2",
            font=dict(color="#2B2B2B"),
            title_font=dict(size=20),
            margin=dict(l=40, r=40, t=60, b=40)
        )

    # Return all updated charts to the dashboard
    return fig1, fig2, fig3, fig4


# Run the Dash app locally
if __name__ == "__main__":
    app.run(debug=True)
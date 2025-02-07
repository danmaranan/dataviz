import pandas as pd
import dash
import plotly.express as px
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Load dataset
file_path = "Merged_IPEDS_Data.xlsx"  # Ensure this file is in the same folder as this script
df = pd.read_excel(file_path)

# State name to abbreviation mapping
state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

# Select relevant columns & make a copy to avoid warnings
leaderboard_data = df[["Institution Name", "State",
                       "Graduation rate - Bachelor degree within 6 years  total (DRVGR2023)",
                       "Graduation rate - Bachelor degree within 6 years  men (DRVGR2023)",
                       "Graduation rate - Bachelor degree within 6 years  women (DRVGR2023)",
                       "Graduation rate - Bachelor degree within 6 years  Black  non-Hispanic (DRVGR2023)",
                       "Graduation rate - Bachelor degree within 6 years  Hispanic (DRVGR2023)",
                       "Graduation rate - Bachelor degree within 6 years  White  non-Hispanic (DRVGR2023)"]].copy()

# Rename columns for clarity
leaderboard_data.columns = ["Institution", "State", "Overall Graduation Rate",
                            "Men Graduation Rate", "Women Graduation Rate",
                            "Black Graduation Rate", "Hispanic Graduation Rate", "White Graduation Rate"]

# Compute graduation gaps
leaderboard_data["Gender Gap"] = leaderboard_data["Women Graduation Rate"] - leaderboard_data["Men Graduation Rate"]
leaderboard_data["Black-White Gap"] = leaderboard_data["White Graduation Rate"] - leaderboard_data["Black Graduation Rate"]
leaderboard_data["Hispanic-White Gap"] = leaderboard_data["White Graduation Rate"] - leaderboard_data["Hispanic Graduation Rate"]

# Add state abbreviations
leaderboard_data["State Abbreviation"] = leaderboard_data["State"].map(state_abbreviations)

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("🏆 University Graduation Rate Leaderboard", style={"textAlign": "center", "color": "#004c99"}),
        html.H3("📊 Compare graduation rates & equity gaps across universities", 
                style={"textAlign": "center", "color": "#333", "fontSize": "18px"}),
    ], style={"padding": "20px"}),

    html.Div([
        html.Label("🔎 Search for an Institution:", style={"fontSize": "16px", "fontWeight": "bold", "color": "#004c99"}),
        dcc.Input(id="search-box", type="text", placeholder="Type a university name...",
                  style={"width": "100%", "padding": "10px", "borderRadius": "8px"})
    ], style={"width": "50%", "margin": "auto", "paddingBottom": "20px"}),

    html.Div([
        html.Label("🌍 Filter by State:", style={"fontSize": "16px", "fontWeight": "bold", "color": "#004c99"}),
        dcc.Dropdown(id="state-filter",
                     options=[{"label": state, "value": state} for state in sorted(leaderboard_data["State"].dropna().astype(str).unique())],
                     value=None, placeholder="Select a state...", multi=False,
                     style={"width": "50%", "margin": "auto", "borderRadius": "8px", "padding": "5px"})
    ], style={"paddingBottom": "20px"}),

    html.Div([
        html.Label("📌 Sort by:", style={"fontSize": "16px", "fontWeight": "bold", "color": "#004c99"}),
        dcc.Dropdown(id="sort-selector",
                     options=[{"label": col, "value": col} for col in [
                         "Overall Graduation Rate", "Gender Gap", "Black-White Gap", "Hispanic-White Gap"]],
                     value="Overall Graduation Rate", multi=False,
                     style={"width": "50%", "margin": "auto", "borderRadius": "8px", "padding": "5px"})
    ], style={"paddingBottom": "20px"}),

    dash_table.DataTable(id="leaderboard-table",
                         columns=[{"name": col, "id": col} for col in leaderboard_data.columns],
                         style_table={"overflowX": "auto", "width": "90%", "margin": "auto"},
                         style_header={"backgroundColor": "#004c99", "color": "white", "fontWeight": "bold", "textAlign": "center"},
                         style_cell={"textAlign": "center", "padding": "10px", "fontSize": "14px"}),

    html.H3("📊 Graduation Rate Gaps by State", style={"textAlign": "center", "color": "#004c99", "paddingTop": "20px"}),

    dcc.Graph(id="state-boxplot")
], style={"maxWidth": "1200px", "margin": "auto", "backgroundColor": "#f8f9fa", "padding": "20px", "borderRadius": "10px"})


@app.callback(
    Output("leaderboard-table", "data"),
    Output("state-boxplot", "figure"),
    Input("sort-selector", "value"),
    Input("search-box", "value"),
    Input("state-filter", "value")
)
def update_leaderboard(sort_by, search_query, selected_state):
    df_filtered = leaderboard_data.copy()

    if selected_state:
        df_filtered = df_filtered[df_filtered["State"] == selected_state]

    if search_query:
        df_filtered = df_filtered[df_filtered["Institution"].str.contains(search_query, case=False, na=False)]

    df_filtered = df_filtered.sort_values(by=sort_by, ascending=(sort_by != "Overall Graduation Rate"))

    # Generate box plot
    fig = px.box(df_filtered, x="State", y=sort_by, points="all",
                 title="Distribution of Graduation Gaps by State",
                 labels={"State": "State", sort_by: "Graduation Rate Gap"})

    return df_filtered.to_dict("records"), fig


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8080)

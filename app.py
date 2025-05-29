import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
df = pd.read_csv("earthquakes_last30d.csv")
df['time'] = pd.to_datetime(df['time'])

# Classify region based on lat/lon
def classify_region(row):
    lat, lon = row['latitude'], row['longitude']
    if 35 <= lat <= 70 and -25 <= lon <= 60:
        return 'Europe'
    elif 7 <= lat <= 72 and -170 <= lon <= -50:
        return 'North America'
    elif -60 <= lat <= 15 and -90 <= lon <= -30:
        return 'South America'
    elif -35 <= lat <= 37 and -20 <= lon <= 55:
        return 'Africa'
    elif 5 <= lat <= 80 and 60 <= lon <= 180:
        return 'Asia'
    elif -50 <= lat <= 10 and 110 <= lon <= 180:
        return 'Oceania'
    else:
        return 'Sea'

df['region'] = df.apply(classify_region, axis=1)

# Filter data by date
def filter_data(days):
    today = pd.Timestamp("2025-05-29", tz="UTC")
    return df[df['time'] >= (today - pd.Timedelta(days=days))]

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("🌍 Earthquake Dashboard", style={"textAlign": "center"}),

    dcc.RadioItems(
        id='date-filter',
        options=[
            {'label': 'Today', 'value': 0},
            {'label': 'Last 7 Days', 'value': 7},
            {'label': 'Last 14 Days', 'value': 14},
            {'label': 'Last 30 Days', 'value': 30},
        ],
        value=30,
        inline=True
    ),

    html.Div(id='summary', style={"marginTop": "20px"}),

    dcc.Dropdown(
        id='region-filter',
        options=[
            {'label': region, 'value': region} for region in
            ['All', 'Africa', 'Europe', 'North America', 'South America', 'Asia', 'Oceania', 'Sea']
        ],
        value='All',
        placeholder="Filter by region",
        clearable=False,
        style={"marginTop": "20px"}
    ),

    dcc.Graph(id='mag-line'),
    dcc.Graph(id='depth-line'),
    dcc.Graph(id='map'),
    dcc.Graph(id='hist')
])

@app.callback(
    Output('mag-line', 'figure'),
    Output('depth-line', 'figure'),
    Output('map', 'figure'),
    Output('hist', 'figure'),
    Output('summary', 'children'),
    Input('date-filter', 'value'),
    Input('region-filter', 'value')
)
def update_dashboard(days, selected_place):
    dff = filter_data(days)
    if selected_place and selected_place != 'All':
        dff = dff[dff['region'] == selected_place]

    mag_fig = px.line(dff, x='time', y='mag', title='Magnitude Over Time')
    depth_fig = px.line(dff, x='time', y='depth', title='Depth Over Time')

    map_fig = px.scatter_geo(
        dff,
        lat='latitude',
        lon='longitude',
        hover_name='place',
        size='mag',
        title='Earthquake Locations',
        projection='natural earth'
    )

    hist_fig = px.histogram(dff, x='mag', nbins=20, title='Magnitude Distribution')

    total = len(dff)
    max_mag = dff['mag'].max()
    most_common_place = dff['place'].mode()[0] if not dff['place'].mode().empty else 'N/A'

    summary = html.Div([
        html.H4(f"Total Earthquakes: {total}"),
        html.H4(f"Max Magnitude: {max_mag:.2f}"),
        html.H4(f"Most Frequent Location: {most_common_place}")
    ])

    return mag_fig, depth_fig, map_fig, hist_fig, summary

# Run the server for Render (or locally)
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)

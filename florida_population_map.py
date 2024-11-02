import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

# Load GeoJSON data for Florida
geojson_url = 'data/USA_Counties_(Generalized).geojson'
usa_geojson = gpd.read_file(geojson_url)
florida_geojson = usa_geojson[usa_geojson['STATE_FIPS'] == '12']

# Convert the GeoDataFrame to a GeoJSON dictionary
florida_geojson = florida_geojson.__geo_interface__

# Load the disability data from the Excel file
file_path = 'disable_data.xlsx'
df_disability = pd.read_excel(file_path)

# Clean the data: Skip header rows and rename columns
df_disability = df_disability.iloc[3:]  # Skip the first three rows
df_disability = df_disability.rename(columns={
    'Developmentally Disabled Clients': 'County',
    'Unnamed: 1': '2023 Count'
})
df_disability = df_disability[['County', '2023 Count']]
df_disability['2023 Count'] = pd.to_numeric(df_disability['2023 Count'], errors='coerce')
df_disability = df_disability.dropna()  # Remove any rows with missing values
df_disability['County'] = df_disability['County'].str.strip()

# Population data
data = {
    'County': [
        'Miami-Dade', 'Broward', 'Palm Beach', 'Hillsborough', 'Orange', 'Duval',
        'Pinellas', 'Lee', 'Polk', 'Brevard', 'Pasco', 'Volusia', 'Seminole', 
        'Sarasota', 'Manatee', 'Osceola', 'Lake', 'Marion', 'Collier', 'St. Lucie',
        'Escambia', 'St. Johns', 'Leon', 'Alachua', 'Clay', 'Okaloosa', 
        'Hernando', 'Charlotte', 'Santa Rosa', 'Bay', 'Indian River', 'Citrus', 
        'Martin', 'Sumter', 'Flagler', 'Highlands', 'Nassau', 'Walton', 'Monroe', 
        'Putnam', 'Columbia', 'Jackson', 'Levy', 'Suwannee', 'Hendry', 
        'Gadsden', 'Okeechobee', 'Wakulla', 'DeSoto', 'Baker', 'Bradford', 
        'Hardee', 'Washington', 'Taylor', 'Holmes', 'Gilchrist', 'Madison', 
        'Dixie', 'Gulf', 'Jefferson', 'Union', 'Hamilton', 'Calhoun', 
        'Glades', 'Franklin', 'Lafayette', 'Liberty'
    ],
    'Population': [
        2686867, 1962531, 1533801, 1535564, 1471416, 1030822, 961596, 834573,
        818330, 643979, 632996, 590357, 484271, 469013, 441095, 437784, 424462,
        409959, 404310, 373586, 329996, 320110, 296913, 285994, 238244, 220464,
        218679, 209686, 208125, 196328, 172323, 170884, 164643, 158363, 136120,
        109579, 105176, 89304, 79610, 77174, 74256, 48989, 47837, 46855, 45275,
        44273, 42481, 37729, 36638, 28950, 28420, 25869, 25799, 21851, 20235,
        20172, 18808, 17810, 16087, 15831, 15550, 13748, 13475, 13109, 12696,
        8379, 7799
    ]
}
df_population = pd.DataFrame(data)

# Create the figure with two choropleth layers
fig = go.Figure()

# Add Population layer
fig.add_trace(go.Choropleth(
    geojson=florida_geojson,
    locations=df_population['County'],
    z=df_population['Population'],
    featureidkey="properties.NAME",
    colorscale="Viridis",
    colorbar_title="Population",
    name="Population",
    visible=True  # Initially visible
))

# Add Disabled Population layer
fig.add_trace(go.Choropleth(
    geojson=florida_geojson,
    locations=df_disability['County'],
    z=df_disability['2023 Count'],
    featureidkey="properties.NAME",
    colorscale="Reds",
    colorbar_title="Disabled Population",
    name="Disabled Population",
    visible=False  # Initially hidden
))

# Add dropdown menu to switch between layers
fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(
                    args=[{"visible": [True, False]}],
                    label="Population",
                    method="update"
                ),
                dict(
                    args=[{"visible": [False, True]}],
                    label="Disabled Population",
                    method="update"
                )
            ],
            direction="down",
            showactive=True,
            x=0.9,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )
    ]
)

# Update layout for the map
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(title="Florida Population and Disabled Population Map")
fig.show()

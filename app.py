import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output, callback, no_update
import matplotlib.pyplot as plt
import os
from dash import Dash, html

# Load your dataframe
data_path = 'embedding_dash.csv'
df = pd.read_csv(data_path)

# Optional: map numeric tumor types to string labels for readability
tumor_type_labels = {0: "Adenocarcinoma", 1: "Squamous cells"}
df["tumor_type_str"] = df["tumor_type"].map(tumor_type_labels)

# Get unique tumor type labels
unique_tumor_types = df["tumor_type_str"].unique()

# Use matplotlib colormap (tab10 is good for ≤10 categories)
cmap = plt.get_cmap("tab10")

# Map each tumor type to a distinct RGB color
tumor_type_to_color = {
    tumor_type: f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"
    for tumor_type, (r, g, b) in zip(unique_tumor_types, cmap.colors)
}

# Add color column
df["tumor_color_str"] = df["tumor_type_str"].map(tumor_type_to_color)

# Create Plotly figure with separate trace for each tumor type
fig = go.Figure()

for tumor_type in unique_tumor_types:
    sub_df = df[df["tumor_type_str"] == tumor_type]
    fig.add_trace(go.Scatter(
        x=sub_df["x"],
        y=sub_df["y"],
        mode="markers",
        name=tumor_type,
        marker=dict(
            size=10,
            color=tumor_type_to_color[tumor_type],
            opacity=0.8,
        )
    ))

fig.update_traces(hoverinfo="none", hovertemplate=None)
fig.update_layout(
    xaxis=dict(title='X', scaleanchor='y'),  # Ensure square plot
    yaxis=dict(title='Y'),
    plot_bgcolor='rgba(255,255,255,0.1)',
    legend=dict(title='Tumor Type'),
    width=800,   # Increased figure width
    height=800   # Increased figure height
)

# Initialize Dash app
app = Dash()

app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig, clear_on_unhover=True),
    dcc.Tooltip(id="graph-tooltip"),
])

# ... (rest of your code unchanged)

@callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("graph", "clickData"),
)
def display_click(clickData):
    if clickData is None:
        return False, no_update, no_update

    pt = clickData["points"][0]
    bbox = pt["bbox"]
    idx = pt["pointIndex"]
    curve_number = pt["curveNumber"]

    tumor_type = unique_tumor_types[curve_number]
    sub_df = df[df["tumor_type_str"] == tumor_type].reset_index()
    row = sub_df.iloc[idx]

    image_src = f"/assets/images/{row['image_filename']}"
    patient_id = row['patient_ids']
    tumor_type_label = row['tumor_type_str']

    children = [
        html.Div([
            html.Img(
                src=image_src,
                style={
                    "width": "700px",  # Bigger image width
                    "height": "auto",
                    "display": "block",
                    "margin": "0 auto"
                }
            ),
            html.H4(f"Patient ID: {patient_id}", style={"color": "darkgreen", "textAlign": "center"}),
            html.P(f"Tumor Type: {tumor_type_label}", style={"textAlign": "center"}),
        ], style={
            'width': '720px',  # Adjust container width accordingly
            'white-space': 'normal',
            'padding': '10px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
            'backgroundColor': 'white',
            'borderRadius': '8px'
        })
    ]

    return True, bbox, children


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("TumorDash works!")
])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
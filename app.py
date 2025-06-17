import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import psycopg2
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Подключение к БД
conn = psycopg2.connect(
    dbname="consulting",
    user="admin",
    password="pass123",
    host="localhost"
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Загрузка данных
def load_data():
    query = """
    SELECT 
        date_trunc('day', created_at) as day,
        status,
        COUNT(*) as requests
    FROM requests
    GROUP BY 1, 2
    """
    return pd.read_sql(query, conn)

df = load_data()

# Макет дашборда
app.layout = dbc.Container([
    dbc.Row([
        html.H1("Аналитика консалтинговых заявок", className="text-center my-4")
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='status-filter',
                options=[{'label': s, 'value': s} for s in df['status'].unique()],
                multi=True,
                value=['new', 'paid']
            )
        ], width=6),
        
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=df['day'].min(),
                max_date_allowed=df['day'].max()
            )
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='requests-trend')
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='stats-cards')
        ], width=12)
    ])
])

# Callback для графиков
@app.callback(
    Output('requests-trend', 'figure'),
    [Input('status-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graph(statuses, start_date, end_date):
    filtered = df[df['status'].isin(statuses)]
    if start_date and end_date:
        filtered = filtered[(filtered['day'] >= start_date) & (filtered['day'] <= end_date)]
    
    fig = px.line(
        filtered, 
        x='day', 
        y='requests', 
        color='status',
        title='Динамика заявок'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

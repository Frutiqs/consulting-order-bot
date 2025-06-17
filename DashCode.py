
import dash
from dash import dcc, html, Input, Output, State, dash_table, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import base64
import io

# Инициализация приложения
app = dash.Dash(__name__, exter-nal_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Для развертывания

# Глобальная переменная для хранения данных
global_df = None

# Макет приложения
app.layout = dbc.Container([
   html.H1("Дашборд анализа посещений сайта", className="text-center my-4"),

   dcc.Upload(
       id='upload-data',
       children=html.Div(['Перетащите или ', html.A('выберите файл')]),
       style={
           'width': '100%',
           'height': '60px',
           'lineHeight': '60px',
           'borderWidth': '1px',
           'borderStyle': 'dashed',
           'borderRadius': '5px',
           'textAlign': 'center',
           'margin': '10px'
       },
       multiple=False
   ),

   html.Div(id='output-data-upload', style={'display': 'none'}),

   dbc.Row([
       dbc.Col([
           html.Label("Выберите период анализа:"),
           dcc.Dropdown(
               id='dropdown-period',
               options=[
                   {'label': 'По дням', 'value': 'D'},
                   {'label': 'По неделям', 'value': 'W'},
                   {'label': 'По месяцам', 'value': 'ME'}
               ],
               value='ME'
           )
       ], width=4),
       dbc.Col([
           html.Label("Фильтр по странице:"),
           dcc.Dropdown(id='dropdown-page', multi=True)
       ], width=8)
   ]),

   dbc.Row([
       dbc.Col(dcc.Graph(id='time-on-site-line-chart'), width=6),
       dbc.Col(dcc.Graph(id='views-pie-chart'), width=6)
   ]),

   dbc.Row([
       dbc.Col(dcc.Graph(id='visitors-histogram'), width=6),
       dbc.Col(dcc.Graph(id='scatter-visits-vs-views'), width=6)
   ]),

   dbc.Row([
       dbc.Col(html.Div(id='indicators'), width=12)
   ]),

   dbc.Row([
       dbc.Col([
           html.H4("Таблица данных за выбранный период"),
           dash_table.DataTable(id='datatable')
       ])
   ])

], fluid=True)

def parse_contents(contents, filename):
   """Парсинг содержимого загруженного файла"""
   content_type, content_string = contents.split(',')


   decoded = base64.b64decode(content_string)
   try:
       if 'csv' in filename:
           df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=None, engine='python')
       elif 'xls' in filename or 'xlsx' in filename:
           df = pd.read_excel(io.BytesIO(decoded))
       else:
           return None

       # Переименовываем колонки, если нужно
       df.rename(columns={'Время на сайте(мин)': 'Время на сайте (мин)'}, inplace=True, errors='ignore')

       # Преобразуем дату
       if 'Дата' in df.columns:
           df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')

       return df
   except Exception as e:
       print(f"Ошибка парсинга файла: {e}")
       return None

@app.callback(
   [Output('output-data-upload', 'children'),
    Output('dropdown-page', 'options'),
    Output('dropdown-page', 'value')],
   [Input('upload-data', 'contents')],
   [State('upload-data', 'filename')]
)
def load_data(contents, filename):
   global global_df

   if contents is None:
       return no_update, no_update, no_update

   df = parse_contents(contents, filename)
   if df is None:
       return "Ошибка загрузки файла", [], []

   global_df = df

   pages = [{'label': page, 'value': page} for page in df['Страница'].unique()]
   selected_pages = df['Страница'].unique().tolist()

   return "Загружено", pages, selected_pages

@app.callback(
   [Output('time-on-site-line-chart', 'figure'),
    Output('views-pie-chart', 'figure'),
    Output('visitors-histogram', 'figure'),
    Output('scatter-visits-vs-views', 'figure'),
    Output('datatable', 'data'),
    Output('datatable', 'columns'),
    Output('indicators', 'children')],
   [Input('output-data-upload', 'children'),
    Input('dropdown-period', 'value'),
    Input('dropdown-page', 'value')]
)
def update_charts(_, period, selected_pages):

   global global_df

   if global_df is None or not selected_pages:
       return {}, {}, {}, {}, [], [], []

   if period is None:
       period = 'ME'  # или 'D', если нужно

   df = global_df[global_df['Страница'].isin(selected_pages)]

   # Агрегация по периоду
   dfg = df.resample(period, on='Дата').agg({
       'Посетители': 'sum',
       'Просмотры': 'sum',
       'Время на сайте (мин)': 'mean'
   }).reset_index()

   # Линейный график
   line_fig = px.line(dfg, x='Дата', y='Время на сайте (мин)', title='Среднее время на сайте')

   # Круговая диаграмма
   pie_fig = px.pie(df.groupby('Страница')['Просмотры'].sum().reset_index(),
                    names='Страница', values='Просмотры', title='Распределение просмотров')

   # Гистограмма
   hist_fig = px.histogram(df, x='Посетители', title='Распределение посе-тителей')

   # Scatter plot
   scatter_fig = px.scatter(df, x='Посетители', y='Просмотры', color='Страница',
                            title='Посетители vs Просмотры')

   # Таблица
   table_data = df.to_dict('records')
   columns = [{"name": i, "id": i} for i in df.columns]

   # Индикаторы
   total_visitors = df['Посетители'].sum()
   avg_views = df['Просмотры'].mean()
   avg_time = df['Время на сайте (мин)'].mean()

   indicators = html.Div([
       dbc.Alert(f"Общее число посетителей: {total_visitors}", col-or="primary"),
       dbc.Alert(f"Среднее число просмотров: {avg_views:.2f}", col-or="success"),
       dbc.Alert(f"Среднее время на сайте: {avg_time:.2f} мин", col-or="info")
   ])

   return line_fig, pie_fig, hist_fig, scatter_fig, table_data, columns, indica-tors

if __name__ == '__main__':
   app.run(debug=True)

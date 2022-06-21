import time
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
import base64

FILENAME_BLANC = "ch_4-7_0-7KBE_1500.xlsx"
PARAMETER = "Z / Ohm"

BAKTERIA_MESSUREMENTS = ["0", "3", "5", "7"]
BAKTERIA_MESSUREMENTS_INT = [0, 3, 5, 7]
LIST_CHANNELS = ["CH 4", "CH 5", "CH 6", "CH 7"]
LIST_CHANNELS_NAMES = ["CH 4 [G1]", "CH 5 [G2]", "CH 6 [G6]", "CH 7 [G7]"]

df_table = pd.DataFrame(columns=['Sensor', 'Bestimmtheitsmaß', 'Slope', 'Intercept'])

image_filename = 'domatec_logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


def get_freq_df():
    FREQUENZYS = pd.read_excel(get_bak_xls(), header=[1])
    return FREQUENZYS


def get_bak_xls():
    FILENAME_BAKTERIA = "ch_4-7_0-7KBE.xlsx"
    bakteria_xls = pd.ExcelFile(FILENAME_BAKTERIA)
    return bakteria_xls


# Text field
def drawImg():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Col([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                      style={'height': '100%', 'width': '100%'})]),
                ],
                )
            ])
        ),
    ])


def drawText(text):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Col([html.H1(f'{text}')]),
                ],
                )
            ])
        ),
    ])


# Build App
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    drawText('Erstellen einer Kalibrierungskurve mit Trendline (Ordinary Least Squares)')
                ], width=10),
                dbc.Col([
                    drawImg()
                ], width=2),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.H2("Frequenz: "),
                                dcc.Dropdown(id='dropdown',
                                             options=[
                                                 {'label': i, 'value': i} for i in get_freq_df()["freq / Hz"].unique()
                                             ],
                                             multi=False, value=62505.5), ]))])
                ], width=8),
                dbc.Col([
                    drawText('Trendlinenenparameter')
                ], width=4),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([dcc.Graph(id='graph',
                                                    figure={},
                                                    config={
                                                    }
                                                    )]))])
                ], width=8),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i}
                                         for i in df_table.columns],
                                style_header=dict(backgroundColor="#25292e"),
                                style_data=dict(backgroundColor="#32363b"),
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': i},
                                        'textAlign': 'left'
                                    } for i in ['Sensor']
                                ],
                            ), ]))])
                ], width=4),

            ], align='top'),
        ]), color='dark'
    )
])


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
)
def update_line_chart(value):
    time.sleep(0.2)
    print(value)
    # lets get nacl value for each channel rdy
    y_blanc = []
    xls = get_bak_xls()
    for channel in LIST_CHANNELS:
        temp_nacl_df = pd.read_excel(xls, f'{channel} 0', header=[1])
        blanc_value = float(temp_nacl_df.loc[temp_nacl_df['freq / Hz'] == value][PARAMETER])
        y_blanc.append(blanc_value)

    y_bac = []
    df = pd.DataFrame(columns=['x', 'y', 'Channel'])

    for idx, channel in enumerate(LIST_CHANNELS):
        bac_value_for_channel = []
        for bac_conc in BAKTERIA_MESSUREMENTS:
            temp_bac_df = pd.read_excel(xls, f'{channel} {bac_conc}', header=[1])
            bac_value = float(temp_bac_df.loc[temp_nacl_df['freq / Hz'] == value][PARAMETER])
            bac_value_for_channel.append(bac_value)
        channel_list = [channel] * len(bac_value_for_channel)
        df2 = pd.DataFrame(list(zip(BAKTERIA_MESSUREMENTS_INT, bac_value_for_channel, channel_list)),
                           columns=['x', 'y', 'Channel'])
        df = df.append(df2)
    print(df)
    fig = px.scatter(df, x="x", y="y", color="Channel", trendline="ols").update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            title='log Bakterien-Konzentration [KBE / ml]'
        ),
        yaxis=dict(
            title=f'Impedanz {PARAMETER}'
        ))

    newnames = {'CH 4': "CH 4 [G1]", 'CH 5': "CH 5 [G2]", 'CH 6': "CH 6 [G6]", 'CH 7': "CH 7 [G7]"}
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                          legendgroup=newnames[t.name]))
    return fig


@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='dropdown', component_property='value')]
)
def update_table(value):
    time.sleep(0.5)
    # lets get nacl value for each channel rdy
    y_blanc = []
    xls = get_bak_xls()
    for channel in LIST_CHANNELS:
        temp_nacl_df = pd.read_excel(xls, f'{channel} 0', header=[1])
        blanc_value = float(temp_nacl_df.loc[temp_nacl_df['freq / Hz'] == value][PARAMETER])
        y_blanc.append(blanc_value)

    df = pd.DataFrame(columns=['x', 'y', 'Channel'])

    for idx, channel in enumerate(LIST_CHANNELS):
        bac_value_for_channel = []
        for bac_conc in BAKTERIA_MESSUREMENTS:
            temp_bac_df = pd.read_excel(xls, f'{channel} {bac_conc}', header=[1])
            bac_value = float(temp_bac_df.loc[temp_nacl_df['freq / Hz'] == value][PARAMETER])
            bac_value_for_channel.append(bac_value)
        channel_list = [channel] * len(bac_value_for_channel)
        df2 = pd.DataFrame(list(zip(BAKTERIA_MESSUREMENTS_INT, bac_value_for_channel, channel_list)),
                           columns=['x', 'y', 'Channel'])
        df = df.append(df2)

    fig_table = px.scatter(df, x="x", y="y", color="Channel", trendline="ols").update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            title='Bakteria Knonzentration [KBE / ml]'
        ),
        yaxis=dict(
            title=f'{PARAMETER} Änderung [%]'
        ))

    newnames = {'CH 4': "CH 4 [G1]", 'CH 5': "CH 5 [G2]", 'CH 6': "CH 6 [G6]", 'CH 7': "CH 7 [G7]"}
    fig_table.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                                legendgroup=newnames[t.name]))

    global df_table
    df_table_temp = pd.DataFrame(columns=['Sensor', 'Bestimmtheitsmaß', 'Slope', 'Intercept'])
    results = px.get_trendline_results(fig_table)
    i = 0
    for channel in LIST_CHANNELS:
        r2 = results.iloc[i]["px_fit_results"].rsquared.round(3)
        intercept, slope = results.iloc[i]["px_fit_results"].params.round(3)
        new_row = {'Sensor': channel, 'Bestimmtheitsmaß': r2, 'Slope': slope, 'Intercept': intercept}
        df_table_temp = df_table_temp.append(new_row, ignore_index=True)
        i += 1
    df_table = df_table_temp
    return df_table.to_dict('records')


# ------------------- MAIN --------------------------#

if __name__ == "__main__":
    app.run_server(debug=False)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table,dash_auth
import base64,sys

df = pd.read_csv('Big_mart_train.csv')
plot_list = ['Bar','Pie','Histogram','Scatter']
cat_cols =[]
num_cols = []
for i in df.columns:
    if df[i].dtypes == 'object':
        cat_cols.append(i)
    elif df[i].dtypes in ['float','int']:
        num_cols.append(i)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,
                          {'nehal':'summer@274',
                           'jinal':'rain@107'})
def table_type(df_column):
    if sys.version_info < (3, 0):  
        return 'any'
    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return 'datetime',
    elif (isinstance(df_column.dtype, pd.StringDtype) or
            isinstance(df_column.dtype, pd.BooleanDtype) or
            isinstance(df_column.dtype, pd.CategoricalDtype) or
            isinstance(df_column.dtype, pd.PeriodDtype)):
        return 'text'
    elif (isinstance(df_column.dtype, pd.SparseDtype) or
            isinstance(df_column.dtype, pd.IntervalDtype) or
            isinstance(df_column.dtype, pd.Int8Dtype) or
            isinstance(df_column.dtype, pd.Int16Dtype) or
            isinstance(df_column.dtype, pd.Int32Dtype) or
            isinstance(df_column.dtype, pd.Int64Dtype)):
        return 'numeric'
    else:
        return 'any'
    
app.layout = html.Div([
                    html.H1('Dashboard',style={'color':'seagreen','fontFamily':'Times New Roman','margin-left':'20px'}),
                    html.Div([
                            dcc.Input(
                                id='adding-rows-name',
                                placeholder='Enter a column name',
                                value = ''),
                            html.Button('Add Column', id='adding-columns-button', n_clicks=0)],
                                style = {'display':'inline-block','height':'50px','width':'30%','padding':10}),
                            html.Button('Add Row', id='editing-rows-button', n_clicks=0),
                        
                    dash_table.DataTable(
                    id='our-table',
                    data = df.to_dict('records'),
                    columns = [{'name': i, 'id': i,'type': table_type(df[i]),
                                'deletable':True,'renamable':True,'selectable':True} 
                               for i in df.columns],
                    css = [{ 'selector': 'table','rule': 'table-layout: fixed'}],
                    editable=True,                  # allow user to edit data inside table
                    row_deletable=True,             # allow user to delete rows
                    row_selectable = 'multi',
                    sort_action="native",           # give user capability to sort columns
                    sort_mode="single",             # sort across 'multi' or 'single' columns
                    filter_action="native",         # allow filtering of columns
                    page_action='native',             # render all of the data at once. No paging.
                    page_size=40,
                    page_current=0,
                    #fixed_rows = {'headers': True}, # fixed header of table
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
                    style_cell_conditional=[{'if': {'column_id': c},
                            'textAlign': 'right'} for c in num_cols],
                    style_header={
                        'backgroundColor': 'wheat',
                        'fontWeight': 'bold',
                        'color':'brown'},
                    style_data={      
                        'whiteSpace': 'normal',
                        'height': 'auto'},
                ),
                html.Br(),
                dcc.Dropdown(id='plot-id',
                            options = [{'label': i, 'value': i} for i in plot_list],
                            placeholder = 'Select plot',
                            multi = False,
                            clearable = False,
                            style={'display':'inline-block','width':'200px','margin-left':'10px','float':'center'}
                        ),
                dcc.Dropdown(id='xaxis-column',
                            options=[
                                     {'label': i, 'value': i} for i in df.columns],
                            placeholder="X-axis",
                            multi = False,
                            clearable = False,
                            style={'display':'inline-block','width':'200px','float':'center','margin-left':'10px'}
                        ),
                dcc.Dropdown(id='yaxis-column',
                            options=[
                                     {'label': i, 'value': i} for i in df.columns],
                            placeholder="Y-axis",
                            multi = False,
                            clearable = False,
                            style={'display':'inline-block','width':'200px','margin-left':'10px','float':'center'}
                        ),
    
                html.Button(id='submit-plot',n_clicks=0, children = 'Plot',
                            style={'display':'inline-block','float':'centre','marginLeft':'20px'}),
    
                dcc.Dropdown(id='save-id',placeholder="Save as..",searchable=False,
                                     options=[{'label': 'Excel', 'value': 'Excel'},
                                                {'label': 'HTML', 'value': 'HTML'},
                                                {'label': 'CSV', 'value': 'CSV'}],
                            style={'display':'inline-block','width':'150px','margin-left':'50px'}),
                html.Button('Export', id='save_file', n_clicks=0,style={'display':'inline-block','margin-left':'60px'}),
              
                # Create notification when saving the file
                html.Div(id='placeholder', children=[]),
                dcc.Store(id="store", data=0),
                dcc.Interval(id='interval', interval = 1000),
        
                dcc.Graph(id='my_graph')
        ])
# ------------------------------------------------------------------------------------------------
@app.callback(
    Output('my_graph', 'figure'),
    Input('submit-plot', 'n_clicks'),
    State('xaxis-column', 'value'),State('yaxis-column', 'value'), State('plot-id', 'value'))
def display_graph(n_clicks, xaxis_name, yaxis_name, plot):
    fig = go.Figure()
    if(plot == 'Bar'):
        df_bar = df.groupby(xaxis_name).sum()[yaxis_name].reset_index()
        fig.add_trace(go.Bar(x = df_bar[xaxis_name],y = df_bar[yaxis_name]))
        fig.update_traces(marker_color='brown', marker_line_color='white',
                  marker_line_width=1.5, opacity=0.6,texttemplate='%{text:.2s}')
        fig.update_layout(xaxis_title = xaxis_name,xaxis_zeroline=False,yaxis_zeroline=False,yaxis_showgrid=False,
                          yaxis_title = yaxis_name,plot_bgcolor='wheat',xaxis_showgrid=False,height=700)
    elif(plot == 'Scatter'):
        fig.add_trace(go.Scatter(x = df[xaxis_name], y = df[yaxis_name],mode='markers'))
        fig.update_traces(marker_color='brown')
        fig.update_layout(xaxis_title = xaxis_name,
                          yaxis_title = yaxis_name,
                          xaxis_zeroline=False,yaxis_zeroline=False,yaxis_showgrid=False,
                          plot_bgcolor='wheat',xaxis_showgrid=False,height=700)
    elif(plot == 'Histogram'):
        fig.add_trace(go.Histogram(x = df[xaxis_name]))
        fig.update_layout(xaxis_title = xaxis_name,
                          plot_bgcolor='wheat',xaxis_showgrid=False,height=700,
                         xaxis_zeroline=False,yaxis_zeroline=False,yaxis_showgrid=False)
    elif(plot == 'Pie'):
        x = df[xaxis_name]
        y = df[yaxis_name]
        fig.add_trace(go.Pie(labels = x, values = y ,hole=0.2,textinfo='percent+value+label'))
        fig.update_layout(xaxis_title = xaxis_name,
                          yaxis_title = yaxis_name,plot_bgcolor='wheat',xaxis_showgrid=False,height=700,
                         xaxis_zeroline=False,yaxis_zeroline=False,yaxis_showgrid=False)
    
    return fig

@app.callback(
    Output('our-table', 'columns'),
    [Input('adding-columns-button', 'n_clicks')],
    [State('adding-rows-name', 'value'),
     State('our-table', 'columns')],
)
def add_columns(n_clicks, value, existing_columns):
    print(existing_columns)
    if n_clicks > 0:
        existing_columns.append({
            'name': value, 'id': value,
            'renamable': True, 'deletable': True
        })
    #print(existing_columns)
    return existing_columns

@app.callback(
    Output('our-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('our-table', 'data'),
     State('our-table', 'columns')],
)
def add_row(n_clicks, rows, columns):
    # print(rows)
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    # print(rows)
    return rows
    
@app.callback(
    [Output('placeholder', 'children'),Output("store", "data")],
    [Input('save_file', 'n_clicks'),Input("interval", "n_intervals"),Input('save-id','value')],
    [State('our-table', 'data'),State('store', 'data')]
)
def df_to_file(n_clicks, n_intervals, fname, dataset, s):
    output = html.Plaintext("The data has been saved to your folder.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    
    if input_triggered == "save_file":
        s = 6
        df = pd.DataFrame(dataset)        
        if fname == 'CSV':
            df.to_csv(f"Dummy{n_clicks}.csv")
        elif fname == 'Excel':
            df.to_excel(f"Dummy{n_clicks}.xls")
        elif fname == 'HTML':
            df.to_html(f'Dummy{n_clicks}.html')
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s-1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s
    
if __name__ == '__main__':

    app.run_server(debug=False)

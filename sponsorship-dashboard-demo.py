#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from matplotlib import pyplot as plt

import dash
from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output, State

df = pd.read_excel('./data/all_APs_Child_Media_Submissions_1-OCT-21_to_30-NOV-21 - Demo.xlsx', header=8)

df.columns

media = df.drop(['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4',
                 'Unnamed: 8', 'Unnamed: 10', 'Unnamed: 13',
                 'Unnamed: 14', 'Unnamed: 19', 'Unnamed: 20',
                 'Unnamed: 21'], axis=1)

# This dataframe is for use in the Data Table display when user needs detail (e.g. Sponsorship Leads/ Coordinators)
media_df = media[['Project Name', 'Child Code', 'Content Type', 'FY Year', 'Approval Status', 'Reject Reason']]
media_df.head()

new_df = df[['Approval Status', 'Content Type']].value_counts()
new_df = pd.DataFrame(new_df)
new_df

new_df.rename(columns={0: 'Count'}, inplace=True)
new_df.unstack()

dff = new_df.groupby(['Approval Status', 'Content Type']).sum()
dff

dff.loc[(['Approved', 'Pending', 'Rejected'], 'Photo-Type2'), :]
dff.loc[(slice(None), ['Photo-Type1', 'Video-Type1', 'Image-Type1']), :]
dff.loc[('Approved', ['Photo-Type2', 'Video-Type2', 'Photo-Type1', 'Video-Type1', 'Image-Type1']), :]

dff.reset_index(inplace=True)
dff.rename(columns={0: 'Count'}, inplace=True)
dff

rej_by_proj_type = pd.DataFrame(media[['Project Name', 'Content Type', 'Approval Status']].value_counts()).sort_values(
    ['Project Name', 'Content Type'])
rej_by_proj_type.rename(columns={0: 'Count'}, inplace=True)
rej_by_proj_type.reset_index(inplace=True)
rej_by_proj_type.head()

rej = media_df[['Project Name', 'Content Type', 'Approval Status', 'Reject Reason']]
rej.head()

top_rej = rej.value_counts(['Project Name', 'Content Type', 'Reject Reason'])
top_rej = pd.DataFrame(top_rej)
top_rej = top_rej.sort_values(['Project Name', 'Content Type'])
top_rej.rename(columns={0: 'Count'}, inplace=True)
top_rej

top_rej.reset_index(inplace=True)
top_rej.head(3)
########################################## Date Wrangling #######################################################
media['Upload Date']
media['date'] = pd.to_datetime(media['Upload Date'], format='%d-%b-%Y')
media['Upload Date'].max(), media['Upload Date'].min(), media['date'].max(), media['date'].min()

start_date = media['date'].min()
end_date = media['date'].max()
dat_rang = pd.date_range(start=start_date, end=end_date, freq='W-MON')
dat_rang
{d.strftime('%d-%b-%Y'): '{}'.format(d.strftime('%d-%b-%Y')) for d in dat_rang}
{d.date() for d in dat_rang}
dat_rang.strftime('%b-%Y')
type(media['date'][0])

## ********** Filter a Data Frame by Date Range *********************

media[(media['date'] >= '2021-10-05') & (media['date'] <= '2021-11-15')] # 'date' column is timestamp version of 'Upload Date'
media[media['date'] < '2021-10-04']

{key: '{}'.format(d.strftime('%d-%b-%Y')) for key, d in enumerate(dat_rang)}
dat_rang.day
len(dat_rang)
######################################### End of Date Wrangling ###############################################

import base64

linkedin_filename = './assets/linkedin-logo.png'
encoded_linkedin = base64.b64encode(open(linkedin_filename, 'rb').read()).decode('ascii')

github_filename = './assets/GitHub-Mark-120px-plus.png'
encoded_github = base64.b64encode(open(github_filename, 'rb').read()).decode('ascii')

app = dash.Dash()

app.layout = html.Div([
    html.Div([

        html.H1('WV ZIM Weekly Media Review', style={'width': '50%'}),

        html.Div(id='dash-author-details', children=[  # container for author/creator details

            html.H3('Dashboard by Tawanda Musabaika'),

            html.Div([  # container for socials links and icons

                html.A(href="https://www.linkedin.com/in/tawanda-musabaika", target='_blank',
                       children=[
                           html.Img(
                               alt="Link to my LinkedIn",
                               src="data:image/png;base64, {}".format(encoded_linkedin), style={'height': '50px'}
                           )]
                       ),
                html.A(href="https://github.com/tmusabaika", target='_blank',
                       children=[
                           html.Img(
                               alt="Link to my GitHub",
                               src="data:image/png;base64, {}".format(encoded_github), style={'height': '32px'}
                           )]
                       )
            ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center', 'width': '50%'})
    ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'}),

    html.Div([

        html.Div([

            html.Label(['Content Type to View'], style={'font-weight': 'bold'}),
            dcc.RadioItems(

                id='cont_type',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Photo-Type1', 'value': 'Photo-Type1'},
                    {'label': 'Video-Type1', 'value': 'Video-Type1'},
                    {'label': 'Photo-Type2', 'value': 'Photo-Type2'},
                    {'label': 'Video-Type2', 'value': 'Video-Type2'},
                    {'label': 'Image-Type1', 'value': 'Image-Type1'}
                ],

                value='All'  # default selected value

            )

        ], style={'padding': 10, 'border': '1px solid ghostwhite', 'width': '50%'}),

        html.Div([

            html.Label(['Area Program'], style={'font-weight': 'bold'}),
            dcc.Dropdown(

                id='selected_ap',
                options=[
                    {'label': k, 'value': k} for k in sorted(media_df['Project Name'].unique())
                ],
                placeholder='Select Area Program',
                value=''  # default selected value

            )

        ], style={'padding': 10, 'border': '1px solid ghostwhite', 'width': '50%'})

    ], style={'display': 'flex', 'flex-direction': 'row'}),  # wrapper for HTML Components

    html.Div([

        html.Div([
            html.Div(id='media_table', style={'border': '1px solid ghostwhite'}),
            html.H3('Top 3 Rejections'),
            html.Div(id='top_rej_table', style={'border': '1px solid ghostwhite'})
        ],
            style={'width': '40%', 'border': '1px solid ghostwhite'}),

        html.Div(dcc.Graph(id='sample_graph'), style={'width': '60%'})

    ], style={'display': 'flex', 'flex-direction': 'row'})

], style={'font-family': 'sans-serif'})  # Global styles for the DIV


@app.callback(

    Output(component_id='sample_graph', component_property='figure'),
    Output(component_id='media_table', component_property='children'),
    Output(component_id='top_rej_table', component_property='children'),
    Input(component_id='cont_type', component_property='value'),
    Input(component_id='selected_ap', component_property='value')

)
def update_graph(content_type,
                 area_program):  # the arg 'content_type' refers to the 'value' in Input(component_property)

    if area_program == '' or area_program == None:

        if content_type == 'All':
            df_final = rej_by_proj_type
            # x_lim = (df_final['Count'].sum().max())/2
            area_program = 'All Area Programs'  # for the bar graph title

            # Get Top 3 rejection reasons,
            # Make sure the df is sorted by the Count column

            top3_rej = top_rej.sort_values('Count', ascending=False).head(3)

        else:

            df_final = rej_by_proj_type[rej_by_proj_type['Content Type'] == content_type]
            #             x_lim = (df_final['Count'].sum().max())
            #             x_lim = x_lim + ( x_lim * .2)

            # Get Top 3 rejection reasons,
            # Make sure the df is sorted by the Count column

            top3_rej = top_rej[top_rej['Content Type'] == content_type].sort_values('Count', ascending=False).head(3)
    else:

        if content_type == 'All':

            df_final = rej_by_proj_type[rej_by_proj_type['Project Name'] == area_program]
            #             x_lim = df_final['Count'].max()
            #             x_lim = x_lim + ( x_lim * .2)

            # Get Top 3 rejection reasons,
            # Make sure the df is sorted by the Count column

            top3_rej = top_rej[top_rej['Project Name'] == area_program].sort_values('Count', ascending=False).head(3)

        else:
            df_final = rej_by_proj_type[(rej_by_proj_type['Project Name'] == area_program) &
                                        (rej_by_proj_type['Content Type'] == content_type)]

            #             x_lim = df_final['Count'].max()
            #             x_lim = x_lim + ( x_lim * .2)

            # Get Top 3 rejection reasons,
            # Make sure the df is sorted by the Count column

            top3_rej = top_rej[(top_rej['Project Name'] == area_program) &
                               (top_rej['Content Type'] == content_type)].sort_values('Count', ascending=False).head(3)

    table_data = dash_table.DataTable(data=df_final.to_dict(orient='records'),
                                      columns=[{'name': i, 'id': i} for i in df_final.columns],
                                      page_size=10
                                      )

    top_rej_table = dash_table.DataTable(data=top3_rej.to_dict(orient='records'),
                                         columns=[{'name': i, 'id': i} for i in top3_rej.columns],
                                         style_table={'overflowX': 'auto'},
                                         page_size=10
                                         )

    barchart = px.histogram(  # px.histogram for solid bars, px.bar for disagregated, stripped bars

        data_frame=df_final,
        x='Content Type',
        y='Count',

        color='Approval Status',
        color_discrete_map={

            'Approved': '#008968',
            'Pending': '#FE7701',
            'Rejected': '#E50C4C'
        },
        barmode='group',
        title=area_program,

    )

    x_lim = (dff['Count'].max())
    x_lim = x_lim + (x_lim * .1)

    barchart.update_layout(yaxis_range=[0, x_lim])
    return barchart, table_data, top_rej_table

app.run_server()
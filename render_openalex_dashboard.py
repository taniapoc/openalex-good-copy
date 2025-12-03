#!/usr/bin/env python
# coding: utf-8

# # Create the dashboard

# ### Import Dash and other necessary packages

# In[1]:


import plotly # i had to downgrade to plotly 5.19.0 because plotly 6.x+ appear to have issues with plotting certain things (specifically tree maps and sunbursts)
print(plotly.__version__)

import plotly.express as px

import pandas as pd
import numpy as np
 
import papermill as pm
from datetime import datetime
import socket
import psutil
import time

import dash
from dash import html, Dash, dcc, Input, Output, State, callback, dash_table

pd.set_option('display.max_columns', None)


# ### Call data previously scraped from OpenAlex

# In[2]:


# gonna have to do something different here because this only lists up to the top 25 topics for sfu, but I care more about the overall 
sfu_topics = pd.read_csv('data_pulls/sfu_topics.csv')
sfu_topics.head()


# In[3]:


sfu_works_count_by_year = pd.read_csv('data_pulls/sfu_works_count_by_year.csv')
sfu_works_count_by_year.head()


# In[4]:


sfu_associated_institutions = pd.read_csv('data_pulls/sfu_associated_institutions.csv')
sfu_associated_institutions.head()


# In[5]:


sfu_summary_stats = pd.read_csv('data_pulls/sfu_summary_stats.csv')
sfu_fwci = pd.read_csv('data_pulls/sfu_fwci.csv')

print(sfu_summary_stats)


# In[6]:


sfu_works_domain  = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_by_domain.csv'))
sfu_works_field  = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_by_field.csv'))
sfu_works_subfield  = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_by_subfield.csv'))
sfu_works_topic  = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_by_topic.csv'))

sfu_works_domain


# In[7]:


sfu_annual_works = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_count_by_year.csv'))
sfu_annual_works


# _____________________________________________________________________________________________________________________

# #### THE BELOW CODE IS FOR THE WORKS PAGE OF THE DASHBOARD

# In[8]:


sfu_cleaned_table = pd.DataFrame(pd.read_csv('data_pulls/sfu_cleaned_table.csv'))
sfu_cleaned_table['Citation Percentile'] = sfu_cleaned_table['Citation Percentile'].round(4)
sfu_cleaned_table[sfu_cleaned_table['OpenAlex ID'] == 'W4306871314']['Citation Percentile']


# In[9]:


top_500_table = pd.DataFrame(pd.read_csv('data_pulls/top_500_table.csv'))
top_500_table.head()


# In[10]:


past_5_years_table = pd.DataFrame(pd.read_csv('data_pulls/past_5_years_table.csv'))
past_5_years_table.head()


# # INCORPORATE THE THING BELOW INTO AN ACTUAL INTERACTIVE TOGGLE!!!!!

# In[11]:


# PLEASE SELECT ONE
    # ensure that the selection matches that in the file '5. detailed works cleaning.ipynb'

#x = past_5_years_table
#x = top_500_table
x = sfu_cleaned_table


# In[12]:


year_range = list(range(min(x['Year']), max(x['Year'])+1, 1))
year_range.sort(reverse=True)
print(year_range)


# In[13]:


open_access_counts = pd.DataFrame(pd.read_csv('data_pulls/open_access_counts.csv'))
open_access_counts.head()


# In[14]:


publication_types = pd.DataFrame(pd.read_csv('data_pulls/publication_types.csv'))
publication_types.head()


# In[15]:


citation_percentile_categories = pd.DataFrame(pd.read_csv('data_pulls/citation_percentile_categories.csv'))
citation_percentile_categories.head()


# In[16]:


domains_for_works_pg = pd.DataFrame(pd.read_csv('data_pulls/domains_for_works_pg.csv'))
domains_for_works_pg.head()


# In[17]:


sdg_t_f = pd.DataFrame(pd.read_csv('data_pulls/publication_sdg_t_f.csv'))
sdg_t_f.head()


# In[18]:


first_auth_sfu = pd.DataFrame(pd.read_csv('data_pulls/first_auth_sfu.csv'))
first_auth_sfu.head()


# In[19]:


collab_statuses = pd.DataFrame(pd.read_csv('data_pulls/collab_statuses.csv'))
collab_statuses.head()


# ___________________

# #### THE BELOW CODE IS FOR THE SDGs PAGE OF THE DASHBOARD

# In[20]:


sdg_publications_list = pd.DataFrame(pd.read_csv('data_pulls/sdg_publications_list.csv'))
sdg_publications_list.head()


# In[21]:


sdg_publications_t_f = pd.DataFrame(pd.read_csv('data_pulls/sdg_publications_grouped_by_amount.csv'))
sdg_publications_t_f.head()


# In[22]:


sdg_counter = pd.DataFrame(pd.read_csv('data_pulls/sdg_counts_for_works.csv'))
sdg_counter['SDG'] = sdg_counter['SDG'].astype(str)
sdg_counter['SDG'] = sdg_counter['SDG'].apply(lambda x: 'SDG ' + x)
sdg_counter.head()


# In[23]:


top_sdgs_by_year_tall = pd.DataFrame(pd.read_csv('data_pulls/top_sdgs_by_year_tall.csv',dtype={'Top SDG Number':str}))
top_sdgs_by_year_tall.head()


# In[24]:


top_sdgs_by_year_wide = pd.DataFrame(pd.read_csv('data_pulls/top_sdgs_by_year_wide.csv'))
top_sdgs_by_year_wide = top_sdgs_by_year_wide.fillna(0)
top_sdgs_by_year_wide.head()


# In[25]:


top_sdgs_for_line = top_sdgs_by_year_wide.melt(
        id_vars="Year", 
        value_vars=top_sdgs_by_year_wide.columns.drop("Year"),
        var_name="SDG Number", 
        value_name="Publications"
    )

top_sdgs_for_line['SDG Number'] = top_sdgs_for_line['SDG Number'].apply(lambda x: x if x=='Total' else 'SDG '+x)

top_sdgs_for_line


# In[26]:


sdg_topic_comp_by_year = pd.DataFrame(pd.read_csv('data_pulls/sdg_topic_comp_by_year.csv'))
sdg_topic_comp_by_year['SDG Name'] = sdg_topic_comp_by_year['SDG Name'].apply(lambda x: "Life on Land" if x=='Life in Land' else x)
sdg_topic_comp_by_year.head()


# In[27]:


sdg_topic_comp_by_year['SDG Name'].unique()


# In[28]:


sdg_topic_comp_overall = pd.DataFrame(pd.read_csv('data_pulls/sdg_topic_comp_overall.csv'))
sdg_topic_comp_overall.head()


# _________________________

# ### BELOW IS THE CODE FOR THE TOPICS PAGE

# In[29]:


sfu_cleaned_topics = pd.DataFrame(pd.read_csv('data_pulls/sfu_works_cleaned_topics.csv'))
sfu_cleaned_topics = sfu_cleaned_topics.iloc[:-1].replace('','n/a')

sfu_cleaned_topics.head()


# In[30]:


sfu_topics_agg = sfu_cleaned_topics.groupby(["Year", "Domain", "Field", "Subfield", "Topic"]).size().reset_index(name="count")
sfu_subfields_agg = sfu_cleaned_topics.groupby(["Year", "Domain", "Field", "Subfield"]).size().reset_index(name="count")

subfield_list = sfu_subfields_agg['Subfield'].unique().tolist()

print(type(subfield_list))
sfu_subfields_agg


# ____________________________________

# #### CODE FOR THE AUTHORS PAGE

# In[31]:


sfu_authors_table = pd.DataFrame(pd.read_csv('data_pulls/sfu_authors_table.csv'))
sfu_authors_table.head()


# In[32]:


sfu_authors_full = pd.DataFrame(pd.read_csv('data_pulls/sfu_authors_cleaned.csv'))
sfu_authors_full.head()


# In[33]:


# using name as the primary identifier is unorthodox but this is actually better than using ID. 
    # case in point: there are ~60 different IDs associated with Dugan, but only 5 Dugans when deduplicating by name, as is the casde with lots of other researchers as well
sfu_num_authors = len(sfu_authors_table['Name'].unique())
sfu_num_authors


# ___________________________

# Kill port 8050

# # check port 8050 and kill existing process if needed 
# PORT = 8050
# 
# # First check if the port is in use
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     try:
#         s.bind(("127.0.0.1", PORT))
#         print(f"Port {PORT} is free.")
#     except OSError:
#         # Port is in use -> find and kill the process
#         killed_any = False
#         for proc in psutil.process_iter(['pid', 'name']):
#             try:
#                 for conn in proc.net_connections(kind='inet'):
#                     if conn.laddr.port == PORT:
#                         print(f"Killing process {proc.pid} ({proc.name()}) using port {PORT}")
#                         proc.kill()
#                         killed_any = True
#                         time.sleep(1)  # wait a bit for OS to free port
#                         break
#             except (psutil.AccessDenied, psutil.NoSuchProcess):
#                 continue
#         if not killed_any:
#             print(f"Port {PORT} is in use, but no process could be killed.")

# ### Initialize and run app

# In[34]:


###############################
### Initialize the Dash app ###
###############################

app = dash.Dash(__name__)
app.title = "SFU OpenAlex"



#########################################
### SET CSS STYLES FOR APP COMPONENTS ###
#########################################

tabs_styles = {
    'height': '44px'
}

tab_style = {
    'border': '1px solid #cccccc', #d6d6d6
    'padding': '12px',
    #'backgroundColor': '#70caff',
    'backgroundColor': '#ebebeb',
    'color': '#525252',
    
}

tab_selected_style = {
    'borderTop': '1px solid #cccccc', #d6d6d6
    #'borderBottom': '1px solid #d6d6d6',
    #'backgroundColor': '#119DFF',
    #'backgroundColor': '#70caff',
    #'color': 'white',
    'padding': '12px', 
    'fontWeight': 'bold'
}



#########################
### SET UP APP LAYOUT ###
#########################

app.layout = html.Div(
    style={'font-family': 'Arial'}, # CHANGE THIS TO A SERIOUS FONT BEFORE SHOWING PEOPLE herculanum is atla font
    children=[
    # Tab 1: Summary
    dcc.Tabs(id="tabs", value='tab-1', style=tabs_styles, children=[
        dcc.Tab(label='Summary', style=tab_style, selected_style=tab_selected_style, children=[
            html.Div(
                style = {'display': 'flex', 'flex-basis': '100%', 'padding': '25px'}, 
                children = [
                    html.Div(
                        style = {'width': '60%'},
                        children=[
                            html.H2('Summary statistics'),
                            html.Div('This page displays SFU\'s summary statistics in the time frame selected by the toggle below. The data is scraped from OpenAlex. '),
                            html.Br(),
                            dcc.Dropdown(
                                id="summary-toggle",
                                options=['5 years', '10 years', 'All-time'],
                                value='5 years'
                            ),
                            html.Br(),
                            html.Br(),
                            html.Div(
                                children = [
                                    html.Div(
                                        style = {'display': 'flex', 'height': '200px'}, 
                                        children = [
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("Publications")), 
                                                    html.Div(id="pub-number", style={'font-size': '52px'}), 
                                                    html.Br()
                                                ]
                                            ), 
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("Authors")), 
                                                    html.Div(id="auth-number", style={'font-size': '52px'}), 
                                                    html.Br()
                                                ]
                                            ),
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("Field-Weighted Citation Impact")), 
                                                    html.Div(id="fwci-number", style={'font-size': '52px'}), 
                                                    html.Br()

                                                ]
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        style = {'display': 'flex'}, 
                                        children = [
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("Citations")), 
                                                    html.Div(id="cite-number", style={'font-size': '52px'})
                                                ]
                                            ), 
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("Citations per Publication")), 
                                                    html.Div(id="cite-per-pub-number", style={'font-size': '52px'})
                                                ]
                                            ),
                                            html.Div(
                                                style = {'width': '33%'}, 
                                                children = [
                                                    html.Div(html.B("h-Index")), 
                                                    html.Div(id="h-ind-number", style={'font-size': '52px'})
                                                ]
                                            )
                                        ]
                                    ),                                
                                ])
                        ]), 
                    html.Div(
                        style = {'width': '40%', 'height':'450px', 'word-wrap': 'break-word'}, 
                        children = [
                        html.H2('Publications by subject area'), 
                        dcc.Graph(
                            id='subj-area-pie',
                            #figure=px.pie(data_frame=sfu_works_domain, names=sfu_works_domain['domain'], values=sfu_works_domain['count'], color_discrete_sequence=px.colors.qualitative.T10)
                            )
                        ]
                    )
                ]
            ), 
            html.Div(
                style = {'width': '100%', 'padding': '25px'}, 
                children = [
                    html.H2('Historical Publications and Citation Count'),
                    dcc.Graph(
                        style={'height': '400px', 'padding': '0px'},
                        id='pub-line'
                    ),
                    dcc.Graph(
                        style={'height': '400px', 'padding': '0px'},
                        id='cite-line'
                    ) 
                ]
            )
        ]),
        # Tab 2: Works
        dcc.Tab(label='Works', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    style={'padding':'25px'}, 
                    children=[
                        html.H2('SFU Publications & at-a-glance stats'),
                        html.Div('Use the slider below to select the publication year (or range of years) in which the works were published. The table contains the top 100 works based on citation count for the selected time frame, whereas the pie charts are based on the full set of publications in the selected time frame. '),
                        html.Br(),
                        dcc.RangeSlider(
                            id='works-pg-yr-selector', 
                            min=min(x['Year']), 
                            max=max(x['Year']), 
                            step=1, 
                            value=[2021,2025], 
                            marks={year: {"label": str(year), "style": {"transform": "rotate(90deg)"}}
                                    for year in x['Year'] if year % 5 == 0},
                            tooltip={"always_visible": True, "placement": "top"}
                        ), 
                        html.Br(),
                        html.H4(id='works-text-output'),
                        html.Br(), 
                        dash_table.DataTable(
                            id='works-table',
                            data=[],
                            columns=[{"name": i, "id": i} for i in x], 
                            style_table={
                                "height": "400px", 
                                "overflowY": "auto",
                                "width": "100%",
                                "overflowX": "hidden",   
                            },
                            style_header={
                                'whiteSpace': 'normal', 
                                'height': '50px', 
                                'textAlign': 'left'
                            },
                            style_data={
                                "maxHeight": "50px",
                                "minHeight": "50px",
                                "height": "50px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "whiteSpace": "normal",
                            },
                            fixed_rows={'headers': True, 'data': 0},
                            cell_selectable=False,
                            style_cell_conditional=[
                                {'if': {'column_id': 'OpenAlex ID'}, 'width': '96px', 'text-align': 'left'}, # 6%
                                {'if': {'column_id': 'Year'}, 'width': '64px', 'text-align': 'center'}, # 4%
                                {'if': {'column_id': 'FWCI'}, 'width': '64px', 'text-align': 'center'}, # 4%
                                {'if': {'column_id': 'Citations Received'}, 'width': '96px', 'text-align': 'center'}, # 6%
                                {'if': {'column_id': 'Citation Percentile'}, 'width': '96px', 'text-align': 'center'}, # 6%
                                {'if': {'column_id': 'Top Matching SDG'}, 'width': '80px', 'text-align': 'center'}, # 5%
                                {'if': {'column_id': 'Domain'}, 'width': '80px', 'text-align': 'left'}, # 5%
                                {'if': {'column_id': 'Collaboration Status'}, 'width': '120px', 'text-align': 'left'}, # 6%
                                {'if': {'column_id': 'Topic'}, 'width': '288px', 'text-align': 'left'}, # 18%
                                {'if': {'column_id': 'Title'}, 'width': '400px', 'text-align': 'left'}, # 40%
                                {'if': {'column_id': 'Source Name'}, 'width': '210px', 'text-align': 'left'}
                            ],
                            page_size=100, 
                            sort_action='native',
                        ),
                        html.Div(
                            style={'display': 'flex'}, 
                            children=[
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-open-access-pie')
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-publication-type-pie')
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-citation-percentile-pie')
                                        )
                                    ]
                                )
                            ]
                        ), 
                        html.Div(
                            style={'display': 'flex'}, 
                            children=[
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-domain-pie')
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-sdg-pie')
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-first-auth-pie')
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            style={'display': 'flex'}, 
                            children=[
                                html.Div(
                                    style={'width': '33%'}, 
                                    children=[
                                        html.Div(
                                            dcc.Graph(id='works-pg-collab-pie')
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '66%'},
                                    children=[
                                        html.Div('There is enough space for 2 more pie charts here if we need to add anything else, otherwise can centre the pie chart here')
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ), 
        # Tab 3: Topics
        # NOTE: the tab is slightly laggy when you open it, takes a sec to load. most likely because of the gigantic graphic, may need to change something or else accept the fact that it's a little slow 
        dcc.Tab(label='Topics', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    style={'padding':'25px'}, 
                    children=[
                        html.H2('SFU Publication Topics'), 
                        html.Div('Publications in OpenAlex have an associated Topic, Subfield, Field, and Domain. The tree map below shows all SFU publication down to the subfield level. If you would like more information about SFU publications within a specific subfield, search the subfield name and select it from the dropdown to the right. The table will display a detailed breakdown of all topics within the subfield.'), 
                        html.Br(),
                        html.Div(
                            style={'display': 'flex'}, 
                            children=[
                                html.Div(
                                    style={'height': '750px', 'width': '60%'},
                                    children=[
                                        html.Br(),
                                        'Select a time frame to filter by:',
                                        html.Br(),
                                        html.Br(),
                                        dcc.Dropdown(id="topics-toggle", options=['5 years', '10 years', 'All-time'], value='5 years'),
                                        html.Br(),
                                        dcc.Graph(
                                        id='topic-tree-map', 
                                        )
                                    ]
                                ), 
                                html.Div(
                                    style={'width': '40%'}, 
                                    children=[
                                        html.Br(),
                                        'Select a subfield from the dropdown below to see all related topics:', 
                                        html.Br(),
                                        html.Br(),
                                        dcc.Dropdown(
                                            options=[{"label": i, "value": i} for i in subfield_list], 
                                            id='subfield-dropdown', 
                                            value='' #subfield_list[0]
                                        ),
                                        html.Br(),
                                        html.Div(id='topic-text-output'), 
                                        html.Br(),
                                        dash_table.DataTable(
                                            id='topics-table', 
                                            data=[],
                                            columns=[{"name": i, "id": i} for i in ['count', 'Topic']], 
                                            fixed_rows={'headers': True, 'data': 0},
                                            cell_selectable=False,
                                            style_table={
                                                "height": "450px", 
                                                "overflowY": "auto",
                                                "width": "100%",
                                                "overflowX": "hidden",  
                                            },
                                            style_data={
                                                'textAlign': 'left' 
                                            },
                                            style_header={
                                                'textAlign': 'left' 
                                            },
                                            style_cell_conditional=[
                                                {'if': {'column_id': 'count'}, 'width': '75px'}, # 6%
                                            ], 
                                            sort_action='native',
                                        ), 
                                        html.Br(),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        # Tab 4: SDGs 
        dcc.Tab(label='SDGs', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    style={'padding':'25px'}, 
                    children=[
                        html.H2('Alignment to Sustainable Development Goals (SDGs)'), 
                        html.Br(),
                        dcc.Dropdown(id="sdg-toggle", options=['5 years', '10 years', 'All-time'], value='5 years'), 
                        html.Br(), 
                        html.Div('NOTE: The OpenAlex assignment of SDGs to publications uses a different methodology than Times Higher Education/Scopus/SciVal. Additionally, OpenAlex only lists up to 2 SDGs per publication, and only the top 1 is taken into account when producing the below infographics. This section is intended to only be used as an approximate reference. '),
                        html.Div(
                            style={'height': '700px'},
                            children = [
                                dcc.Graph(
                                    id='sdgs-bar'
                                )
                            ]
                        ), 
                        html.Div(
                            style={'height': '750px', 'width': '100%'},
                            children=[
                                dcc.Graph(
                                    id='sdg-topic-tree-map',
                                )
                            ]
                        ),
                        html.Div(
                            children = [
                                html.Div('Use the dropdown below to select a year, and the table will display the number of publications for each SDG in that year.'),
                                #html.Br(),
                                html.Div(
                                    style={'display': 'flex'}, 
                                    children=[
                                        html.Div(
                                            style={'width': '20%', 'padding': '10px'},
                                            children=[
                                                dcc.Dropdown(
                                                    year_range,
                                                    value=2025,
                                                    id='sdg-pg-yr-selector', 
                                                    placeholder="Select a year..."
                                                )   
                                            ]
                                        ),
                                        html.Div(
                                            style={'width': '75%', 'padding': '10px'}, 
                                            children=[
                                                dash_table.DataTable(
                                                id="top-sdgs", 
                                                data=[],
                                                columns=[{"name": i, "id": i} for i in top_sdgs_by_year_tall.columns], 
                                                sort_action='native',
                                                page_size=25,
                                                )
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Div(
                            children = [
                                html.Div('Use the dropdown below to select an SDG (or group of SDGs), and the graph will update to show SFU\'s publications in that SDG over time.'),
                                html.Div(
                                    style={'display': 'flex'}, 
                                    children=[
                                        html.Div(
                                            style={'width': '20%', 'padding': '10px'},
                                            children=[
                                                dcc.Dropdown(
                                                    top_sdgs_for_line['SDG Number'].unique(),
                                                    id='sdg-pg-sdg-selector', 
                                                    placeholder="Select an SDG (or group of SDGs)...", 
                                                    multi=True
                                                )   
                                            ]
                                        ),
                                        html.Div(
                                            style={'width': '75%', 'padding': '10px', 'height': '600px'}, 
                                            children=[
                                                dcc.Graph(
                                                    id="sdg-line",
                                                    figure=px.line(
                                                        data_frame=[],
                                                        title='SFU SDG Publications by Year', 
                                                        markers=True, 
                                                        range_x=[min(top_sdgs_by_year_wide['Year']),max(top_sdgs_by_year_wide['Year'])]
                                                    ).update_traces(line_color=px.colors.qualitative.T10[0], line_width=2, marker=dict(color=px.colors.qualitative.T10[0], size=8))
                                                )
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ]
                )
            ]
        ), 
        # Tab 5: Author Stats
        dcc.Tab(label='Authors', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    style={'padding':'25px'}, 
                    children=[
                        html.H2('SFU Authors'),
                        dcc.Dropdown(id="author-toggle", options=['5 years', '10 years', 'All-time'], value='5 years'),
                        html.Br(),
                        #html.Div(f"There have been {sfu_num_authors:,} authors who have published with SFU since 1965."),
                        html.Div(id="author-msg"),
                        html.Br(),
                        html.Div('DISCLAIMER: the authorship data is not entirely accurate, with some authors erroneously included in this list, some authors excluded, and some authors\' number of publications incorrectly counted. Please take results with a grain of salt, and verify affiliation of individual authors manually, checking the OpenAlex URL or Scopus URL, if necessary. '),
                        html.Br(),
                        html.Div('The table below displays the top 200 SFU authors by publication count. '),
                        html.Br(),
                        html.Div([
                            dash_table.DataTable(
                                id='author-table', 
                                columns=[{"name": i, "id": i} for i in sfu_authors_table.columns], 
                                data=[],
                                sort_action="native", 
                                sort_mode="multi", 
                                cell_selectable=False,
                                row_selectable="single", 
                                selected_rows=[],
                                style_table={
                                    "overflowY": "auto",
                                    "width": "100%",
                                    "overflowX": "hidden",   
                                },
                                style_header={
                                    'whiteSpace': 'normal', 
                                    'height': '50px', 
                                    'textAlign': 'left'
                                },
                                style_cell_conditional=[
                                {'if': {'column_id': 'Name'}, 'width': '200px'}, # 6%
                                {'if': {'column_id': 'Works Count'}, 'width': '64px'}, # 4%
                                {'if': {'column_id': 'Citations Received'}, 'width': '64px'}, # 4%
                                {'if': {'column_id': 'h-index'}, 'width': '64px'}, # 6%
                                {'if': {'column_id': 'Author Top Published Topic'}, 'width': '300px'}, # 6%
                                {'if': {'column_id': 'Last Published Year'}, 'width': '100px'}, # 6%
                                {'if': {'column_id': 'OpenAlex ID'}, 'width': '120px'}, # 5%
                                {'if': {'column_id': 'ORCID'}, 'width': '150px'}, # 5%
                                {'if': {'column_id': 'Scopus ID'}, 'width': '100px'}, # 6%
                                ],
                                fixed_rows={'headers': True, 'data': 0},
                                page_size=10,
                            )
                        ]), 
                        html.Br(), 
                        html.Div([
                            dash_table.DataTable(
                                id="author-detail",
                                data=[], 
                                columns=[{"name": i, "id": i} for i in sfu_authors_full.columns], 
                                sort_action="native", 
                                sort_mode="multi", 
                                cell_selectable=False,
                                style_cell={
                                    "whiteSpace": "normal", 
                                    "height": "auto", 
                                    "textOverflow": "ellipsis"
                                },
                                style_table={
                                    "width": "100%",
                                },
                                style_cell_conditional=[
                                {'if': {'column_id': 'Name'}, 'width': '80px'}, 
                                {'if': {'column_id': 'OpenAlex ID'}, 'width': '80px'}, 
                                {'if': {'column_id': 'Works Count'}, 'width': '40px'}, 
                                {'if': {'column_id': 'Citations Received'}, 'width': '40px'}, 
                                {'if': {'column_id': 'Alt Names'}, 'width': '150px'}, 
                                {'if': {'column_id': 'Number of Alt Names'}, 'width': '64px'}, 
                                {'if': {'column_id': 'Last Affiliation Names'}, 'width': '100px'}, 
                                {'if': {'column_id': 'Topic Names'}, 'width': '240px'}, 
                                {'if': {'column_id': 'Author Top Published Topic'}, 'width': '64px'}, 
                                {'if': {'column_id': 'Top Topic Publication Count'}, 'width': '64px'}, 
                                {'if': {'column_id': 'Top Topic Proportion'}, 'width': '64px'}, 
                                ]
                            )
                        ]),
                    ]
                )
            ]
        )
    ])
])

#############################################################
##### make interactive components respond to user input #####
#############################################################

##################################
### SUMMARY PAGE INTERACTIVITY ###
##################################
 
@app.callback(
    [
        Output("pub-number", "children"), # pub number
        Output("auth-number", "children"), # auth number
        Output("fwci-number", "children"), # fwci number
        Output("cite-number", "children"), # cite number
        Output("cite-per-pub-number", "children"), # cit/pub number
        Output("h-ind-number", "children"), # h-ind number
        Output("subj-area-pie", "figure"), # pie chart 
        Output("pub-line", "figure"), # pub line
        Output("cite-line", "figure"), # cite line
        Input("summary-toggle", "value") # dropdown
    ]
)
def update_summary_page(time_frame):
    yrs = time_frame

    pub_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Publications']
    pub_number = int(pub_number.iloc[0])
    pub_number = f"{pub_number:,}"

    auth_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Authors']
    auth_number = int(auth_number.iloc[0])
    auth_number = f"{auth_number:,}"

    fwci_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Field-Weighted Citation Impact']
    fwci_number = float(fwci_number.iloc[0])
    fwci_number = f"{fwci_number:.2f}"

    cite_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Citations']
    cite_number = int(cite_number.iloc[0])
    cite_number = f"{cite_number:,}"

    cite_per_pub_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Citations per Publication']
    cite_per_pub_number = float(cite_per_pub_number.iloc[0])
    cite_per_pub_number = f"{cite_per_pub_number:.2f}"
    
    h_ind_number = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'h-Index']
    h_ind_number = int(h_ind_number.iloc[0])
    h_ind_number = f"{h_ind_number:,}"

    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)
    
    pie_dat = sfu_works_domain[sfu_works_domain['publication_year'] >= min_year].groupby(['domain']).sum()['count'].reset_index()
    line_dat = sfu_annual_works[sfu_annual_works['Year'] >= min_year]

    subj_area_pie = px.pie(data_frame=pie_dat, 
                           names=pie_dat['domain'], 
                           values=pie_dat['count'], 
                           color_discrete_sequence=px.colors.qualitative.T10
                           ).update_layout(
                               margin=dict(t=25,b=10)
                            ).update_traces(
                                textinfo='percent+value+label'
                            )

    pub_line = px.line(data_frame=line_dat, 
                       x=line_dat['Year'], 
                       y=line_dat['Publications'],
                       title='SFU Publication by Year', 
                       markers=True, 
                       range_x=[min(line_dat['Year']), max(line_dat['Year'])], 
                       range_y=[0, None]
                       ).update_traces(
                           line_color=px.colors.qualitative.T10[0], line_width=2, marker=dict(color=px.colors.qualitative.T10[0], size=8)
                           ).update_layout(margin=dict(t=25,b=10), 
                                           xaxis=dict(tickmode='array',
                                                      tickvals=list(range(min_year, current_yr+1))))

    cite_line = px.line(data_frame=line_dat,
                        x=line_dat['Year'],
                        y=line_dat['Citations Received'], 
                        title='Citations Received by SFU publications by Year',
                        markers=True, 
                        range_x=[min(line_dat['Year']), max(line_dat['Year'])],
                        range_y=[0, None],
                       ).update_traces(
                           line_color=px.colors.qualitative.T10[1], line_width=2, marker=dict(color=px.colors.qualitative.T10[1], size=8)
                           ).update_layout(margin=dict(t=25, b=25),
                                           xaxis=dict(tickmode='array', 
                                           tickvals=list(range(min_year, current_yr+1))  
                                           ))

    return pub_number, auth_number, fwci_number, cite_number, cite_per_pub_number, h_ind_number, subj_area_pie, pub_line, cite_line



################################
### WORKS PAGE INTERACTIVITY ###
################################

@app.callback( 
    [
        Output("works-table", "data"), 
        Output("works-text-output", "children"),
        Output("works-pg-open-access-pie", "figure"),
        Output("works-pg-publication-type-pie", "figure"), 
        Output("works-pg-citation-percentile-pie", "figure"), 
        Output("works-pg-domain-pie", "figure"), 
        Output("works-pg-sdg-pie", "figure"),
        Output("works-pg-first-auth-pie", "figure"),
        Output("works-pg-collab-pie", "figure"),
    ],
    Input("works-pg-yr-selector", "value")
)
def update_works_page(year_range):
    start_year, end_year = year_range

    total_dat = x[(x['Year']>=start_year) & (x['Year']<=end_year)]
    display_dat_dict = total_dat.head(100).to_dict("records")

    num_pubs = len(total_dat['OpenAlex ID'])

    msg = f"SFU has published {num_pubs:,} works between {start_year} and {end_year}."

    # Pie chart 1: open access
    open_access_dat = open_access_counts[(open_access_counts['Year']>=start_year) & (open_access_counts['Year']<=end_year)]
    pie_open_access = px.pie(open_access_dat, 
                             names="Is Open Access", values="Count", title="Are Publications Open Access?", color_discrete_sequence=px.colors.qualitative.T10
                             ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))
    
    # Pie chart 2: publication types
    pub_type_dat = publication_types[(publication_types['Year']>=start_year) & (publication_types['Year']<=end_year)]
    pie_pub_type = px.pie(pub_type_dat, 
                          names='Publication Type', values='Count', title='Publication Types', color_discrete_sequence=px.colors.qualitative.T10
                          ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    # Pie chart 3: citation percentiles
    citation_dat = citation_percentile_categories[(citation_percentile_categories['Year']>=start_year) & (citation_percentile_categories['Year']<=end_year)]
    pie_cite = px.pie(citation_dat, 
                      names='Citation Percentile Category', values='Count', title='Citation Percentiles', color_discrete_sequence=px.colors.qualitative.T10
                      ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    # Pie chary 4: work domains
    domain_dat = domains_for_works_pg[(domains_for_works_pg['Year']>=start_year) & (domains_for_works_pg['Year']<=end_year)]
    pie_domain = px.pie(domain_dat, 
                        names='Domain', values='Count', title='Publication Domain', color_discrete_sequence=px.colors.qualitative.T10
                        ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    # Pie chart 5: sdg classification
    sdg_dat = sdg_t_f[(sdg_t_f['Year']>=start_year) & (sdg_t_f['Year']<=end_year)]
    pie_sdg = px.pie(sdg_dat, 
                     names='Has SDG', values='Count', title='Has at least one SDG associated', color_discrete_sequence=px.colors.qualitative.T10
                     ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    #Pie chart 6: first authorship
    first_auth_dat = first_auth_sfu[(first_auth_sfu['Year']>=start_year) & (first_auth_sfu['Year']<=end_year)]
    pie_first_auth = px.pie(first_auth_dat, 
                            names='First Author From SFU', values='Count', title='Is First Author from SFU?', color_discrete_sequence=px.colors.qualitative.T10
                            ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    #Pie chart 7: collaboration stats
    collab_dat = collab_statuses[(collab_statuses['Year']>=start_year) & (collab_statuses['Year']<=end_year)]
    pie_collab = px.pie(collab_dat, 
                        names='Collaboration Status', values='Count', title='Collaboration of SFU Publications', color_discrete_sequence=px.colors.qualitative.T10
                        ).update_traces(textposition='inside', textinfo='percent+value+label').update_layout(margin=dict(t=80,b=80))

    # return updated graphics
    return display_dat_dict, msg, pie_open_access, pie_pub_type, pie_cite, pie_domain, pie_sdg, pie_first_auth, pie_collab



#################################
### TOPICS PAGE INTERACTIVITY ###
#################################

@app.callback(
    [
        Output("topic-tree-map", "figure"),
        Output("topic-text-output", "children"), 
        Output("topics-table", "data")
    ],
    [
        Input("topics-toggle", "value"),
        Input("subfield-dropdown", "value")
    ]
)
def update_topic_page(time_frame, subfield):
    yrs = time_frame
    
    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)

    tree_map_dat = sfu_subfields_agg[sfu_subfields_agg['Year'] >= min_year].groupby(['Domain', 'Field', 'Subfield']).sum()['count'].reset_index()
    topic_tree_map = px.treemap(tree_map_dat,
                                path=['Domain', 'Field', 'Subfield'], 
                                values="count", 
                                title="SFU Publications by Domain, Field, and Subfield", 
                                color_discrete_sequence=px.colors.qualitative.T10
                                ).update_layout(margin=dict(t=25))

    if subfield is None:
        return topic_tree_map, f' ', [] 
    
    display_dat = sfu_topics_agg[(sfu_topics_agg['Year']>=min_year) & (sfu_topics_agg['Subfield']==subfield)][['count', 'Topic']]
    display_dat = display_dat.sort_values(by="count", ascending=False)
    display_dat_dict = display_dat.to_dict("records")

    num_topics = len(display_dat['Topic'].unique())
    num_pubs = sum(display_dat['count'])

    msg = f"SFU researchers have published {num_pubs:,} works across {num_topics:,} topics in the {subfield} subfield."

    return topic_tree_map, msg, display_dat_dict



###############################
### SDGS PAGE INTERACTIVITY ###
###############################

@app.callback(
    [
        Output("sdgs-bar", "figure"), 
        Output("sdg-topic-tree-map", "figure")
    ],
    Input("sdg-toggle", "value")
)
def update_sdg_figures(time_frame):
    yrs = time_frame

    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)
    

    legend_map = {
        "SDG 1": "SDG 1 - No poverty", 
        "SDG 2": "SDG 2 - Zero hunger", 
        "SDG 3": "SDG 3 - Good health and well-being", 
        "SDG 4": "SDG 4 - Quality education", 
        "SDG 5": "SDG 5 - Gender equality", 
        "SDG 6": "SDG 6 - Clean water and sanitation", 
        "SDG 7": "SDG 7 - Affordable and clean energy", 
        "SDG 8": "SDG 8 - Decent work and economic growth", 
        "SDG 9": "SDG 9 - Industry, innovation and infrastructure", 
        "SDG 10": "SDG 10 - Reduced inequalities", 
        "SDG 11": "SDG 11 - Sustainable cities and communities", 
        "SDG 12": "SDG 12 - Responsible consumption and production", 
        "SDG 13": "SDG 13 - Climate action", 
        "SDG 14": "SDG 14 - Life below water", 
        "SDG 15": "SDG 15 - Life on land", 
        "SDG 16": "SDG 16 - Peace, justice, and strong institutions", 
        "SDG 17": "SDG 17 - Partnerships for the goals", 
    }

    sdg_bar_dat = sdg_counter[sdg_counter['Year'] >= min_year].groupby('SDG').sum()['Number of Publications'].reset_index()
    sdg_bar = px.bar(data_frame=sdg_bar_dat,
                    x='SDG', 
                    y='Number of Publications', 
                    title='Ranking of SDGs in SFU publications', 
                    color='SDG', 
                    color_discrete_map={
                        "SDG 1": "#E5233D", 
                        "SDG 2": "#DDA73A", 
                        "SDG 3": "#4CA146", 
                        "SDG 4": "#C5192D", 
                        "SDG 5": "#EF402C", 
                        "SDG 6": "#27BFE6", 
                        "SDG 7": "#FBC412", 
                        "SDG 8": "#A31C44", 
                        "SDG 9": "#F26A2D", 
                        "SDG 10": "#E01483", 
                        "SDG 11": "#F89D2A", 
                        "SDG 12": "#BF8D2C", 
                        "SDG 13": "#407F46", 
                        "SDG 14": "#1F97D4", 
                        "SDG 15": "#59BA48", 
                        "SDG 16": "#126A9F", 
                        "SDG 17": "#13496B", 
                    }
                    ).update_xaxes(
                        type='category', 
                        title_font=dict(size=18),
                        tickfont=dict(size=14)
                    ).update_yaxes(
                        title_font=dict(size=18),
                        tickfont=dict(size=14)
                    )

                    
    for trace in sdg_bar.data:
        if trace.name in legend_map:
            trace.name = legend_map[trace.name]

    sdg_bar.update_layout(
        xaxis={'categoryorder':'total descending'}, 
        margin=dict(t=60), 
        legend=dict(traceorder="normal")
    )
    
    sdg_tree_map_dat = sdg_topic_comp_by_year[sdg_topic_comp_by_year['Year'] >= min_year].groupby(['SDG', 'SDG Name', 'Subfield']).sum()['Count'].reset_index()
    sdg_tree_map = px.treemap(data_frame=sdg_tree_map_dat,
                              path=['SDG Name', 'Subfield'], 
                              values='Count', 
                              title="Subfields and SDGs of SFU Publications",
                              color='SDG Name', 
                              color_discrete_map={
                                "No poverty": "#E5233D", 
                                "Zero hunger": "#DDA73A", 
                                "Good health and well-being": "#4CA146", 
                                "Quality Education": "#C5192D", 
                                "Gender equality": "#EF402C", 
                                "Clean water and sanitation": "#27BFE6", 
                                "Affordable and clean energy": "#FBC412", 
                                "Decent work and economic growth": "#A31C44", 
                                "Industry, innovation and infrastructure": "#F26A2D", 
                                "Reduced inequalities": "#E01483", 
                                "Sustainable cities and communities": "#F89D2A", 
                                "Responsible consumption and production": "#BF8D2C", 
                                "Climate action": "#407F46", 
                                "Life below water": "#1F97D4", 
                                "Life on Land": "#59BA48", 
                                "Peace, Justice and strong institutions": "#126A9F", 
                                "Partnerships for the goals": "#13496B", 
                                }
                              )

    return sdg_bar, sdg_tree_map

@app.callback(
    Output("top-sdgs", "data"),
    Input("sdg-pg-yr-selector", "value")
)
def update_sdg_table(year_selected):
    year = year_selected

    filtered_dat = top_sdgs_by_year_tall[top_sdgs_by_year_tall['Year']==year]
    filtered_dat = filtered_dat.sort_values(by="Count", ascending=False)

    filtered_dat = filtered_dat.to_dict("records")

    return filtered_dat

@app.callback(
    Output("sdg-line", "figure"), 
    [
        Input("sdg-toggle", "value"),
        Input("sdg-pg-sdg-selector", "value")
    ]
)
def update_sdg_line(time_frame, selected):
    yrs = time_frame

    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)

    sdg_line_dat = top_sdgs_for_line[top_sdgs_for_line['Year'] >= min_year]

    if not selected:
        return px.line(
            title="SFU SDG Publications by Year"
        ).update_layout(
            xaxis=dict(range=[min_year, top_sdgs_by_year_wide["Year"].max()], 
                              tickmode='array', 
                              tickvals=list(range(min_year, top_sdgs_by_year_wide["Year"].max()+1)))
        )
    
    filter_dat = sdg_line_dat[sdg_line_dat['SDG Number'].isin(selected)]

    sdg_line = px.line(
                    data_frame=filter_dat,
                    x="Year", 
                    y="Publications", 
                    color="SDG Number",
                    color_discrete_map={
                        "SDG 1": "#E5233D", 
                        "SDG 2": "#DDA73A", 
                        "SDG 3": "#4CA146", 
                        "SDG 4": "#C5192D", 
                        "SDG 5": "#EF402C", 
                        "SDG 6": "#27BFE6", 
                        "SDG 7": "#FBC412", 
                        "SDG 8": "#A31C44", 
                        "SDG 9": "#F26A2D", 
                        "SDG 10": "#E01483", 
                        "SDG 11": "#F89D2A", 
                        "SDG 12": "#BF8D2C", 
                        "SDG 13": "#407F46", 
                        "SDG 14": "#1F97D4", 
                        "SDG 15": "#59BA48", 
                        "SDG 16": "#126A9F", 
                        "SDG 17": "#13496B", 
                    },
                    title='SFU SDG Publications by Year', 
                    markers=True, 
                ).update_traces(
                    line_width=2, marker=dict(size=8)
                ).update_layout(
                    xaxis=dict(range=[min_year,top_sdgs_by_year_wide["Year"].max()], 
                               tickmode='array', 
                               tickvals=list(range(min_year, top_sdgs_by_year_wide["Year"].max()+1)))
                )

    return sdg_line



##################################
### AUTHORS PAGE INTERACTIVITY ### 
##################################

@callback(
    [
        Output("author-msg", "children"),
        Output('author-table', 'data'), 
    ],
    Input('author-toggle', 'value')
)
def update_author_table(time_frame):
    yrs = time_frame

    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)

    author_dat = sfu_authors_table[sfu_authors_table['Last Published Year'] >= min_year]

    author_dat = author_dat.head(200)
    author_dat = author_dat.to_dict("records")

    num_auth = sfu_summary_stats.loc[sfu_summary_stats['Time Frame']==yrs, 'Authors'].iloc[0]

    msg = f"There have been {num_auth:,} authors who have published with SFU since {min_year}."

    return msg, author_dat

@callback(
    Output('author-table', 'style_data_conditional'),
    Input('author-table', 'selected_rows')
)
def update_styles(selected_rows):
    return [{
        'if': {'row_index': i },
        'background_color': '#e6f7ff'
    } for i in selected_rows]

@callback(
    Output("author-detail", "data"), 
    [
        Input("author-table", "selected_rows"),
        Input('author-toggle', 'value') 
    ]
)
def update_auth_detail(selected_rows, time_frame):
    yrs = time_frame

    current_yr = datetime.now().year
    if yrs == '5 years':
        min_year = current_yr - 4
    elif yrs == '10 years':
        min_year = current_yr - 9
    else: 
        min_year = min(year_range)

    temp = sfu_authors_table[sfu_authors_table['Last Published Year'] >= min_year]
    temp = temp.head(200)

    if not selected_rows:
        return []
    
    selected_index = selected_rows[0]
    selected_row = temp.iloc[selected_index]
    selected_id = selected_row['OpenAlex ID']

    filtered_detail = sfu_authors_full.loc[sfu_authors_full['OpenAlex ID'] == selected_id]

    return filtered_detail.to_dict("records")


###################
### RUN THE APP ###
###################
#app.run(jupyter_mode="tab", host='localhost', debug = False) # this works locally :)
if __name__ == '__main__':

    ## may need to run the code below if not cooperating when you try to run it 
    """
    # check port 8050 and kill existing process if needed 
    PORT = 8050

    # First check if the port is in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", PORT))
            print(f"Port {PORT} is free.")
        except OSError:
            # Port is in use -> find and kill the process
            killed_any = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.net_connections(kind='inet'):
                        if conn.laddr.port == PORT:
                            print(f"Killing process {proc.pid} ({proc.name()}) using port {PORT}")
                            proc.kill()
                            killed_any = True
                            time.sleep(1)  # wait a bit for OS to free port
                            break
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            if not killed_any:
                print(f"Port {PORT} is in use, but no process could be killed.")
    """

    app.run(jupyter_mode="tab", host='localhost', debug=False)


# In[ ]:





# In[ ]:





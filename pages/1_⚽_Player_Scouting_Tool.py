#%%
from bs4 import BeautifulSoup
import pandas as pd
from pyparsing import col
from sqlalchemy import column
from sympy import CoercionFailed
import unicodedata
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='EPL 21/22 Scouting Database',
    layout='wide',
    page_icon='⚽'
)

#Generate DFs
#%%
url = 'Clean Database.csv'

@st.cache
def get_data(url):
    df_player = pd.read_csv(url,index_col=0)
    return df_player

df_player = get_data(url)

#Create App
#%%
# st.set_page_config(
#     page_title='EPL 21/22 Scouting Database',
#     layout='wide'
# )

st.header('🔎 Player Scouting Tool')
st.markdown("""**Help your favourite team find the right player!**""")

with st.expander('🛎️ Click here for a quick guide'):
    st.markdown(
        """
        1) This tool is divided into 5 sections: Attacking, Buildup, Defending, Pressing and Attacking Position.
        
        2) To find players in a specific league, team or position, utilize the General filters. Remember to untick the "Select All" boxes.

        3) To find players who excel at certain attributes, utilize the Attribute filters. Untick the "Select All" box.

        4) To reset any filter, retick the respective "Select All" boxes.

        5) Every section has a violin plot where you can get a quick sense of player percentile ranks.

            You have the ability to categorize by Position, Competition or Squad.

            There will also be a table of that shows the players' important sub-metrics.
        -----
        Not interested in filtering? Scroll down and dive straight into the data :)

        Have fun being a scout & analyst!


        """
    )

# ----- FILTERS ------
# st.sidebar.header('Filters')

with st.expander('⬇️ Click here for General Filters'):
    st.markdown("""**General Filters**""")

    top1, top2 = st.columns(2)

    with top1:
        team = st.multiselect(
            'Select Team',
            options=df_player['Squad'].unique(),
            # default=list(df_player['Squad'].unique())
        )

        all_options = st.checkbox('Select All Teams (Uncheck when filtering)',value=True)

        if all_options:
            team = list(df_player['Squad'].unique())

    with top2:
        league = st.multiselect(
            'Select League',
            options=df_player['Competition'].unique(),
            # default=list(df_player['Squad'].unique())
        )

        all_options4 = st.checkbox('Select All Leagues (Uncheck when filtering)',value=True)

        if all_options4:
            league = list(df_player['Competition'].unique())    

    left_column, mid_column, right_column = st.columns(3)

    with left_column:
        mins = st.number_input(
            "Minimum 90s Played",
            min_value=df_player['Games'].min(),
            max_value=df_player['Games'].max(),
            value=20.0
        )

    with mid_column:
        pos = st.multiselect(
            "Position",
            options=df_player['Pos'].unique()
        )

        all_options3 = st.checkbox('Select All Positions (Uncheck when filtering)',value=True)

        if all_options3:
            pos=list(df_player['Pos'].unique())

    with right_column:
        mets = st.multiselect(
            "Player",
            options=df_player['Player Name'].unique()
        )

        all_options2 = st.checkbox('Select All Players (Uncheck when filtering)',value=True)

        if all_options2:
            mets=list(df_player['Player Name'].unique())

    st.markdown("""
    
    """)
with st.expander('🦾 Click here for Attribute Filters'): 
    st.markdown("""**Attribute Filters** (min value: 0.0, max value: 1.0)""")
    st.markdown("""Eg: Entering 0.8 would mean you are looking for players in the top 80th percentile and above.""")
    st.markdown("""
    
    """)

    left_column4, mid_column4, right_column4,col4 = st.columns(4)

    with left_column4:
        percone = st.number_input(
            "xG per 90 Percentile More Than",
            min_value=df_player['xG Percentile'].min(),
            max_value=df_player['xG Percentile'].max(),
            value=0.2
        )   


    with mid_column4:
        perctwo = st.number_input(
            "xA per 90 Percentile More Than",
            min_value=df_player['xA Percentile'].min(),
            max_value=df_player['xA Percentile'].max(),
            value=0.2
        )


    with right_column4:
        percthree = st.number_input(
            "Att 3rd Presses Percentile More Than",
            min_value=df_player['P_Att 3rd % Percentile'].min(),
            max_value=df_player['P_Att 3rd % Percentile'].max(),
            value=0.2
        )  

    with col4:
        percfour = st.number_input(
            "Presses Out Of Poss Perc More Than",
            min_value=df_player['Presses OOP Percentile'].min(),
            max_value=df_player['Presses OOP Percentile'].max(),
            value=0.03
        )

    defaultsetting = st.checkbox('Default ALL Percentiles Setting (Uncheck When Filtering)',value=True)
    if defaultsetting:
        percone = 0.2
        perctwo = 0.2
        percthree = 0.2
        percfour = 0.03

link = '[Go To Player Comparison Tool Instead](https://share.streamlit.io/amylikeapple/player-scouting-tool-top-five-leagues/main/Hello.py/Player_Comparison_Tool)'
st.markdown(link,unsafe_allow_html=True)

df_selection = df_player.query(
    "Squad == @team and Games >= @mins and Pos == @pos and `Player Name` == @mets and `xG Percentile` >= @percone and `xA Percentile` >= @perctwo and `P_Att 3rd % Percentile` >= @percthree and `Presses OOP Percentile` >= @percfour and Competition == @league",
    engine='python'
)

#----- CALCULATE BENCHMARK METRICS -----
xGper90 = df_player['xG'].quantile(0.90)
shots90 = df_player['Shots/90'].quantile(0.90)
xGperShot = str(round(df_player['xG/Shot'].quantile(0.90), 2))

xAper90 = df_player['xA'].quantile(0.90)
kp90 = df_player['Key Passes'].quantile(0.90)
progpass = df_player['Prog Pass'].quantile(0.90)

tkl90 = df_player['Tkl'].quantile(0.90)
tklsoop = str(round(df_player['Tkls OOP'].quantile(0.90), 2))
tklatt3rd = str(round(df_player['T_Att 3rd %'].quantile(0.90), 2))

press90 = df_player['Press'].quantile(0.90)
patt3rd = str(round(df_player['P_Att 3rd %'].quantile(0.90), 2))
pressoop = str(round(df_player['Presses OOP'].quantile(0.90), 2))

attpentouches = df_player['Att Pen Touches'].quantile(0.90)
progrec = df_player['Prog Receives'].quantile(0.90)
carries = df_player['Carries'].quantile(0.90)

# ----- XG TABLES ------

st.header('Goal Threat (Per 90 min)')
st.markdown("""**xG/90 Percentiles in Big 5 Leagues**""")
st.markdown("""
            Graph Tips:

            1) Double click on a legend to focus on one category.
            2) Hover over the dots for the player name.
            3) On mobile & zoomed in by accident? Double tap on the chart to reset zoom.
            4) Be patient, the graph will load :)

""")
st.markdown("""

""")
fila = st.selectbox(
    "Categorize xG by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig = px.violin(df_selection, y='xG',hover_data=['Player Name'],points='all',box=True,color=fila)
fig.update_layout(legend=dict(orientation='h'))
st.plotly_chart(fig, use_container_width=True)

attcol1,attcol2,attcol3 = st.columns([1,2,1])

with attcol2:
    st.markdown("""
    
        **Deeper Goal Threat Statistics**
        
        90th percentile benchmarks for reference:
    
    """)
    st.text(f"xG/90: {xGper90}  Shots/90: {shots90}  xG/Shot: {xGperShot}")
    st.dataframe(df_selection[list(df_selection.columns)[:9]].drop(columns=['Competition']).sort_values(by=['xG'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

    with st.expander('Metrics Explanation'):
        st.markdown(
            """
            **xG:** Expected Goals per 90 mins. 

            **xG/Shot:** How much xG every shot generates. This is a good indication of how potent at finishing the player is.

            """
        )   

# left_column_1,right_column_1 = st.columns(2)

# with left_column_1:
#     st.header('Goal Threat (Per 90 min)')
#     st.markdown("""**xG Percentiles in Big 5 Leagues**""")
#     # st.plotly_chart(fig, use_container_width=True)
#     st.text('90th Percentile Benchmarks')
#     st.text(f"xG/90: {xGper90}  Shots/90: {shots90}  xG/Shot: {xGperShot}")
#     st.dataframe(df_selection[list(df_selection.columns)[:9]].drop(columns=['Competition']).sort_values(by=['xG'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

# with right_column_1:
#     st.text('90th Percentile Benchmarks')
#     st.text(f"xG/90: {xGper90}  Shots/90: {shots90}  xG/Shot: {xGperShot}")
#     st.dataframe(df_selection[list(df_selection.columns)[:9]].drop(columns=['Competition']).sort_values(by=['xG'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

# ----- BUILD UP TABLES ------
buildup = ['Player Name','Pos','Squad','Games','xG'] + list(df_selection.columns)[10:18]

st.header('Build Up (Per 90 min)')
st.markdown("""**xA/90 Percentiles in Big 5 Leagues**""")
filb = st.selectbox(
    "Categorize xA by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig2 = px.violin(df_selection, y='xA',hover_data=['Player Name'],points='all',box=True,color=filb)
fig2.update_layout(legend=dict(orientation='h'))
st.plotly_chart(fig2, use_container_width=True)

bucol1,bucol2,bucol3 = st.columns([1,2,1])

with bucol2:
    st.markdown("""
    
        **Deeper Build Up Statistics**
        
        90th percentile benchmarks for reference:
    
    """)
    st.text(f"xA/90: {xAper90}  KP/90: {kp90}  Prog Passes/90: {progpass}")
    st.dataframe(df_selection[buildup].drop(columns=['18Yrd Passes','Att Passes','Cmp Passes','Pass Dist']).sort_values(by=['xA'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

    with st.expander('Metrics Explanation'):
        st.markdown(
            """
            **xA:** Expected Assists per 90 mins. 

            **Key Passes:** Passes made that directly led to a shot per 90 mins.

            **Prog Pass:** Passes made that moved more than 18 yards per 90 mins.

            **Prog Pass Dist:** Total distance of progressive passes, a good indicator of how long the team plays.

            """
        )

# with right_column_1:
#     st.header('Build Up (Per 90 min)')
#     st.text('90th Percentile Benchmarks')
#     st.text(f"xA/90: {xAper90}  KP/90: {kp90}  Prog Passes/90: {progpass}")
#     st.dataframe(df_selection[buildup].drop(columns=['18Yrd Passes','Att Passes','Cmp Passes','Pass Dist']).sort_values(by=['xA'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

# ----- DEFENDING TABLES ------
defending = ['Player Name','Pos','Squad','Games','xG'] + list(df_selection.columns)[18:24]
pressing = ['Player Name','Pos','Squad','Games','xG'] + list(df_selection.columns)[24:30]

st.header('Defending (Per 90 min)')
st.markdown("""**Tackles Out Of Poss Percentiles in Big 5 Leagues**""")
fild = st.selectbox(
    "Categorize Tackles OOP by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig3 = px.violin(df_selection, y='Tkls OOP',hover_data=['Player Name'],points='all',box=True,color=fild)
fig3.update_layout(legend=dict(orientation='h'))
st.plotly_chart(fig3, use_container_width=True)

defcol1,defcol2,defcol3 = st.columns([1,2,1])

with defcol2:
    st.markdown("""
    
        **Deeper Defensive Statistics**
        
        90th percentile benchmarks for reference:
    
    """)
    st.text(f"Tkls/90: {tkl90}  Tkls Out Of Poss/90: {tklsoop}  Tkls in Att 3rd %: {tklatt3rd}")
    st.dataframe(df_selection[defending].sort_values(by=['Tkls OOP'], ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Tkl','Tkls OOP','Tkl Won','T_Att 3rd %','T_Mid 3rd %']).set_precision(2))
    with st.expander('Metrics Explanation'):
        st.markdown(
            """
            **Tkls OOP:** Number of tackles made per 90 min when the team is out of possession. This evens out lesser Tkls/90 numbers for dominant teams.

            **T_Att 3rd %:** Percentage of tackles made that were in the Att 3rd. A good measure of the high press, which is a hallmark of the modern game and an effective way of defending.
            
            """
        )

# left_column_2,right_column_2 = st.columns(2)

# with left_column_2:
#     st.header('Defending (Per 90 min)')
#     st.text('90th Percentile Benchmarks')
#     st.text(f"Tkls/90: {tkl90}  Tkls Out Of Poss/90: {tklsoop}  Tkls in Att 3rd %: {tklatt3rd}")
#     st.dataframe(df_selection[defending].sort_values(by=['Tkls OOP'], ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Tkl','Tkls OOP','Tkl Won','T_Att 3rd %','T_Mid 3rd %']).set_precision(2))

# with right_column_2:
#     st.header('Pressing (Per 90 min)')
#     st.text('90th Percentile Benchmarks')
#     st.text(f"Presses/90: {press90}  Presses In Att 3rd: {patt3rd}  Presses Out Of Poss/90: {pressoop}")
#     st.dataframe(df_selection[pressing].sort_values(by=['Presses OOP'],ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Press','Presses OOP','Succ Presses','P_Att 3rd %','P_Med 3rd %']).set_precision(2))

# ----- PRESSING TABLES ------
pressing = ['Player Name','Pos','Squad','Games','xG'] + list(df_selection.columns)[24:30]

st.header('Pressing (Per 90 min)')
st.markdown("""**Presses Out Of Possession Percentiles in Big 5 Leagues**""")
fild = st.selectbox(
    "Categorize Presses OOP by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig4 = px.violin(df_selection, y='Presses OOP',hover_data=['Player Name'],points='all',box=True,color=fild)
fig4.update_layout(legend=dict(orientation='h'))
st.plotly_chart(fig4, use_container_width=True)

presscol1,presscol2,presscol3 = st.columns([1,2,1])

with presscol2:
    st.markdown("""
    
        **Deeper Pressing Statistics**
        
        90th percentile benchmarks for reference:
    
    """)
    st.text(f"Presses/90: {press90}  Presses In Att 3rd: {patt3rd}  Presses Out Of Poss/90: {pressoop}")
    st.dataframe(df_selection[pressing].sort_values(by=['Presses OOP'],ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Press','Presses OOP','Succ Presses','P_Att 3rd %','P_Med 3rd %']).set_precision(2))
    with st.expander('Metrics Explanation'):
        st.markdown(
            """
            **Presses OOP:** Number of presses made per 90 min when the team is out of possession. This evens out lesser Presses/90 numbers for dominant teams.

            **P_Att 3rd %:** Percentage of presses made that were in the Att 3rd. A good measure of high pressing, which is a hallmark of the modern game and an effective way of defending.

            
            """
        )


# ----- POSSESION TABLES ------
possession = ['Player Name','Pos','Squad','Games','xG'] + list(df_selection.columns)[31:35]

st.header('Attacking Position (Per 90 min)')
st.markdown("""**Att Penalty Touches Percentiles in Big 5 Leagues**""")
filp = st.selectbox(
    "Categorize Attacking Penalty Touches/90 by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig5 = px.violin(df_selection, y='Att Pen Touches',hover_data=['Player Name'],points='all',box=True,color=filp)
fig5.update_layout(legend=dict(orientation='h'))
st.plotly_chart(fig5, use_container_width=True)

posscol1,posscol2,posscol3 = st.columns([1,2,1])

with posscol2:
    st.markdown("""
    
        **Deeper Attacking Position Statistics**
        
        90th percentile benchmarks for reference:
    
    """)
    st.text(f"Att Pen Touches/90: {attpentouches}  Prog Passes Rec: {progrec}  Carries: {carries}")
    st.dataframe(df_selection[possession].sort_values(by=['Att Pen Touches'],ascending=False).style.background_gradient(cmap='Blues').set_precision(2))
    with st.expander('Metrics Explanation'):
        st.markdown(
            """
            **Att Pen Touches:** Number of touches made in the penalty box per 90 min

            **Prog Receives:** Number to passes received per 90 in a position that moves play up the field. A good measure of attacking position.

            **Carries:** Actions that move the ball forward.

            **Prog Carries Dist:** Total distance of progressive carries.
            
            """
        )
# left_column_3,right_column_3 = st.columns(2)

# with left_column_3:
#     st.header('Attacking Position (Per 90 min)')
#     st.text('90th Percentile Benchmarks')
#     st.text(f"Att Pen Touches/90: {attpentouches}  Prog Passes Rec: {progrec}  Carries: {carries}")
#     st.dataframe(df_selection[possession].sort_values(by=['xG'],ascending=False).style.background_gradient(cmap='Blues').set_precision(2))


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# df_selection2 = df_selection.sort_values(by=['xG per 90'],ascending=False)

# fig_player_data = go.Figure(data=[go.Table(columnwidth = [200],
#     header=dict(values=list(df_selection2.columns)[:8],
#                 fill_color='wheat',
#                 align='left'),
#     cells=dict(values=[df_selection2['Player Name'],df_selection2['Pos'],df_selection2['Squad'],
#     df_selection2['Games'],df_selection2['Gls'],df_selection2['Sh/90'],df_selection2['xG per Shot'],
#     df_selection2['xG per 90']],
#                fill_color='white',
#                align='left'))
# ])

# main_column,main2_column=st.columns(2)
# main_column.plotly_chart(fig_player_data,use_container_width=True)

#Tomorrow
#Clean up metrics, add position filter, add comparison radar chart

# %%

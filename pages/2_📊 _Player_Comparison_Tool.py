#%%
from bs4 import BeautifulSoup
from matplotlib.pyplot import margins
import pandas as pd
from pyparsing import col
from sqlalchemy import column
from sympy import CoercionFailed
import unicodedata
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

#Generate DFs
#%%
st.set_page_config(
    page_title='Scouting Tool',
    layout='wide'
)

url = 'Clean Database.csv'

@st.cache
def get_data(url):
    df_player = pd.read_csv(url,index_col=0)
    return df_player

df_player = get_data(url)

df_player = df_player[['Player Name', 'Pos', 'Squad', 'Competition', 'Games','xG Percentile', 'Shots/90 Percentile',
       'xG/Shot Percentile','xA Percentile','Key Passes Percentile','Prog Pass Percentile','Tkl Percentile','Tkls OOP Percentile',
       'T_Att 3rd % Percentile','Press Percentile',
       'Presses OOP Percentile','P_Att 3rd % Percentile','Touches Percentile',
       'Att Pen Touches Percentile', 'Prog Receives Percentile',]]

#---CREATE APP---
#%%
# st.set_page_config(
#     page_title='Scouting Tool',
#     layout='wide'
# )

st.header('📊 Player Comparison Tool')

st.subheader('Select 2 players for comparison')

link = '[Go To Player Scouting Tool Instead](https://share.streamlit.io/amylikeapple/player-scouting-tool-top-five-leagues/main/Hello.py/Player_Scouting_Tool)'
st.markdown(link,unsafe_allow_html=True)

#---FILTERS---
#%%

left_column, right_column = st.columns(2)

with left_column:
    mets = st.multiselect(
        "Player 1",
        options=df_player['Player Name'].unique(),
        default='João Cancelo'
    )

with right_column:
    mets2 = st.multiselect(
        "Player 2",
        options=df_player['Player Name'].unique(),
        default='Harry Maguire'
    ) 

df_player_one = df_player.query(
    "`Player Name` == @mets",
    engine='python'
)

df_player_two = df_player.query(
    "`Player Name` == @mets2",
    engine='python'
)
# %%

st.dataframe(df_player_one.style.set_precision(2))
st.dataframe(df_player_two.style.set_precision(2))


#---CREATE RADAR CHART---
#%%
list1 = list(df_player_one.columns)[5:]
columns1 = ['xG',
 'Shots',
 'xG/Shot',
 'xA',
 'Key Passes',
 'Prog Passes',
 'Tackles',
 'Tackles OOP ',
 'Tackles Att 3rd %',
 'Presses ',
 'Presses OOP ',
 'Presses Att 3rd % ',
 'Touches',
 'Att Pen Touches',
 'Prog Passes Received']

fig = px.bar_polar(
    r=[df_player_one[list1[0]].values[0],
    df_player_one[list1[1]].values[0],
    df_player_one[list1[2]].values[0],
    df_player_one[list1[3]].values[0],
    df_player_one[list1[4]].values[0],
    df_player_one[list1[5]].values[0],
    df_player_one[list1[6]].values[0],
    df_player_one[list1[7]].values[0],
    df_player_one[list1[8]].values[0],
    df_player_one[list1[9]].values[0],
    df_player_one[list1[10]].values[0],
    df_player_one[list1[11]].values[0],
    df_player_one[list1[12]].values[0],
    df_player_one[list1[13]].values[0],
    df_player_one[list1[14]].values[0],
    ],
    theta=columns1,
    template="plotly_dark",
    color_discrete_sequence= px.colors.sequential.Oranges,
    range_r=[0,1]
)

fig.update_layout(font=dict(size=10),margin_autoexpand=False,margin=dict(l=120, r=60, t=10, b=10),modebar_remove=['zoom', 'select'],dragmode = False)


list2 = list(df_player_two.columns)[5:]
columns2 = ['xG',
 'Shots',
 'xG/Shot',
 'xA',
 'Key Passes',
 'Prog Passes',
 'Tackles',
 'Tackles OOP ',
 'Tackles Att 3rd %',
 'Presses ',
 'Presses OOP ',
 'Presses Att 3rd % ',
 'Touches',
 'Att Pen Touches',
 'Prog Passes Received']

fig2 = px.bar_polar(
    r=[df_player_two[list1[0]].values[0],
    df_player_two[list1[1]].values[0],
    df_player_two[list1[2]].values[0],
    df_player_two[list1[3]].values[0],
    df_player_two[list1[4]].values[0],
    df_player_two[list1[5]].values[0],
    df_player_two[list1[6]].values[0],
    df_player_two[list1[7]].values[0],
    df_player_two[list1[8]].values[0],
    df_player_two[list1[9]].values[0],
    df_player_two[list1[10]].values[0],
    df_player_two[list1[11]].values[0],
    df_player_two[list1[12]].values[0],
    df_player_two[list1[13]].values[0],
    df_player_two[list1[14]].values[0],
    ],
    theta=columns2,
    template="plotly_dark",
    color_discrete_sequence= px.colors.sequential.Pinkyl,
    range_r=[0,1]
)

fig2.update_layout(font=dict(size=10),margin_autoexpand=False,margin=dict(l=120, r=60, t=10, b=10),modebar_remove=['zoom', 'select'],dragmode = False)

left_column1, right_column1 = st.columns(2)
with left_column1:
    st.subheader(mets[0])
    st.text(df_player_one['Pos'].values[0] + ', ' + df_player_one['Squad'].values[0])
    st.plotly_chart(fig,use_container_width=True)

with right_column1:
    st.subheader(mets2[0])
    st.text(df_player_two['Pos'].values[0] + ', ' + df_player_two['Squad'].values[0])
    st.plotly_chart(fig2,use_container_width=True)
# %%

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

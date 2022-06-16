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
import statsmodels.api as sm

st.set_page_config(
    page_title='EPL 21/22 Scouting Database',
    layout='wide',
    page_icon='⚽'
)

#Generate DFs
#%%
# str='https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F9%2F{}%2FPremier-League-Stats&div=div_stats_{}'
# dynamic_url = ['shooting','passing','gca','defense','possession']
raw_dfs=[]

# for i in dynamic_url:
#     url=str.format(i,i)
#     print(url)
#     df=pd.read_html(url)[0]
#     df.columns=df.columns.droplevel(0)
#     raw_dfs.append(df)

file_names = [
    'FBRef Database Top Five Leagues - Shooting.csv',
    'FBRef Database Top Five Leagues - Passing.csv',
    'FBRef Database Top Five Leagues - GCA.csv',
    'FBRef Database Top Five Leagues - Defence.csv',
    'FBRef Database Top Five Leagues - Poss.csv'
]

for i in file_names:
    df=pd.read_csv(i,header=[0, 1])
    df.columns=df.columns.droplevel(0)
    raw_dfs.append(df)    

#Data Cleaning
# %%

#Basic Cleaning - Remove of unwanted columns and rows
cleaned_dfs = []
for i in list(range(0,5)):
    df=raw_dfs[i]
    df=df.convert_dtypes()
    df=df.drop(columns=['Matches'])
    df=df.drop(df[df.Player == 'Player'].index)
    cleaned_dfs.append(df)

#Creating sub dataframes and converting to correct dtypes
#Shooting
dfshooting = cleaned_dfs[0]
for i in list(dfshooting.columns)[6:]:
    dfshooting[i]=pd.to_numeric(dfshooting[i],errors='coerce')

#Passing
cleaned_dfs[1].columns = ['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', '90s', 'Cmp',
       'Att', 'Cmp%', 'TotDist', 'PrgDist', 'Cmp2', 'Att2', 'Cmp%1', 'Cmp3', 'Att3',
       'Cmp%2', 'Cmp4', 'Att4', 'Cmp%3', 'Ast', 'xA', 'A-xA', 'KP', '1/3', 'PPA',
       'CrsPA', 'Prog']
dfpassing = cleaned_dfs[1][list(cleaned_dfs[1])[:14]+list(cleaned_dfs[1])[23:]]
for i in list(dfpassing.columns)[6:]:
    dfpassing[i]=pd.to_numeric(dfpassing[i],errors='coerce')

#SCA & GCA
dfgca = cleaned_dfs[2][['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', '90s', 'SCA','SCA90','GCA','GCA90']]
for i in list(dfgca.columns)[6:]:
    dfgca[i]=pd.to_numeric(dfgca[i],errors='coerce')

#Defense
cleaned_dfs[3].columns = ['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', '90s', 'Tkl',
       'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl1', 'Att', 'Tkl%', 'Past',
       'Press', 'Succ', 'Press Succ %', 'Def 3rd1', 'Mid 3rd1', 'Att 3rd1', 'Blocks', 'Sh',
       'ShSv', 'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err']

dfdefense = cleaned_dfs[3][['Rk', 'Player', 'Nation', 'Pos', 'Squad','Comp', 'Age', 'Born', '90s', 'Tkl',
       'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd','Blocks', 'Sh',
       'ShSv', 'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err']]

#Add Poss Stats
teamposs = pd.read_csv('FBRef Database Top Five Leagues - Team Poss.csv')

dfdefensemerge = pd.merge(dfdefense,teamposs, on='Squad',how='left').drop(columns=['Rk_y'])

for i in list(dfdefensemerge.columns)[6:]:
    dfdefensemerge[i]=pd.to_numeric(dfdefensemerge[i],errors='coerce')

#Press
dfpress = cleaned_dfs[3][['Press', 'Succ', 'Press Succ %', 'Def 3rd1', 'Mid 3rd1', 'Att 3rd1']]
for i in list(dfpress.columns):
    dfpress[i]=pd.to_numeric(dfpress[i],errors='coerce')

#Possesion
cleaned_dfs[4].columns = ['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', '90s',
       'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen',
       'Live', 'Succ', 'Att', 'Succ%', '#Pl', 'Megs', 'Carries', 'TotDist',
       'PrgDist', 'Prog', '1/3', 'CPA', 'Mis', 'Dis', 'Targ', 'Rec', 'Rec%',
       'Prog Receives']
dfposs = cleaned_dfs[4][['Rk', 'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', '90s',
       'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Targ', 'Rec', 'Rec%','Prog Receives']]
for i in list(dfposs.columns)[6:]:
    dfposs[i]=pd.to_numeric(dfposs[i],errors='coerce')

#Dribbling
dfdribble = cleaned_dfs[4][['Live', 'Succ', 'Att', 'Succ%','Carries', 'TotDist',
       'PrgDist', 'Prog', '1/3', 'CPA']]
for i in list(dfdribble.columns):
    dfdribble[i]=pd.to_numeric(dfdribble[i],errors='coerce')

# dfshooting,dfpassing,dfgca,dfdefense,dfposs =raw_dfs[0],raw_dfs[1],raw_dfs[2],raw_dfs[3],raw_dfs[4]
# dftackle = dfdefense[list(dfdefense.columns)[:12]]
# dfpress_and_tklint = dfdefense[list(dfdefense.columns)[17:]].drop(columns=['Matches'])

# #Clean up dtypes and names
# dfshooting = dfshooting.convert_dtypes()

# for i in list(dfshooting.columns)[5:]:
#     dfshooting[i]=pd.to_numeric(dfshooting[i],errors='coerce')



#Add needed metrics
#%%
# dfshooting['xG per 90'] = dfshooting['xG']/dfshooting['90s']
dfshooting['xG per Shot'] = dfshooting['xG']/dfshooting['Sh']
# dfpassing['xA per 90'] = dfpassing['xA']/dfpassing['90s']
# dfpassing['Attempted Passes per 90'] = dfpassing['Att']/dfpassing['90s']
# dfpassing['Completed Passes per 90'] = dfpassing['Cmp']/dfpassing['90s']
# dfpassing['Total Passing Distance per 90'] = dfpassing['TotDist']/dfpassing['90s']
# dfpassing['Prog Pass Dist/90']=dfpassing['PrgDist']/dfpassing['90s']
# dfpassing['KP/90']=dfpassing['KP']/dfpassing['90s']
# dfpassing['Passes Into 18 Yard Box per 90']=dfpassing['PPA']/dfpassing['90s']
# dfpassing['ProgP/90']=dfpassing['Prog']/dfpassing['90s']
# dfdefense['Tackles/90']=dfdefense['Tkl']/dfdefense['90s']
# dfdefense['Tackles Per Touch']=dfdefense['Tkl']/dfposs['Touches']
# dfdefense['Tackles Won Per 90']=dfdefense['TklW']/dfdefense['90s']
dfdefensemerge['T_Att 3rd %']=dfdefensemerge['Att 3rd']/dfdefensemerge['Tkl']
dfdefensemerge['T_Mid 3rd %']=dfdefensemerge['Mid 3rd']/dfdefensemerge['Tkl']
dfdefensemerge['T_Def 3rd %']=dfdefensemerge['Def 3rd']/dfdefensemerge['Tkl']
dfdefensemerge['Tkls OOP'] = dfdefensemerge['Tkl']/(1-(dfdefensemerge['Poss']/100))
# dfpress['Presses/90']=dfpress['Press']/dfdefense['90s']
# dfpress['Presses Per Touch']=dfpress['Press']/dfposs['Touches']
# dfpress['Succesful Presses Per 90']=dfpress['Succ']/dfdefense['90s']
dfpress['P_Att 3rd %']=dfpress['Att 3rd1']/dfpress['Press']
dfpress['P_Med 3rd %']=dfpress['Mid 3rd1']/dfpress['Press']
dfpress['P_Def 3rd %']=dfpress['Def 3rd1']/dfpress['Press']
dfpress['Presses OOP']=dfpress['Press']/(1-(dfdefensemerge['Poss']/100))
# dfposs['Touches Per 90']=dfposs['Touches']/dfposs['90s']
# dfposs['Att Pen Touches Per 90']=dfposs['Att Pen']/dfposs['90s']
# dfposs['Att 3rd Touches Per 90']=dfposs['Att 3rd']/dfposs['90s']
# dfdribble['Carries Per 90']=dfdribble['Carries']/dfposs['90s']
# dfdribble['P_Carry_Dist/90']=dfdribble['TotDist']/dfposs['90s']
# dfposs['P_Rec_Passes/90']=dfposs['Prog Receives']/dfposs['90s']

#Rename Repeats
dfpassing['Prog Pass Dist'] = dfpassing['PrgDist']
dfdribble['Prog Carries Dist'] = dfdribble['PrgDist']
# %%


#Creating Final DF
#%%
df_player = pd.concat(
    [
        dfshooting[['Player', 'Pos', 'Squad', 'Comp','90s','Gls', 'xG', 'Sh/90', 'xG per Shot']],
        dfpassing[['Ast', 'xA', 'Att', 'Cmp', 'TotDist', 'KP', 'PPA', 'Prog','Prog Pass Dist']],
        dfdefensemerge[['Tkl', 'Tkls OOP', 'TklW', 'T_Att 3rd %', 'T_Mid 3rd %', 'T_Def 3rd %']],
        dfpress[['Press', 'Presses OOP', 'Succ', 'P_Att 3rd %', 'P_Med 3rd %', 'P_Def 3rd %']],
        dfposs[['Touches', 'Att Pen', 'Prog Receives']],
        dfdribble[['Carries', 'Prog Carries Dist']]
    ],axis=1
)
# %%


#Split Player Names
#%%
# clean_names = []
# for i in list(df_player['Player']):
#     clean = unicodedata.normalize('NFKD', i).encode('ascii', 'ignore')
#     clean = clean.decode('utf-8')
#     df_player.loc[df_player['Player'] == i, 'Player'] = clean

# df_player['Games'] = df_player['90s']

df_player[['Player Name', 'Code']] = df_player['Player'].str.split('\\', 1, expand=True)
df_player=df_player.drop(columns=['Code'])
cols = df_player.columns.tolist()
cols = cols[-1:] + cols[:-1]
df_player=df_player[cols]
df_player=df_player.drop(columns=['Player'])

#%%
df_player['Games'] = df_player['90s']
cols2 = list(df_player.columns)[5:]
cols2 = cols2[-1:] + cols2[:-1]
cols2 = ['Player Name', 'Pos', 'Squad','Comp'] + cols2
df_player=df_player[cols2]
# df_player=df_player.drop(columns=['90s'])

df_player = df_player.fillna(0)


#Rename Repeat Columns
#%%

df_player.columns = ['Player Name',
 'Pos',
 'Squad',
 'Competition',
 'Games',
 'Gls',
 'xG',
 'Shots/90',
 'xG/Shot',
 'Ast',
 'xA',
 'Att Passes',
 'Cmp Passes',
 'Pass Dist',
 'Key Passes',
 '18Yrd Passes',
 'Prog Pass',
 'Prog Pass Dist',
 'Tkl',
 'Tkls OOP',
 'Tkl Won',
 'T_Att 3rd %',
 'T_Mid 3rd %',
 'T_Def 3rd %',
 'Press',
 'Presses OOP',
 'Succ Presses',
 'P_Att 3rd %',
 'P_Med 3rd %',
 'P_Def 3rd %',
 'Touches',
 'Att Pen Touches',
 'Prog Receives',
 'Carries',
 'Prog Carries Dist']

#Add Percentiles
#%%
for i in list(df_player.columns)[5:]:
    col = i + ' ' + 'Percentile'
    df_player[col] = df_player[i].rank(pct=True)

# %%

#Create App
#%%
# st.set_page_config(
#     page_title='EPL 21/22 Scouting Database',
#     layout='wide'
# )

st.header('🔎 Player Scouting Tool')

with st.expander('⬇️ Click here for a quick guide'):
    st.markdown(
        """
        1) This tool is divided into 5 sections: Attacking, Buildup, Defending, Pressing and Attacking Position.
        
        2) To find players in a specific league, team or position, select them under the relevant filters and uncheck the "Select All" boxes.

        3) To find players who excel at certain attributes, utilize the percentile filters. Uncheck the "Select All" box.
        
            As an example, entering 0.8 would mean you are looking for players in the top 80th percentile and above.

        4) To reset any filter, check the respective "Select All" boxes.

        5) Every section has a violin plot where you can get a quick sense of player percentile ranks within your selected segement. 

            You have the ability to categorize by Position, Competition or Squad.

            There will also be a table of that shows the players' important sub-metrics.

        """
    )

st.markdown(
    """
    
    
    """
)

# ----- FILTERS ------
# st.sidebar.header('Filters')

with st.expander('⬇️ Click here for filters'):
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
    st.markdown("""**Attribute Filters**""")

    left_column4, mid_column4, right_column4,col4 = st.columns(4)

    with left_column4:
        percone = st.number_input(
            "xG per 90 Percentile More Than (min:0.0, max:1.0)",
            min_value=df_player['xG Percentile'].min(),
            max_value=df_player['xG Percentile'].max(),
            value=0.2
        )   


    with mid_column4:
        perctwo = st.number_input(
            "xA per 90 Percentile More Than (min:0.0, max:1.0)",
            min_value=df_player['xA Percentile'].min(),
            max_value=df_player['xA Percentile'].max(),
            value=0.2
        )


    with right_column4:
        percthree = st.number_input(
            "Att 3rd Presses Percentile More Than (min:0.0, max:1.0)",
            min_value=df_player['P_Att 3rd % Percentile'].min(),
            max_value=df_player['P_Att 3rd % Percentile'].max(),
            value=0.2
        )  

    with col4:
        percfour = st.number_input(
            "Presses Out Of Poss Perc More Than (min:0.0, max:1.0)",
            min_value=df_player['Presses OOP Percentile'].min(),
            max_value=df_player['Presses OOP Percentile'].max(),
            value=0.2
        )

    defaultsetting = st.checkbox('Default ALL Percentiles Setting (Uncheck When Filtering)',value=True)
    if defaultsetting:
        percone = 0.2
        perctwo = 0.2
        percthree = 0.2
        percfour = 0.2

link = '[Go To Player Comparison Tool Instead](https://share.streamlit.io/amylikeapple/player-scouting-tool-top-5-european-leagues/main/Hello.py/📊 _Player_Comparison_Tool)'
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
fila = st.selectbox(
    "Categorize xG by:",
    options=['Pos','Competition','Squad'],
    index=1
)
fig = px.violin(df_selection, y='xG',hover_data=['Player Name'],points='all',box=True,color=fila)
st.plotly_chart(fig, use_container_width=True)

attcol1,attcol2,attcol3 = st.columns([1,2,1])

with attcol2:
    st.markdown("""**90th Percentile Benchmarks**""")
    st.text(f"xG/90: {xGper90}  Shots/90: {shots90}  xG/Shot: {xGperShot}")
    st.dataframe(df_selection[list(df_selection.columns)[:9]].drop(columns=['Competition']).sort_values(by=['xG'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

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
st.plotly_chart(fig2, use_container_width=True)

bucol1,bucol2,bucol3 = st.columns([1,2,1])

with bucol2:
    st.markdown("""**90th Percentile Benchmarks**""")
    st.text(f"xA/90: {xAper90}  KP/90: {kp90}  Prog Passes/90: {progpass}")
    st.dataframe(df_selection[buildup].drop(columns=['18Yrd Passes','Att Passes','Cmp Passes','Pass Dist']).sort_values(by=['xA'],ascending=False).style.background_gradient(cmap='Greens').set_precision(2))

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
st.plotly_chart(fig3, use_container_width=True)

defcol1,defcol2,defcol3 = st.columns([1,2,1])

with defcol2:
    st.markdown("""**90th Percentile Benchmarks**""")
    st.text(f"Tkls/90: {tkl90}  Tkls Out Of Poss/90: {tklsoop}  Tkls in Att 3rd %: {tklatt3rd}")
    st.dataframe(df_selection[defending].sort_values(by=['Tkls OOP'], ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Tkl','Tkls OOP','Tkl Won','T_Att 3rd %','T_Mid 3rd %']).set_precision(2))

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
st.plotly_chart(fig4, use_container_width=True)

presscol1,presscol2,presscol3 = st.columns([1,2,1])

with presscol2:
    st.markdown("""**90th Percentile Benchmarks**""")
    st.text(f"Presses/90: {press90}  Presses In Att 3rd: {patt3rd}  Presses Out Of Poss/90: {pressoop}")
    st.dataframe(df_selection[pressing].sort_values(by=['Presses OOP'],ascending=False).style.background_gradient(cmap='Oranges',subset=['xG','Press','Presses OOP','Succ Presses','P_Att 3rd %','P_Med 3rd %']).set_precision(2))


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
st.plotly_chart(fig5, use_container_width=True)

posscol1,posscol2,posscol3 = st.columns([1,2,1])

with posscol2:
    st.markdown("""**90th Percentile Benchmarks**""")
    st.text(f"Att Pen Touches/90: {attpentouches}  Prog Passes Rec: {progrec}  Carries: {carries}")
    st.dataframe(df_selection[possession].sort_values(by=['Att Pen Touches'],ascending=False).style.background_gradient(cmap='Blues').set_precision(2))
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

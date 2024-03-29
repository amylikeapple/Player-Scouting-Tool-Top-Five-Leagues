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


#Save to CSV
#%%
df_player.to_csv('Clean Database.csv')
# %%

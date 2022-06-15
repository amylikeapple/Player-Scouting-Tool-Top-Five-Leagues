import streamlit as st

st.set_page_config(
    page_title="Player Scouting & Comparison Tool",
    page_icon="⚽"
)

st.title("Big 5 European Leagues Player Scouting & Comparison Tool")

st.sidebar.success("Select A Tool Above")

st.markdown(
    """
    Welcome to The FPL Analyst's Player Scouting & Performance Tools. 
    
    Utilize the Player Scouting Tool to discover players based on key attributes in goal scoring, defensive actions and pressing actions.

    Utilize the Player Comparison Tool to compare 2 players and highlight their strengths and weaknesses.

    Players are ranked according to percentiles relative to all players in the Big 5 European Leagues.

    Data gathered from FBRef

    **👈 Select a tool from the side bar to get started** 
    ### Looking for analyses and deepdives of teams and players?
    - Check out [The FPL Analyst Blog](https://the-fpl-analyst.webflow.io/)

"""
)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
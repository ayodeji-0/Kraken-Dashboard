import streamlit as st
import json

#from nav import create_navbar

## Page Layout
st.set_page_config(layout="wide")

## Page Selection Menu

# from streamlit_navigation_bar import st_navbar

#page = st_navbar(["Home", "Overview_🧑‍💻", "Performance 🎯", "Tools 🛠️"], selected= "Overview_🧑‍💻")#, show_sidebar= True)

# if page == "Home":
#     st.switch_page("Home.py")
# elif page == "Overview 🧑‍💻":
#     st.switch_page("pages\Overview_🧑‍💻.py")
# elif page == "Performance 🎯":
#     st.switch_page("pages\Performance_🎯.py")
# elif page == "Tools 🛠️":
#     st.experimental_set_query_params("pages\Tools_🛠️.py")



st.markdown(
                """
                <style>
                div[data-baseweb="base-input"] > markdown {
                    text-align: center;
                    },
                </style>
                <style>
                div[data-baseweb="base-input"] > textarea {
                    min-height: 1px;
                    min-width: 1px;
                    padding: 0;
                    resize: none;
                    -webkit-text-fill-color: black;
                    text-align: center;
                    font-size: 20px;
                    background-color: white;
                },
                </style>
                """,
                unsafe_allow_html=True,
            )
## Overview Page

st.markdown("Overview Page")

st.markdown('## Overview 🧑‍💻')
st.markdown("Welcome to the Overview page. This page provides an overview of your portfolio.")
st.markdown("Here you can find information on the performance of your portfolio, as well as tools to help you make informed decisions.")

## Navigation Bar   
# from nav import create_navbar as cn
# options = ["Home","Performance", "Tools"]
# selectedPage = cn(options, "Overview")

# if selectedPage == "Home":
#     st.switch_page("Home.py")
# elif selectedPage == "Performance":
# #st.experimental_set_query_params(page="Performance_🎯")
#     st.switch_page("pages/Performance.py")
# elif selectedPage == "Tools":
#     st.switch_page("pages/Tools.py")

    
# if st.button("Home"):
#     st.switch_page('Home.py')
cont = st.container()
## All Kraken Assets Scatter Plot

#Scatter plot showing performance of all assets on Kraken
# Axes are the % change in price over the last 24 hours and the % change in price over the last 7 days

with cont:
    st.markdown("### All Kraken Assets Scatter Plot")
    st.markdown("This scatter plot shows the performance of all assets on Kraken.")
    st.markdown("The x-axis represents the % change in price over the last 24 hours, while the y-axis represents the % change in price over the last 7 days.")
    st.markdown("The size of the points represents the market cap of the asset.")
    st.markdown("Hover over the points to see the name of the asset.")
    st.markdown("The color of the points represents the sector of the asset.")
    st.markdown("Click on the legend to filter the assets by sector.")
    st.markdown("Use the slider to filter the assets by market cap.")
    st.markdown("Click on the points to see more information about the asset.")

#     st.plotly_chart(fig)

with cont:
    bullish = "images\candlestick-patterns-bullish.png"
    bearish = "images\candlestick-patterns-bearish.png"

    with st.expander("Candlestick Patterns", expanded=False):
        st.image(bullish, caption='Bullish Candlestick Patterns', use_column_width=True)
        st.image(bearish, caption='Bearish Candlestick Patterns', use_column_width=True)
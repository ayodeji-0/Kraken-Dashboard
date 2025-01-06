#Tools.py
import config as cfg

import streamlit as st
import streamlit.components.v1 as components
#from streamlit_option_menu import option_menu
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time

from datetime import datetime as dt, timedelta as td
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"

from stock_indicators import indicators
import json
import pandas as pd

import altair as alt
import numpy as np
import os

from Home import grab_ohlc_data, ohlc_to_df, ohlcDict, possible_intervals, possible_timeframes, balancePairsDict, df, assetPairs
#from nav import create_navbar
## Page Layout
st.set_page_config(layout="wide")

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

# from streamlit_navigation_bar import st_navbar as navbar

# page = navbar(["Home", "Overview 🧑‍💻", "Performance 🎯", "Tools 🛠️"])

# if page == "Home":
#     st.switch_page("Home.py")
# elif page == "Overview 🧑‍💻":
#     st.switch_page("pages\Overview_🧑‍💻.py")
# elif page == "Performance 🎯":
#     st.switch_page("pages\Performance_🎯.py")
# elif page == "Tools 🛠️":
#     st.switch_page("pages\Tools_🛠️.py")


# st.markdown('## Tools 🛠️')
# st.write("Use the tools below to analyse your portfolio and make informed decisions.")

## Page Selection Menu

# selected = create_navbar()

# pages = {
#     'Home': 'Home.py',
#     'Overview 🧑‍💻': 'pages\Overview_🧑‍💻.py',
#     'Performance 🎯': 'pages\Performance_🎯.py',
#     'Tools 🛠️': 'pages\Tools_🛠️.py'
# }

    

    # pagePaths = ['Home.py', 'pages/overview.py', 'pages/Performance.py', 'pages/Tools_🛠️.py']
    # # Switch pages based on the selected option
    # if selected == 'Home':
    #     st.switch_page(pagePaths[0])
    # elif selected == 'Overview 🧑‍💻':
    #     st.switch_page(pagePaths[1])
    # elif selected == 'Performance 🎯':
    #     st.switch_page(pagePaths[2])
    # elif selected == 'Tools 🛠️':
    #     st.switch_page(pagePaths[3])

## Preliminary Data Processing

tenure = '1Y' #default tenure for the tools page
ohlcDict = grab_ohlc_data(balancePairsDict.keys(),tenure)
dfOHLC = ohlc_to_df(ohlcDict)

# Convert imported dataframe df to integer type only
df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)

# Remove the summing row
df = df.iloc[:-1, :]

# Change all values not in the first row, first column to float type
df.iloc[1:, 1:] = df.iloc[1:, 1:].astype(float)

#calculate percentage allocation in a new column allocation
df['Allocation'] = ((df['Value (£)'] / df['Value (£)'].sum()) * 100).map("{:.2f}%".format)

##

@st.cache_data
def dfTools(df):
    

    return df

st.container(border=True)

## Starting Portfolio
# st.text_area("", value="Current Portfolio Distribution", height=30, max_chars=None, key=None)
# piecol, dfcol = st.columns([1,1])

#     with piecol:
#         fig = px.pie(df, values='Value (£)', names='Asset (Crypto)', hole=0.6, height=500)
#         st.plotly_chart(fig, use_container_width=True)

#     with dfcol:
#         #st.write("Drag and Drop Stocks to Reorder Portfolio")
#         st.dataframe(df, hide_index=True, use_container_width=True, height = 500)



## Tools Page

# Indexes or Chart Indicators
# Performance Indicators, Momentum Indicators, Volatility Indicators, Volume Indicators, Directional Movement Indicator DMI, Average Directional Index ADX
# MACD, RSI, OBV, CROI Multiple, Bollinger Bands, Altman Z-Score, Sharpe Ratio, PME Equivalent,
#  Ichimoku Cloud Technical Analysis 
tools = {
    'Chart Indicators': ['MACD', 'RSI', 'OBV', 'CROI Multiple', 'Bollinger Bands', 'Altman Z-Score']
}
with st.container(border=True):

    st.text_area("", value="Drag and Drop Stocks to Create a Test Portfolio", height=30, max_chars=None, key=None)
    # Page Layout
    # Wide mode

    tenDF = df.iloc[:, :2]
    # 3 columns for the tools page size ratio 1:3:1
    col1, col2, col3 = st.columns([1,3,1])

    # Sidebar for tools with assets, placeholder for top 15 assets for now, till i can get drag and drop working and api fetching for coinbase's top movers category
    with col1:
        fig = px.pie(df, values='Value (£)', names='Asset (Crypto)', hole=0.6, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Main column for tools
        st.markdown("Select a tool to analyse your portfolio.")
        appliedTools = st.selectbox('Select Tool', tools['Chart Indicators'], key='tools')
        #tools
    # Main column for tools


    # Show top 10 assets according to all asset pairs grabbed in homne page, check their iohlc data and store the 10 assets in a drag and drop editable dataframe



    #st.text_area("", value="Portfolio Backetsting", height=30, max_chars=None, key=None)


    with col2:
    # Show appendable dataframe of portfolio assets with rows and columns switched

        toolsDf = st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=True, height=250)#, show_toolbar=True, use_container_width=True, key='toolsDf')
        #store last row to a temp variable
        temp = toolsDf.iloc[-1]
        #check if 

    with col3:
        st.markdown("All Tradeable Pairs")
        st.table(assetPairs)
## Portfolio Allocation Buttons Setup
# Create three columns
with col2:
    col_2_1, col_2_2, col_2_3 = st.columns(3)

    
# Add buttons to add or remove assets from the portfolio
with col_2_1:
    if st.button("Add (+)"):
        #check for asset in current dataframe
        if temp['Asset (Crypto)'] in df['Asset (Crypto)'].values:
            #st.error(f"{temp['Asset (Crypto)']} already exists in the portfolio.")
            #add to existing row
            df.loc[df['Asset (Crypto)'] == temp['Asset (Crypto)'], 'Amount'] += temp['Amount']
            #recalculate value
            df['Value (£)'] = df['Amount'] * df['Price (£)']
            #recalculate allocation
            df['Allocation'] = ((df['Value (£)'] / df['Value (£)'].sum()) * 100).map("{:.2f}%".format)
        else:
            #append to dataframe
            df = df.append(temp, ignore_index=True)
            #add summation row
            df.loc['Total'] = df.sum()
#         #prompt user for asset name, and amount of asset to add
#         assetName = st.text_input("Enter Asset Name (Example Solana = SOL)")
#         assetAmount = st.number_input("Enter Amount of Asset")
#         #append to dataframe
#         df.loc[assetName] = assetAmount
#         #add summation row
#         #df.loc['Total'] = df.sum()
with col_2_2:
    if st.button("Remove (-)"):
        #prompt user for asset name to remove
        assetName = st.text_input("Enter Asset Name (Example Solana = SOL)")
        #remove from dataframe
        df.drop(assetName, inplace=True)
        #add summation row
        #df.loc['Total'] = df.sum()

with col_2_3:
    if st.button("Update"):
        #update the dataframe
        df = toolsDf
        #add summation row
        df.loc['Total'] = df.sum()

with col2:
    
    st.divider()

## Timeframe and Interval Selection


st.divider()
timeframe = list(possible_timeframes.keys())
tenure = st.selectbox('Select Timeframe', timeframe,placeholder="Select Timeframe", index=len(timeframe)-1, key='toolsTenure')
st.divider()

st.markdown("Drag and drop assets to the chart area, then select a tool to analyse your portfolio.")
## Asset Plots

with col2:
    with st.container(border=True):
        # Plot individual assets using a for loop but from the last asset to the first asset
        subplotCount = len(dfOHLC[0])
        rowC = subplotCount//2 + subplotCount%2
        colC = 2
        #row and col count for debugging 
        # st.write(f"Plots: {subplotCount}, Rows: {rowC}, Columns: {colC}")
        #fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(balanceDict.keys())[-2::-1])
        fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(dfOHLC[1]))

        
        #fig = make_subplots(rows=3, cols=2, subplot_titles= list(balanceDict.keys())[-1:0], column_widths=[1, 1])
        #Scatter plots of ohlc close prices for assets in the portfolio
        # Smooth the Close prices using a moving average
        window_size = 20

        for i in range(len(dfOHLC[0])):
            dfOHLC[0][i]['Close'] = (dfOHLC[0][i]['Close'].rolling(window_size, min_periods=1).mean()).round(2)

        #convert back to string types
        for i in range(len(dfOHLC[0])):
            dfOHLC[0][i]['Close'] = dfOHLC[0][i]['Close'].astype(str)






        
        # row1 = st.columns(3)
        # row2 = st.columns(3)
        # for col in row1 + row2:
        #     tile = col.container(height=120)
        #     tile.title(":balloon:")
        
        #Create columns dynamically
        columns = st.columns(3)
        st.write("Rows: ", rowC)    
        
    

        for i in range(len(dfOHLC[0])):
            max_val = 2.5* float(dfOHLC[0][i]['High'].max())  # Set the maximum value for the y-axis
            for row in range(rowC):
                rowi = st.columns(2)
                # Rest of the code for each row
                for col in rowi:                    
                    tile = col.container(height=120)
                    #tile.title(":balloon:")
                    tile.title(list(dfOHLC[1][i].keys(i)))

                        # tile.write("Asset: ", dfOHLC[1][i])
                        # tile.write("Time: ", dfOHLC[0][i]['Time'][0].strftime('%Y-%m-%d'))
                        # fig.add_trace(go.Scatter(x=dfOHLC[0][i]['Time'], y=dfOHLC[0][i]['Open'], mode='lines+markers', name=dfOHLC[0][i]['Time'][0].strftime('%Y-%m-%d') + ' ' + dfOHLC[0][i]['Open'][0], showlegend=False, fill = 'tozeroy'), row= i//2 + 1 , col=(i%2) +1)
                        # fig.update_yaxes(range = [0, max_val],title_text='Open Price (GBP)', row= i//2 + 1, col=(i%2) +1)
                        # fig.update_xaxes(title_text='Date and Time', row= i//2 + 1, col=(i%2) +1)
                        # fig.update_layout(autotypenumbers='convert types')
                        # fig.update_xaxes(rangeslider_visible=True)
                        # fig.update_xaxes(rangeslider_thickness = 0.05)
                        # #onhover show the asset name, date and close price
                        # fig.update_traces(hovertemplate='Date: %{x}<br>Close Price: £%{y}')
                        # fig.update_layout(height=1000, width=1000, title_text="Individual Assets", title_x=0.457)
                        # fig.update_layout(showlegend=True)
                        # fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
                        # fig.print_grid()
                        # st.plotly_chart(fig, use_container_width=True)

        # fig.update_layout(height=1000, width=1000, title_text="Individual Assets", title_x=0.457)
        # fig.update_layout(showlegend=True)
        # fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
        # fig.print_grid()
        # st.plotly_chart(fig, use_container_width=True)
        # Calculate the number of columns needed

## Charting Tools (Right)
with col3:
    st.markdown("Charting Tools")
    st.table(assetPairs)
    #st.table(dfTools(df))
# sidebard dropdown from tools to select tool type
# Indexes or Chart Indicators
# Performance Indicators, Momentum Indicators, Volatility Indicators, Volume Indicators, Directional Movement Indicator DMI, Average Directional Index ADX
# MACD, RSI, OBV, CROI Multiple, Bollinger Bands, Altman Z-Score, Sharpe Ratio, PME Equivalent,
#  Ichimoku Cloud Technical Analysis 
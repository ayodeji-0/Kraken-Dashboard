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

from stock_indicators import Quote
from stock_indicators import indicators
from stock_indicators import ChandelierType


import json
import pandas as pd

import altair as alt
import numpy as np
import os

from Home import grab_ohlc_data, ohlc_to_df, grab_price,rate, ohlcDict, possible_intervals, possible_timeframes, balancePairsDict, df, assetPairs
#from nav import create_navbar




##Todo List
#1. Change min max values to be based on tenure selection not the entire data set
## Navbar

# from nav import create_navbar as cn
# options = ["Home","Overview", "Performance"]
# selectedPage = cn(options, "Tools")
# st.session_state.pageName = selectedPage

# if selectedPage == "Home":
#     st.switch_page("Home.py")
#     st.rerun()
# if selectedPage == "Overview":
# #st.experimental_set_query_params(page="Overview_🧑‍💻")
#     st.switch_page("pages/Overview.py")
#     st.rerun()
# elif selectedPage == "Performance":
# #st.experimental_set_query_params(page="Performance_🎯")
#     st.switch_page("pages/Performance.py")
#     st.rerun()

## Page Selection Menu


#page = st_navbar(["Home", "Overview 🧑‍💻", "Performance 🎯", "Tools 🛠️"], selected= "Tools 🛠️", options = {'show_sidebar': True, 'show_menu': True})

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
                    font-size: 24px;
                    bold: True;
                    background-color: white;
                    margin-bottom: 8px;
                },
                </style>
                <style>
                [data-baseweb="select"] {
                    margin-top: -30px;
                    margin-bottom: 8px;
                    text-align: center;
                }
                </style>
                """,
    unsafe_allow_html=True,
)

## Tools Intro
with st.container(border=True):
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown('### Tools 🛠️')
        st.markdown("Welcome to the Tools page. Here you can analyse your portfolio using a variety of tools.")

        st.markdown("Drag and drop assets to the chart area, then select a tool to analyse your portfolio.")



    #Asset Moves for the day and 24 hours ago
    with col2:
        
            # Check if the HTML content is stored in session state
        if 'moves_today_html' in st.session_state and 'moves_24h_html' in st.session_state:
            moves_today_html = st.session_state['moves_today_html']
            moves_24h_html = st.session_state['moves_24h_html']

            st.markdown(f"### Asset Moves")

            col2_1, col2_2, col2_3 = st.columns([0.7, 0.7  ,1])

            with col2_1:
                with st.container():
                    st.write("Today")
                    st.markdown(moves_today_html, unsafe_allow_html=True)
            with col2_2:
                with st.container():
                    st.write("24h. Ago")
                    st.markdown(moves_24h_html, unsafe_allow_html=True)
        else:
            st.warning("No asset moves data available.")

    # st.comtainer = assetMovesCont
## Preliminary Data Processing

tenure = '1Y' #default tenure for the tools page


# Convert imported dataframe df to integer type only
df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)

# Remove the summing row
df = df.iloc[:-1, :]

# Change all values not in the first row, first column to float type
df.iloc[1:, 1:] = df.iloc[1:, 1:].astype(float)

#calculate percentage allocation in a new column allocation
df['Allocation'] = ((df['Value (£)'] / df['Value (£)'].sum()) * 100).map("{:.2f}%".format)

@st.cache_data
def dfTools(df):
    

    return df

assetCountOG = 0
def updateBalancePairs(toolsDf, reset=False):
    assetCount = len(toolsDf)
    assetCountOG = len(df)
    st.write("Asset Count: ", assetCount, "Original Asset Count: ", assetCountOG)
    # Iterate over each row in toolsDf
    #Clear BalancePairsDict
    st.write("Adding new asset to the portfolio")
    if reset == True:
        balancePairsDict.clear()
        for index, row in toolsDf.iterrows():
            balancePairsDict[row['Asset (Crypto)'] + 'USD'] = float(row['Balance (Asset)'])

        # backtest = []
        # backtest += assetPrices['Value (GBP)'] if toolsDf['Asset (Crypto)'].values == (assetPrices['Assets'] + "USD").values else [0]
        # st.write(backtest)
        # toolsDf['Value (£)'] = toolsDf['Asset Price'] * toolsDf['Balance (Asset)']
        # toolsDf['Allocation'] = ((toolsDf['Value (£)'] / toolsDf['Value (£)'].sum()) * 100).map("{:.2f}%".format)
        # toolsDf = st.data_editor(toolsDf, hide_index=True, num_rows="dynamic", use_container_width=True, height=480, on_change=None, key='toolsDf' + st.session_state())

        #Update ohlc data even outside function
        ohlcDict = grab_ohlc_data(balancePairsDict.keys(), tenure)
        dfOHLC = ohlc_to_df(ohlcDict)


        
        toolsDf.iat[assetCountOG, 2] = assetPrices.loc[assetPrices['Assets'] == toolsDf.iat[assetCountOG, 0], 'Value (GBP)'].values[0]
        toolsDf.iat[assetCountOG, 3] = toolsDf.iat[assetCountOG, 2] * toolsDf.iat[assetCountOG, 1]


        for asset in range(len(toolsDf)):
            toolsDf.iat[asset, 4] = round(((toolsDf.iat[asset, 3] / toolsDf['Value (£)'].sum()) * 100),2)#.map("{:.2f}%".format)
            #add % to the allocation column
            toolsDf.iat[asset, 4] = str(toolsDf.iat[asset, 4]) + "%"

    #st.write(toolsDf)
    st.write(balancePairsDict)
    return balancePairsDict  # example ["BTCUSD": 1.0, "ETHUSD": 2.0, "ADAUSD": 3.0]


#function to process a quote list and return a data frame with values of interest
def process_quotes(quotes_list, indicator):
    if indicator == 'MACD':
        result = indicators.get_macd(quotes_list, 12, 26, 9)
        macddf = pd.DataFrame(columns=['Time', 'MACD', 'Signal', 'Histogram'])
        macddf['Time'] = dfOHLC[0][0]['Time']
        macddf['MACD'] = [r.macd for r in result]
        macddf['Signal'] = [r.signal for r in result]
        macddf['Histogram'] = [r.histogram for r in result]
        return macddf
    elif indicator == 'RSI':
        result = indicators.get_rsi(quotes_list, 14)
        rsidf = pd.DataFrame(columns=['Time', 'RSI'])
        rsidf['Time'] = dfOHLC[0][0]['Time']
        rsidf['RSI'] = [r.rsi for r in result]
        return rsidf
    
    elif indicator == "Connor's RSI":
        result = indicators.get_connors_rsi(quotes_list, 3, 2, 100)
        crsidf = pd.DataFrame(columns=['Time', 'RSI Close', 'RSI Streak', '% Rank', 'CRSI'])
        crsidf['Time'] = dfOHLC[0][0]['Time']
        crsidf['RSI Close'] = [r.rsi_close for r in result]
        crsidf['RSI Streak'] = [r.rsi_streak for r in result]
        crsidf['% Rank'] = [r.percent_rank for r in result]
        crsidf['CRSI'] = [r.connors_rsi for r in result]
        return crsidf
    
    elif indicator == 'OBV':
        result = indicators.get_obv(quotes_list)
        obvdf = pd.DataFrame(columns=['Time', 'OBV'])
        obvdf['Time'] = dfOHLC[0][0]['Time']
        obvdf['OBV'] = [r.obv for r in result]
        return obvdf

    elif indicator == 'Bollinger Bands':
        result = indicators.get_bollinger_bands(quotes_list, 20, 2)
        bollingerdf = pd.DataFrame(columns=['Time', 'Upper Band', 'Lower Band'])
        bollingerdf['Time'] = dfOHLC[0][0]['Time']
        bollingerdf['Upper Band'] = [r.upper_band for r in result]
        bollingerdf['Lower Band'] = [r.lower_band for r in result]
        return bollingerdf

    elif indicator == 'Ichimoku Cloud':
        result = indicators.get_ichimoku(quotes_list)
        ichimokudf = pd.DataFrame(columns=['Time', 'Tenkan Sen', 'Kijun Sen', 'Senkou Span A', 'Senkou Span B', 'Chikou Span'])
        ichimokudf['Time'] = dfOHLC[0][0]['Time']
        ichimokudf['Tenkan Sen'] = [r.tenkan_sen for r in result]
        ichimokudf['Kijun Sen'] = [r.kijun_sen for r in result]
        ichimokudf['Senkou Span A'] = [r.senkou_span_a for r in result]
        ichimokudf['Senkou Span B'] = [r.senkou_span_b for r in result]
        ichimokudf['Chikou Span'] = [r.chikou_span for r in result]
        return ichimokudf
    
    elif indicator == 'Chandelier Exit':
        resultShort = indicators.get_chandelier(quotes_list, 22, chandelier_type=ChandelierType.SHORT)
        resultLong = indicators.get_chandelier(quotes_list, 22, chandelier_type=ChandelierType.LONG)
        chandelierdf = pd.DataFrame(columns=['Time', 'Long Exit', 'Short Exit'])
        chandelierdf['Time'] = dfOHLC[0][0]['Time']
        chandelierdf['Long Exit'] = [r.chandelier_exit for r in resultLong]
        chandelierdf['Short Exit'] = [r.chandelier_exit for r in resultShort]
        return chandelierdf



ohlcDict = grab_ohlc_data(balancePairsDict.keys(),tenure)
dfOHLC = ohlc_to_df(ohlcDict)

ohlcCounter = 0

if ohlcCounter == 0:
    ogdfOHLC = dfOHLC

#@st.cache_data
def updateChart(toolsDf, appliedTool, selectedChart, assetPlot):
    if selectedChart != "All Plots":
        for asset in dfOHLC[1]:
            index = list(dfOHLC[1]).index(asset)
            #convert ohlc data to a list of quotes
            quotes_list = [
                Quote(
                d.to_pydatetime(),  # Convert pandas Timestamp to datetime
                float(o),
                float(h),
                float(l),
                float(c),
                float(v)
                )
                for d, o, h, l, c, v in zip(
                dfOHLC[0][index]['Time'],
                dfOHLC[0][index]['Open'],
                dfOHLC[0][index]['High'],
                dfOHLC[0][index]['Low'],
                dfOHLC[0][index]['Close'],
                dfOHLC[0][index]['Volume']
                )
            ]
            # find row and column, depending on the asset selected
            if selectedChart in toolsDf['Asset (Crypto)'].values:
                row = (toolsDf['Asset (Crypto)'].tolist().index(selectedChart)) // 2 + 1
                col = (toolsDf['Asset (Crypto)'].tolist().index(selectedChart)) % 2
            else:
                continue

                #st.write("Row: ", row, "Column: ", col + 1)
                # determine the tool to apply to which chart
            if appliedTool == 'Select Tool':
                return assetPlot
            
            if appliedTool == 'Bollinger Bands':   
                bollingerdf = process_quotes(quotes_list, 'Bollinger Bands')
                #st.write("Bollinger Bands", bollingerdf)

                # Create a new internal filled area trace for the bollinger bands
                assetPlot.add_trace(go.Scatter(x=bollingerdf['Time'], y=bollingerdf['Upper Band'], fill='tonexty', mode='lines', line=dict(width=0), fillcolor='purple', name='Upper Band'), row=row, col=col+1)
                assetPlot.add_trace(go.Scatter(x=bollingerdf['Time'], y=bollingerdf['Lower Band'], fill='tonexty', mode='lines', line=dict(width=0), fillcolor='yellow', name='Lower Band'), row=row, col=col+1)

                assetPlot.update_yaxes(range = [min(bollingerdf['Lower Band']), max(bollingerdf['Upper Band'])], row=row, col=col+1)
            
            elif appliedTool == 'MACD': 
                macddf = process_quotes(quotes_list, 'MACD')
                #st.write("MACD", macddf)
                # Create a new trace for the MACD line
                assetPlot.add_trace(go.Scatter(x=macddf['Time'], y=macddf['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=row, col=col+1)
                # Create a new trace for the Signal line
                assetPlot.add_trace(go.Scatter(x=macddf['Time'], y=macddf['Signal'], mode='lines', name='Signal', line=dict(color='red')), row=row, col=col+1)
                # Create a new trace for the Histogram
                assetPlot.add_trace(go.Bar(x=macddf['Time'], y=macddf['Histogram'], name='Histogram', marker_color='grey'), row=row, col=col+1)

                #update axes to include negative values
                assetPlot.update_yaxes(range = [min(macddf['Histogram']), max(macddf['Histogram'])], row=2, col=1)

            elif appliedTool == 'RSI':
                rsidf = process_quotes(quotes_list, 'RSI')
                #st.write("RSI", rsidf)
                # Create a new trace for the RSI
                assetPlot.add_trace(go.Scatter(x=rsidf['Time'], y=rsidf['RSI'], mode='lines', name='RSI', line=dict(color='blue')), row=row, col=col+1)

                assetPlot.update_yaxes(range = [min(rsidf['RSI']), max(rsidf['RSI'])], row=row, col=col+1)
            
            elif appliedTool == "Connor's RSI":
                crsidf = process_quotes(quotes_list, "Connor's RSI")
                #st.write("Connors RSI", crsidf)
                # Create a new trace for the RSI Close
                st.write("Row",row,"Column",col)
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['RSI Close'], mode='lines', name='RSI Close', line=dict(color='blue')), row=row, col=col+1)
                # Create a new trace for the RSI Streak
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['RSI Streak'], mode='lines', name='RSI Streak', line=dict(color='red')), row=row, col=col+1)
                # Create a new trace for the % Rank
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['% Rank'], mode='lines', name='% Rank', line=dict(color='green')), row=row, col=col+1)
                # Create a new trace for the CRSI
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['CRSI'], mode='lines', name='CRSI', line=dict(color='orange')), row=row, col=col+1)

                assetPlot.update_yaxes(range = [min(crsidf['CRSI']), max(crsidf['CRSI'])], row=row, col=col+1)


            elif appliedTool == 'OBV':
                obvdf = process_quotes(quotes_list, 'OBV')
                #st.write("OBV", obvdf)
                # Create a new trace for the OBV
                assetPlot.add_trace(go.Scatter(x=obvdf['Time'], y=obvdf['OBV'], mode='lines', name='OBV', line=dict(color='blue')), row=row, col=col+1)
            
            elif appliedTool == 'Ichimoku Cloud':
                ichimokudf = process_quotes(quotes_list, 'Ichimoku Cloud')
                #st.write("Ichimoku Cloud", ichimokudf)
                # Create a new trace for the Tenkan Sen
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Tenkan Sen'], mode='lines', name='Tenkan Sen', line=dict(color='blue')), row=row, col=col+1)
                # Create a new trace for the Kijun Sen
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Kijun Sen'], mode='lines', name='Kijun Sen', line=dict(color='red')), row=row, col=col+1)
                # Create a new trace for the Senkou Span A
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Senkou Span A'], mode='lines', name='Senkou Span A', line=dict(color='green')), row=row, col=col+1)
                # Create a new trace for the Senkou Span B
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Senkou Span B'], mode='lines', name='Senkou Span B', line=dict(color='orange')), row=row, col=col+1)
                # Create a new trace for the Chikou Span
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Chikou Span'], mode='lines', name='Chikou Span', line=dict(color='purple')), row=row, col=col+1)

                senkou_span_b = [val for val in ichimokudf['Senkou Span B'] if val is not None]
                senkou_span_a = [val for val in ichimokudf['Senkou Span A'] if val is not None]
                assetPlot.update_yaxes(range = [min(senkou_span_b), max(senkou_span_a)], row=row, col=col+1)
            
            elif appliedTool == 'Chandelier Exit':
                chandelierdf = process_quotes(quotes_list, 'Chandelier Exit')
                #st.write("Chandelier Exit", chandelierdf)
                # Create a new trace for the Long Exit
                assetPlot.add_trace(go.Scatter(x=chandelierdf['Time'], y=chandelierdf['Long Exit'], mode='lines', name='Long Exit', line=dict(color='blue')), row=row, col=col+1)
                # Create a new trace for the Short Exit
                assetPlot.add_trace(go.Scatter(x=chandelierdf['Time'], y=chandelierdf['Short Exit'], mode='lines', name='Short Exit', line=dict(color='red')), row=row, col=col+1)

                assetPlot.update_yaxes(range = [min(chandelierdf['Short Exit']), max(chandelierdf['Long Exit'])], row=row, col=col+1)   
        

            
            return assetPlot
    elif selectedChart == 'All Plots':
        for asset in dfOHLC[1]:
            index = list(dfOHLC[1]).index(asset)
            #convert ohlc data to a list of quotes
            quotes_list = [
                Quote(
                d.to_pydatetime(),  # Convert pandas Timestamp to datetime
                float(o),
                float(h),
                float(l),
                float(c),
                float(v)
                )
                for d, o, h, l, c, v in zip(
                dfOHLC[0][index]['Time'],
                dfOHLC[0][index]['Open'],
                dfOHLC[0][index]['High'],
                dfOHLC[0][index]['Low'],
                dfOHLC[0][index]['Close'],
                dfOHLC[0][index]['Volume']
                )
            ]
            row = (toolsDf['Asset (Crypto)'].tolist().index(asset)) // 2 + 1
            col = (toolsDf['Asset (Crypto)'].tolist().index(asset)) % 2 + 1

            #st.write("Asset: ", asset,"Index: ", index, "Row: ", row, "Column: ", col) # Debugging
            
            # if Exception:
            #     return assetPlot
            if appliedTool == 'Bollinger Bands':
                bollingerdf = process_quotes(quotes_list, 'Bollinger Bands')

                # Create a new internal filled area trace for the Bollinger Bands
                assetPlot.add_trace(go.Scatter(x=bollingerdf['Time'], y=bollingerdf['Upper Band'], fill='tonexty', mode='lines', line=dict(width=0), fillcolor='purple', name=f'{asset} Upper Band'), row=row, col=col)
                assetPlot.add_trace(go.Scatter(x=bollingerdf['Time'], y=bollingerdf['Lower Band'], fill='tonexty', mode='lines', line=dict(width=0), fillcolor='red', name=f'{asset} Lower Band'), row=row, col=col)

            elif appliedTool == 'MACD':
                macddf = process_quotes(quotes_list, 'MACD')

                # Create a new trace for the MACD line
                assetPlot.add_trace(go.Scatter(x=macddf['Time'], y=macddf['MACD'], mode='lines', name=f'{asset} MACD', line=dict(color='blue')), row=row, col=col)
                # Create a new trace for the Signal line
                assetPlot.add_trace(go.Scatter(x=macddf['Time'], y=macddf['Signal'], mode='lines', name=f'{asset} Signal', line=dict(color='red')), row=row, col=col)
                # Create a new trace for the Histogram
                assetPlot.add_trace(go.Bar(x=macddf['Time'], y=macddf['Histogram'], name=f'{asset} Histogram', marker_color='grey'), row=row, col=col)


            elif appliedTool == 'RSI':
                rsidf = process_quotes(quotes_list, 'RSI')

                # Create a new trace for the RSI
                assetPlot.add_trace(go.Scatter(x=rsidf['Time'], y=rsidf['RSI'], mode='lines', name=f'{asset} RSI', line=dict(color='blue')), row=row, col=col)

                assetPlot.update_yaxes(range = [min(rsidf['RSI']), max(rsidf['RSI'])], row=row, col=col)
            
            elif appliedTool == "Connor's RSI":
                crsidf = process_quotes(quotes_list, "Connor's RSI")
                #st.write("Connors RSI", crsidf)
                # Create a new trace for the RSI Close
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['RSI Close'], mode='lines', name='RSI Close', line=dict(color='blue')), row=row, col=col)
                # Create a new trace for the RSI Streak
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['RSI Streak'], mode='lines', name='RSI Streak', line=dict(color='red')), row=row, col=col)
                # Create a new trace for the % Rank
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['% Rank'], mode='lines', name='% Rank', line=dict(color='green')), row=row, col=col)
                # Create a new trace for the CRSI
                assetPlot.add_trace(go.Scatter(x=crsidf['Time'], y=crsidf['CRSI'], mode='lines', name='CRSI', line=dict(color='orange')), row=row, col=col)

                assetPlot.update_yaxes(range = [min(crsidf['CRSI']), max(crsidf['CRSI'])], row=row, col=col)

            elif appliedTool == 'OBV':
                obvdf = process_quotes(quotes_list, 'OBV')

                # Create a new trace for the OBV
                assetPlot.add_trace(go.Scatter(x=obvdf['Time'], y=obvdf['OBV'], mode='lines', name=f'{asset} OBV', line=dict(color='blue')), row=row, col=col)

                assetPlot.update_yaxes(range = [min(obvdf['OBV']), max(obvdf['OBV'])], row=row, col=col)
            


            elif appliedTool == 'Ichimoku Cloud':
                ichimokudf = process_quotes(quotes_list, 'Ichimoku Cloud')

                # Create a new trace for the Tenkan Sen
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Tenkan Sen'], mode='lines', name=f'{asset} Tenkan Sen', line=dict(color='blue')), row=row, col=col)
                # Create a new trace for the Kijun Sen
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Kijun Sen'], mode='lines', name=f'{asset} Kijun Sen', line=dict(color='red')), row=row, col=col)
                # Create a new trace for the Senkou Span A
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Senkou Span A'], mode='lines', name=f'{asset} Senkou Span A', line=dict(color='green')), row=row, col=col)
                # Create a new trace for the Senkou Span B
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Senkou Span B'], mode='lines', name=f'{asset} Senkou Span B', line=dict(color='orange')), row=row, col=col)
                # Create a new trace for the Chikou Span
                assetPlot.add_trace(go.Scatter(x=ichimokudf['Time'], y=ichimokudf['Chikou Span'], mode='lines', name=f'{asset} Chikou Span', line=dict(color='purple')), row=row, col=col)

                senkou_span_b = [val for val in ichimokudf['Senkou Span B'] if val is not None]
                senkou_span_a = [val for val in ichimokudf['Senkou Span A'] if val is not None]
                assetPlot.update_yaxes(range = [min(senkou_span_b), max(senkou_span_a)], row=row, col=col)
            elif appliedTool == 'Chandelier Exit':
                chandelierdf = process_quotes(quotes_list, 'Chandelier Exit')

                # Create a new trace for the Long Exit
                assetPlot.add_trace(go.Scatter(x=chandelierdf['Time'], y=chandelierdf['Long Exit'], mode='lines', name=f'{asset} Long Exit', line=dict(color='blue')), row=row, col=col)
                # Create a new trace for the Short Exit
                assetPlot.add_trace(go.Scatter(x=chandelierdf['Time'], y=chandelierdf['Short Exit'], mode='lines', name=f'{asset} Short Exit', line=dict(color='red')), row=row, col=col)
            
       
    return assetPlot



def updatePort(toolsDf):
    balancePairsDict = updateBalancePairs(toolsDf, reset=True)
    dfOHLC = ohlc_to_df(ohlcDict)
    if "ogtoolsDf" not in st.session_state:
        ogtoolsDf = toolsDf
        st.session_state["ogtoolsDf"] = ogtoolsDf
    #grab tools df by referencing sessions state key
    #update toolsDf data editor with new data through session state key

    #clear toolsDf cont
    toolsDfCont = st.empty()

    toolsDf.iloc[:3, :] = st.session_state.ogtoolsDf.iloc[:3, :]

    toolsDf = toolsDfCont.data_editor(toolsDf, hide_index=True, num_rows="dynamic", use_container_width=True, height=380,key= st.session_state.get("de_key", 0) + 1, on_change=updatePort(toolsDf))
    st.session_state["de_key"] = toolsDfCont.key

def resetPort(toolsDf):
    st.session_state.de_key = 0
    updatePort(toolsDf)

    return toolsDf
    # # Reset the dataframe, pie chart, and subplot area
    # st.session_state["de_key"] = 0
    # st.session_state["subplot"] = 0

    # # Convert the tuple to a list
    # dfOHLC_list = list(dfOHLC)
    # balancePairs_list = list(balancePairsDict)

    # # Modify the first element of the list
    # dfOHLC_list[1] = dict.fromkeys(list(dfOHLC_list[1])[:assetCountOG-1])
    # balancePairs_list = dict.fromkeys(list(balancePairs_list)[:assetCountOG-1])
    


    # # Convert the list back to a tuple
    # dfOHLC = tuple(dfOHLC_list)
    
    # num_to_pop = len(dfOHLC[0]) - len(toolsDf['Asset (Crypto)'])       

    # for _ in range(num_to_pop):        
    #     if num_to_pop > 0:
    #         dfOHLC[0].pop(-1)         # Pop items if the number of entries is greater than the count in toolsDf        
    # st.write(dfOHLC[1])
    # #restart the app
    # st.rerun()
    #st.session_state.toolsTenure += 1
    # st.write(dfOHLC[0])
    # st.write(dfOHLC[1])
#@st.cache_data
def allAssetPrices():
    url = "https://api.kraken.com/0/public/Ticker"
    response = requests.get(url)
    data = response.json()
    allAssetPairs = data['result'].keys()

    assetPrices = {asset[:-3]: round(float(data['result'][asset]['c'][0]) * rate, 2) for asset in allAssetPairs if asset[-3:] == "USD"}

    # # remove all assets with 0 value
    # assetPrices = {asset: value for asset, value in assetPrices.items() if value != 0}

    # Convert the dictionary to a DataFrame with columns "Asset" and "Value"
    assetPrices = pd.DataFrame(list(assetPrices.items()), columns=['Assets', 'Value (GBP)'])

    return assetPrices

##
if __name__ == "__main__":
    # This code will not run on import

    assetPrices = allAssetPrices()
    ## Tools Page
    st.container(border=True)
    # Indexes or Chart Indicators
    # Performance Indicators, Momentum Indicators, Volatility Indicators, Volume Indicators, Directional Movement Indicator DMI, Average Directional Index ADX
    # MACD, RSI, OBV, CROI Multiple, Bollinger Bands, Altman Z-Score, Sharpe Ratio, PME Equivalent,
    #  Ichimoku Cloud Technical Analysis 
    tools = {
        'Chart Indicators': ['MACD', 'RSI', "Connor's RSI", 'OBV', 'Bollinger Bands', 'Ichimoku Cloud', 'Chandelier Exit', 'Select Tool']
    }

    toolTips = {'MACD': 'Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. The MACD is calculated by subtracting the 26-period EMA from the 12-period EMA.',
                'RSI': 'The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. The RSI oscillates between zero and 100. Traditionally the RSI is considered overbought when above 70 and oversold when below 30.',
                "Connor's RSI": "Connor's RSI is a composite indicator consisting of three components. Two of the three components utilize the Relative Strength Index (RSI) calculations developed by Welles Wilder in the 1970s, and the third component ranks the most recent price change on a scale of 0 to 100.",
                'OBV': 'On-Balance Volume (OBV) is a technical trading momentum indicator that uses volume flow to predict changes in stock price. Joseph Granville first developed the OBV metric in the 1963 book Granville’s New Key to Stock Market Profits.',
                'Bollinger Bands': 'Bollinger Bands are a type of statistical chart characterizing the prices and volatility over time of a financial instrument or commodity, using a formulaic method propounded by John Bollinger in the 1980s. Financial traders employ these charts as a methodical tool to inform trading decisions, control automated trading systems, or as a component of technical analysis.',
                'Ichimoku Cloud': 'The Ichimoku Cloud, also known as Ichimoku Kinko Hyo, is a versatile indicator that defines support and resistance, identifies trend direction, gauges momentum and provides trading signals. Ichimoku Kinko Hyo translates into “one look equilibrium chart”. With one look, chartists can identify the trend and look for potential signals within that trend.',
                'Chandelier Exit': 'The Chandelier Exit is a volatility-based indicator that identifies stop loss levels for long and short trading positions. The indicator was created by Chuck LeBeau and is often used as a component of trading strategies. The indicator is designed to keep traders in a position during a strong trend and exit a position during a weak trend.',
                'Select Tool': 'Select a tool to apply to the chart'}

    toolsDf = pd.DataFrame(columns=['Asset (Crypto)', 'Balance (Asset)'])
    

    with st.container(border=True):

        st.text_area("", value="Drag and Drop Stocks to Create a Test Portfolio", height=30, max_chars=None, key=None)
        # Page Layout
        # Wide mode

        tenDF = df.iloc[:, :2]
        # 3 columns for the tools page size ratio 1:3:1
        col1, col2, col3 = st.columns([2,5,2])

        with col2:
        # Show appendable dataframe of portfolio assets with rows and columns switched
            toolsDf = df
            #toolsDf = st.data_editor(toolsDf, hide_index=True, num_rows="dynamic", use_container_width=True, height=480, on_change=None)#, column_config= )#, show_toolbar=True, use_container_width=True, key='toolsDf')
            og = df # original dataframe
        with col3:
            st.dataframe(assetPrices,height=495, hide_index=True, use_container_width=True, key = 0)
            st.divider()
            timeframe = list(possible_timeframes.keys())
            
            #pageName = st.session_state.get("pageName", 0)

            def grab_tenure():
                return st.selectbox('Select Timeframe', timeframe,placeholder="Select Timeframe", index=len(timeframe)-1, key=0)
            tenure = grab_tenure()
            
            
            ohlcDict = grab_ohlc_data(balancePairsDict.keys(),tenure)
            # st.write(ohlcDict)
            dfOHLC = ohlc_to_df(ohlcDict)
            #st.write(dfOHLC[1])

    
    if "de_key" not in st.session_state:
        st.session_state.de_key = 0  
    if "toolsDf" not in st.session_state:
        st.session_state["toolsDf"] = toolsDf
   
    ## Portfolio Allocation Buttons Setup
    # Create three columns
    with col2:
        toolsDfCont = st.container(border=True)

        with toolsDfCont:
            toolsDf = st.data_editor(toolsDf, hide_index=True, num_rows="dynamic", use_container_width=True, height=460,key= st.session_state.de_key + 1)#, on_change=updatePort(toolsDf))
            #st.session_state["de_key"] += 1
            st.session_state["toolsDf"] = toolsDf
        st.divider()


        col2_1, col2_2 = st.columns([0.7,.3])

        

        with col2_2:
            if st.button("Reset Portfolio", use_container_width=True):
                resetPort(toolsDf)
        
        with col2_1:
            if st.button("Update Portfolio", use_container_width=True):
                #update the dataframe, pie chart, and subplot area

                updatePort(toolsDf)
        

    ## Charting Tools (Left) - Pie Chart, Indicator and Chart Seletors

    # Sidebar for tools with assets, placeholder for top 15 assets for now, till i can get drag and drop working and api fetching for coinbase's top movers category
        with col1:
            def update_pie_chart(toolsDf):
                fig = px.pie(toolsDf, values='Value (£)', names='Asset (Crypto)', hole=0.6, height=500,color_discrete_sequence=px.colors.sequential.Viridis, 
                            title=f"Assets in Portfolio")
                fig.update_layout(title_x=0.288, title_y=0.48)#, color_discrete_sequence=px.colors.sequential.Viridis)
                return fig

            fig = update_pie_chart(toolsDf)

            
            st.plotly_chart(fig, use_container_width=True)

            # colors = ['blue', 'red', 'green', 'orange', 'purple', 'yellow', 'pink', 'brown', 'black', 'grey']
            # fig = go.Figure(go.Barpolar(theta=toolsDf['Asset (Crypto)'], r=toolsDf['Allocation'], marker=dict(color = colors), wid), layout=go.Layout(polar={'radialaxis':{'visible':False}}))
            # st.plotly_chart(fig, use_container_width=True)
            st.divider()
            # Main column for tools
            appliedTool = st.selectbox('', tools['Chart Indicators'], key='tools', index=len(tools['Chart Indicators'])-1) 

            selectedCharts = st.select_slider('', options=list(toolsDf['Asset (Crypto)']) + ["All Plots"], value="All Plots", key='chart', help="Select the asset(s) to apply the tool to")

    ## Asset Plots


    # initialize sessiona state key for asset plots, and save the default plot in session state
    if "subplot" not in st.session_state:
        st.session_state["subplot"] = 0


    with col2:
        with st.container(border=True):
            with col2:
                with st.container(border=True):
                    st.markdown(f"<div><h3><strong>Individual Assets</strong></h3></div><div style='text-align:center;'>", unsafe_allow_html=True)
                    st.text_area("", "Individual Assets", height=30, max_chars=None, key=None)
                    # Plot individual assets using a for loop but from the last asset to the first asset
                    subplotCount = len(dfOHLC[0])
                    rowC = subplotCount//2 + subplotCount%2
                    colC = 2
                    #row and col count for debugging 
                    # st.write(f"Plots: {subplotCount}, Rows: {rowC}, Columns: {colC}")
                    #fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(balanceDict.keys())[-2::-1])
                    fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(dfOHLC[1]), vertical_spacing=0.1, horizontal_spacing=0.2)
                    fig.print_grid()

                    
                    #fig = make_subplots(rows=3, cols=2, subplot_titles= list(balanceDict.keys())[-1:0], column_widths=[1, 1])
                    #Scatter plots of ohlc close prices for assets in the portfolio
                    # Smooth the Close prices using a moving average
                    window_size = 20

                    for i in range(len(dfOHLC[0])):
                        dfOHLC[0][i]['Close'] = (dfOHLC[0][i]['Close'].rolling(window_size, min_periods=1).mean()).round(2)

                    #convert back to string types
                    for i in range(len(dfOHLC[0])):
                        dfOHLC[0][i]['Close'] = dfOHLC[0][i]['Close'].astype(str)       
                    #Create columns dynamically
                    columns = st.columns(3)
                    #st.write("Subplots:", subplotCount," Columns", colC , " Rows: " ,rowC)    
                    
                

                    for i in range(len(dfOHLC[0])):
                        max_val = 2.5* float(dfOHLC[0][i]['High'].max())  # Set the maximum value for the y-axis
                        for row in range(rowC):
                    #         rowi = st.columns(2)
                    #         # Rest of the code for each row
                    #         for col in rowi:                    
                    #             tile = col.container(height=120)
                    #             #tile.title(":balloon:")
                    #             tile.title(list(dfOHLC[1].keys())[i])

                    #             tile.write("Asset: ", dfOHLC[1][i])
                    #             tile.write("Time: ", dfOHLC[0][i]['Time'][0].strftime('%Y-%m-%d'))
                                fig.add_trace(go.Scatter(x=dfOHLC[0][i]['Time'], y=dfOHLC[0][i]['Open'], mode='lines+markers', name=dfOHLC[0][i]['Time'][0].strftime('%Y-%m-%d') + ' ' + dfOHLC[0][i]['Open'][0], showlegend=False, fill = 'tozeroy'), row= i//2 + 1 , col=(i%2) +1)
                                fig.update_yaxes(range = [0, max_val],title_text='Open Price (GBP)', row= i//2 + 1, col=(i%2) +1)
                                fig.update_xaxes(title_text='Date and Time', row= i//2 + 1, col=(i%2) +1)
                                fig.update_layout(autotypenumbers='convert types')
                                fig.update_xaxes(rangeslider_visible=True)
                                fig.update_xaxes(rangeslider_thickness = 0.05)
                                #onhover show the asset name, date and close price
                                fig.update_traces(hovertemplate='Date: %{x}<br>Close Price: £%{y}')
                                fig.update_layout(height=1000, width=1000, title_text="", title_x=0.457)
                                fig.update_layout(showlegend=True)
                                fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
                                fig.print_grid()
                    #             st.plotly_chart(fig, use_container_width=True)

                    fig.update_layout(height=1000, width=1000, title_text="Individual Assets\n\n", title_x=0.457)
                    fig.update_layout(showlegend=True)
                    fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
                    fig.print_grid()
                    assetPlot = fig
                    #store default plot in session state
                    st.session_state["subplot"] = assetPlot
                    # Apply necessary tools to the chart
                    assetPlot = updateChart(toolsDf, appliedTool, selectedCharts, assetPlot) # add traces corresponding to the selected tool and asset
                    st.plotly_chart(assetPlot, use_container_width=True, key=st.session_state["subplot"]) 
                    

                    


    ## Charting Tools (Left) - Update Chart Button

        with col1:    
            if st.button("Update Chart", use_container_width=True):
                #update the chart with the selected asset
                st.spinner("Updating Charts...")
                st.write(toolsDf)
                assetPlot = updateChart(toolsDf, appliedTool, selectedCharts, assetPlot)

        with col1:
            if appliedTool != 'Select Tool':
                st.markdown("### Tool Description")
                st.write(toolTips[appliedTool])





                


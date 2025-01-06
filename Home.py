import config as cfg

import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


#from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from streamlit.components.v1 import html


import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
from datetime import datetime as dt, timedelta as td

# Other necessary imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
import json
import pandas as pd
#import altair as alt
import numpy as np
import os

from difflib import get_close_matches

## Streamlit Configuration
st.markdown(
                """
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
                <style>
                [data-baseweb="select"] {
                    margin-bot: -30px;
                    text-align: center;
                    container-align-items: right;
                    width: 10%;
                }
                </style>
                <style>
                div[data-testid="collapsedControl"]{
                    visibility: hidden;}
                </style>

                
                <style> text_title {text-align: center;}</style>
                """, unsafe_allow_html=True
                )


'''
                <style>
                div[data-testid="stSidebarNav"] {
                        display: none;}
                /style>

'''
# st.markdown('## Home 🏠')
# st.write("Welcome to the Portfolio Dashboard. This dashboard provides an overview of your portfolio, including the performance of your assets and tools to help you make informed decisions.")

## Page Selection Menu
#selected = create_navbar()

## Home Page
st.markdown("# Portfolio Dashboard 📊")

## Navbar

# from nav import create_navbar as cn
# options = ["Overview", "Performance", "Tools"]
# selectedPage = cn(options, "Home")
# st.session_state.pageName = selectedPage


# if selectedPage == "Overview":
#     st.switch_page("pages/Overview.py")
# elif selectedPage == "Performance":

#     st.switch_page("pages/Performance.py")
    
# elif selectedPage == "Tools":
# #st.experimental_set_query_params(page="Tools_🛠️")
#     st.switch_page("pages/Tools.py")
# elif selectedPage == "Home":
#     st.write("Home Page")


##

api_url = "https://api.kraken.com"

# Read Kraken API key and secret stored in config file
api_key = cfg.api_key
api_sec = cfg.api_priv

# Create dictionary to map API endpoints to their respective names and respective request types
api_endpoints = {
    'Assets': '/0/public/Assets',
    'AssetPairs': '/0/public/AssetPairs',
    'Ticker': '/0/public/Ticker',
    'OHLC': '/0/public/OHLC',
    'default OHLC': '/0/public/OHLC',

    'Balance': '/0/private/Balance',
    'ExtendedBalance': '/0/private/BalanceEx',
    'Ledgers': '/0/private/Ledgers',
    'QueryLedgers': '/0/private/QueryLedgers',
    'TradeVolume': '/0/private/TradeVolume',
    'TradesHistory': '/0/private/TradesHistory',
    'OpenOrders': '/0/private/OpenOrders',

}

# Function to generate a nonce
def generate_nonce():
    nonce = str(int(1000 * time.time()))
    return nonce

# Function to get Kraken signature
def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode() 

# Function to make Kraken API request
def kraken_request(uri_path, data, api_key, api_sec, headers=None):
    if headers is None:
        headers = {}

    headers['API-Key'] = api_key
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req

#Function to make more non-trivial Kraken API get request
def kraken_get_request(uri_path, data=None, headers=None):
    if uri_path != api_endpoints['OHLC']:
        if headers is None:
            headers = {
                'Accept': 'application/json'
            }
        
        headers.update(headers)
        req = requests.get((api_url + uri_path), headers=headers, data=data)
    elif uri_path == api_endpoints['OHLC']:
        temp_endpoint = api_endpoints['OHLC'] + '?pair=' + data['pair'] + '&interval=' + data['interval']
        req = requests.get((api_url + temp_endpoint), headers=headers)
    return req


# Function to grab the current GBPUSD rate from the Kraken API
def grab_rate():
    resp = kraken_get_request(api_endpoints['Ticker'], {"pair": 'GBPUSD'}).json()
    rate = 1/float(resp['result']['ZGBPZUSD']['c'][0])
    return rate

#cache to not make multiple requests to the api
@st.cache_resource
# Function to get the altnames of all tradeable Kraken asset pairs
def grab_all_assets():
    # Construct the Kraken API request and get all asset pairs from the Kraken API
    assetPairs = kraken_get_request(api_endpoints['AssetPairs']).json()['result']
    
    # Extract 'altname' for each asset pair
    altNames = [details['altname'] for details in assetPairs.values()]
    return altNames, assetPairs# altNames is a list of all tradeable asset pairs on Kraken example: ['XXBTZUSD', 'XETHZUSD', 'XETHXXBT']


# Function to get the balance of all assets in the Kraken account with the given API keys
@st.cache_resource
def grab_ext_bal():
    # Construct the Kraken API request and get the External Balance Information
    resp = kraken_request(api_endpoints['ExtendedBalance'], {"nonce": generate_nonce(),}, api_key, api_sec).json()
    balanceDict = {}
    # Extract the balance of each asset and the asset name
    for asset, details in resp['result'].items():
        balance = details['balance']
        if float(balance) == 0:
            continue   
        balanceDict[asset] = float(balance)
    return balanceDict # balanceDict is a dictionary with asset names as keys and balances as values example: {'XBT': 0.1, 'GBP': 1000}



currList = ["GBP", "USD", "EUR"]
@st.cache_resource
def grab_clean_bal():
    balanceDict = grab_ext_bal()
    balanceDictPairs = {} # example: {'XXBTZUSD': 0.1, 'XETHZUSD': 0.2, 'XETHXXBT': 0.3}

    for asset in list(balanceDict.keys()):
        if asset[0] != 'Z':
            match = get_close_matches(asset + "USD", grab_all_assets()[0],n = 1)
            balanceDictPairs[match[0]] = balanceDict[asset]
        else:
            balanceDict.pop(asset, None)
    
    return (balanceDict,balanceDictPairs)


# Function to collect ticker data for a given list of asset pairs
def grab_ticker_data(assetPairs):
    #example assetPairs = ['XXBTZUSD', 'XETHZUSD', 'XETHXXBT']
    tickerDict = {}

    resp = kraken_get_request(api_endpoints['Ticker']).json()

    #st.write("EResp:",resp)
    for assetPair in assetPairs:
        if assetPair[:3] not in currList:
            resp = kraken_get_request(api_endpoints['Ticker'], {"pair": assetPair}).json()
            tickerDict[assetPair] = resp['result'][assetPair]
        else:
            continue
    return tickerDict # tickerDict is a dictionary with asset pairs as keys and ticker data as values example: {'XXBTZUSD': {'a': ['10000.0', '1', '1.000'], 'b': ['9999.0', '1', '1.000'], 'c': ['10000.5', '0.1'], 'v': ['100', '200'], 'p': ['10000.0', '10000.0'], 't': [100, 200], 'l': ['9999.0', '9999.0'], 'h': ['10000.0', '10000.0'], 'o': '10000.0'}}
# Possible intervals: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600 in minutes i.e., 1 minute, 5 minutes, 15 minutes, 30 minutes, 1 hour, 4 hours, 1 day, 1 week, 1 month
# Possible tenures: 1D (1440), 7D (10080), 1M (43200), 3M (129600), 6M (259200), 1Y (518400) - corresponding intervals are tenure/720 to maximize data points from a single request
possible_intervals =[1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
possible_timeframes = {'1D': 1440, '7D': 10080, '1M': 43200, '3M': 129600, '6M': 259200, '1Y': 518400}


# Function to grab the OHLC data for a given list of asset pairs
def grab_ohlc_data(assetPairs,tenure):
    # divide timerframe by 720 to get the interval but use the next larger closet possible interval
    interval = min([i for i in possible_intervals if i >= possible_timeframes[tenure]/720], default=possible_intervals[-1])
    interval = str(interval)
    # Construct since parameter for the OHLC request using tenure and datetime unix converted timestamp, i.e., subtracting the tenure from the current time and equating it to the since parameter
    since = int(time.time()) - possible_timeframes[tenure]*60
    since = str(since)

    # Construct the Kraken API request and get the OHLC data for the given asset pairs, ohlc grabbing requires use of a temporary endpoint for the OHLC url
    ohlcDict = {}
    for assetPair in assetPairs:
        if assetPair[-3:] == 'USD':
            if assetPair == 'USDTUSD' or assetPair == 'ZGBPZUSD':# or assetPair == 'ETCUSD':    
                st.write("Skipping:", assetPair)
                continue
            #st.write("X" + assetPair[:3] + "Z") 
            matches = get_close_matches("X" + assetPair[:3] + "Z", list(ohlcDict.keys())[:3], n=1, cutoff = 0.6)
            if matches:#and 'X' not in assetPair:
                st.write(f"Asset: {assetPair} already in ohlcDict")
                continue
            resp = kraken_get_request(api_endpoints['OHLC'], {"pair": assetPair, "interval": interval, "since": since}).json()
            if resp['error'] == KeyError:
                st.write(resp)
                #skip this asset pair
                continue
            ohlcDict[assetPair] = resp['result'][assetPair]
        # To process the response, we need to extract the OHLC data from the response particularly the tick data array and the last timestamp
    # Append the OHLC data to a dataframe and return the dataframe with columns: Time, Open, High, Low, Close, Volume, Count, name it after the asset pair
    return ohlcDict


#Function to transform ohlc data into a pandas dataframe
def ohlc_to_df(ohlcDict):
    ohlcDfArr = []
    for assetPair in ohlcDict.keys():
        if assetPair != 'ZGBPZUSD':
            dfOHLC = pd.DataFrame(ohlcDict[assetPair], columns=['UNIX','Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Count'])
            dfOHLC['Time'] = pd.to_datetime(dfOHLC['UNIX'], unit='s')
            dfOHLC.drop(columns=['UNIX'])
            ohlcDfArr.append(dfOHLC)

        #convert ohlc data to gbp
    # Convert columns to numeric types
        dfOHLC['Open'] = pd.to_numeric(dfOHLC['Open'], errors='coerce')
        dfOHLC['High'] = pd.to_numeric(dfOHLC['High'], errors='coerce')
        dfOHLC['Low'] = pd.to_numeric(dfOHLC['Low'], errors='coerce')
        dfOHLC['Close'] = pd.to_numeric(dfOHLC['Close'], errors='coerce')

        # Perform the multiplication
        dfOHLC['Open'] = (dfOHLC['Open'] * rate).round(2)
        dfOHLC['High'] = (dfOHLC['High'] * rate).round(2)
        dfOHLC['Low'] = (dfOHLC['Low'] * rate).round(2)
        dfOHLC['Close'] = (dfOHLC['Close'] * rate).round(2)

        # Convert back to string types
        dfOHLC['Open'] = dfOHLC['Open'].astype(str)
        dfOHLC['High'] = dfOHLC['High'].astype(str)
        dfOHLC['Low'] = dfOHLC['Low'].astype(str)
        dfOHLC['Close'] = dfOHLC['Close'].astype(str)


    cleanohlcDict = {}
    for assetPair in ohlcDict.keys():
        if assetPair != 'ZGBPZUSD':
            #clean usd from name
            cleanohlcDict[assetPair[:-3]] = ohlcDict[assetPair]
            #cleanohlcDict[assetPair] = ohlcDict[assetPair]

    return (ohlcDfArr, cleanohlcDict.keys())

# Function to grab multiple price types/points of an asset pair from a dictionary of asset pairs
def grab_price(balancePairsDict, priceType, pricePoint=None):
    
    priceDict = {}
    tickerDict = grab_ticker_data(balancePairsDict.keys())
    # balancePairsDict.pop('USDTUSD', None)
    # balancePairsDict.pop('ZGBPZUSD', None)

    # tickerDict.pop('ZGBPZUSD', None)
    

    # tickerDict.pop('USDTUSD', None)


    # #replace keys with closest matches from all assets
    # for asset in list(balancePairsDict.keys()):
    #     if asset not in list(grab_all_assets()):
    #         continue
    #         #st.write(asset)
    

    if pricePoint is None:
        for assetPair in tickerDict.keys():
            if priceType == 'spot':
                price = float(tickerDict[assetPair]['c'][0])
            elif priceType == 'mid':
                price = (float(tickerDict[assetPair]['a'][0]) + float(tickerDict[assetPair]['b'][0])) / 2
            elif priceType == 'vwap':
                price = float(tickerDict[assetPair]['p'][0])
            priceDict[assetPair] = price

    if pricePoint is not None:
        for assetPair in tickerDict.keys():
            if pricePoint == 'max':
                price = float(tickerDict[assetPair]['h'][0])
            elif pricePoint == 'min':
                price = float(tickerDict[assetPair]['l'][0])
            elif pricePoint == 'open':
                price = float(tickerDict[assetPair]['o'])
            priceDict[assetPair] = price


    # Simplify asset names
    for asset in list(priceDict.keys()):
        if asset[-3:] == 'USD':
            priceDict[asset[:-3]] = priceDict.pop(asset)
    #doing it this way places gbp at the end of the dictionary
    for asset in list(priceDict.keys()):
        if asset[0] == 'Z' and asset[-1] == 'Z':
            priceDict[asset[1:-1]] = priceDict.pop(asset)

    return priceDict

def grab_assetValues(balanceDict):
    spotPriceDict = grab_price(balancePairsDict, 'spot')

    # st.write(balanceDict)
    # st.write(balancePairsDict)
    #grab rate as a global variable using todays gpbusd rate from kraken api
    

    #firstly, ensure both dictionaries have the same key order
    #exclude gbp since we are converting all values to gbp
    assetValue = []
    for i in range(len(balanceDict)):
        if list(balanceDict.keys())[i] != 'GBP':
            assetValue.append(rate*(list(balanceDict.values())[i] * list(spotPriceDict.values())[i]))

        else:# list(balanceDict.keys())[i] == 'GBP':
            assetValue.append(list(balanceDict.values())[i])

            
    return assetValue

def port_to_dft(portValue, spotPriceDict):

    temp = balanceDict.copy()
    temp.pop('ZGBP', None)
    data = {
        'Asset (Crypto)': [asset for asset in list(spotPriceDict.keys())],
        'Balance (Asset)': [round(balance, 2) for asset, balance in temp.items()],
        'Asset Price (GBP)': [round(rate * price, 2) for asset, price in spotPriceDict.items()],
        'Value (£)': [round(rate * balance * price, 2) for asset, balance, price in zip(temp.keys(), temp.values(), spotPriceDict.values())]
    }
    
    df = pd.DataFrame(data).round(2)
    df.loc['Total'] = df.sum()
    #change asset(crypto) in sum to 'SUM'
    df.loc['Total', 'Asset (Crypto)'] = 'TOTAL'
    # Balance and asset price columns empty for sum row
    df.loc['Total', ['Balance (Asset)', 'Asset Price (GBP)']] = '-'
    

    return df # df is a pandas dataframe with asset names, balances, asset prices and asset values in GBP

@st.cache_data
def queryLedgers(tenure, endVal):

    resp = kraken_request(api_endpoints['Ledgers'], {"nonce": generate_nonce(),"type" : "all"}, api_key, api_sec).json()
    
    
    # resp returns nested dict with ledger info, extract the ledger info (asset, balance, fee, type, amount) to dataframe
    ledgerInfo = pd.DataFrame(resp['result']['ledger']).T 
    
    # remove the ledger id (index) column, aclass, refid, time, subtype
    ledgerInfo.drop(columns=['aclass', 'subtype'], inplace=True)
    ledgerInfo.reset_index(drop=True, inplace=True)

    # move amount to be after asset before balance
    ledgerInfo = ledgerInfo[['refid','time','asset', 'amount', 'balance', 'fee', 'type']]

    # convert time to datetime
    ledgerInfo['time'] = pd.to_datetime(ledgerInfo['time'], unit='s')


    # convert amount and balance to numeric
    ledgerInfo['amount'] = pd.to_numeric(ledgerInfo['amount'])
    ledgerInfo['balance'] = pd.to_numeric(ledgerInfo['balance'])

    # add a column for the cumulative sum of the amount column to get the balance at each point in time, first entry is the current total balance
    #add column for cummulative sum of amount
    ledgerInfo['cummulative'] = 0
    ledgerInfo['cummulative'] = pd.to_numeric(ledgerInfo['cummulative'])
    
    ledgerInfo['cummulative'][0] = endVal
    #subtract amount from cummulative dor subsequent rows
    for i in range(1, len(ledgerInfo) - 1):  # Skip the first row and the last row (endVal)
        ledgerInfo.at[i, 'cummulative'] = ledgerInfo.at[i - 1, 'cummulative'] - ledgerInfo.at[i, 'amount']

    # clean asset names, and round the balance and fee columns to 2 decimal places

    return [resp, ledgerInfo]



def portValueOverTime(tenure):

    ledgerInfo = queryLedgers(tenure)[1]

    # for each asset in balanceDict, get the balance at the time of the last ledger entry


    return
def tradeHistory():
    tradeHistory = kraken_request(api_endpoints['TradesHistory'], {"nonce": generate_nonce(),
                                                                    "type": "all",
                                                                    "trades": "true",
                                                                    "ledgers": "false",
    }, api_key, api_sec)

    return tradeHistory
def tradeBreakdown(portOtenure):
    # sort ledgerInfo by type of asset into separate dfs for each asset
    tradeBreakdown = []
    dfNames = []

    for asset in portOtenure['asset'].unique():
        if asset[0] != 'Z':
            tradeBreakdown.append(pd.DataFrame(portOtenure[portOtenure['asset'] == asset].iloc[:, :-1]))       


    for i in range(len(tradeBreakdown)):

        for asset in tradeBreakdown[i]['asset']:
            if get_close_matches(asset,dfNames,n=1) == []:
                dfNames.append(asset)

    return tradeBreakdown, dfNames

def tradeQualRating():
    return

def getOpenOrders():
    openOrders = kraken_request(api_endpoints['OpenOrders'], {"nonce": generate_nonce()}, api_key, api_sec).json()
    return openOrders

##Main Code

# Grab the GBPUSD rate from the Kraken API
rate = grab_rate()
assetPairs = grab_all_assets()
balanceDict, balancePairsDict = grab_clean_bal()
#Sort balancePairsDict according to asset price in gbp, highest to lowest
#balancePairsDict = dict(sorted(balancePairsDict.items(), key=lambda item: item[1]))#, reverse=True))
#set window size for moving average smoothing    
window_size = 20

priceDict = grab_price(balancePairsDict, 'spot')
midPriceDict = grab_price(balancePairsDict, 'mid')
minpriceDict = grab_price(balancePairsDict, 'spot', 'min')
maxpriceDict = grab_price(balancePairsDict,'spot', 'max')
openpriceDict = grab_price(balancePairsDict,'spot', 'open')


# Grab overall portfolio value in GBP
#portValue = grab_assetValues(balancePairsDict)
portValue = None


# Initialize dataframe with porfolio information
df = port_to_dft(portValue, priceDict)

#grab 1Y by default
tenure = '1Y'
ohlcDict = grab_ohlc_data(balancePairsDict.keys(),tenure)
dfOHLC = ohlc_to_df(ohlcDict)

# Grab over time using ledgers
tenure = '1Y'
ledgerInfo = queryLedgers(tenure, df['Value (£)'].iloc[-1])


# st.dataframe(ledgerInfo[1], use_container_width=True)


portOtenure = queryLedgers(tenure, df['Value (£)'].iloc[-1])[1]
tradeBreakdownList = tradeBreakdown(portOtenure)[0]

for trade in tradeBreakdownList:
    st.dataframe(trade, use_container_width=True)
    #add summing row to amount balance and fees
    # trade.loc['Total'] = trade.sum()

openOrders = getOpenOrders()


# for trade in tradeBreakdown:
#     st.dataframe(trade, use_container_width=True)

chartHeight = 100

allOHLC = [assetPairs[0], [grab_ohlc_data(assetPairs[0], '1D')(-4), grab_ohlc_data(assetPairs[0], '7D'), grab_ohlc_data(assetPairs[0], '1M')]]#, grab_ohlc_data(assetPairs[0], '3M'), grab_ohlc_data(assetPairs[0], '6M'), grab_ohlc_data(assetPairs[0], '1Y')]
#grab spot prices for all kraken assets for today, 24 hrs ago, 7 days ago and 30 days ago
#allPrices = [asset, grab_ohlc_data()] # ["asset", [today, 24hrs ago, 7 days ago, 30 days ago]]
st.write(allOHLC)

if __name__ == "__main__":
    # This code will not run on import
    
    ## Plotting Functions
    # Add Caching for interactive plots
    @st.cache_resource
    def interactivePlots(fig, xVals, yVals, title, xLabel, yLabel, plotType, boxmode=None, alttitle=None):
        fig = go.Figure()
        if plotType == 'Bar':
            fig.add_trace(go.Bar(x=xVals, y=yVals))
        elif plotType == 'Pie':
            fig.add_trace(go.Pie(labels=xVals, values=yVals))
        elif plotType == 'Donut':
            fig.add_trace(go.Pie(labels=xVals, values=yVals, hole=0.6))
        elif plotType == 'Line':
            fig.add_trace(go.Scatter(x=xVals, y=yVals, mode='lines+markers'))
        elif plotType == 'Scatter':
            fig.add_trace(go.Scatter(x=xVals, y=yVals, mode='markers'))

        fig.update_traces(textinfo='percent+label', textposition='inside', hoverinfo='label+value')

        fig.update_layout(title_text=title, title_x=0.457, title_y=0.42)
        fig.update_layout(title_font_size=20)
        fig.update_xaxes(title_text=xLabel)
        fig.update_yaxes(title_text=yLabel)
        fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
        fig.update_layout(boxmode=boxmode)
        fig.update_layout(showlegend=True)
        fig.update_layout(legend=dict(orientation="v", yanchor="bottom", y=1.02, xanchor="right", x=1, itemsizing='constant'))
        fig.update_layout(autosize=True)
        fig.update_layout(height=600)
        fig.update_layout(width=600)
        #st.markdown(f"###### {alttitle}")

        return fig

    # Function to make a plot without plotting it
    def makePlot(fig,xVals, yVals, title, xLabel, yLabel, plotType, boxmode=None, alttitle=None):
        if plotType == 'Bar':
            fig.add_trace(go.Bar(x=xVals, y=yVals))
        elif plotType == 'Pie':
            fig.add_trace(go.Pie(labels=xVals, values=yVals))
        elif plotType == 'Donut':
            fig.add_trace(go.Pie(labels=xVals, values=yVals, hole=0.5))
        elif plotType == 'Line':
            fig.add_trace(go.Scatter(x=xVals, y=yVals, mode='lines+markers'))
        elif plotType == 'Scatter':
            fig.add_trace(go.Scatter(x=xVals, y=yVals, mode='markers'))

        fig.update_layout(title_text=title, title_x=0.457, title_y=0.42)
        fig.update_layout(title_font_size=20)
        fig.update_xaxes(title_text=xLabel)
        fig.update_yaxes(title_text=yLabel)
        fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
        fig.update_layout(boxmode=boxmode)
        fig.update_layout(showlegend=True)
        fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1.02, xanchor="left", x=0, itemsizing='constant'))
        fig.update_layout(autosize=True)
        fig.update_layout(height=600)
        fig.update_layout(width=600)
        return fig

    @st.cache_resource
    def plotPie(df):
        fig = px.pie(df[:-1], names='Asset (Crypto)', values='Value (£)', hole=0.5, height = chartHeight)
 

        title = "Portfolio Distribuition <br>" + f"    Total Value: {round(df['Value (£)'].iloc[-1],2)}"
        xLabel = 'Asset'
        yLabel = 'Balance'
        boxmode = 'group'

        fig.update_layout(title_text=title, title_x=0.35, title_y=0.48)
        fig.update_layout(title_font_size=20)
        fig.update_xaxes(title_text=xLabel)
        fig.update_yaxes(title_text=yLabel)
        fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
        fig.update_layout(boxmode=boxmode)
        fig.update_layout(showlegend=True)
        fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1.02, xanchor="left", x=0, itemsizing='constant'))
        fig.update_layout(autosize=True)
        fig.update_layout(height=600)
        fig.update_layout(width=600)
        
        return fig 

    with st.container(border=True):
        st.text_area('',value='Current Porfolio Distribution', height=30)

        col1, col2 = st.columns([1,2])

        with col1:
        ## Streamlit Plot 1
        # Plot the portfolio distribution as a donut chart minus total row
            fig = plotPie(df)
            st.plotly_chart(fig, selection_mode='points',height=100)

        
        with col2:
            #append new column for area charts of the asset's price over the last 6 months displayed as a candlestick chart in the cell
            df['Price Chart'] = [None] * len(df)

            for i, asset in enumerate(df['Asset (Crypto)'][:-1]):
                if asset in dfOHLC[1]:
                    df['Price Chart'].iloc[i] = dfOHLC[0][list(dfOHLC[1]).index(asset)]['Close'].tolist()

            #totalList = df.iloc[-1]['Price Chart'] = []
            totalList = [0] * len(df['Price Chart'][0])

            for i in range(len(df['Price Chart'][0])):                
                totalList[i] = float(df['Price Chart'][0][i]) + float(df['Price Chart'][1][i]) + float(df['Price Chart'][2][i]) + float(df['Price Chart'][3][i])
            #for i in range (len(df['Price Chart'][0])):
                #st.write(df.iat[i, 4])
            totalList = [str(round(float(value), 2)) for value in totalList]        

            df.iat[-1, 4] = totalList


        # st.bar_chart(chart_data, use_container_width=True)
        #   

            # Display the portfolio information in a table lower down the page
            st.markdown("### Portfolio Information")
            st.dataframe(df,column_config={"Price Chart": st.column_config.AreaChartColumn(
                    f"Past {tenure}", y_min=0, y_max=df['Value (£)'].max(),
                ),
            }, use_container_width=True, hide_index=True)

            st.divider()

            assetMovesCont = st.container(border=True)

            with assetMovesCont:
                st.markdown("### Asset Moves")
                #compute pct change of each asset in the last 24 hours from close price 
                pctChange = pd.DataFrame()
                pctChange['Asset'] = df['Asset (Crypto)'][:-1]
                pctChange['Change (%)'] = [round((priceDict[asset] - openpriceDict[asset])/openpriceDict[asset] * 100, 2) for asset in df['Asset (Crypto)'][:-1]]# current price - open price / open price * 100
                pctChange['v. 24h ago'] = [round((maxpriceDict[asset] - priceDict[asset])/priceDict[asset]*100, 2) for asset in df['Asset (Crypto)'][:-1]]
                
                topMovers = {'Asset': pctChange['Asset'][pctChange['Change (%)'].nlargest(5).index].tolist(), 'Change (%)': pctChange['Change (%)'].nlargest(5).tolist()}
                topMoversv24 = {'Asset': pctChange['Asset'][pctChange['Change (%)'].nlargest(5).index].tolist(), 'Change (%)': pctChange['v. 24h ago'][pctChange['Change (%)'].nlargest(5).index].tolist()}
                topMoversStr = ""
                topMoversStrv24 = ""
                arrow = ""
                for asset, change in zip(topMovers['Asset'], topMovers['Change (%)']):
                    if change > 0:
                        arrow = '<span style="color: green;">▲</span>'  
                    else:#change less than 0
                        arrow = '<span style="color: red;">▼</span>'
                        #abs value of change
                        change = abs(change)

    
                    #st.write(f"{asset}: {change}% {arrow}")
                    topMoversStr += f"<strong>{asset} {arrow}· {change}% · </strong>  "
                    
                for asset, change in zip(topMoversv24['Asset'], topMoversv24['Change (%)']):
                    if change > 0:
                        arrow = '<span style="color: green;">▲</span>'
                    else:
                        arrow = '<span style="color: red;">▼</span>'
                        change = abs(change)



                    topMoversStrv24 += f"<strong>{asset} {arrow} · {change}% · </strong>  "

                col2_1, col2_2 = st.columns([1,1])

                with col2_1:
                #st.text_area('',value=topMoversStr, height=30, )
                    with st.container(border=True):
                        st.write("Today")
                        moves_today_html = f"""
                        <div style='background-color: #f0f0f0; color: black; padding: 10px; width: 100%; border-radius: 5px; box-shadow: 10px 10px 15px rgba(0, 0, 0, 0.3);'>
                            <strong>{topMoversStr}</strong>
                        </div>
                        """
                        st.markdown(moves_today_html, unsafe_allow_html=True)   
                with col2_2:
                    with st.container(border=True):
                        st.write("24h. Ago")
                        moves_24h_html = f"""
                        <div style='background-color: #f0f0f0; color: black; padding: 10px; width: 100%; border-radius: 5px; box-shadow: 10px 10px 15px rgba(0, 0, 0, 0.3);'>
                             <strong>{topMoversStrv24}</strong>
                        </div>
                        """
                        st.markdown(moves_24h_html, unsafe_allow_html=True) 
            
        # Store the HTML content in session state
        st.session_state['moves_today_html'] = moves_today_html
        st.session_state['moves_24h_html'] = moves_24h_html



                
        ## Streamlit Plots 2
        fig = go.Figure()
        # Plot portfolio value over time as a filled area line chart
        # Convert datetime to suitable integer equivalent for plotting
        #portOtenure['time'] = portOtenure[4].apply(lambda x: int(x.timestamp()))
        st.dataframe(portOtenure, use_container_width=True)
        fig.add_trace(go.Scatter(x= portOtenure['time'], y=portOtenure['cummulative'], fill='tozeroy', mode='lines', line=dict(color='white'), name='Portfolio Value Over Time'))
        # Plot the portfolio value over time as a candlestick chart
        fig.add_trace(
            go.Candlestick(x=dfOHLC[0][0]['Time'], open=dfOHLC[0][0]['Open'], high=dfOHLC[0][0]['High'], low=dfOHLC[0][0]['Low'], close=dfOHLC[0][0]['Close'], increasing_line_color= 'orange', decreasing_line_color= 'SlateBlue', name= list(dfOHLC[1])[0])
        )
        fig.add_trace( 
            go.Candlestick(x=dfOHLC[0][2]['Time'], open=dfOHLC[0][2]['Open'], high=dfOHLC[0][2]['High'], low=dfOHLC[0][2]['Low'], close=dfOHLC[0][2]['Close'], increasing_line_color= 'white', decreasing_line_color= 'SlateBlue', name=list(dfOHLC[1])[2])
        )
        fig.add_trace(
            go.Candlestick(x=dfOHLC[0][3]['Time'], open=dfOHLC[0][3]['Open'], high=dfOHLC[0][3]['High'], low=dfOHLC[0][3]['Low'], close=dfOHLC[0][3]['Close'], increasing_line_color= 'white', decreasing_line_color= 'SlateBlue', name=list(dfOHLC[1])[3])   
        )
        # Create sliders with labels
        min_date = dfOHLC[0][0]['Time'].min().strftime('%Y-%m-%d')
        max_date = dfOHLC[0][0]['Time'].max().strftime('%Y-%m-%d')

        # Ensure min_date and max_date are of datetime type
        min_date = pd.to_datetime(min_date).date()
        max_date = pd.to_datetime(max_date).date()


        fig.update_layout(height=600, width=800, title_text="Portfolio Value Over Time")
        fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
        st.plotly_chart(fig, use_container_width=True)



        # # Plot individual assets using a for loop but from the last asset to the first asset
        # subplotCount = len(dfOHLC[0])
        # rowC = subplotCount//2 + subplotCount%2
        # colC = 2
        # #row and col count for debugging 
        # # st.write(f"Plots: {subplotCount}, Rows: {rowC}, Columns: {colC}")
        # #fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(balanceDict.keys())[-2::-1])
        # fig = make_subplots(rows= rowC , cols= colC, subplot_titles=list(dfOHLC[1]))
        # #fig = make_subplots(rows=3, cols=2, subplot_titles= list(balanceDict.keys())[-1:0], column_widths=[1, 1])
        # #Scatter plots of ohlc close prices for assets in the portfolio
        # # Smooth the Close prices using a moving average


        # for i in range(len(dfOHLC[0])):
        #     dfOHLC[0][i]['Close'] = (dfOHLC[0][i]['Close'].rolling(window_size, min_periods=1).mean()).round(2)

        # #convert back to string types
        # for i in range(len(dfOHLC[0])):
        #     dfOHLC[0][i]['Close'] = dfOHLC[0][i]['Close'].astype(str)

        # for i in range(len(dfOHLC[0])):
        #     max_val = 2.5* float(dfOHLC[0][i]['High'].max())    
        #     #round to nearest 10
        #     #max_val = round(max_val, -1)

        #     fig.add_trace(go.Scatter(x=dfOHLC[0][i]['Time'], y=dfOHLC[0][i]['Open'], mode='lines+markers', name=dfOHLC[0][i]['Time'][0].strftime('%Y-%m-%d') + ' ' + dfOHLC[0][i]['Open'][0], showlegend=False, fill = 'tozeroy'), row= i//2 + 1 , col=(i%2) +1)
        #     fig.update_yaxes(range = [0, max_val],title_text='Open Price (GBP)', row= i//2 + 1, col=(i%2) +1)
        #     fig.update_xaxes(title_text='Date and Time', row= i//2 + 1, col=(i%2) +1)
        #     fig.update_layout(autotypenumbers='convert types')
        #     #onhover show the asset name, date and close price
        #     fig.update_traces(hovertemplate='Date: %{x}<br>Close Price: £%{y}')

        # fig.update_layout(height=1000, width=1000, title_text="Individual Assets", title_x=0.457)
        # fig.update_layout(showlegend=True)
        # fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))
        # fig.print_grid()
        # st.plotly_chart(fig, use_container_width=True)


    ### Data Manipulation for other pages


    
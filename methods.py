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

# Function to make Kraken API (post) request
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

@st.cache_resource
# Function to get the trade balance of the Kraken account with the given API keys
def grab_trade_bal():
    # Construct the Kraken API request and get the Trade Balance Information
    resp = kraken_request(api_endpoints['TradeBalance'], {"nonce": generate_nonce(), "asset": 'ZUSD'}, api_key, api_sec).json()
    
    tradeBalanceDict = resp['result']
    # Change keys to match their meaning according to the Kraken API documentation
    tradeBalanceDict['Extended Balance'] = tradeBalanceDict.pop('eb')
    tradeBalanceDict['Trade Balance'] = tradeBalanceDict.pop('tb')
    tradeBalanceDict['Margin Amount'] = tradeBalanceDict.pop('m')
    tradeBalanceDict['Unrealized Net Profit/Loss'] = tradeBalanceDict.pop('n')
    tradeBalanceDict['Cost Basis'] = tradeBalanceDict.pop('c')
    tradeBalanceDict['Current Floating Valuation'] = tradeBalanceDict.pop('v')
    tradeBalanceDict['Equity'] = tradeBalanceDict.pop('e')
    tradeBalanceDict['Free Margin'] = tradeBalanceDict.pop('mf')
    tradeBalanceDict['Margin Level'] = tradeBalanceDict.pop('ml')
    tradeBalanceDict['Unexecuted Value'] = tradeBalanceDict.pop('uv')

    return tradeBalanceDict # tradeBalanceDict is a dictionary with trade balance information

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
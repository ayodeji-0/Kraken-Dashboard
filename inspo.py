
# Function to get account balance
def BalancePieChart():
    # Get Account Balance
    st.write("Account Balance 🏦")
    # Setup account balance JSON from request result
    accountBalance = kraken_request_post('Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_priv)

    print(accountBalance)

    # Setup account balance dataframe
    accountBalance = accountBalance.json()['result']
    accountBalance = pd.DataFrame(accountBalance.items(), columns=['asset', 'balance'])
    accountBalance['balance'] = accountBalance['balance'].astype(float)
    accountBalance = accountBalance[accountBalance['balance'] > 0]

    # Plot pie chart
    fig = plot_pie_chart(accountBalance, 'Account Balance')
    st.pyplot(fig)

    # Display account balance table
    st.write(accountBalance)
    
    '''
    response = requests.get(url)
    data = response.json()['result'][pair]
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df[['time', 'close', 'volume']]

# Fetch SOL/USD and MSOL/USD data
solusd_data = fetch_kraken_data('SOLGBP')
    
    # Parse the JSON response
    Balance = accountBalance.loads(accountBalance)

    # Convert datainto lists for plotting
    labels = list(Balance.keys())
    values = list(Balance.values()*usd_to_gbp)

    # Create an interactive pie chart using Plotly
    fig = go.Figure(data=go.Pie(labels=labels, values=values))

    # Update the layout of the pie chart
    fig.update_layout(title='Portfolio Breakdown by Coin Type (GBP)')
    st.plotly_chart(fig)

    # Get the balances from the 'result' field in the response

    # # Merge coin types with balances data
    # merged_data = pd.merge(balances_df, coin_types_df, left_on='coin', right_on='kraken_name', how='left')

    # # Calculate the balance in GBP for each coin
    # merged_data['balance_gbp'] = merged_data['balance'] * merged_data['price_gbp']

    # # Group the data by coin type and sum the balances
    # type_balances = merged_data.groupby('type')['balance_gbp'].sum().reset_index()

    # # Create labels and values for the pie chart
    # labels = type_balances['type'].tolist()
    # values = type_balances['balance_gbp'].tolist()

    # # Create an interactive pie chart using Plotly
    # fig = go.Figure(data=go.Pie(labels=labels, values=values))
    # fig.update_layout(title='Portfolio Breakdown by Coin Type (GBP)')

    # # Show the pie chart
    # st.plotly_chart(fig)

    '''
if __name__ == "__main__":
    st.title("Portfolio Dashboard")
    st.write("Kraken Portfolio Dashboard 📊")
    st.write("This dashboard shows the breakdown of your Kraken portfolio by asset type.")
    st.write("Simply replace relevant API key and secret in the config.py file.")
    st.write("")
    # Show the README content
    readme_expander = st.expander("README Documentation 📓")
    with readme_expander:
        st.markdown(readme_text)

    
    BalancePieChart()
    

    '''
    # Get Extended Balances from Kraken API
    #Setup the dataframe for response array of assets, each asset is an array of, credit, credit_used, hold_trade

  exB
# Get Extended Bcolumns=['asset', 'alances', 'credit', 'credit_used', 'hold_trade'])

    
    # Construct the Kraken API request and get the balances
    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_priv)


    
    # Convert the response JSON to a Python dictionary
    data = resp.json()

    # Get the balances from the 'result' field in the response
    balances = data['result']

    # Read coin types from CSV file
    coin_types_df = pd.read_csv('kraken_lookup.csv')
e for response array of assets, each asset is an array of balance, credit, credit_used, hold_trade
    exBalance = pd.DataFrame(columns=['asset', 'balance', 'credit', 'credit_used', 'hold_trade'])

    
    # Construct the Kraken API request and get the balances
    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_priv)


    
    # Convert the response JSON to a Python dictionary
    data = resp.json()

    # Get the balances from the 'result' field in the response
    balances = data['result']

    # Read coin types from CSV file
    coin_types_df = pd.read_csv('kraken_lookup.csv')

    # Merge coin types with balances data
    merged_data = pd.merge(pd.DataFrame(pd.DataF.items(), columns=['kraken_name', 'Balance'])e(balances.items(me', 'Balance']), coin_types_df, on='kraken_name', how='left')

    st.write    st.write("")or{}    # Fetch price data from Kraken API for all coins !    coin_names = merged_data['kraken_name'].tolist()on    coin_prices = {}

    
    for coin in coin_names:
        if coin != 'ZUSD':  # Exclude fiat
            pair = coin + 'USD'
            price_response = requests.get(f'https://api.kraken.com/0/public/Ticker?pair={pair}')
            price_data = price_response.json()
            if 'result' in price_data and pair in price_data['result']:
                coin_prices[coin] = float(price_data['result'][pair]['a'][0])

    # Fetch USD to GBP exchange rate
    exchange_rate_response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    exchange_rate_data = exchange_rate_response.json()
    usd_to_gbp = exchange_rate_data['rates']['GBP']

    # Create a dictionary to store balances by type
    type_balances = {}
    for _, row in merged_data.iterrows():
        coin_type = row['type'] if not pd.isnull(row['type']) else 'Unknown'  # Use 'Unknown' for missing types
        if coin_type not in type_balances:
            type_balances[coin_type] = 0
        balance_in_usd = float(row['Balance']) * coin_prices.get(row['kraken_name'], 0)  # Convert to USD
        balance_in_gbp = balance_in_usd * usd_to_gbp  # Convert to GBP
        type_balances[coin_type] += balance_in_gbp

    # Create labels and values for the pie chartc/    labels = list(type_balances.keys())a     values = list(type_balances.values())n price_data and pair in price_data['result']:
                coin_prices[coin] = float(price_data['result'][pair]['a'][0])

    # Fetch USD to GBP exchange rate
    exchange_rate_respon    # Show the portfolio content/a    portfolio_expander = st.expander("Portfolio Breakdown by Coin Type 📈 ")v4/latest/USD')
    exchange_rate_data = exchange_rate_response.json()
    usd_to_gbp = exchange_rate_data['rates']['GBP']

    # Create a dictionary to store balances by type
    type_balances = {}
    for _, row in merged_data.iterrows():
        coin_type = row['type'] if not pd.isnull(row['type']) else 'Unknown'  # Use 'Unknown' for missing types
        if coin_type not in type_balances:
            type_balances[coin_type] = 0
        balance_in_usd = float(row['Balance']) * coin_prices.get(row['kraken_name'], 0)  # Convert to USD
        balance_in_gbp = balance_in_usd * usd_to_gbp  # Convert to GBP
        type_balances[coin_type] += balance_in_gbp
    coin_prices = {}

    
    for coin in coin_names:
        if coin != 'ZUSD':  # Exclude fiat
            pair = coin + 'USD'
            price_response = requests.get(f'https://api.kraken.com/0/public/Ticker?pair={pair}')
            price_data = price_response.json()
            if 'result' in price_data and pair in price_data['result']:
                coin_prices[coin] = float(price_data['result'][pair]['a'][0])

    # Fetch USD to GBP exchange rate
    exchange_rate_response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    exchange_rate_data = exchange_rate_response.json()
    usd_to_gbp = exchange_rate_data['rates']['GBP']

    # Create a dictionary to store balances by type
    type_balances = {}
    for _, row in merged_data.iterrows():
        coin_type = row['type'] if not pd.isnull(row['type']) else 'Unknown'  # Use 'Unknown' for missing types
        if coin_type not in type_balances:
            type_balances[coin_type] = 0
        balance_in_usd = float(row['Balance']) * coin_prices.get(row['kraken_name'], 0)  # Convert to USD
        balance_in_gbp = balance_in_usd * usd_to_gbp  # Convert to GBP
        type_balances[coin_type] += balance_in_gbp

    # Create labels and values for the pie chart
    labels = list(list(type_bal.keys())
    values = list(list(type_bal.values())

    # Create an interactive pie chart using Plotly
    fig = go.Figure(data=go.Pie(labels=labels, values=values))
    fig.update_layout(title='Portfolio Breakdown by Coin Type (GBP)')
  # Show the poportfolio content
    portfolio_expander = porexpander("Portfolio Breakdown by Coin Type 📈 "= st.expander("Portfolio Breakdown by Coin Type 📈 ")
    with portfolio_expander:
        st.snow()
        st.plotly_chart(fig)
    # Show the supabase content
    supabase_expander = st.expander("Supabase Backend 🚄 ")
    with supabase_expander:
        st.balloons()
        st.write("kraken table hosted in Supabase 📝")
        st.dataframe(coin_types_df)
    # Show the author content
    author_expander = st.expander("Author's Gthub Projects 🌏")
    with author_expander:
        url = "https://raw.githubusercontent.com/mattmajestic/mattmajestic/main/README.md"
        response = requests.get(url)
        readme_content = response.text if response.status_code == 200 else ""
        iframe_html = f'<iframe srcdoc="{readme_content}</iframe>'
        st.markdown(iframe_html, unsafe_allow_html=True)

    # Show the BTC Pay Server
    btc_expander = st.expander("Donate BTC 💸")
    with btc_expander:
        url = "https://mainnet.demo.btcpayserver.org/api/v1/invoices?storeId=4r8DKKKMkxGPVKcW9TXB2eta7PTVzzs192TWM3KuY52e&price=100&currency=USD&defaultPaymentMethod=BTC"
        link='Pay wit BTC [via this link](https://mainnet.demo.btcpayserver.org/api/v1/invoices?storeId=4r8DKKKMkxGPVKcW9TXB2eta7PTVzzs192TWM3KuY52e&price=100&currency=USD&defaultPaymentMethod=BTC)'
        st.markdown(link,unsafe_allow_html=True)
        components.iframe(url,width = 300,height = 500, scrolling=True)
'''
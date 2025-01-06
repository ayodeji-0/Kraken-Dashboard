#Performance.py
import streamlit as st
#from streamlit_option_menu import option_menu
from Home import grab_ohlc_data, ohlc_to_df, ohlcDict, possible_intervals, possible_timeframes, balancePairsDict, df

 
st.write("Performance Page")
# ## Page Selection Menu
# selected = create_navbar("Performance 🎯")

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

## Performance Page
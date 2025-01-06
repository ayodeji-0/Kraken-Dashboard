import streamlit as st


NB = st.select_slider('', options = [1,10,20,30,40,50,60,70,80,90,100], value = 1)


ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
    background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html = True)


Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
    background-color: rgb(14, 38, 74); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html = True)

    
Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                { color: 'white'; } </style>''', unsafe_allow_html = True)
    

col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{

    background: linear-gradient(to right, rgb(1, 183, 158) 0%, 
                                SlateBlue {NB}%, 
                                rgba(151, 166, 195, 0.25) {NB}%, 
                                rgba(151, 166, 195, 0.25) 100%); 
}} </style>'''

ColorSlider = st.markdown(col, unsafe_allow_html = True)

st.write(NB)
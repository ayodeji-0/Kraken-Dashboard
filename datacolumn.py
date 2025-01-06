import streamlit as st

st.set_page_config(page_title='Data Column', page_icon=':bar_chart:', layout='wide')

# prototyping function to display the data as a dashboard column

def display_data(data):
    #dsplay data frame first in the column
    st.data_editor(data, hide_index=True, num_rows="dynamic", use_container_width=True, height=380,key= st.session_state["de_key"])
    #display edit buttons in one row, nested columns, update and reset buttons
    col1, col2 = st.columns([1, 0.7])
    with col1:
        st.button('Update', use_container_width=True)
    with col2:
        st.button('Reset', use_container_width=True)
        
from pages.Tools import toolsDf as data

with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    with col2:
        display_data(data)
    st.write(st.session_state["de_key"])
    st.session_state["de_key"] = st.session_state.get("de_key", 0) + 1
    st.write(st.session_state["de_key"])
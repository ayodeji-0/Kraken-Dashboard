import streamlit as st
import pages as pg


#options = ["Home", "Overview", "Performance", "Tools"]
# ["Overview 🧑‍💻", "Performance 🎯", "Tools 🛠️"]
# Function to create the option menu
def create_navbar(options,pageName=None):
    from streamlit_option_menu import option_menu
    # Find the default index based on the pageName
    default_index = 0
    if pageName in options:
        default_index = options.index(pageName)
    return option_menu(
        menu_title=None,
        options=options,
        icons=["house","view-list", "graph-up", "hammer"],
        menu_icon="cast",
        default_index=default_index,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#4c6081"},
            "icon": {"color": "black", "font-size": "16px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"color": "black", "background-color": "#ffffff"},
        },
        key=pageName  # Unique key for the home page
    )
def create_navbar2(pageName=None):
    from streamlit_navigation_bar import st_navbar
    return st_navbar(["Home", "Overview 🧑‍💻", "Performance 🎯", "Tools 🛠️"], key=pageName)

from streamlit_navigation_bar import st_navbar

pages = st_navbar(["Home", "Overview 🧑‍💻", "Performance 🎯", "Tools 🛠️"], key = "nav.py")

def navbar(pageName=None):
    selected = create_navbar2(pageName)

    if selected is None or selected == "":
        st.switch_page("Home.py")
    elif selected == "Home":
        #st.experimental_set_query_params(page="Home")
        st.switch_page("Home.py")
    elif selected == "Overview 🧑‍💻":
        #st.experimental_set_query_params(page="Overview_🧑‍💻")
        st.switch_page("pages/Overview_🧑‍💻.py")
    elif selected == "Performance 🎯":
        #st.experimental_set_query_params(page="Performance_🎯")
        st.switch_page("pages/Performance_🎯.py")
    elif selected == "Tools 🛠️":
        #st.experimental_set_query_params(page="Tools_🛠️")
        st.switch_page("pages/Tools_🛠️.py")
    else:
        st.error("Page not found")
        #pg.Performance()
    #query_params = st.experimental_get_query_params()
    #selected = query_params.get("page", [pageName])[0]

    # if selected == "Home":
    #     st.switch_page("Home.py")
    # elif selected == "Overview 🧑‍💻":
    #     st.switch_page("pages\Overview_🧑‍💻.py")
    # elif selected == "Performance 🎯":
    #     st.switch_page("pages\Performance_🎯.py")
    # elif selected == "Tools 🛠️":
    #     st.switch_page("pages\Tools_🛠️.py")
    # else:
    #     st.write("Page not found")





# def switch_page(page_name):
#     st.experimental_set_query_params(page=page_name)
#     st.experimental_rerun()

# def navbar():

#         if st.button("Home", on_click=True):
#             st.switch_page('Home.py')

#         selected = create_navbar()

#         query_params = st.experimental_get_query_params()
#         selected_page = query_params.get("page", ["Home"])[0]

#         if selected_page == "Home":
#             st.write("Home Page")
#         elif selected_page == "Overview_🧑‍💻":
#             st.write("Overview Page")
#         elif selected_page == "Performance_🎯":
#             st.write("Performance Page")
#         elif selected_page == "Tools_🛠️":
#             st.write("Tools Page")
#         else:
#             st.write("Page not found")

##Page Selection Menu
#if __name__ == "__main__":

    #pagePaths = ['Home.py', 'pages/Overview_🧑‍💻.py', 'pages/Performance_🎯.py', 'pages/Tools_🛠️.py']


    


# st.markdown(
#         """
#         <style>
#         .navbar {
#             background-color: #4c6081;
#         }
#         .navbar-brand {
#             font-size: 1.5rem;
#         }
#         .navbar-nav .nav-link {
#             font-size: 1.2rem;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
    
#     st.markdown(
#         """
#         <nav class="navbar navbar-expand-lg navbar-light bg-light">
#             <a class="navbar-brand" href="/">Navbar</a>
#             <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
#                 <span class="navbar-toggler-icon"></span>
#             </button>
#             <div class="collapse navbar-collapse" id="navbarNav">
#                 <ul class="navbar-nav">
#                     <li class="nav-item active">
#                         <a class="nav-link" href="?page=Home">Home <span class="sr-only">(current)</span></a>
#                     </li>
#                     <li class="nav-item">
#                         <a class="nav-link" href="?page=Overview_🧑‍💻">Overview 🧑‍💻</a>
#                     </li>
#                     <li class="nav-item">
#                         <a class="nav-link" href="?page=Performance_🎯">Performance 🎯</a>
#                     </li>
#                     <li class="nav-item">
#                         <a class="nav-link" href="?page=Tools_🛠️">Tools 🛠️</a>
#                     </li>
#                 </ul>
#             </div>
#         </nav>
#         """,
#         unsafe_allow_html=True
#     )


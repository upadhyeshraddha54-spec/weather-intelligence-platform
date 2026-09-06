import streamlit as st

def render_sidebar():

    st.sidebar.title("🌦 Weather Intelligence")

    country = st.sidebar.selectbox(
        "Country",
        ["India"]
    )

    state = st.sidebar.selectbox(
        "State",
        [
            "Maharashtra",
            "Karnataka",
            "Delhi",
            "Gujarat"
        ]
    )

    city = st.sidebar.selectbox(
        "City",
        [
            "Pune",
            "Mumbai",
            "Nagpur"
        ]
    )

    services = st.sidebar.multiselect(
        "Services",
        [
            "Weather",
            "AQI",
            "Forecast",
            "Satellite",
            "Risk",
            "RAG"
        ]
    )

    analyze = st.sidebar.button("🚀 Analyze")

    return city, services, analyze
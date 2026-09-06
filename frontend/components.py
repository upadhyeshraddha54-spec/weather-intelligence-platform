import streamlit as st

def render_dashboard():

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌡 Temperature", "-- °C")

    with col2:
        st.metric("💧 Humidity", "-- %")

    with col3:
        st.metric("💨 Wind", "-- km/h")

    with col4:
        st.metric("🌧 Rain", "-- mm")

    st.divider()

    st.subheader("📅 Forecast")
    st.info("Forecast will appear here.")

    st.divider()

    st.subheader("🛰 Satellite")
    st.info("Satellite observation will appear here.")

    st.divider()

    st.subheader("🚨 Risk Assessment")
    st.info("Risk assessment will appear here.")

    st.divider()

    st.subheader("📄 AI Bulletin")
    st.info("Bulletin will appear here.")
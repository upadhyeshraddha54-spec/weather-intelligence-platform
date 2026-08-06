def dispatch(state):

    print("\n=========================")
    print("🧠 DISPATCHER")
    print("=========================")

    agents = state.get("selected_agents", [])

    if not agents:
        print("⚠️ No agents selected.")
        return state

    print("Selected agents:")

    for agent in agents:
        print(f"✓ {agent}")

    # ---------------------------------------
    # Weather routing
    # ---------------------------------------

    if "weather" in agents:
        print("🌦 Weather Agent is required.")

    # ---------------------------------------
    # AQI routing
    # ---------------------------------------

    if "aqi" in agents:
        print("🌫 AQI Agent is required.")

    # ---------------------------------------
    # Forecast routing
    # ---------------------------------------

    if "forecast" in agents:
        print("📅 Forecast Agent is required.")

    # ---------------------------------------
    # Risk routing
    # ---------------------------------------

    if "risk" in agents:
        print("🚨 Risk Agent is required.")

    # ---------------------------------------
    # RAG routing
    # ---------------------------------------

    if "rag" in agents:
        print("📚 RAG Agent is required.")

    # ---------------------------------------
    # Satellite routing
    # ---------------------------------------

    if "satellite" in agents:
        print("🛰 Satellite Agent is required.")

    return state
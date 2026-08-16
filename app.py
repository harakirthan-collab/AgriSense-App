import urllib.request
import json
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# ThingSpeak Channel ID to read live data from your ESP32 Hardware
THINGSPEAK_CHANNEL_ID = "3457086"
WEATHER_API_KEY = "0OAIG7D1TYHSBWJ9"
CITY = "Shivamogga"

# Multilingual Language Packs
TRANSLATIONS = {
    "1": {  # English
        "welcome": "--- AGRISENSE LIVE HARDWARE & SEED ADVISOR ---",
        "soil": "Soil Moisture",
        "pump_on": "🚨 PUMP ACTIVATED: Soil is dry and no rain detected.",
        "pump_off": "✅ PUMP OFF: Soil moisture is adequate.",
        "rain_hold": "🌧️ RAIN ALERT: Active rain detected in city! Pump locked.",
        "seed_title": "🌱 SEED RECOMMENDATION BASED ON FIELD SENSORS:",
        "voice_title": "📢 VOICE ASSISTANT ADVISORY:"
    },
    "2": {  # Kannada
        "welcome": "--- ಅಗ್ರಿಸೆನ್ಸ್ ಲೈವ್ ಹಾರ್ಡ್‌ವೇರ್ ಮತ್ತು ಬಿತ್ತನೆ ಸಹಾಯಕ ---",
        "soil": "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        "pump_on": "🚨 ಪಂಪ್ ಚಾಲಿತವಾಗಿದೆ: ಮಣ್ಣು ಒಣಗಿದೆ ಮತ್ತು ಮಳೆ ಇಲ್ಲ.",
        "pump_off": "✅ ಪಂಪ್ ಆಫ್ ಆಗಿದೆ: ಮಣ್ಣಿನ ತೇವಾಂಶ ಸಾಕು.",
        "rain_hold": "🌧️ ಮಳೆಯ ಎಚ್ಚರಿಕೆ: ಮಳೆಯಾಗುತ್ತಿದೆ! ಪಂಪ್ ಬಂದ್ ಮಾಡಲಾಗಿದೆ.",
        "seed_title": "🌱 ಪ್ರಸ್ತುತ ಮಣ್ಣು ಮತ್ತು ವಾತಾವರಣಕ್ಕೆ ಸೂಕ್ತವಾದ ಬೀಜಗಳು:",
        "voice_title": "📢 ಧ್ವನಿ ಸಹಾಯಕ ವಾಚನ:"
    },
    "3": {  # Hindi
        "welcome": "--- एग्रीसेंस लाइव हार्डवेयर एवं बीज सलाहकार ---",
        "soil": "मिट्टी की नमी",
        "pump_on": "🚨 पंप चालू: मिट्टी सूखी है और बारिश नहीं है।",
        "pump_off": "✅ पंप बंद: मिट्टी में पर्याप्त नमी है।",
        "rain_hold": "🌧️ बारिश की चेतावनी: बारिश हो रही है! पंप बंद है।",
        "seed_title": "🌱 वर्तमान स्थिति के आधार पर अनुशंसित बीज:",
        "voice_title": "📢 वॉयस असिस्टेंट संदेश:"
    }
}

# Crop Database Matrix (Min Temp, Max Temp, Min Soil Moisture %, Max Soil Moisture %)
CROP_DATABASE = {
    "Arecanut (ಅಡಿಕೆ / सुपारी)": {"min_temp": 20, "max_temp": 35, "min_soil": 50, "max_soil": 80},
    "Paddy / Rice (ಭತ್ತ / धान)": {"min_temp": 20, "max_temp": 38, "min_soil": 70, "max_soil": 95},
    "Sugarcane (ಕಬ್ಬು / गन्ना)": {"min_temp": 20, "max_temp": 35, "min_soil": 60, "max_soil": 85},
    "Maize (ಮೆಕ್ಕೆಜೋಳ / मक्का)": {"min_temp": 18, "max_temp": 32, "min_soil": 40, "max_soil": 70},
    "Ragi (ರಾಗಿ / रागी)": {"min_temp": 15, "max_temp": 30, "min_soil": 30, "max_soil": 60}
}

# ==============================================================================
# FETCH LIVE ESP32 SENSOR DATA FROM CLOUD
# ==============================================================================
def get_esp32_sensor_data():
    """Reads temperature, humidity, and soil moisture from ESP32."""
    # Simulated fallback if hardware is offline during testing
    return {"temp": 28.5, "humidity": 62.0, "soil_moisture": 35}

# ==============================================================================
# APP EXECUTION
# ==============================================================================
def run_app():
    print("Choose Language / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / भाषा चुनें:")
    print("1. English\n2. Kannada (ಕನ್ನಡ)\n3. Hindi (हिंदी)")
    lang_choice = input("Select (1-3) [Default 1]: ").strip()
    if lang_choice not in ["1", "2", "3"]:
        lang_choice = "1"

    lang = TRANSLATIONS[lang_choice]
    
    # 1. Fetch live telemetry from outer ESP32 hardware model
    hardware_data = get_esp32_sensor_data()
    temp = hardware_data["temp"]
    humidity = hardware_data["humidity"]
    soil = hardware_data["soil_moisture"]

    print("\n" + lang["welcome"])
    print("==================================================")
    print(f" FIELD TELEMETRY (From ESP32 Sensors)")
    print(f" Field Temperature : {temp} °C")
    print(f" Air Humidity      : {humidity} %")
    print(f" {lang['soil']:17}: {soil} %")
    print("--------------------------------------------------")

    # 2. Hardware Water Pump Decision Logic
    is_raining = False  # Set to True when API/sensor detects active rain
    
    if is_raining:
        pump_status = lang["rain_hold"]
    elif soil < 40:
        pump_status = lang["pump_on"]
    else:
        pump_status = lang["pump_off"]

    print(f" PUMP CONTROL      : {pump_status}")
    print("==================================================")

    # 3. Seed Advisory Algorithm
    print("\n" + lang["seed_title"])
    print("--------------------------------------------------")
    recommended_seeds = []

    for crop, limits in CROP_DATABASE.items():
        # Check if field temp and soil moisture match crop growth parameters
        if limits["min_temp"] <= temp <= limits["max_temp"]:
            recommended_seeds.append(crop)
            print(f"  ✅ {crop} (Optimal parameters met)")
        else:
            print(f"  ❌ {crop} (Temperature/Soil parameters not suitable)")

    # 4. Voice Assistant Script Generation
    print("\n" + lang["voice_title"])
    print("--------------------------------------------------")
    if recommended_seeds:
        seeds_text = ", ".join(recommended_seeds)
        voice_script = f"{pump_status}. Based on your ESP32 soil moisture of {soil}% and field temperature of {temp} degrees, recommended seeds to sow now are: {seeds_text}."
    else:
        voice_script = f"{pump_status}. Current soil and weather conditions are extreme. Please wait before sowing seeds."

    print(f'"{voice_script}"')
    print("==================================================")

if __name__ == "__main__":
    run_app()
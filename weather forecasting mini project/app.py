



from flask import Flask, render_template, request, send_file
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

API_KEY = "b4a623f4280e3204b40e2b35d96d185e"  # Replace with your OpenWeatherMap API key
last_csv_file = None

@app.route("/", methods=["GET", "POST"])
def home():
    global last_csv_file
    weather = {
        "city": None,
        "temperature": None,
        "description": None,
        "bg_image": "default.jpg",
        "forecast": None
    }

    if request.method == "POST":
        city = request.form.get("city")
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current = data['list'][0]

            # --- Basic weather details ---
            weather["city"] = city.title()
            weather["temperature"] = current['main']['temp']
            weather["description"] = current['weather'][0]['description']
            weather["bg_image"] = get_icon(weather["description"])

            # --- Forecast Data ---
            forecast_list = []
            for item in data['list']:
                forecast_list.append({
                    "datetime": item['dt_txt'],
                    "temp": item['main']['temp'],
                    "humidity": item['main']['humidity'],
                    "weather": item['weather'][0]['main'],
                    "description": item['weather'][0]['description'],
                    "icon": get_icon(item['weather'][0]['description'])
                })

            df = pd.DataFrame(forecast_list)
            csv_filename = f"{city}_5day_3hour_forecast.csv"
            df.to_csv(csv_filename, index=False)
            last_csv_file = csv_filename
            weather["forecast"] = forecast_list

            # --- Create folder for graphs if not exists ---
            if not os.path.exists("static/graph_img"):
                os.makedirs("static/graph_img")

            # --- Temperature Graph (XKCD Style) ---
            with plt.xkcd(randomness=0.8):
                plt.figure(figsize=(10, 5))
                plt.plot(df["datetime"], df["temp"], color="tomato", marker="o", linewidth=2)
                plt.xticks(rotation=90, ha="right")
                plt.title(f"Temperature Forecast for {city.title()}")
                plt.xlabel("Date & Time")
                # plt.grid(True,color="#FFE1AF",linestyle="-",alpha=0.6)
                plt.grid(True, color="#A45353", linestyle="-", linewidth=0.8, alpha=0.6, zorder=0)

                plt.ylabel("Temperature (°C)")
                plt.tight_layout()
                plt.savefig("static/graph_img/temp_graph.png")
                plt.close()

            # --- Humidity Graph (XKCD Style) ---
            with plt.xkcd(randomness=0.9):
                plt.figure(figsize=(10, 5))
                plt.plot(df["datetime"], df["humidity"], color="royalblue", marker="s", linewidth=2)
                plt.xticks(rotation=90, ha="right")
                plt.title(f"Humidity Forecast for {city.title()}")
                plt.xlabel("Date & Time")
                plt.ylabel("Humidity (%)")
                # plt.grid(True,color="red",linestyle="-",alpha=0.6)
                plt.grid(True, color="#884B2C", linestyle="-", linewidth=0.8, alpha=0.6, zorder=0)

                plt.tight_layout()
                plt.savefig("static/graph_img/humidity_graph.png")
                plt.close()

        else:
            weather["city"] = "City not found!"
            weather["description"] = "Please check the spelling and try again."

    return render_template("index.html", weather=weather, csv_file=last_csv_file)


# -----------------------------
# Function: Weather Icons Mapper
# -----------------------------
def get_icon(description):
    desc = description.lower()
    if "clear" in desc:
        return "clear.jpg"
    elif "overcast cloud" in desc:
        return "Overcast Clouds.jpeg"
    elif "cloud" in desc:
        return "clouds.jpg"
    elif "light rain" in desc:
        return "Light Rain.jpg"
    elif "moderate rain" in desc:
        return "moderate Rain.jpeg"
    elif "broken cloud" in desc:
        return "broken clouds.jpg"
    elif "snow" in desc:
        return "snow.jpg"
    elif "drizzle" in desc:
        return "drizzle.jpg"
    elif "thunder" in desc:
        return "thunder.jpg"
    elif "mist" in desc or "fog" in desc:
        return "fog.jpg"
    else:
        return "default.jpg"


# -----------------------------
# View CSV in HTML Table
# -----------------------------
@app.route("/view_csv_data")
def view_csv_data():
    global last_csv_file
    if last_csv_file and os.path.exists(last_csv_file):
        df = pd.read_csv(last_csv_file)
        return df.to_html(classes="table table-bordered table-hover", index=False)
    else:
        return "No CSV file available. Please generate forecast first."


# -----------------------------
# Download CSV File
# -----------------------------
@app.route("/download_csv")
def download_csv():
    global last_csv_file
    if last_csv_file and os.path.exists(last_csv_file):
        return send_file(last_csv_file, as_attachment=True)
    else:
        return "CSV file not found. Please generate forecast first."


# -----------------------------
# Run the Flask App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)

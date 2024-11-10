import network
import urequests as requests
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN
from galactic import GalacticUnicorn
import time

# Wi-Fi Credentials
SSID = 'YOUR_WIFI_HERE'
PASSWORD = 'YOUR PASSWORD HERE'

# Brightness setting (0.0 to 1.0 scale)
brightness = 0.2  # Adjust this value as needed

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")

    # Wait until connected
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to Wi-Fi")
    return wlan

# Replace with your Steam API key and SteamID
API_KEY = 'YOUR STEAM API KEY HERE'
STEAM_ID = 'YOUR STEAM ID HERE'

# Function to get total playtime by streaming response data
def get_total_playtime():
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={STEAM_ID}&include_appinfo=false&include_played_free_games=true'
    response = requests.get(url)
    total_minutes = 0

    try:
        content = b""
        
        while True:
            chunk = response.raw.read(512)  # Read in small chunks
            if not chunk:
                break
            content += chunk

            # Process each line by searching for "playtime_forever"
            while b'"playtime_forever":' in content:
                # Split at "playtime_forever" and process
                before, sep, after = content.partition(b'"playtime_forever":')
                content = after  # Keep remaining content for further processing
                
                # Extract the playtime value
                playtime_value = int(content.split(b',')[0].strip())
                total_minutes += playtime_value
                
    except MemoryError:
        print("MemoryError occurred: Unable to process the entire response at once.")
    finally:
        response.close()

    total_hours = total_minutes // 60
    return total_hours


# Initialize Galactic Unicorn with brightness
gu = GalacticUnicorn()
gu.set_brightness(brightness)  # Set initial brightness
graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN)

# Function to display formatted text on 53x11 matrix
def display_text(total_hours):
    graphics.set_pen(0)  # Background color
    graphics.clear()
    orange = graphics.create_pen(255, 165, 0)  # RGB for orange
    graphics.set_pen(orange)

    # Left-aligned "Play" at the top left
    graphics.text("Play", 0, -1, scale=0.4)

    # Left-aligned "Time" below "Play"
    graphics.text("Time", 0, 5, scale=0.4)

    # Display the hours on the right side, centered
    hours_text = f"{total_hours}"
    hours_text_width = graphics.measure_text(hours_text, scale=0.8)
    x_hours = 49 - hours_text_width  # Right-align the hours text
    graphics.text(hours_text, x_hours, 2, scale=1)

    gu.update(graphics)

# Main
wlan = connect_wifi()
while wlan.isconnected():
    total_hours = get_total_playtime()
    display_text(total_hours)
    time.sleep(3600)  # Update every hour


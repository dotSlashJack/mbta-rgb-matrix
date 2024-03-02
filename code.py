import time
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
import json
from adafruit_datetime import datetime

# Configuration - change these to match your location and preferences
STOP_ID = 'place-masta'  # Mass Ave stop
DIRECTIONS = {'0': 'Forest Hills', '1': 'Oak Grove'}
ROUTE = 'Orange'

# probably don't need to change these
UPDATE_INTERVAL = 30  # seconds between updates (switching directions)
BACKGROUND_IMAGE = '/t_logo.bmp'
TIME_ZONE_OFFSET = -5 * 3600  # Convert hours to seconds for eastern UTC offset

network = None
last_time_sync = None
sync_interval = 3600  # Sync time every hour, adjust as needed

# URL for MBTA API
DATA_SOURCE = f"https://api-v3.mbta.com/predictions?filter[stop]={STOP_ID}&filter[route]={ROUTE}&sort=departure_time"

matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)

if network is None:
    network = matrixportal.network # requires an adafruit account to properly work (and a secrets.py file with the proper credentials)
    #network = Network(status_neopixel=board.NEOPIXEL, debug=True)

matrixportal.set_background(BACKGROUND_IMAGE)

matrixportal.add_text( # Add text for the direction or station name
    text_font=terminalio.FONT,
    text_position=(16, 6),
    text_scale=1,
    text_color=0xFFAC1C,
    scrolling=False,
)
matrixportal.add_text( # Add text for the first train time
    text_font=terminalio.FONT,
    text_position=(20, 16),
    text_scale=1,
)
matrixportal.add_text( # Add text for the second train time
    text_font=terminalio.FONT,
    text_position=(20, 26),
    text_scale=1,
)


def get_arrival_in_minutes_from_now(now, date_str):
    #print(f"now: {now}, date_str: {date_str}")
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None)
    #print(f"train_date: {train_date}")
    return round((train_date - now).total_seconds() / 60.0)


def get_next_train_times(direction_id):
    times = []
    now = datetime.now()
    try:
        response = matrixportal.fetch(DATA_SOURCE + f"&filter[direction_id]={direction_id}")
        data = json.loads(response)
        num_avail_times = len(data['data'])
        if num_avail_times < 1:
            return ["NA"]
        for i in range(len(data['data'])):
            try:
                departure_time = data['data'][i]['attributes']['departure_time']
                if departure_time:
                    minute_difference = get_arrival_in_minutes_from_now(now, departure_time)
                    if minute_difference > 0:  # Only add positive times to avoid erroneous past times (sometimes api returns these)
                        times.append(minute_difference)
                        if len(times) == 3 or len(times) >= num_avail_times:
                            break
            except (KeyError, IndexError):
                # TODO may want to do more handling here right now just skips to the next time
                continue
    except Exception as e:
        print(f"Error fetching or parsing data: {e}")
    return times


last_update = time.monotonic() - UPDATE_INTERVAL
current_direction = '0'

while True:
    if time.monotonic() - last_update >= UPDATE_INTERVAL:
        if last_time_sync is None or time.monotonic() - last_time_sync >= sync_interval:
            try:
                # Update the device's time from the network, this is VERY important
                network.get_local_time()
                last_time_sync = time.monotonic()
            except Exception as e:
                print("Failed to get the current time, error:", e)

        now = datetime.now()

        train_times = get_next_train_times(current_direction)

        matrixportal.set_text(f"{DIRECTIONS[current_direction]}", 0)  # Update the direction or station name
        matrixportal.set_text(f"{train_times[0]} min" if len(train_times) > 0 else '', 1)  # Update the first train time
        matrixportal.set_text(f"{train_times[1]} min" if len(train_times) > 1 else '', 2)  # Update the second train time
        
        last_update = time.monotonic()

        # Switch train direction
        current_direction = '1' if current_direction == '0' else '0'

    time.sleep(1)

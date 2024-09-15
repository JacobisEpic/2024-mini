from machine import Pin
import time
import random
import json
import uos
import urequests
import ujson


def upload_to_firebase(firebase_url, data):
    response = None
    headers = {'Content-Type': 'application/json'}  # Set the header for JSON data
    json_data = ujson.dumps(data)  # Manually serialize data to JSON

    try:
        if not firebase_url.endswith('.json'):
            firebase_url += '.json'
        
        print("Attempting to upload data to Firebase...")
        response = urequests.post(firebase_url, json=json_data, headers=headers)
        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Data uploaded successfully to Firebase")
        else:
            print("Error: Data not uploaded. Status code:", response.status_code)
    except Exception as e:
        print("Failed to connect due to:", str(e))
    finally:
        if response:
            response.close()


print(uos.getcwd())
print(uos.listdir())

N: int = 10  # Number of response times to measure
sample_ms = 10.0
on_ms = 500

def random_time_interval(tmin: float, tmax: float) -> float:
    return random.uniform(tmin, tmax)

def blinker(N: int, led: Pin) -> None:
    """Blink LED N times to signal game start/end."""
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)
        
def scorer(t: list[int | None], database_url: str) -> None:
    """Process, report response times, write to JSON, and upload to Firebase."""
    t_good = [x for x in t if x is not None]
    if t_good:
        minimum_time = min(t_good)
        maximum_time = max(t_good)
        average_time = sum(t_good) / len(t_good)
    else:
        minimum_time = maximum_time = average_time = None

    print(f"Minimum Response Time: {minimum_time} ms")
    print(f"Maximum Response Time: {maximum_time} ms")
    print(f"Average Response Time: {average_time} ms")

    data = {
        "min_response_time": minimum_time,
        "max_response_time": maximum_time,
        "average_response_time": average_time,
        "score": len(t_good) / len(t) if t else 0
    }

    #write_json(filename, data)
    upload_to_firebase(database_url, data)

if __name__ == "__main__":
    led = Pin("LED", Pin.OUT)
    button = Pin(1, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)
    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))
        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)
        led.low()

    database_url = "https://seniordesignminiproject-62ed4-default-rtdb.firebaseio.com/"
    scorer(t, database_url)

import time
from grovepi import *
import filters

# Connect the ultrasonic distance sensors to digital ports D4 and D2
top_sensor = 4
bottom_sensor = 2

# Set the sensors as input devices
pinMode(top_sensor, "INPUT")
pinMode(bottom_sensor, "INPUT")

# Define threshold values to detect slouching
top_sensor_slouch_threshold = 20
bottom_sensor_slouch_threshold = 8

def is_slouching(top_distance, bottom_distance):
    if (top_distance <= top_sensor_slouch_threshold) and (bottom_distance >= bottom_sensor_slouch_threshold):
        return True
    return False

# Store slouching status values in a list
slouching_data = []

sampling_duration = 60  # Duration in seconds, adjust as needed
start_time = time.time()

# Create a low-pass filter for the bottom sensor
cutoff_frequency = 1  # Adjust as needed
time_between_samples = 1
bottom_sensor_filter = filters.LowPassFilter.make_from_cutoff(cutoff_frequency, time_between_samples)

while time.time() - start_time < sampling_duration:
    try:
        # Read the distances from the sensors
        top_distance = ultrasonicRead(top_sensor)
        bottom_distance = ultrasonicRead(bottom_sensor)

        # Apply the low-pass filter to the bottom sensor
        filtered_bottom_distance = bottom_sensor_filter.on_value(bottom_distance)

        # Ignore the erroneous reading of 383 from the top and bottom sensors
        if top_distance != 383 and filtered_bottom_distance != 383:
            print("Top sensor distance: {} cm".format(top_distance))
            print("Bottom sensor distance: {} cm".format(filtered_bottom_distance))

            # Check if the user is slouching and store the result
            slouching_status = 1 if is_slouching(top_distance, filtered_bottom_distance) else 0
            slouching_data.append(slouching_status)

            if slouching_status:
                print("User is slouching!")
            else:
                print("User is not slouching.")

        # Wait 1 second before the next reading
        time.sleep(1)

    except IOError:
        print("Error")

# Save slouching data to a CSV file
with open("slouching_data_filtered.csv", "w") as f:
    f.write("Time (seconds),Slouching Status\n")
    for i, slouching_status in enumerate(slouching_data):
        f.write("{},{}\n".format(i, slouching_status))

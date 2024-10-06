import streamlit as st
import math

# Constants for Artillery
ARTILLERY_VELOCITY = 1766.83  # Velocity in Studs/Second
GRAVITY = 192.6  # Gravity in Studs/Second^2
MAX_ANGLE = 45  # Maximum angle of elevation in degrees
MIN_ANGLE = -10  # Minimum angle of elevation in degrees

# Function to calculate the bearing angle
def calculate_bearing(mortar_coords, target_coords):
    dx = target_coords[0] - mortar_coords[0]
    dz = target_coords[2] - mortar_coords[2]
    
    # Bearing 1 calculation
    bearing_1 = math.atan2(dz, dx) * (180 / math.pi)
    bearing_1 -= 90
    if bearing_1 < 0:
        bearing_1 += 360
    
    # Bearing 2 calculation (opposite bearing)
    bearing_2 = (bearing_1 + 180) % 360
    
    return bearing_1, bearing_2

# Function to calculate the horizontal range
def calculate_horizontal_range(mortar_coords, target_coords):
    dx = target_coords[0] - mortar_coords[0]
    dz = target_coords[2] - mortar_coords[2]
    return math.sqrt(dx**2 + dz**2)

# Function to calculate elevation angle and time of flight
def calculate_elevation_and_time_of_flight(mortar_coords, target_coords):
    horizontal_range = calculate_horizontal_range(mortar_coords, target_coords)
    dy = target_coords[1] - mortar_coords[1]

    term = (ARTILLERY_VELOCITY**4) - GRAVITY * (GRAVITY * horizontal_range**2 + 2 * dy * ARTILLERY_VELOCITY**2)

    # Check if the term is negative (no real solution possible)
    if term < 0:
        return None, None
    
    sqrt_term = math.sqrt(term)
    angle_radians_1 = math.atan((ARTILLERY_VELOCITY**2 + sqrt_term) / (GRAVITY * horizontal_range))
    angle_radians_2 = math.atan((ARTILLERY_VELOCITY**2 - sqrt_term) / (GRAVITY * horizontal_range))
    
    angle_degrees_1 = math.degrees(angle_radians_1)
    angle_degrees_2 = math.degrees(angle_radians_2)

    # Determine which angles are valid
    valid_angle_1 = MIN_ANGLE <= angle_degrees_1 <= MAX_ANGLE
    valid_angle_2 = MIN_ANGLE <= angle_degrees_2 <= MAX_ANGLE

    time_of_flight_1 = (ARTILLERY_VELOCITY * math.sin(angle_radians_1) + math.sqrt((ARTILLERY_VELOCITY * math.sin(angle_radians_1))**2 + 2 * GRAVITY * dy)) / GRAVITY if valid_angle_1 else None
    time_of_flight_2 = (ARTILLERY_VELOCITY * math.sin(angle_radians_2) + math.sqrt((ARTILLERY_VELOCITY * math.sin(angle_radians_2))**2 + 2 * GRAVITY * dy)) / GRAVITY if valid_angle_2 else None

    if valid_angle_1:
        return angle_degrees_1, time_of_flight_1
    elif valid_angle_2:
        return angle_degrees_2, time_of_flight_2
    else:
        return None, None

# Function to calculate artillery settings
def artillery_calculator(mortar_coords, target_coords):
    bearing_1, bearing_2 = calculate_bearing(mortar_coords, target_coords)
    angle, time_of_flight = calculate_elevation_and_time_of_flight(mortar_coords, target_coords)
    return bearing_1, bearing_2, angle, time_of_flight

# Streamlit app interface
st.title("Artillery Calculator")

# Input fields (modified to display integers)
st.sidebar.header("Launch Point (x0, y0, z0)")
x0 = st.sidebar.number_input("x0", value=0, format="%d")
y0 = st.sidebar.number_input("y0", value=0, format="%d")
z0 = st.sidebar.number_input("z0", value=0, format="%d")

st.sidebar.header("Target Point (xt, yt, zt)")
xt = st.sidebar.number_input("xt", value=0, format="%d")
yt = st.sidebar.number_input("yt", value=0, format="%d")
zt = st.sidebar.number_input("zt", value=0, format="%d")

# Perform calculation when the button is clicked
if st.button("Calculate"):
    # Convert inputs to float for calculations
    mortar_coords = (float(x0), float(y0), float(z0))
    target_coords = (float(xt), float(yt), float(zt))
    
    bearing_1, bearing_2, angle, time_of_flight = artillery_calculator(mortar_coords, target_coords)
    distance = calculate_horizontal_range(mortar_coords, target_coords)

    # Display results
    st.subheader("Results")
    st.write(f"Bearing 1: **{bearing_1:.2f} degrees**")
    st.write(f"Bearing 2 (Opposite): **{bearing_2:.2f} degrees**")
    st.write(f"Distance: **{distance:.2f} studs**")
    
    if angle is not None:
        st.write(f"**Elevation Angle:** {angle:.2f} degrees")
        st.write(f"**Time of Flight:** {time_of_flight:.2f} seconds")
    else:
        st.write("No feasible solution within angle limits.")

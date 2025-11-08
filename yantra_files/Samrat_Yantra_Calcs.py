import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta

# ====== INPUT ======
latitude = float(input("Enter Latitude (e.g., 28.6139): "))
longitude = float(input("Enter Longitude (e.g., 77.2090): "))
scale_m = float(input("Enter scale (meters, e.g., 3.0): "))
date_str = input("Enter date (YYYY-MM-DD): ")

# ====== DATE HANDLING ======
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
day_of_year = date_obj.timetuple().tm_yday

# ====== LOCAL SOLAR TIME CALC ======
standard_meridian = 82.5  # IST

# Equation of Time (more precise)
B = 2 * np.pi * (day_of_year - 1) / 365
EoT = 229.18 * (
    0.000075 + 0.001868*np.cos(B) - 0.032077*np.sin(B)
    - 0.014615*np.cos(2*B) - 0.040849*np.sin(2*B)
)

# Longitude correction (minutes)
longitude_correction = 4 * (longitude - standard_meridian)

# True Solar Time at local noon
LST_noon = 12 + (longitude_correction + EoT) / 60  # in hours

# ====== SOLAR DECLINATION ======
# δ = 23.45° * sin(360*(284 + n)/365)
declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year)/365))

# ====== PARAMETERS ======
platform_radius = scale_m
gnomon_height = scale_m
gnomon_tilt = latitude  
hours = np.arange(-6, 7, 1)  # -6 to +6 hrs from noon

# ====== HOUR LINE CALC (using declination) ======
def hour_line_angle(phi_deg, delta_deg, t_hours):
    """
    θ = hour line angle relative to noon
    phi_deg = latitude
    delta_deg = solar declination
    t_hours = hours from local noon
    """
    H = np.radians(15 * t_hours)  # hour angle
    phi = np.radians(phi_deg)
    delta = np.radians(delta_deg)
    theta = np.arctan(np.sin(phi) * np.tan(H))
    return np.degrees(theta)

hour_lines = []
for t in hours:
    theta = hour_line_angle(latitude, declination, t)
    x_end = platform_radius * np.sin(np.radians(theta))
    y_end = platform_radius * np.cos(np.radians(theta))
    hour_lines.append({
        "time": f"{12+t:02.0f}:00",
        "t": 12+t,
        "angle_deg": theta,
        "start": [0,0],
        "end": [x_end, y_end]
    })

# ====== FIGURE ======
plt.figure(figsize=(8,8))

# Platform (circle)
circle = plt.Circle((0,0), platform_radius, fill=False, color='saddlebrown', linewidth=3)
plt.gca().add_patch(circle)

# Side walls
plt.fill_between([-platform_radius, -platform_radius/2], -platform_radius, platform_radius, 
                 color='peru', alpha=0.3)
plt.fill_between([platform_radius/2, platform_radius], -platform_radius, platform_radius, 
                 color='peru', alpha=0.3)

# Hour lines
for line in hour_lines:
    x0, y0 = line['start']
    x1, y1 = line['end']
    plt.plot([x0,x1],[y0,y1], color='red', linewidth=1)

# ====== GREEN LINE for actual solar time ======
# Use fractional hours for higher accuracy
t_frac = LST_noon - 12
theta_frac = hour_line_angle(latitude, declination, t_frac)
x_end_frac = platform_radius * np.sin(np.radians(theta_frac))
y_end_frac = platform_radius * np.cos(np.radians(theta_frac))
total_seconds = LST_noon * 3600  # convert hours to total seconds
LST_hour = int(total_seconds // 3600)
LST_minute = int((total_seconds % 3600) // 60)
LST_second = int(total_seconds % 60)

if LST_second == 60:
    LST_minute += 1
    LST_second = 0
if LST_minute == 60:
    LST_hour += 1
    LST_minute = 0
LST_str = f"{LST_hour:02d}:{LST_minute:02d}"

plt.plot([0, x_end_frac], [0, y_end_frac], color='green', linewidth=2.5, 
         label=f"Solar Time ≈ {LST_str}")

# Gnomon
gnomon_top = [0, gnomon_height * np.tan(np.radians(gnomon_tilt))]
plt.plot([0,0], [0, gnomon_top[1]], color='blue', linewidth=4, label='Gnomon')
plt.fill_betweenx([0, gnomon_top[1]], -0.2, 0.2, color='lightblue', alpha=0.5)

# ====== FINAL STYLING ======
plt.gca().set_aspect('equal')
plt.title(f"Samrat Yantra Simulation (Lat {latitude}, Scale {scale_m} m)")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.legend()
plt.grid(True)
plt.show()

# ====== JSON SAVE ======
output = {
    "yantra_type": "samrat",
    "latitude": latitude,
    "longitude": longitude,
    "scale_m": scale_m,
    "date": date_str,
    "solar_time_highlighted": LST_str,
    "components": {
        "platform": {"radius_m": platform_radius},
        "gnomon": {"height_m": gnomon_height, "tilt_deg": gnomon_tilt},
        "hour_lines": hour_lines,
        "fractional_line": {
            "t_hours": LST_noon,
            "angle_deg": theta_frac,
            "end": [x_end_frac, y_end_frac]
        }
    }
}

with open("samrat_yantra.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Samrat Yantra generated! Highlighted Solar Time ≈ {LST_str}. JSON saved as samrat_yantra.json")

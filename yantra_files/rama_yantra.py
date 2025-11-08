import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta

# ====== INPUT ======
latitude = float(input("Enter Latitude (e.g., 28.6139): "))
longitude = float(input("Enter Longitude (e.g., 77.2090): "))
scale_m = float(input("Enter scale (meters, e.g., 3.0): "))
date_str = input("Enter date (YYYY-MM-DD): ")
time_str = input("Enter time (HH:MM, 24hr format): ")

# ====== DATE AND TIME HANDLING ======
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
time_obj = datetime.strptime(time_str, "%H:%M")
datetime_obj = datetime.combine(date_obj.date(), time_obj.time())
day_of_year = date_obj.timetuple().tm_yday
hour_decimal = time_obj.hour + time_obj.minute / 60.0

# ====== SOLAR CALCULATIONS ======
standard_meridian = 82.5  # IST

# Equation of Time
B = 2 * np.pi * (day_of_year - 1) / 365
EoT = 229.18 * (
    0.000075 + 0.001868*np.cos(B) - 0.032077*np.sin(B)
    - 0.014615*np.cos(2*B) - 0.040849*np.sin(2*B)
)

# Longitude correction
longitude_correction = 4 * (longitude - standard_meridian)

# Solar declination
declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year)/365))

# Solar hour angle
solar_time = hour_decimal + (longitude_correction + EoT) / 60
hour_angle = 15 * (solar_time - 12)

# Solar altitude and azimuth
lat_rad = np.radians(latitude)
dec_rad = np.radians(declination)
ha_rad = np.radians(hour_angle)

sin_alt = np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(ha_rad)
solar_altitude = np.degrees(np.arcsin(np.clip(sin_alt, -1, 1)))

cos_az = (np.sin(dec_rad) - np.sin(lat_rad) * sin_alt) / (np.cos(lat_rad) * np.cos(np.radians(solar_altitude)))
solar_azimuth = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
if np.sin(ha_rad) > 0:
    solar_azimuth = 360 - solar_azimuth

# ====== YAMA YANTRA PARAMETERS ======
yantra_radius = scale_m
central_pillar_height = scale_m * 1.5
base_thickness = scale_m * 0.1

# The Yama Yantra has graduated scales for measuring altitude
max_altitude = 90  # degrees
altitude_divisions = np.arange(0, 91, 10)  # 10-degree intervals
fine_divisions = np.arange(0, 91, 5)      # 5-degree intervals

# ====== CELESTIAL BODIES FOR DEMONSTRATION ======
# Major stars and planets visible during day/night
celestial_bodies = [
    # Bright stars
    {"name": "Sirius", "ra": 6.752, "dec": -16.716, "mag": -1.46, "type": "star"},
    {"name": "Canopus", "ra": 6.400, "dec": -52.696, "mag": -0.74, "type": "star"},
    {"name": "Arcturus", "ra": 14.261, "dec": 19.182, "mag": -0.05, "type": "star"},
    {"name": "Vega", "ra": 18.615, "dec": 38.784, "mag": 0.03, "type": "star"},
    {"name": "Capella", "ra": 5.278, "dec": 45.998, "mag": 0.08, "type": "star"},
    {"name": "Rigel", "ra": 5.242, "dec": -8.202, "mag": 0.13, "type": "star"},
    {"name": "Procyon", "ra": 7.655, "dec": 5.225, "mag": 0.34, "type": "star"},
    {"name": "Betelgeuse", "ra": 5.919, "dec": 7.407, "mag": 0.50, "type": "star"},
    {"name": "Altair", "ra": 19.846, "dec": 8.868, "mag": 0.77, "type": "star"},
    {"name": "Aldebaran", "ra": 4.599, "dec": 16.509, "mag": 0.85, "type": "star"},
]

# ====== SIDEREAL TIME FOR STAR POSITIONS ======
# Greenwich Sidereal Time calculation
J2000_epoch = datetime(2000, 1, 1, 12, 0, 0)
days_since_J2000 = (datetime_obj - J2000_epoch).total_seconds() / 86400.0
GMST0 = 18.697374558 + 24.06570982441908 * days_since_J2000
GMST0 = GMST0 % 24
GMST = (GMST0 + 1.00273790935 * hour_decimal) % 24
LST = (GMST + longitude / 15.0) % 24

# ====== COORDINATE TRANSFORMATION ======
def celestial_to_altaz(ra_hours, dec_deg, lst_hours, lat_deg):
    """Convert celestial coordinates to altitude-azimuth"""
    ha = (lst_hours - ra_hours) * 15
    ha_rad = np.radians(ha)
    dec_rad = np.radians(dec_deg)
    lat_rad = np.radians(lat_deg)
    
    sin_alt = np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(ha_rad)
    altitude = np.degrees(np.arcsin(np.clip(sin_alt, -1, 1)))
    
    cos_az = (np.sin(dec_rad) - np.sin(lat_rad) * sin_alt) / (np.cos(lat_rad) * np.cos(np.radians(altitude)))
    azimuth = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    
    if np.sin(ha_rad) > 0:
        azimuth = 360 - azimuth
    
    return altitude, azimuth

# ====== CALCULATE POSITIONS OF CELESTIAL BODIES ======
visible_bodies = []
for body in celestial_bodies:
    alt, az = celestial_to_altaz(body["ra"], body["dec"], LST, latitude)
    
    if alt > 0:  # Above horizon
        visible_bodies.append({
            "name": body["name"],
            "type": body["type"],
            "magnitude": body["mag"],
            "altitude": alt,
            "azimuth": az,
            "ra": body["ra"],
            "dec": body["dec"]
        })

# ====== YAMA YANTRA GEOMETRY ======
def create_altitude_scale():
    """Create the graduated altitude measurement scale"""
    scale_points = []
    
    # Main altitude divisions (every 10 degrees)
    for alt in altitude_divisions:
        # Distance from center proportional to (90 - altitude)
        radius = yantra_radius * (90 - alt) / 90
        scale_points.append({
            "altitude": alt,
            "radius": radius,
            "type": "major",
            "label": f"{alt}°"
        })
    
    # Fine divisions (every 5 degrees)  
    for alt in fine_divisions:
        if alt not in altitude_divisions:
            radius = yantra_radius * (90 - alt) / 90
            scale_points.append({
                "altitude": alt,
                "radius": radius,
                "type": "minor",
                "label": f"{alt}°"
            })
    
    return scale_points

def create_azimuth_divisions():
    """Create azimuth angle divisions"""
    azimuth_lines = []
    
    # 16 main directions (every 22.5 degrees)
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    
    for i, direction in enumerate(directions):
        angle = i * 22.5
        angle_rad = np.radians(angle - 90)  # Convert to math convention
        
        x_end = yantra_radius * np.cos(angle_rad)
        y_end = yantra_radius * np.sin(angle_rad)
        
        azimuth_lines.append({
            "direction": direction,
            "angle": angle,
            "start": [0, 0],
            "end": [x_end, y_end]
        })
    
    return azimuth_lines

# ====== RAMA YANTRA MEASUREMENT FUNCTIONS ======
def project_celestial_body(altitude, azimuth):
    """Project celestial body onto Yama Yantra surface"""
    # Radius based on altitude (90° at center, 0° at edge)
    r = yantra_radius * (90 - altitude) / 90
    
    # Convert azimuth to mathematical angle
    theta = np.radians(azimuth - 90)
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    return x, y

def create_seasonal_sun_paths():
    """Create sun paths for different seasons"""
    seasons = [
        {"name": "Summer Solstice", "declination": 23.45, "color": "#FF6B6B", "day": 172},
        {"name": "Spring Equinox", "declination": 0, "color": "#4ECDC4", "day": 80},
        {"name": "Winter Solstice", "declination": -23.45, "color": "#45B7D1", "day": 355},
        {"name": "Autumn Equinox", "declination": 0, "color": "#96CEB4", "day": 266}
    ]
    
    sun_paths = []
    for season in seasons:
        path_points = []
        times = np.linspace(6, 18, 50)  # 6 AM to 6 PM
        
        for t in times:
            # Calculate sun position for this time
            ha = 15 * (t - 12)
            ha_rad = np.radians(ha)
            dec_rad = np.radians(season["declination"])
            
            sin_alt = np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(ha_rad)
            alt = np.degrees(np.arcsin(np.clip(sin_alt, -1, 1)))
            
            if alt > 0:  # Above horizon
                cos_az = (np.sin(dec_rad) - np.sin(lat_rad) * sin_alt) / (np.cos(lat_rad) * np.cos(np.radians(alt)))
                az = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
                if ha > 0:
                    az = 360 - az
                
                x, y = project_celestial_body(alt, az)
                path_points.append([x, y, alt, az, t])
        
        if path_points:
            sun_paths.append({
                "season": season["name"],
                "color": season["color"],
                "points": path_points,
                "declination": season["declination"]
            })
    
    return sun_paths

# ====== FIGURE SETUP ======
fig, ax = plt.subplots(1, 1, figsize=(16, 16))

# ====== DRAW ALTITUDE SCALE CIRCLES ======
altitude_scale = create_altitude_scale()
for scale_point in altitude_scale:
    if scale_point["type"] == "major":
        circle = plt.Circle((0, 0), scale_point["radius"], fill=False,
                          color='black', linewidth=2, alpha=0.7)
        ax.add_patch(circle)
        
        # Add altitude labels
        ax.text(scale_point["radius"] + 0.1, 0, scale_point["label"],
               ha='left', va='center', fontsize=10, fontweight='bold')
    else:
        circle = plt.Circle((0, 0), scale_point["radius"], fill=False,
                          color='gray', linewidth=1, alpha=0.5)
        ax.add_patch(circle)

# ====== DRAW OUTER YANTRA BOUNDARY ======
outer_boundary = plt.Circle((0, 0), yantra_radius, fill=False,
                          color='saddlebrown', linewidth=4)
ax.add_patch(outer_boundary)

# Central pillar base
central_base = plt.Circle((0, 0), yantra_radius * 0.02, fill=True,
                        color='#5C4033', alpha=0.8)
ax.add_patch(central_base)

# ====== DRAW AZIMUTH DIRECTION LINES ======
azimuth_divisions = create_azimuth_divisions()
for az_line in azimuth_divisions:
    x0, y0 = az_line['start']
    x1, y1 = az_line['end']
    
    # Main cardinal directions in bold
    if az_line['direction'] in ['N', 'E', 'S', 'W']:
        ax.plot([x0, x1], [y0, y1], color='darkblue', linewidth=2.5, alpha=0.8)
    else:
        ax.plot([x0, x1], [y0, y1], color='blue', linewidth=1, alpha=0.6)
    
    # Direction labels
    label_radius = yantra_radius * 1.08
    label_x = label_radius * np.cos(np.radians(az_line['angle'] - 90))
    label_y = label_radius * np.sin(np.radians(az_line['angle'] - 90))
    
    ax.text(label_x, label_y, az_line['direction'], ha='center', va='center',
           fontsize=11, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan', alpha=0.8))

# ====== DRAW SEASONAL SUN PATHS ======
sun_paths = create_seasonal_sun_paths()
for path in sun_paths:
    if len(path["points"]) > 1:
        points = np.array(path["points"])
        ax.plot(points[:, 0], points[:, 1], color=path["color"],
               linewidth=3, alpha=0.7, label=f'{path["season"]} (δ={path["declination"]:.1f}°)')
        
        # Mark noon position (highest point)
        if len(points) > 0:
            noon_idx = len(points) // 2
            noon_point = points[noon_idx]
            ax.scatter(noon_point[0], noon_point[1], color=path["color"],
                     s=150, marker='o', edgecolors='black', linewidth=2, zorder=8)
            
            # Time labels at key points
            for i in [0, noon_idx, -1]:
                if i < len(points):
                    point = points[i]
                    time_label = f"{int(point[4]):02d}:00"
                    ax.text(point[0], point[1] + yantra_radius * 0.03, time_label,
                           ha='center', va='bottom', fontsize=8, color=path["color"],
                           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

# ====== DRAW CURRENT SUN POSITION ======
if solar_altitude > 0:
    sun_x, sun_y = project_celestial_body(solar_altitude, solar_azimuth)
    ax.scatter(sun_x, sun_y, color='gold', s=400, marker='*',
              edgecolors='orange', linewidth=3, zorder=10, label='Current Sun Position')
    
    # Sun altitude and azimuth labels
    ax.text(sun_x, sun_y + yantra_radius * 0.05,
           f'☀️ Alt: {solar_altitude:.1f}°\nAz: {solar_azimuth:.1f}°',
           ha='center', va='bottom', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.9))

# ====== DRAW VISIBLE STARS ======
star_colors = {'star': 'white', 'planet': 'yellow'}
for body in visible_bodies:
    x, y = project_celestial_body(body["altitude"], body["azimuth"])
    
    # Star size based on magnitude (brighter = larger)
    size = max(30, 150 - body["magnitude"] * 40)
    color = star_colors.get(body["type"], 'white')
    
    ax.scatter(x, y, color=color, s=size, marker='*' if body["type"] == 'star' else 'o',
              edgecolors='lightgray', linewidth=1, alpha=0.9, zorder=7)
    
    # Star labels for bright objects
    if body["magnitude"] < 1.0:
        ax.text(x, y + yantra_radius * 0.03, body["name"],
               ha='center', va='bottom', fontsize=8, color='white',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.7))

# ====== MEASUREMENT CROSSHAIRS ======
# Add measuring crosshairs at center for precise alignment
crosshair_size = yantra_radius * 0.05
ax.plot([-crosshair_size, crosshair_size], [0, 0], color='red', linewidth=2)
ax.plot([0, 0], [-crosshair_size, crosshair_size], color='red', linewidth=2)

# ====== CENTRAL PILLAR REPRESENTATION ======
# Vertical pillar for sighting
pillar_x = [0, 0]
pillar_y = [0, central_pillar_height * 0.1]  # Projected height
ax.plot(pillar_x, pillar_y, color='#654321', linewidth=8,
        label=f'Central Pillar ({central_pillar_height:.1f}m)')

# Pillar shadow
if solar_altitude > 0:
    shadow_length = central_pillar_height / np.tan(np.radians(solar_altitude))
    shadow_direction = np.radians(solar_azimuth - 90)
    shadow_x = shadow_length * 0.1 * np.cos(shadow_direction)
    shadow_y = shadow_length * 0.1 * np.sin(shadow_direction)
    ax.plot([0, shadow_x], [0, shadow_y], color='gray', linewidth=4,
           alpha=0.6, linestyle=':', label='Pillar Shadow')

# ====== ALTITUDE MEASUREMENT ARCS ======
# Show measurement arcs for current observations
measurement_altitudes = [30, 45, 60]
for alt in measurement_altitudes:
    if any(abs(body["altitude"] - alt) < 5 for body in visible_bodies if body["altitude"] > 0):
        radius = yantra_radius * (90 - alt) / 90
        circle = plt.Circle((0, 0), radius, fill=False,
                          color='red', linewidth=3, linestyle='--', alpha=0.8)
        ax.add_patch(circle)

# ====== FINAL STYLING ======
ax.set_aspect('equal')
ax.set_xlim(-yantra_radius*1.2, yantra_radius*1.2)
ax.set_ylim(-yantra_radius*1.2, yantra_radius*1.2)

plt.title(f"Yama Yantra - Altitude Measurement Instrument\n"
          f"Location: {latitude:.2f}°N, {longitude:.2f}°E | {date_str} {time_str}\n"
          f"Sun: Alt {solar_altitude:.1f}°, Az {solar_azimuth:.1f}° | "
          f"Visible Objects: {len(visible_bodies) + (1 if solar_altitude > 0 else 0)}", 
          fontsize=14, pad=20)

plt.xlabel("East-West (meters)", fontsize=12)
plt.ylabel("North-South (meters)", fontsize=12)
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ====== JSON SAVE ======
output = {
    "yantra_type": "yama",
    "latitude": latitude,
    "longitude": longitude,
    "scale_m": scale_m,
    "observation_date": date_str,
    "observation_time": time_str,
    "local_sidereal_time": round(LST, 4),
    "solar_data": {
        "altitude_deg": round(solar_altitude, 2),
        "azimuth_deg": round(solar_azimuth, 2),
        "declination_deg": round(declination, 2),
        "hour_angle_deg": round(hour_angle, 2),
        "equation_of_time_min": round(EoT, 2)
    },
    "components": {
        "yantra": {"radius_m": yantra_radius},
        "central_pillar": {"height_m": central_pillar_height},
        "base_thickness": {"thickness_m": base_thickness},
        "altitude_scale": [
            {
                "altitude_deg": scale["altitude"],
                "radius_m": scale["radius"],
                "type": scale["type"]
            } for scale in altitude_scale
        ],
        "azimuth_divisions": [
            {
                "direction": az["direction"],
                "angle_deg": az["angle"]
            } for az in azimuth_divisions
        ]
    },
    "seasonal_sun_paths": [
        {
            "season": path["season"],
            "declination_deg": path["declination"],
            "color": path["color"],
            "path_points": len(path["points"])
        } for path in sun_paths
    ],
    "visible_celestial_bodies": [
        {
            "name": body["name"],
            "type": body["type"],
            "magnitude": body["magnitude"],
            "altitude_deg": round(body["altitude"], 2),
            "azimuth_deg": round(body["azimuth"], 2),
            "right_ascension_hours": body["ra"],
            "declination_deg": body["dec"]
        } for body in visible_bodies
    ],
    "measurements": {
        "sun_visible": solar_altitude > 0,
        "total_visible_objects": len(visible_bodies) + (1 if solar_altitude > 0 else 0),
        "measurement_precision": "1 degree",
        "altitude_range": "0-90 degrees",
        "azimuth_range": "0-360 degrees"
    }
}

with open("rama_yantra.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ rama Yantra generated!")
print(f"☀️ Sun Position: Alt {solar_altitude:.1f}°, Az {solar_azimuth:.1f}°" if solar_altitude > 0 else "☀️ Sun below horizon")
print(f"⭐ Visible Stars/Objects: {len(visible_bodies)}")
print(f"📐 Measurement Range: 0-90° altitude, 0-360° azimuth")
print(f"📊 JSON saved as yama_yantra.json")
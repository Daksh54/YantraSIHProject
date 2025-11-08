import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta

# ====== INPUT ======
latitude = float(input("Enter Latitude (e.g., 28.6139): "))
longitude = float(input("Enter Longitude (e.g., 77.2090): "))
scale_m = float(input("Enter scale (meters, e.g., 4.0): "))
date_str = input("Enter date (YYYY-MM-DD): ")
time_str = input("Enter time (HH:MM, 24hr format): ")

# ====== DATE AND TIME HANDLING ======
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
time_obj = datetime.strptime(time_str, "%H:%M")
datetime_obj = datetime.combine(date_obj.date(), time_obj.time())
day_of_year = date_obj.timetuple().tm_yday
hour_decimal = time_obj.hour + time_obj.minute / 60.0

# ====== MAGNETIC DECLINATION CALCULATION ======
# Simplified magnetic declination model (varies by location)
# This is approximate - real applications would use detailed magnetic models
def calculate_magnetic_declination(lat, lon, year=2024):
    """
    Simplified magnetic declination calculation
    Returns magnetic declination in degrees (positive = East, negative = West)
    """
    # Simplified model based on location
    # For India, magnetic declination is generally between 0° to 2° West
    if 6 <= lat <= 38 and 68 <= lon <= 98:  # India region
        declination = -1.2 + 0.03 * (lat - 20) - 0.01 * (lon - 77)
    else:
        # Global approximation
        declination = -11.5 + 0.4 * lat - 0.02 * lon
    
    return declination

magnetic_declination = calculate_magnetic_declination(latitude, longitude)

# ====== SOLAR CALCULATIONS FOR TRUE NORTH ======
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

# ====== DIGANSHA YANTRA PARAMETERS ======
yantra_radius = scale_m
inner_compass_radius = scale_m * 0.8
direction_line_radius = scale_m * 0.9
gnomon_height = scale_m * 0.3
central_post_radius = scale_m * 0.02

# ====== DIRECTION SYSTEMS ======
# 32-point compass rose (traditional navigation)
compass_directions = [
    # Cardinal directions
    {"name": "N", "angle": 0, "type": "cardinal", "color": "#FF0000", "full_name": "North"},
    {"name": "E", "angle": 90, "type": "cardinal", "color": "#FF0000", "full_name": "East"},
    {"name": "S", "angle": 180, "type": "cardinal", "color": "#FF0000", "full_name": "South"},
    {"name": "W", "angle": 270, "type": "cardinal", "color": "#FF0000", "full_name": "West"},
    
    # Intercardinal directions
    {"name": "NE", "angle": 45, "type": "intercardinal", "color": "#0066CC", "full_name": "Northeast"},
    {"name": "SE", "angle": 135, "type": "intercardinal", "color": "#0066CC", "full_name": "Southeast"},
    {"name": "SW", "angle": 225, "type": "intercardinal", "color": "#0066CC", "full_name": "Southwest"},
    {"name": "NW", "angle": 315, "type": "intercardinal", "color": "#0066CC", "full_name": "Northwest"},
    
    # Half-wind directions
    {"name": "NNE", "angle": 22.5, "type": "half-wind", "color": "#00AA44", "full_name": "North-northeast"},
    {"name": "ENE", "angle": 67.5, "type": "half-wind", "color": "#00AA44", "full_name": "East-northeast"},
    {"name": "ESE", "angle": 112.5, "type": "half-wind", "color": "#00AA44", "full_name": "East-southeast"},
    {"name": "SSE", "angle": 157.5, "type": "half-wind", "color": "#00AA44", "full_name": "South-southeast"},
    {"name": "SSW", "angle": 202.5, "type": "half-wind", "color": "#00AA44", "full_name": "South-southwest"},
    {"name": "WSW", "angle": 247.5, "type": "half-wind", "color": "#00AA44", "full_name": "West-southwest"},
    {"name": "WNW", "angle": 292.5, "type": "half-wind", "color": "#00AA44", "full_name": "West-northwest"},
    {"name": "NNW", "angle": 337.5, "type": "half-wind", "color": "#00AA44", "full_name": "North-northwest"},
    
    # Quarter-wind directions (for precision)
    {"name": "NbE", "angle": 11.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "North by East"},
    {"name": "NEbN", "angle": 33.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "Northeast by North"},
    {"name": "NEbE", "angle": 56.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "Northeast by East"},
    {"name": "EbN", "angle": 78.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "East by North"},
    {"name": "EbS", "angle": 101.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "East by South"},
    {"name": "SEbE", "angle": 123.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "Southeast by East"},
    {"name": "SEbS", "angle": 146.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "Southeast by South"},
    {"name": "SbE", "angle": 168.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "South by East"},
    {"name": "SbW", "angle": 191.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "South by West"},
    {"name": "SWbS", "angle": 213.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "Southwest by South"},
    {"name": "SWbW", "angle": 236.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "Southwest by West"},
    {"name": "WbS", "angle": 258.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "West by South"},
    {"name": "WbN", "angle": 281.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "West by North"},
    {"name": "NWbW", "angle": 303.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "Northwest by West"},
    {"name": "NWbN", "angle": 326.25, "type": "quarter-wind", "color": "#AA6600", "full_name": "Northwest by North"},
    {"name": "NbW", "angle": 348.75, "type": "quarter-wind", "color": "#AA6600", "full_name": "North by West"}
]

# Traditional Indian direction system (Dik system)
vedic_directions = [
    {"name": "उत्तर (Uttar)", "angle": 0, "english": "North", "deity": "Kubera", "element": "Earth"},
    {"name": "ईशान (Ishan)", "angle": 45, "english": "Northeast", "deity": "Shiva", "element": "Water"},
    {"name": "पूर्व (Purva)", "angle": 90, "english": "East", "deity": "Indra", "element": "Air"},
    {"name": "आग्नेय (Agneya)", "angle": 135, "english": "Southeast", "deity": "Agni", "element": "Fire"},
    {"name": "दक्षिण (Dakshin)", "angle": 180, "english": "South", "deity": "Yama", "element": "Fire"},
    {"name": "नैऋत्य (Nairitya)", "angle": 225, "english": "Southwest", "deity": "Nirriti", "element": "Earth"},
    {"name": "पश्चिम (Paschim)", "angle": 270, "english": "West", "deity": "Varuna", "element": "Water"},
    {"name": "वायव्य (Vayavya)", "angle": 315, "english": "Northwest", "deity": "Vayu", "element": "Air"}
]

# ====== DIRECTION MEASUREMENT FUNCTIONS ======
def get_direction_from_angle(angle_deg):
    """
    Convert angle to nearest compass direction
    """
    # Normalize angle to 0-360
    angle_deg = angle_deg % 360
    
    # Find closest direction
    min_diff = float('inf')
    closest_dir = None
    
    for direction in compass_directions:
        diff = min(abs(direction["angle"] - angle_deg), 
                  abs(direction["angle"] - angle_deg + 360),
                  abs(direction["angle"] - angle_deg - 360))
        if diff < min_diff:
            min_diff = diff
            closest_dir = direction
    
    return closest_dir, min_diff

def create_azimuth_scale():
    """
    Create degree markings around the yantra
    """
    scale_marks = []
    
    # Major marks every 10 degrees
    for angle in range(0, 360, 10):
        scale_marks.append({
            "angle": angle,
            "type": "major",
            "length": yantra_radius * 0.05,
            "label": f"{angle}°"
        })
    
    # Minor marks every 5 degrees
    for angle in range(0, 360, 5):
        if angle % 10 != 0:
            scale_marks.append({
                "angle": angle,
                "type": "minor", 
                "length": yantra_radius * 0.03,
                "label": None
            })
    
    return scale_marks

# ====== SHADOW ANALYSIS ======
def calculate_shadow_direction():
    """
    Calculate shadow direction and length for direction finding
    """
    if solar_altitude > 0:
        # Shadow points opposite to sun
        shadow_azimuth = (solar_azimuth + 180) % 360
        
        # Shadow length based on sun altitude
        shadow_length = gnomon_height / np.tan(np.radians(solar_altitude))
        
        # Limit shadow length to yantra size
        max_shadow = yantra_radius * 0.8
        if shadow_length > max_shadow:
            shadow_length = max_shadow
            
        return shadow_azimuth, shadow_length
    else:
        return None, 0

shadow_azimuth, shadow_length = calculate_shadow_direction()

# ====== WIND ROSE CREATION ======
def create_wind_rose_pattern():
    """
    Create traditional wind rose pattern with decorative elements
    """
    rose_points = []
    
    # Main compass points with extended rays
    main_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    
    for angle in main_angles:
        # Inner ray
        inner_length = yantra_radius * 0.6
        outer_length = yantra_radius * 0.95
        
        angle_rad = np.radians(angle)
        
        # Create decorative points
        points = []
        for r in np.linspace(inner_length, outer_length, 5):
            x = r * np.sin(angle_rad)
            y = r * np.cos(angle_rad)
            points.append([x, y])
        
        rose_points.append({
            "angle": angle,
            "points": points,
            "type": "main" if angle % 90 == 0 else "inter"
        })
    
    return rose_points

# ====== FIGURE SETUP ======
fig, ax = plt.subplots(1, 1, figsize=(16, 16))

# ====== DRAW MAIN YANTRA CIRCLE ======
# Outer boundary
outer_circle = plt.Circle((0, 0), yantra_radius, fill=False, color='black', linewidth=4)
ax.add_patch(outer_circle)

# Inner compass circle
inner_circle = plt.Circle((0, 0), inner_compass_radius, fill=False, color='darkblue', linewidth=2, linestyle='--', alpha=0.7)
ax.add_patch(inner_circle)

# Central post
central_post = plt.Circle((0, 0), central_post_radius,facecolor="#654321",edgecolor="black",linewidth=2)

ax.add_patch(central_post)

# ====== DRAW AZIMUTH SCALE ======
azimuth_scale = create_azimuth_scale()
for mark in azimuth_scale:
    angle_rad = np.radians(mark["angle"])
    
    if mark["type"] == "major":
        # Major tick marks
        inner_radius = yantra_radius - mark["length"]
        outer_radius = yantra_radius + mark["length"] * 0.3
        
        x1 = inner_radius * np.sin(angle_rad)
        y1 = inner_radius * np.cos(angle_rad)
        x2 = outer_radius * np.sin(angle_rad)
        y2 = outer_radius * np.cos(angle_rad)
        
        ax.plot([x1, x2], [y1, y2], color='black', linewidth=2)
        
        # Degree labels
        label_radius = yantra_radius + mark["length"] * 0.6
        label_x = label_radius * np.sin(angle_rad)
        label_y = label_radius * np.cos(angle_rad)
        
        if mark["angle"] % 30 == 0:  # Show every 30 degrees
            ax.text(label_x, label_y, mark["label"], ha='center', va='center',
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.8))
    else:
        # Minor tick marks
        inner_radius = yantra_radius - mark["length"]
        outer_radius = yantra_radius
        
        x1 = inner_radius * np.sin(angle_rad)
        y1 = inner_radius * np.cos(angle_rad)
        x2 = outer_radius * np.sin(angle_rad)
        y2 = outer_radius * np.cos(angle_rad)
        
        ax.plot([x1, x2], [y1, y2], color='gray', linewidth=1, alpha=0.7)

# ====== DRAW COMPASS DIRECTIONS ======
for direction in compass_directions:
    angle_rad = np.radians(direction["angle"])
    
    # Direction line length based on type
    if direction["type"] == "cardinal":
        line_length = direction_line_radius
        line_width = 4
        alpha = 1.0
    elif direction["type"] == "intercardinal":
        line_length = direction_line_radius * 0.9
        line_width = 3
        alpha = 0.9
    elif direction["type"] == "half-wind":
        line_length = direction_line_radius * 0.7
        line_width = 2
        alpha = 0.7
    else:  # quarter-wind
        line_length = direction_line_radius * 0.5
        line_width = 1
        alpha = 0.5
    
    x_end = line_length * np.sin(angle_rad)
    y_end = line_length * np.cos(angle_rad)
    
    ax.plot([0, x_end], [0, y_end], color=direction["color"], 
           linewidth=line_width, alpha=alpha)
    
    # Direction labels for major directions
    if direction["type"] in ["cardinal", "intercardinal"]:
        label_radius = line_length + yantra_radius * 0.08
        label_x = label_radius * np.sin(angle_rad)
        label_y = label_radius * np.cos(angle_rad)
        
        ax.text(label_x, label_y, direction["name"], ha='center', va='center',
               fontsize=12, fontweight='bold', color=direction["color"],
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                        edgecolor=direction["color"], alpha=0.9))

# ====== DRAW VEDIC DIRECTION SYSTEM ======
vedic_radius = yantra_radius * 0.5
for i, vdir in enumerate(vedic_directions):
    angle_rad = np.radians(vdir["angle"])
    
    # Create sector for each direction
    start_angle = vdir["angle"] - 22.5
    end_angle = vdir["angle"] + 22.5
    
    # Sector colors based on elements
    element_colors = {
        "Earth": "#8B4513",
        "Water": "#4169E1", 
        "Air": "#87CEEB",
        "Fire": "#FF6347"
    }
    
    color = element_colors.get(vdir["element"], "#CCCCCC")
    
    # Draw sector
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), 20)
    inner_r = yantra_radius * 0.3
    outer_r = vedic_radius
    
    x_outer = outer_r * np.sin(angles)
    y_outer = outer_r * np.cos(angles)
    x_inner = inner_r * np.sin(angles[::-1])
    y_inner = inner_r * np.cos(angles[::-1])
    
    x_sector = np.concatenate([x_outer, x_inner])
    y_sector = np.concatenate([y_outer, y_inner])
    
    ax.fill(x_sector, y_sector, color=color, alpha=0.3, 
           edgecolor='black', linewidth=1)
    
    # Vedic direction labels
    label_radius = (inner_r + outer_r) / 2
    label_x = label_radius * np.sin(angle_rad)
    label_y = label_radius * np.cos(angle_rad)
    
    ax.text(label_x, label_y, vdir["name"].split('(')[0], 
           ha='center', va='center', fontsize=8, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

# ====== DRAW TRUE NORTH INDICATOR ======
true_north_x = yantra_radius * 1.15 * np.sin(np.radians(0))
true_north_y = yantra_radius * 1.15 * np.cos(np.radians(0))
ax.plot([0, 0], [0, true_north_y], color='red', linewidth=6, alpha=0.8, 
        label='True North')
ax.scatter(0, true_north_y, color='red', s=200, marker='^', 
          edgecolors='darkred', linewidth=2, zorder=10)

# ====== DRAW MAGNETIC NORTH INDICATOR ======
magnetic_north_angle = magnetic_declination
magnetic_north_rad = np.radians(magnetic_north_angle)
magnetic_north_x = yantra_radius * 1.1 * np.sin(magnetic_north_rad)
magnetic_north_y = yantra_radius * 1.1 * np.cos(magnetic_north_rad)
ax.plot([0, magnetic_north_x], [0, magnetic_north_y], color='blue', 
        linewidth=4, alpha=0.8, label=f'Magnetic North ({magnetic_declination:.1f}°)')
ax.scatter(magnetic_north_x, magnetic_north_y, color='blue', s=150, marker='^', 
          edgecolors='darkblue', linewidth=2, zorder=10)

# ====== DRAW CURRENT SUN POSITION ======
if solar_altitude > 0:
    sun_direction_rad = np.radians(solar_azimuth)
    sun_x = direction_line_radius * np.sin(sun_direction_rad)
    sun_y = direction_line_radius * np.cos(sun_direction_rad)
    
    ax.plot([0, sun_x], [0, sun_y], color='gold', linewidth=5, 
           label=f'Sun Direction (Az: {solar_azimuth:.1f}°)')
    ax.scatter(sun_x, sun_y, color='gold', s=300, marker='*', 
              edgecolors='orange', linewidth=2, zorder=10)
    
    # Sun position info
    sun_direction, sun_accuracy = get_direction_from_angle(solar_azimuth)
    ax.text(sun_x, sun_y + yantra_radius * 0.05,
           f'☀️ {sun_direction["name"]}\n{solar_azimuth:.1f}° | Alt: {solar_altitude:.1f}°',
           ha='center', va='bottom', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.9))

# ====== DRAW SHADOW DIRECTION ======
if shadow_azimuth is not None:
    shadow_rad = np.radians(shadow_azimuth)
    shadow_x = shadow_length * 0.1 * np.sin(shadow_rad)  # Scale for display
    shadow_y = shadow_length * 0.1 * np.cos(shadow_rad)
    
    ax.plot([0, shadow_x], [0, shadow_y], color='gray', linewidth=4, 
           alpha=0.7, linestyle=':', label=f'Shadow Direction')
    ax.scatter(shadow_x, shadow_y, color='gray', s=100, marker='o', 
              alpha=0.7, zorder=8)

# ====== DRAW WIND ROSE PATTERN ======
wind_rose = create_wind_rose_pattern()
for rose_point in wind_rose:
    points = np.array(rose_point["points"])
    color = '#FF0000' if rose_point["type"] == "main" else '#0066CC'
    alpha = 0.6 if rose_point["type"] == "main" else 0.4
    
    ax.plot(points[:, 0], points[:, 1], color=color, linewidth=1, alpha=alpha)

# ====== MEASUREMENT GRID ======
# Concentric circles for distance measurement
for r in [0.25, 0.5, 0.75]:
    radius = yantra_radius * r
    circle = plt.Circle((0, 0), radius, fill=False, color='lightgray', 
                       linewidth=1, alpha=0.4, linestyle=':')
    ax.add_patch(circle)

# ====== GNOMON FOR SHADOW MEASUREMENT ======
# Central gnomon post
ax.plot([0, 0], [0, gnomon_height * 0.1], color='#654321', linewidth=8, 
        label=f'Gnomon ({gnomon_height:.1f}m)')

# Gnomon shadow for time/direction finding
if shadow_azimuth is not None and solar_altitude > 0:
    # Actual shadow visualization
    shadow_display_length = min(shadow_length * 0.1, yantra_radius * 0.6)
    shadow_x_display = shadow_display_length * np.sin(shadow_rad)
    shadow_y_display = shadow_display_length * np.cos(shadow_rad)
    
    ax.plot([0, shadow_x_display], [0, shadow_y_display], 
           color='darkgray', linewidth=3, alpha=0.8, linestyle='-', 
           label=f'Current Shadow (Length: {shadow_length:.1f}m)')

# ====== DIRECTION FINDING INDICATORS ======
# Show current time's directional significance
current_solar_direction, _ = get_direction_from_angle(solar_azimuth) if solar_altitude > 0 else (None, None)

# ====== FINAL STYLING ======
ax.set_aspect('equal')
ax.set_xlim(-yantra_radius*1.3, yantra_radius*1.3)
ax.set_ylim(-yantra_radius*1.3, yantra_radius*1.3)

# Title with comprehensive information
title_text = f"Digansha Yantra - Directional Measurement Instrument\n"
title_text += f"Location: {latitude:.2f}°N, {longitude:.2f}°E | {date_str} {time_str}\n"
title_text += f"Magnetic Declination: {magnetic_declination:.2f}° | "
if solar_altitude > 0:
    title_text += f"Sun: {current_solar_direction['name'] if current_solar_direction else 'Unknown'} {solar_azimuth:.1f}°"
else:
    title_text += "Sun below horizon"

plt.title(title_text, fontsize=14, pad=20)

plt.xlabel("East-West (meters)", fontsize=12)
plt.ylabel("North-South (meters)", fontsize=12)
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
# The Flask app will look for this exact file.
plt.savefig("rasivalaya_yantra_output.png", bbox_inches='tight', dpi=150)

# ====== JSON SAVE ======
output = {
    "yantra_type": "digansha",
    "latitude": latitude,
    "longitude": longitude,
    "scale_m": scale_m,
    "observation_date": date_str,
    "observation_time": time_str,
    "magnetic_declination_deg": round(magnetic_declination, 3),
    "solar_data": {
        "altitude_deg": round(solar_altitude, 2) if solar_altitude > 0 else None,
        "azimuth_deg": round(solar_azimuth, 2) if solar_altitude > 0 else None,
        "declination_deg": round(declination, 2),
        "hour_angle_deg": round(hour_angle, 2),
        "equation_of_time_min": round(EoT, 2),
        "direction": current_solar_direction["name"] if current_solar_direction else None
    },
    "shadow_data": {
        "shadow_azimuth_deg": round(shadow_azimuth, 2) if shadow_azimuth is not None else None,
        "shadow_length_m": round(shadow_length, 2) if shadow_length > 0 else None,
        "gnomon_height_m": gnomon_height
    },
    "components": {
        "yantra": {"radius_m": yantra_radius},
        "inner_compass": {"radius_m": inner_compass_radius},
        "central_post": {"radius_m": central_post_radius},
        "direction_lines": {"radius_m": direction_line_radius}
    },
    "direction_systems": {
        "compass_directions": [
            {
                "name": d["name"],
                "angle_deg": d["angle"], 
                "type": d["type"],
                "full_name": d["full_name"]
            } for d in compass_directions
        ],
        "vedic_directions": [
            {
                "sanskrit_name": vd["name"],
                "english_name": vd["english"],
                "angle_deg": vd["angle"],
                "deity": vd["deity"],
                "element": vd["element"]
            } for vd in vedic_directions
        ]
    },
    "azimuth_scale": [
        {
            "angle_deg": mark["angle"],
            "type": mark["type"],
            "label": mark["label"]
        } for mark in azimuth_scale if mark["type"] == "major"
    ],
    "measurements": {
        "precision_deg": 1.0,
        "azimuth_range": "0-360 degrees",
        "magnetic_correction_available": True,
        "shadow_measurement_available": solar_altitude > 0,
        "vedic_system_integrated": True
    }
}

with open("digansha_yantra.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Digansha Yantra generated!")
print(f"🧭 Magnetic Declination: {magnetic_declination:.2f}° {'East' if magnetic_declination > 0 else 'West'}")
if solar_altitude > 0:
    print(f"☀️ Sun Position: {current_solar_direction['name'] if current_solar_direction else 'Unknown'} {solar_azimuth:.1f}° (Alt: {solar_altitude:.1f}°)")
    if shadow_azimuth is not None:
        shadow_direction, _ = get_direction_from_angle(shadow_azimuth)
        print(f"🔍 Shadow Direction: {shadow_direction['name']} {shadow_azimuth:.1f}° (Length: {shadow_length:.1f}m)")
else:
    print(f"☀️ Sun below horizon - use for stellar/lunar observations")
print(f"🎯 True North: 0.0° | Magnetic North: {magnetic_declination:.1f}°")
print(f"📊 JSON saved as digansha_yantra.json")
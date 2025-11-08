import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta

# ====== INPUT ======
latitude = float(input("Enter Latitude (e.g., 28.6139): "))
longitude = float(input("Enter Longitude (e.g., 77.2090): "))
scale_m = float(input("Enter scale (meters, e.g., 5.0): "))
date_str = input("Enter date (YYYY-MM-DD): ")

# ====== DATE HANDLING ======
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
day_of_year = date_obj.timetuple().tm_yday

# ====== ZODIAC SIGN CALCULATION ======
# 12 zodiac signs with their date ranges and Sanskrit names
zodiac_signs = [
    {"name": "Mesha (Aries)", "start_day": 80, "end_day": 110, "color": "#FF6B6B"},
    {"name": "Vrishabha (Taurus)", "start_day": 111, "end_day": 141, "color": "#4ECDC4"},
    {"name": "Mithuna (Gemini)", "start_day": 142, "end_day": 172, "color": "#45B7D1"},
    {"name": "Karka (Cancer)", "start_day": 173, "end_day": 203, "color": "#96CEB4"},
    {"name": "Simha (Leo)", "start_day": 204, "end_day": 234, "color": "#FFEAA7"},
    {"name": "Kanya (Virgo)", "start_day": 235, "end_day": 265, "color": "#DDA0DD"},
    {"name": "Tula (Libra)", "start_day": 266, "end_day": 296, "color": "#98D8C8"},
    {"name": "Vrishchika (Scorpio)", "start_day": 297, "end_day": 327, "color": "#F7DC6F"},
    {"name": "Dhanus (Sagittarius)", "start_day": 328, "end_day": 358, "color": "#BB8FCE"},
    {"name": "Makara (Capricorn)", "start_day": 359, "end_day": 19, "color": "#85C1E9"},  # crosses year
    {"name": "Kumbha (Aquarius)", "start_day": 20, "end_day": 50, "color": "#F8C471"},
    {"name": "Meena (Pisces)", "start_day": 51, "end_day": 79, "color": "#82E0AA"}
]

# Find current zodiac sign
current_sign = None
for sign in zodiac_signs:
    if sign["start_day"] <= sign["end_day"]:  # Normal case
        if sign["start_day"] <= day_of_year <= sign["end_day"]:
            current_sign = sign
            break
    else:  # Capricorn case (crosses new year)
        if day_of_year >= sign["start_day"] or day_of_year <= sign["end_day"]:
            current_sign = sign
            break

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
declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year)/365))

# ====== ECLIPTIC COORDINATES ======
# Solar longitude (position along ecliptic)
solar_longitude = (280.460 + 0.9856474 * day_of_year) % 360

# ====== PARAMETERS ======
yantra_radius = scale_m
gnomon_height = scale_m * 0.8
platform_thickness = scale_m * 0.1

# ====== RASIVALAYA SPECIFIC GEOMETRY ======
# The Rasivalaya has 12 segments for zodiac signs
segment_angle = 30  # degrees per zodiac sign
hours = np.arange(-6, 7, 1)  # -6 to +6 hrs from noon

# ====== ZODIAC SEGMENT CALCULATION ======
def create_zodiac_segments():
    """Create 12 zodiac segments around the yantra"""
    segments = []
    for i, sign in enumerate(zodiac_signs):
        start_angle = i * segment_angle - 90  # Start from top (North)
        end_angle = start_angle + segment_angle
        
        # Create arc points
        angles = np.linspace(np.radians(start_angle), np.radians(end_angle), 50)
        inner_radius = yantra_radius * 0.7
        outer_radius = yantra_radius
        
        # Outer arc
        x_outer = outer_radius * np.cos(angles)
        y_outer = outer_radius * np.sin(angles)
        
        # Inner arc
        x_inner = inner_radius * np.cos(angles[::-1])
        y_inner = inner_radius * np.sin(angles[::-1])
        
        # Combine for filled segment
        x_segment = np.concatenate([x_outer, x_inner])
        y_segment = np.concatenate([y_outer, y_inner])
        
        segments.append({
            "sign": sign["name"],
            "start_angle": start_angle,
            "end_angle": end_angle,
            "color": sign["color"],
            "x_coords": x_segment,
            "y_coords": y_segment,
            "center_angle": start_angle + segment_angle/2,
            "text_radius": yantra_radius * 0.85
        })
    
    return segments

# ====== HOUR LINE CALCULATION FOR RASIVALAYA ======
def rasivalaya_hour_line(phi_deg, delta_deg, t_hours, rashi_offset=0):
    """
    Calculate hour line for Rasivalaya Yantra
    phi_deg = latitude
    delta_deg = solar declination  
    t_hours = hours from local noon
    rashi_offset = zodiac position offset
    """
    H = np.radians(15 * t_hours)  # hour angle
    phi = np.radians(phi_deg)
    delta = np.radians(delta_deg)
    
    # Base angle calculation
    if np.cos(H) != 0:
        theta = np.arctan(np.sin(phi) * np.tan(H))
    else:
        theta = np.pi/2 if H > 0 else -np.pi/2
    
    # Adjust for zodiac position
    zodiac_angle = np.radians(solar_longitude - rashi_offset)
    adjusted_theta = theta + zodiac_angle * 0.1  # Small correction factor
    
    return np.degrees(adjusted_theta)

# ====== CREATE HOUR LINES ======
hour_lines = []
for t in hours:
    theta = rasivalaya_hour_line(latitude, declination, t, solar_longitude)
    radius = yantra_radius * 0.6  # Hour lines in inner circle
    x_end = radius * np.sin(np.radians(theta))
    y_end = radius * np.cos(np.radians(theta))
    hour_lines.append({
        "time": f"{12+t:02.0f}:00",
        "t": 12+t,
        "angle_deg": theta,
        "start": [0,0],
        "end": [x_end, y_end]
    })

# ====== SEASONAL CURVES ======
def create_seasonal_curves():
    """Create curves showing sun's path during different seasons"""
    seasons = [
        {"name": "Summer Solstice", "declination": 23.45, "color": "orange"},
        {"name": "Equinox", "declination": 0, "color": "green"},
        {"name": "Winter Solstice", "declination": -23.45, "color": "blue"}
    ]
    
    curves = []
    for season in seasons:
        points = []
        for t in np.linspace(-6, 6, 50):
            theta = rasivalaya_hour_line(latitude, season["declination"], t)
            radius = yantra_radius * 0.5
            x = radius * np.sin(np.radians(theta))
            y = radius * np.cos(np.radians(theta))
            points.append([x, y])
        
        curves.append({
            "name": season["name"],
            "color": season["color"],
            "points": points
        })
    
    return curves

# ====== FIGURE SETUP ======
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

# ====== DRAW ZODIAC SEGMENTS ======
zodiac_segments = create_zodiac_segments()
for segment in zodiac_segments:
    # Fill zodiac segment
    ax.fill(segment["x_coords"], segment["y_coords"], 
           color=segment["color"], alpha=0.3, edgecolor='black', linewidth=0.5)
    
    # Add zodiac sign labels
    text_angle = np.radians(segment["center_angle"])
    text_x = segment["text_radius"] * np.cos(text_angle)
    text_y = segment["text_radius"] * np.sin(text_angle)
    
    # Rotate text to follow the arc
    rotation = segment["center_angle"] + 90
    if rotation > 90 and rotation < 270:
        rotation += 180
    
    ax.text(text_x, text_y, segment["sign"].split('(')[0], 
           rotation=rotation, ha='center', va='center', fontsize=8, fontweight='bold')

# ====== HIGHLIGHT CURRENT ZODIAC SIGN ======
if current_sign:
    current_segment = next(seg for seg in zodiac_segments if current_sign["name"] in seg["sign"])
    ax.fill(current_segment["x_coords"], current_segment["y_coords"], 
           color=current_sign["color"], alpha=0.7, edgecolor='red', linewidth=3)

# ====== DRAW PLATFORM CIRCLES ======
# Outer boundary
outer_circle = plt.Circle((0,0), yantra_radius, fill=False, color='black', linewidth=3)
ax.add_patch(outer_circle)

# Inner measurement circle
inner_circle = plt.Circle((0,0), yantra_radius * 0.6, fill=False, color='gray', linewidth=2, linestyle='--')
ax.add_patch(inner_circle)

# Central gnomon base
gnomon_base = plt.Circle((0,0), yantra_radius * 0.05, fill=True, color='saddlebrown')
ax.add_patch(gnomon_base)

# ====== DRAW HOUR LINES ======
for line in hour_lines:
    x0, y0 = line['start']
    x1, y1 = line['end']
    ax.plot([x0,x1],[y0,y1], color='darkred', linewidth=1.5, alpha=0.8)
    
    # Add time labels
    label_radius = yantra_radius * 0.65
    label_x = label_radius * np.sin(np.radians(line['angle_deg']))
    label_y = label_radius * np.cos(np.radians(line['angle_deg']))
    ax.text(label_x, label_y, line['time'], ha='center', va='center', 
           fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

# ====== DRAW SEASONAL CURVES ======
seasonal_curves = create_seasonal_curves()
for curve in seasonal_curves:
    points = np.array(curve["points"])
    ax.plot(points[:,0], points[:,1], color=curve["color"], 
           linewidth=2, alpha=0.7, label=curve["name"])

# ====== CURRENT SOLAR TIME LINE ======
t_frac = LST_noon - 12
theta_frac = rasivalaya_hour_line(latitude, declination, t_frac, solar_longitude)
radius_frac = yantra_radius * 0.6
x_end_frac = radius_frac * np.sin(np.radians(theta_frac))
y_end_frac = radius_frac * np.cos(np.radians(theta_frac))

# Calculate precise time
total_seconds = LST_noon * 3600
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

# Draw current time line
ax.plot([0, x_end_frac], [0, y_end_frac], color='gold', linewidth=4, 
        label=f"Current Solar Time: {LST_str}")

# Add sun symbol at the end
ax.scatter(x_end_frac, y_end_frac, color='gold', s=200, marker='*', 
          edgecolors='orange', linewidth=2, zorder=10, label='Sun Position')

# ====== GNOMON ======
# The gnomon is tilted at latitude angle
gnomon_top_x = gnomon_height * np.sin(np.radians(latitude))
gnomon_top_y = gnomon_height * np.cos(np.radians(latitude))

ax.plot([0, gnomon_top_x], [0, gnomon_top_y], color='darkblue', 
        linewidth=6, label=f'Gnomon (tilted {latitude:.1f}°)')

# Gnomon shadow based on sun position
shadow_length = gnomon_height / np.tan(np.radians(90 - abs(declination)))
shadow_x = shadow_length * np.sin(np.radians(theta_frac))
shadow_y = shadow_length * np.cos(np.radians(theta_frac))
ax.plot([0, shadow_x], [0, shadow_y], color='gray', linewidth=3, 
        alpha=0.6, linestyle=':', label='Gnomon Shadow')

# ====== DIRECTIONAL MARKERS ======
directions = ['N', 'E', 'S', 'W']
dir_angles = [90, 0, -90, 180]
for direction, angle in zip(directions, dir_angles):
    dir_radius = yantra_radius * 1.1
    dir_x = dir_radius * np.cos(np.radians(angle))
    dir_y = dir_radius * np.sin(np.radians(angle))
    ax.text(dir_x, dir_y, direction, ha='center', va='center', 
           fontsize=12, fontweight='bold', 
           bbox=dict(boxstyle="circle,pad=0.3", facecolor='lightblue'))

# ====== FINAL STYLING ======
ax.set_aspect('equal')
ax.set_xlim(-yantra_radius*1.3, yantra_radius*1.3)
ax.set_ylim(-yantra_radius*1.3, yantra_radius*1.3)

plt.title(f"Rasivalaya Yantra - {current_sign['name'] if current_sign else 'Unknown Rashi'}\n"
          f"Location: {latitude:.2f}°N, {longitude:.2f}°E | Date: {date_str}\n"
          f"Solar Longitude: {solar_longitude:.1f}° | Declination: {declination:.2f}°", 
          fontsize=14, pad=20)

plt.xlabel("East-West (meters)", fontsize=12)
plt.ylabel("North-South (meters)", fontsize=12)
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ====== JSON SAVE ======
output = {
    "yantra_type": "rasivalaya",
    "latitude": latitude,
    "longitude": longitude,
    "scale_m": scale_m,
    "date": date_str,
    "day_of_year": day_of_year,
    "current_zodiac_sign": current_sign["name"] if current_sign else "Unknown",
    "solar_longitude": round(solar_longitude, 2),
    "solar_declination": round(declination, 2),
    "solar_time_highlighted": LST_str,
    "equation_of_time_minutes": round(EoT, 2),
    "components": {
        "yantra": {"radius_m": yantra_radius},
        "gnomon": {"height_m": gnomon_height, "tilt_deg": latitude},
        "zodiac_segments": [
            {
                "sign": seg["sign"],
                "start_angle": seg["start_angle"],
                "end_angle": seg["end_angle"],
                "color": seg["color"]
            } for seg in zodiac_segments
        ],
        "hour_lines": hour_lines,
        "seasonal_curves": [
            {
                "season": curve["name"],
                "color": curve["color"],
                "points": len(curve["points"])
            } for curve in seasonal_curves
        ],
        "current_sun_position": {
            "angle_deg": round(theta_frac, 2),
            "x_pos": round(x_end_frac, 2),
            "y_pos": round(y_end_frac, 2)
        }
    },
    "astronomical_data": {
        "solar_longitude_deg": round(solar_longitude, 2),
        "declination_deg": round(declination, 2),
        "equation_of_time_min": round(EoT, 2),
        "local_solar_time": LST_str,
        "zodiac_position": f"Sun in {current_sign['name'] if current_sign else 'Unknown'}"
    }
}

with open("rasivalaya_yantra.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Rasivalaya Yantra generated!")
print(f"🌟 Current Zodiac Sign: {current_sign['name'] if current_sign else 'Unknown'}")
print(f"☀️ Solar Time: {LST_str}")
print(f"🔄 Solar Longitude: {solar_longitude:.1f}°")
print(f"📊 JSON saved as rasivalaya_yantra.json")
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

# ====== SIDEREAL TIME CALCULATION ======
# Greenwich Sidereal Time at 0h UT
J2000_epoch = datetime(2000, 1, 1, 12, 0, 0)  # J2000.0 epoch
days_since_J2000 = (datetime_obj - J2000_epoch).total_seconds() / 86400.0
centuries_since_J2000 = days_since_J2000 / 36525.0

# Greenwich Mean Sidereal Time at 0h UT (in hours)
GMST0 = 18.697374558 + 24.06570982441908 * days_since_J2000
GMST0 = GMST0 % 24

# Current Greenwich Mean Sidereal Time
GMST = (GMST0 + 1.00273790935 * hour_decimal) % 24

# Local Sidereal Time
LST = (GMST + longitude / 15.0) % 24

# ====== POLARIS COORDINATES ======
# Polaris (α UMi) coordinates for current epoch
polaris_ra_hours = 2.530  # Right Ascension in hours (J2000)
polaris_dec_deg = 89.264  # Declination in degrees (J2000)

# Precession correction (simplified)
precession_correction = 0.0139 * centuries_since_J2000  # degrees per century
current_polaris_dec = polaris_dec_deg + precession_correction

# Hour Angle of Polaris
polaris_hour_angle = (LST - polaris_ra_hours) % 24
if polaris_hour_angle > 12:
    polaris_hour_angle -= 24

# ====== CIRCUMPOLAR STAR PATTERNS ======
# Major circumpolar constellations visible around Polaris
circumpolar_stars = [
    # Ursa Major (Big Dipper) - 7 main stars
    {"name": "Dubhe", "ra": 11.062, "dec": 61.751, "mag": 1.8, "constellation": "UMa"},
    {"name": "Merak", "ra": 11.031, "dec": 56.383, "mag": 2.4, "constellation": "UMa"},
    {"name": "Phecda", "ra": 11.897, "dec": 53.695, "mag": 2.4, "constellation": "UMa"},
    {"name": "Megrez", "ra": 12.257, "dec": 57.033, "mag": 3.3, "constellation": "UMa"},
    {"name": "Alioth", "ra": 12.900, "dec": 55.960, "mag": 1.8, "constellation": "UMa"},
    {"name": "Mizar", "ra": 13.420, "dec": 54.925, "mag": 2.3, "constellation": "UMa"},
    {"name": "Alkaid", "ra": 13.792, "dec": 49.313, "mag": 1.9, "constellation": "UMa"},
    
    # Cassiopeia - 5 main stars (W-shaped)
    {"name": "Schedar", "ra": 0.675, "dec": 56.538, "mag": 2.2, "constellation": "Cas"},
    {"name": "Caph", "ra": 0.153, "dec": 59.150, "mag": 2.3, "constellation": "Cas"},
    {"name": "Gamma Cas", "ra": 0.945, "dec": 60.717, "mag": 2.5, "constellation": "Cas"},
    {"name": "Ruchbah", "ra": 1.430, "dec": 60.235, "mag": 2.7, "constellation": "Cas"},
    {"name": "Segin", "ra": 1.906, "dec": 63.670, "mag": 3.4, "constellation": "Cas"},
    
    # Draco - Dragon constellation
    {"name": "Thuban", "ra": 14.073, "dec": 64.376, "mag": 3.7, "constellation": "Dra"},
    {"name": "Etamin", "ra": 17.943, "dec": 51.489, "mag": 2.2, "constellation": "Dra"},
    {"name": "Rastaban", "ra": 17.507, "dec": 52.301, "mag": 2.8, "constellation": "Dra"},
    
    # Cepheus
    {"name": "Alderamin", "ra": 21.310, "dec": 62.585, "mag": 2.4, "constellation": "Cep"},
    {"name": "Alfirk", "ra": 21.477, "dec": 70.561, "mag": 3.2, "constellation": "Cep"},
]

# ====== PARAMETERS ======
yantra_radius = scale_m
central_pole_height = scale_m * 1.2
inner_circle_radius = scale_m * 0.1  # Central Polaris circle
outer_ring_radius = scale_m * 0.9    # Outer measurement ring

# ====== COORDINATE TRANSFORMATION ======
def celestial_to_local(ra_hours, dec_deg, lst_hours, lat_deg):
    """Convert celestial coordinates to local horizontal coordinates"""
    # Hour angle
    ha = (lst_hours - ra_hours) * 15  # Convert to degrees
    
    # Convert to radians
    ha_rad = np.radians(ha)
    dec_rad = np.radians(dec_deg)
    lat_rad = np.radians(lat_deg)
    
    # Calculate altitude and azimuth
    sin_alt = np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(ha_rad)
    altitude = np.degrees(np.arcsin(sin_alt))
    
    cos_az = (np.sin(dec_rad) - np.sin(lat_rad) * sin_alt) / (np.cos(lat_rad) * np.cos(np.radians(altitude)))
    azimuth = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    
    if np.sin(ha_rad) > 0:
        azimuth = 360 - azimuth
    
    return altitude, azimuth

def polar_projection(altitude, azimuth, max_radius):
    """Project celestial coordinates onto polar grid"""
    # Distance from pole (90° - altitude) scaled to radius
    r = max_radius * (90 - altitude) / 90
    
    # Convert azimuth to mathematical angle (counterclockwise from east)
    theta = np.radians(90 - azimuth)
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    return x, y

# ====== HOUR ANGLE GRID ======
def create_hour_circles():
    """Create hour angle circles for sidereal time measurement"""
    hour_circles = []
    
    # 24 hour lines radiating from center
    for h in range(24):
        angle = h * 15 - 90  # Start from north (0°)
        angle_rad = np.radians(angle)
        
        x_end = yantra_radius * np.cos(angle_rad)
        y_end = yantra_radius * np.sin(angle_rad)
        
        # Sidereal hour (slightly different from solar hour)
        sidereal_hour = h * 23.93447 / 24  # Sidereal hour conversion
        
        hour_circles.append({
            "hour": h,
            "sidereal_hour": sidereal_hour,
            "angle_deg": angle,
            "start": [0, 0],
            "end": [x_end, y_end],
            "label": f"{h:02d}h"
        })
    
    return hour_circles

# ====== DECLINATION CIRCLES ======
def create_declination_circles():
    """Create concentric circles for different declinations"""
    dec_circles = []
    declinations = [30, 45, 60, 75, 85]  # Declination values in degrees
    
    for dec in declinations:
        radius = yantra_radius * (90 - dec) / 90
        dec_circles.append({
            "declination": dec,
            "radius": radius,
            "color": "lightgray"
        })
    
    return dec_circles

# ====== POLARIS POSITION CALCULATION ======
polaris_altitude, polaris_azimuth = celestial_to_local(
    polaris_ra_hours, current_polaris_dec, LST, latitude
)
polaris_x, polaris_y = polar_projection(polaris_altitude, polaris_azimuth, yantra_radius)

# ====== CIRCUMPOLAR STAR POSITIONS ======
star_positions = []
for star in circumpolar_stars:
    alt, az = celestial_to_local(star["ra"], star["dec"], LST, latitude)
    
    # Only include stars above horizon
    if alt > 0:
        x, y = polar_projection(alt, az, yantra_radius)
        star_positions.append({
            "name": star["name"],
            "constellation": star["constellation"],
            "magnitude": star["mag"],
            "x": x,
            "y": y,
            "altitude": alt,
            "azimuth": az
        })

# ====== FIGURE SETUP ======
fig, ax = plt.subplots(1, 1, figsize=(14, 14))

# ====== DRAW DECLINATION CIRCLES ======
declination_circles = create_declination_circles()
for dec_circle in declination_circles:
    circle = plt.Circle((0, 0), dec_circle["radius"], fill=False, 
                       color=dec_circle["color"], linewidth=1, alpha=0.6)
    ax.add_patch(circle)
    
    # Add declination labels
    ax.text(dec_circle["radius"], 0, f"{dec_circle['declination']}°", 
           ha='left', va='center', fontsize=8, color='gray')

# ====== DRAW OUTER YANTRA BOUNDARY ======
outer_boundary = plt.Circle((0, 0), yantra_radius, fill=False, 
                           color='black', linewidth=4)
ax.add_patch(outer_boundary)

# Inner measurement circle
inner_boundary = plt.Circle((0, 0), inner_circle_radius, fill=True, 
                           color='darkblue', alpha=0.8)
ax.add_patch(inner_boundary)

# ====== DRAW HOUR ANGLE LINES ======
hour_circles = create_hour_circles()
for i, hour_line in enumerate(hour_circles):
    x0, y0 = hour_line['start']
    x1, y1 = hour_line['end']
    
    # Highlight current sidereal time
    if abs(hour_line['hour'] - LST) < 0.5 or abs(hour_line['hour'] - LST - 24) < 0.5:
        ax.plot([x0, x1], [y0, y1], color='red', linewidth=3, alpha=0.8)
    else:
        ax.plot([x0, x1], [y0, y1], color='darkblue', linewidth=1, alpha=0.6)
    
    # Add hour labels at outer edge
    label_radius = yantra_radius * 1.05
    label_x = label_radius * np.cos(np.radians(hour_line['angle_deg']))
    label_y = label_radius * np.sin(np.radians(hour_line['angle_deg']))
    
    if i % 2 == 0:  # Show every other hour for clarity
        ax.text(label_x, label_y, hour_line['label'], ha='center', va='center',
               fontsize=9, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))

# ====== DRAW POLARIS POSITION ======
ax.scatter(polaris_x, polaris_y, color='gold', s=300, marker='*', 
          edgecolors='orange', linewidth=2, zorder=10, label='Polaris (Dhruva)')

# Draw Polaris movement circle (due to precession)
precession_radius = yantra_radius * 0.02  # Small circle showing precession
precession_circle = plt.Circle((polaris_x, polaris_y), precession_radius, 
                              fill=False, color='gold', linewidth=2, linestyle='--', alpha=0.7)
ax.add_patch(precession_circle)

# ====== DRAW CIRCUMPOLAR STARS ======
constellation_colors = {
    'UMa': '#FF6B6B',    # Ursa Major - Red
    'Cas': '#4ECDC4',    # Cassiopeia - Teal  
    'Dra': '#45B7D1',    # Draco - Blue
    'Cep': '#96CEB4',    # Cepheus - Green
}

# Group stars by constellation for connecting lines
constellations = {}
for star in star_positions:
    const = star['constellation']
    if const not in constellations:
        constellations[const] = []
    constellations[const].append(star)

# Draw constellation patterns
constellation_patterns = {
    'UMa': [(0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (3,0)],  # Big Dipper
    'Cas': [(0,1), (1,2), (2,3), (3,4)],  # W-shape
    'Dra': [(0,1), (1,2)],  # Simplified dragon
    'Cep': [(0,1)]  # Simplified
}

for const_name, stars in constellations.items():
    if const_name in constellation_patterns and len(stars) > 1:
        color = constellation_colors.get(const_name, 'white')
        
        # Draw constellation lines
        pattern = constellation_patterns[const_name]
        for connection in pattern:
            if connection[0] < len(stars) and connection[1] < len(stars):
                star1 = stars[connection[0]]
                star2 = stars[connection[1]]
                ax.plot([star1['x'], star2['x']], [star1['y'], star2['y']], 
                       color=color, linewidth=1.5, alpha=0.6)

# Draw individual stars
for star in star_positions:
    # Star size based on magnitude (brighter = larger, lower magnitude = brighter)
    size = max(50, 200 - star['magnitude'] * 30)
    color = constellation_colors.get(star['constellation'], 'white')
    
    ax.scatter(star['x'], star['y'], color=color, s=size, marker='o',
              edgecolors='white', linewidth=1, alpha=0.8, zorder=8)
    
    # Add star names for brighter stars
    if star['magnitude'] < 3.0:
        ax.text(star['x'], star['y'] + yantra_radius * 0.03, star['name'],
               ha='center', va='bottom', fontsize=7, color='white',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.7))

# ====== CENTRAL POLE REPRESENTATION ======
# The gnomon represents the celestial pole
pole_x = 0
pole_y = 0
gnomon_tilt_x = central_pole_height * 0.1 * np.sin(np.radians(latitude))
gnomon_tilt_y = central_pole_height * 0.1 * np.cos(np.radians(latitude))

ax.plot([pole_x, gnomon_tilt_x], [pole_y, gnomon_tilt_y], 
        color='darkblue', linewidth=8, label=f'Celestial Pole Axis (tilted {latitude:.1f}°)')

# ====== CURRENT SIDEREAL TIME INDICATOR ======
current_hour_angle = LST * 15 - 90  # Convert to degrees from north
current_angle_rad = np.radians(current_hour_angle)
indicator_radius = yantra_radius * 0.8

indicator_x = indicator_radius * np.cos(current_angle_rad)
indicator_y = indicator_radius * np.sin(current_angle_rad)

ax.plot([0, indicator_x], [0, indicator_y], color='lime', linewidth=4,
        label=f'Current LST: {LST:.2f}h ({int(LST):02d}:{int((LST%1)*60):02d})')

# Add time indicator marker
ax.scatter(indicator_x, indicator_y, color='lime', s=200, marker='D',
          edgecolors='green', linewidth=2, zorder=9)

# ====== DIRECTIONAL MARKERS ======
directions = [('N', 90), ('E', 0), ('S', -90), ('W', 180)]
for direction, angle in directions:
    dir_radius = yantra_radius * 1.15
    dir_x = dir_radius * np.cos(np.radians(angle))
    dir_y = dir_radius * np.sin(np.radians(angle))
    ax.text(dir_x, dir_y, direction, ha='center', va='center',
           fontsize=14, fontweight='bold',
           bbox=dict(boxstyle="circle,pad=0.3", facecolor='lightcyan', edgecolor='navy'))

# ====== SEASONAL POLE STAR VARIATION ======
# Show how pole star position varies slightly with season
season_angles = np.linspace(0, 2*np.pi, 12)
for i, angle in enumerate(season_angles):
    seasonal_x = polaris_x + precession_radius * 0.3 * np.cos(angle)
    seasonal_y = polaris_y + precession_radius * 0.3 * np.sin(angle)
    ax.scatter(seasonal_x, seasonal_y, color='yellow', s=20, alpha=0.5, marker='.')

# ====== FINAL STYLING ======
ax.set_aspect('equal')
ax.set_xlim(-yantra_radius*1.3, yantra_radius*1.3)
ax.set_ylim(-yantra_radius*1.3, yantra_radius*1.3)
ax.set_facecolor('black')

plt.title(f"Dhruva-Protha-Chakra Yantra - Polar Star Tracker\n"
          f"Location: {latitude:.2f}°N, {longitude:.2f}°E | {date_str} {time_str}\n"
          f"LST: {LST:.3f}h | Polaris Alt: {polaris_altitude:.1f}° | "
          f"Visible Stars: {len(star_positions)}", 
          fontsize=14, pad=20, color='white')

plt.xlabel("East-West (meters)", fontsize=12, color='white')
plt.ylabel("North-South (meters)", fontsize=12, color='white')
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10,
          facecolor='lightgray', edgecolor='black')

# Make axes labels white for dark background
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')

plt.grid(True, alpha=0.3, color='gray')
plt.tight_layout()
plt.show()

# ====== JSON SAVE ======
output = {
    "yantra_type": "dhruva_protha_chakra",
    "latitude": latitude,
    "longitude": longitude, 
    "scale_m": scale_m,
    "observation_date": date_str,
    "observation_time": time_str,
    "local_sidereal_time_hours": round(LST, 4),
    "polaris_data": {
        "right_ascension_hours": polaris_ra_hours,
        "declination_deg": round(current_polaris_dec, 3),
        "altitude_deg": round(polaris_altitude, 2),
        "azimuth_deg": round(polaris_azimuth, 2),
        "hour_angle_hours": round(polaris_hour_angle, 3),
        "position_x_m": round(polaris_x, 3),
        "position_y_m": round(polaris_y, 3)
    },
    "components": {
        "yantra": {"radius_m": yantra_radius},
        "central_pole": {"height_m": central_pole_height, "tilt_deg": latitude},
        "inner_circle": {"radius_m": inner_circle_radius},
        "declination_circles": [
            {"declination_deg": dc["declination"], "radius_m": dc["radius"]}
            for dc in declination_circles
        ],
        "hour_angle_lines": [
            {
                "hour": hc["hour"],
                "sidereal_hour": round(hc["sidereal_hour"], 3),
                "angle_deg": hc["angle_deg"]
            } for hc in hour_circles
        ]
    },
    "visible_stars": [
        {
            "name": star["name"],
            "constellation": star["constellation"],
            "magnitude": star["magnitude"],
            "altitude_deg": round(star["altitude"], 2),
            "azimuth_deg": round(star["azimuth"], 2),
            "x_pos_m": round(star["x"], 3),
            "y_pos_m": round(star["y"], 3)
        } for star in star_positions
    ],
    "astronomical_data": {
        "days_since_J2000": round(days_since_J2000, 2),
        "greenwich_mean_sidereal_time": round(GMST, 4),
        "local_sidereal_time": round(LST, 4),
        "precession_correction_deg": round(precession_correction, 4),
        "visible_circumpolar_stars": len(star_positions)
    }
}

with open("dhruva_protha_chakra_yantra.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Dhruva-Protha-Chakra Yantra generated!")
print(f"⭐ Polaris Position: Alt {polaris_altitude:.1f}°, Az {polaris_azimuth:.1f}°")
print(f"🕐 Local Sidereal Time: {LST:.3f}h ({int(LST):02d}:{int((LST%1)*60):02d})")
print(f"🌌 Visible Circumpolar Stars: {len(star_positions)}")
print(f"📊 JSON saved as dhruva_protha_chakra_yantra.json")
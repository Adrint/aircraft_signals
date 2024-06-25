import json
import os
from geopy.distance import great_circle
from shapely.geometry import LineString
from datetime import datetime


import folium
from itertools import cycle

# Ścieżka do pliku JSON
file_path = r'A:\repo_git\aircraft_signals\dane\json\merged_output.json'

# Lista do przechowywania wszystkich obiektów JSON
data = []

# Wczytaj dane z pliku JSON
try:
    with open(file_path, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"Plik {file_path} nie został znaleziony.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Błąd podczas parsowania JSON: {str(e)}")
    exit(1)


def find_flight_data(ident):
    for flight_data in data:
        if flight_data['ident'] == ident:
            reg = flight_data.get('reg', 'Unknown registration')
            waypoints = flight_data.get('waypoints', [])
            if waypoints:
                alt = waypoints[0].get('alt', 'No altitude data')
                clock = waypoints[0].get('clock', 'No clock data')
            else:
                alt = 'No altitude data'
                clock = 'No clock data'
            return reg, alt, clock
    
    return 'Unknown registration', 'No altitude data', 'No clock data' 
	
	from shapely.geometry import Point
from datetime import datetime
from math import sqrt, pow, inf

def find_altitude_and_clock(closest_point, ident, data):
    closest_waypoint = None
    min_distance = inf
    alt = 'Brak danych wysokości'
    clock = 'Brak danych zegarowych'
    
    for flight_data in data:
        if flight_data['ident'] == ident:
            waypoints = flight_data.get('waypoints', [])
            
            # Zmienne do przechowywania informacji o punkcie o najmniejszej odległości
            closest_wp_index = -1  # Indeks najbliższego punktu w waypoints
            closest_wp_point = None  # Punkt o najmniejszej odległości
            
            # Iteracja po wszystkich waypointach
            for index, wp in enumerate(waypoints):
                wp_lon = wp.get('lon')
                wp_lat = wp.get('lat')
                
                if wp_lon is not None and wp_lat is not None:
                    waypoint_point = Point(wp_lon, wp_lat)
                    distance = sqrt(pow(wp_lon - closest_point.x, 2) + pow(wp_lat - closest_point.y, 2))
                    #print(f"Punkt: {waypoint_point}, Odległość: {distance}")
                    
                    # Aktualizacja najmniejszej odległości i punktu
                    if distance < min_distance:
                        min_distance = distance
                        closest_wp_index = index
                        closest_wp_point = waypoint_point
            
            # Jeśli znaleziono najbliższy punkt, pobierz jego dane
            if closest_wp_index != -1:
                closest_waypoint = waypoints[closest_wp_index]
                alt = closest_waypoint.get('alt', 'Brak danych wysokości')
                clock = closest_waypoint.get('clock', 'Brak danych zegarowych')
                lon = closest_waypoint.get('lon', 'Brak danych lon')
                lat = closest_waypoint.get('lat', 'Brak danych lat')
                
                #print(f"Znaleziono najbliższy punkt: {closest_wp_point}")
                break  # Wyjście z pętli po znalezieniu najbliższego punktu
    
    return alt, clock, lon, lat


def check_collisions(paths, idents):
    collisions = []
    
    for i in range(len(paths)):
        path1 = paths[i]
        ident1 = idents[i]
        reg1, _, _ = find_flight_data(ident1)  # Only need registration for printing purposes

        for j in range(i + 1, len(paths)):
            path2 = paths[j]
            ident2 = idents[j]
            reg2, _, _ = find_flight_data(ident2)  # Only need registration for printing purposes

            if path1.intersects(path2):
                intersection = path1.intersection(path2)

                if intersection.is_empty or intersection.geom_type != 'Point':
                    continue
                
                intersection_point = (intersection.x, intersection.y)

                closest_point1 = path1.interpolate(path1.project(intersection))
                closest_point2 = path2.interpolate(path2.project(intersection))
                 

                # Retrieve altitude and clock data for closest points
                alt1, clock1, lon1, lat1 = find_altitude_and_clock(closest_point1, ident1,data)
                alt2, clock2, lon2, lat2 = find_altitude_and_clock(closest_point2, ident2,data)
                
                if clock1 != 'No clock data' and clock2 != 'No clock data':
                    # Calculate time difference
                    time_format = "%Y-%m-%d %H:%M:%S"
                    time1 = datetime.strptime(clock1, time_format)
                    time2 = datetime.strptime(clock2, time_format)
                    time_diff = abs((time1 - time2).total_seconds())
                    time_diff_hours = int(time_diff // 3600)
                    time_diff_minutes = int((time_diff % 3600) // 60)
                else:
                    time_diff_hours = -1  # Placeholder for invalid time difference
                    time_diff_minutes = -1  # Placeholder for invalid time difference

                # Calculate altitude difference
                if alt1 != 'No altitude data' and alt2 != 'No altitude data':
                    alt_diff = abs(int(alt1) - int(alt2))
                else:
                    alt_diff = -1  # Placeholder for invalid altitude difference

                collisions.append((ident1, reg1, alt1, clock1,
                                   ident2, reg2, alt2, clock2,
                                   intersection_point[1], intersection_point[0],
                                   lon1, lat1,
                                   lon2, lat2,
                                   time_diff_hours, time_diff_minutes,
                                   alt_diff))
    
    return collisions
	
	paths = []
idents = []

for flight in data:
    waypoints = flight.get('waypoints', [])
    points = [(wp['lon'], wp['lat']) for wp in waypoints if 'lat' in wp and 'lon' in wp]
    if points:
        line = LineString(points)
        paths.append(line)
        idents.append(flight['ident'])

# Displaying the results
collisions = check_collisions(paths, idents)

if collisions:
    print("Found potential collisions:")
    for collision in collisions:
        print(f"Flight {collision[0]} (Reg: {collision[1]}) and Flight {collision[4]} (Reg: {collision[5]})")
        print(f"Intersect at point ({collision[9]}, {collision[8]})")
        print(f"Closest point on Flight {collision[0]} trajectory: ({collision[10]}, {collision[11]}), Alt: {collision[2]}, Clock: {collision[3]}")
        print(f"Closest point on Flight {collision[4]} trajectory: ({collision[12]}, {collision[13]}), Alt: {collision[6]}, Clock: {collision[7]}")
        print(f"Altitude difference: {collision[16]} and time difference: {collision[14]} hours and {collision[15]} minutes")
        print()
else:
    print("No potential collisions found.")
	
	Found potential collisions:
Flight SWA622 (Reg: N8633A) and Flight AAL2254 (Reg: N177AN)
Intersect at point (-79.98487707535958, 25.99567699112497)
Closest point on Flight SWA622 trajectory: (-79.96436, 25.98681), Alt: 30000, Clock: 2018-01-02 02:10:08
Closest point on Flight AAL2254 trajectory: (-79.98559, 25.99556), Alt: 15900, Clock: 2018-01-02 00:26:39
Altitude difference: 14100 and time difference: 1 hours and 43 minutes

Flight SWA622 (Reg: N8633A) and Flight DAL446 (Reg: N355NB)
Intersect at point (-94.11626131348235, 31.81216786066269)
Closest point on Flight SWA622 trajectory: (-94.14311, 31.82162), Alt: 36000, Clock: 2018-01-02 05:40:11
Closest point on Flight DAL446 trajectory: (-94.15028, 31.77556), Alt: 35000, Clock: 2018-01-02 22:01:01
Altitude difference: 1000 and time difference: 16 hours and 20 minutes

Flight AAL1632 (Reg: N170US) and Flight DAL446 (Reg: N355NB)
Intersect at point (-90.02745229745015, 34.999802856572956)
Closest point on Flight AAL1632 trajectory: (-89.96194, 35.0225), Alt: 30900, Clock: 2018-01-02 01:16:05
Closest point on Flight DAL446 trajectory: (-89.99667, 35.0225), Alt: 34900, Clock: 2018-01-02 22:35:44
Altitude difference: 4000 and time difference: 21 hours and 19 minutes

Flight AAL2254 (Reg: N177AN) and Flight DAL446 (Reg: N355NB)
Intersect at point (-73.471327869252, 40.484711358672875)
Closest point on Flight AAL2254 trajectory: (-73.48156, 40.49044), Alt: 1575, Clock: 2018-01-02 02:34:32
Closest point on Flight DAL446 trajectory: (-73.45528, 40.50167), Alt: 4000, Clock: 2018-01-03 00:42:31
Altitude difference: 2425 and time difference: 22 hours and 7 minutes

Flight AAL2254 (Reg: N177AN) and Flight JBU1197 (Reg: N796JB)
Intersect at point (-73.34799333743534, 39.609096176139836)
Closest point on Flight AAL2254 trajectory: (-73.34509, 39.60692), Alt: 13550, Clock: 2018-01-02 02:18:06
Closest point on Flight JBU1197 trajectory: (-73.35482, 39.60228), Alt: 35975, Clock: 2018-01-01 23:23:05
Altitude difference: 22425 and time difference: 2 hours and 55 minutes

Flight AAL2254 (Reg: N177AN) and Flight SWA622 (Reg: N8633A)
Intersect at point (-79.98487707535958, 25.99567699112497)
Closest point on Flight AAL2254 trajectory: (-79.98559, 25.99556), Alt: 15900, Clock: 2018-01-02 00:26:39
Closest point on Flight SWA622 trajectory: (-79.96436, 25.98681), Alt: 30000, Clock: 2018-01-02 02:10:08
Altitude difference: 14100 and time difference: 1 hours and 43 minutes

Flight CBJ480 (Reg: B8550) and Flight QFA79 (Reg: VHQPI)
Intersect at point (145.45008631493425, -26.824897875714065)
Closest point on Flight CBJ480 trajectory: (145.463, -26.84095), Alt: 36000, Clock: 2018-01-02 02:38:43
Closest point on Flight QFA79 trajectory: (145.45085, -26.79337), Alt: 36000, Clock: 2018-01-02 01:10:07
Altitude difference: 0 and time difference: 1 hours and 28 minutes

Flight DAL446 (Reg: N355NB) and Flight SWA622 (Reg: N8633A)
Intersect at point (-94.11626131348235, 31.81216786066269)
Closest point on Flight DAL446 trajectory: (-94.15028, 31.77556), Alt: 35000, Clock: 2018-01-02 22:01:01
Closest point on Flight SWA622 trajectory: (-94.14311, 31.82162), Alt: 36000, Clock: 2018-01-02 05:40:11
Altitude difference: 1000 and time difference: 16 hours and 20 minutes

Flight KAL124 (Reg: HL7586) and Flight QFA79 (Reg: VHQPI)
Intersect at point (143.13333496561637, 5.9372524446306185)
Closest point on Flight KAL124 trajectory: (142.9, 6.38333), Alt: 38000, Clock: 2018-01-02 04:16:27
Closest point on Flight QFA79 trajectory: (143.25, 5.45), Alt: 38000, Clock: 2018-01-02 05:18:53
Altitude difference: 0 and time difference: 1 hours and 2 minutes

Flight QFA79 (Reg: VHQPI) and Flight VOZ214 (Reg: VHYVC)
Intersect at point (144.80957271105592, -37.516800457486404)
Closest point on Flight QFA79 trajectory: (144.81897, -37.50155), Alt: 12925, Clock: 2018-01-01 23:43:53
Closest point on Flight VOZ214 trajectory: (144.8119, -37.52948), Alt: 2975, Clock: 2018-01-02 01:22:24
Altitude difference: 9950 and time difference: 1 hours and 38 minutes

import folium
from itertools import cycle

# Create a map
map_center = (0, 0)  # Center of the map
mymap = folium.Map(location=map_center, zoom_start=2)

# List of colors for aircraft routes
colors = cycle(['black', 'darkgreen', 'green', 'darkblue', 'darkred', 'gray', 'blue'])

# Dictionary to store assigned colors for each identifier
color_map = {}

# Create feature groups for markers
intersection_group = folium.FeatureGroup(name='Intersections')
closest_points_group = folium.FeatureGroup(name='Closest Points')
mymap.add_child(intersection_group)
mymap.add_child(closest_points_group)

# Function to handle marker click event
def on_marker_click(event):
    popup_content = event.popup
    marker = event.target

    # Remove all markers from map
    intersection_group.clear_layers()
    closest_points_group.clear_layers()

    # Add clicked marker back to the map
    marker.add_to(mymap)

    # Check which popup content is clicked and add corresponding markers
    if popup_content.startswith('<b>Collision at Intersection</b>'):
        intersection_group.add_child(marker)
        # Parse intersection details
        intersection_data = parse_intersection_popup(popup_content)
        add_intersection_markers(intersection_data)
    elif popup_content.startswith('<b>Closest Point on Flight 1</b>'):
        closest_points_group.add_child(marker)
    elif popup_content.startswith('<b>Closest Point on Flight 2</b>'):
        closest_points_group.add_child(marker)

def parse_intersection_popup(popup_content):
    # Parse popup content to extract intersection details
    lines = popup_content.split('<br>')
    intersection_lat = float(lines[-4].split(': ')[-1])
    intersection_lon = float(lines[-3].split(': ')[-1])
    closest_lat1 = float(lines[7].split(': ')[-1])
    closest_lon1 = float(lines[8].split(': ')[-1])
    closest_lat2 = float(lines[12].split(': ')[-1])
    closest_lon2 = float(lines[13].split(': ')[-1])
    return {
        'intersection_lat': intersection_lat,
        'intersection_lon': intersection_lon,
        'closest_lat1': closest_lat1,
        'closest_lon1': closest_lon1,
        'closest_lat2': closest_lat2,
        'closest_lon2': closest_lon2,
    }

def add_intersection_markers(data):
    # Add markers for intersection and closest points
    intersection_marker = folium.Marker((data['intersection_lat'], data['intersection_lon']),
                                        popup="Intersection",
                                        icon=folium.Icon(color='red'))
    intersection_marker.add_to(intersection_group)

    closest_point1_marker = folium.Marker((data['closest_lat1'], data['closest_lon1']),
                                          popup="Closest Point 1",
                                          icon=folium.Icon(color='blue'))
    closest_point1_marker.add_to(closest_points_group)

    closest_point2_marker = folium.Marker((data['closest_lat2'], data['closest_lon2']),
                                          popup="Closest Point 2",
                                          icon=folium.Icon(color='green'))
    closest_point2_marker.add_to(closest_points_group)

# Iterating through each JSON object (representing the route of one aircraft)
for flight_data in data:
    ident = flight_data.get('ident', 'Unknown ident')
    reg = flight_data.get('reg', 'Unknown registration')
    waypoints = flight_data.get('waypoints', [])

    # Create a list of route points for the aircraft
    flight_route = []
    for waypoint in waypoints:
        lat = waypoint.get('lat')
        lon = waypoint.get('lon')

        # Add the route point to the list
        if lat and lon:
            flight_route.append((lat, lon, waypoint.get('alt'), waypoint.get('clock')))

    # Choose the next color for the route
    color = next(colors)

    # Add a line connecting the route points on the map
    folium.PolyLine(locations=[(lat, lon) for lat, lon, _, _ in flight_route], color=color, weight=2.5, opacity=1).add_to(mymap)

    # Add a marker at the start of the route
    if flight_route:
        start_lat, start_lon, start_alt, start_clock = flight_route[0]
        start_popup = f"""
        <div style="min-width: 200px;">
            <b>Start of flight: {ident} <br>Reg: {reg}</b><br>
            <b>Lat:</b> {start_lat}<br>
            <b>Lon:</b> {start_lon}<br>
            <b>Alt:</b> {start_alt} feet<br>
            <b>Clock:</b> {start_clock}
        </div>
        """
    start_marker = folium.Marker((start_lat, start_lon),
                                 popup=start_popup,
                                 icon=folium.Icon(color=color))
    start_marker.add_to(mymap)

    # Add a marker at the end of the route
    if flight_route:
        end_lat, end_lon, end_alt, end_clock = flight_route[-1]
        end_popup = f"""
        <div style="min-width: 200px;">
            <b>End of flight: {ident}<br> Reg: {reg}</b><br>
            <b>Lon:</b> {end_lon}<br>
            <b>Alt:</b> {end_alt} feet <br>
            <b>Clock:</b> {end_clock}
        </div>
        """
    end_marker = folium.Marker((end_lat, end_lon),
                               popup=end_popup,
                               icon=folium.Icon(color=color))
    end_marker.add_to(mymap)

    # Assign the selected color to the identifier
    color_map[ident] = color

# Adding markers at the intersections and closest points of aircraft routes for each collision
for collision in collisions:
    try:
        ident1, reg1, alt1, clock1, ident2, reg2, alt2, clock2, intersection_lat, intersection_lon, lon1, lat1, lon2, lat2, time_diff_hours, time_diff_minutes, alt_diff = collision

        # Create popup content for the intersection
        intersection_popup = f"""
        <div style="min-width: 250px;">
        <b>Risk of collision</b><br><br>
        <b>Flight 1:</b><br> Ident: {ident1}<br> Reg: {reg1}<br><br>
        <b>Flight 2:</b><br> Ident: {ident2}<br> Reg: {reg2}<br>
        <br>
        <b>Altitude Difference:</b> {alt_diff} feet<br>
        <b>Time Difference:</b> {time_diff_hours} h and {time_diff_minutes} min<br>
        <br>
        <b>Intersection Coord:</b><br>
        Latitude: {intersection_lat}<br>
        Longitude: {intersection_lon}<br>
        <br>
        <b>Position of: {reg1}</b><br>
        Ident: {ident1}<br> 
        Latitude: {lat1}<br>
        Longitude: {lon1}<br>
        Altitude: {alt1}<br>
        Time: {clock1}<br>
        <br>
        <b>Position of {reg2}:</b><br>
        Ident: {ident2}<br>
        Latitude: {lat2}<br>
        Longitude: {lon2}<br>
        Altitude: {alt2}<br>
        Time: {clock2}<br>
        </div>
        """
        
        # Add marker for intersection point
        intersection_marker = folium.Marker((intersection_lat, intersection_lon),
                                            popup=intersection_popup,
                                            icon=folium.Icon(color='red'))
        intersection_marker.add_to(intersection_group)
    
    except ValueError as e:
        print(f"Błąd podczas przetwarzania kolizji: {e}")
        print(f"Dane kolizji: {collision}")

# Add layer control to the map
folium.LayerControl().add_to(mymap)

# Save the map to an HTML file
output_map_path = r'D:\aircraft_signals 2\dane\maps\flight_route_map_with_collisions_details_new.html'
mymap.save(output_map_path)

print(f"Mapa trasy lotu z szczegółami kolizji została zapisana do pliku: {output_map_path}")

Mapa trasy lotu z szczegółami kolizji została zapisana do pliku: D:\aircraft_signals 2\dane\maps\flight_route_map_with_collisions_details_new.html


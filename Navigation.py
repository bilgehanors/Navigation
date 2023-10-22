import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
import math
from pyproj import CRS
import contextily as ctx
import warnings
warnings.filterwarnings('ignore')
#Location neighbourhood
basak = "Kayabaşı Mahallesi, Başakşehir, İstanbul"
place_polygon = ox.geocode_to_gdf(basak)
place_polygon = place_polygon.to_crs(epsg=32635)
place_polygon["geometry"] = place_polygon.buffer(900)
place_polygon = place_polygon.to_crs(epsg=4326)

#Determine Number of Buildings
buildloc = ox.geometries_from_place(basak, tags={'building': True})
print("Building number:", len(buildloc))

graph = ox.graph_from_polygon(place_polygon["geometry"].values[0], network_type='drive')
fig, ax = ox.plot_graph(graph)

#Pharmacies and Health Center Numbers
pharmacy = ox.geometries_from_place(basak, tags={"amenity": "pharmacy"})
print("Pharmacy number:", len(pharmacy))
hospital = ox.geometries_from_place(basak, tags={"amenity": ["clinic","hospital"]})
print("Hospital number:", len(hospital))
fig, ax = plt.subplots(figsize=(10, 10))
buildloc.plot(ax=ax, color="grey")
pharmacy.plot(ax=ax, color="purple", markersize=5)
hospital.plot(ax=ax, color="red", markersize=5)
ox.plot_graph(graph, ax=ax, edge_color="black", node_color="none")
plt.tight_layout()
plt.show()

#Green Area Numbers
fltr_build = ox.geometries_from_place(basak, tags={"leisure": True})
green_areas = fltr_build[fltr_build["leisure"].isin(["park"])]
print("Green area number:", len(green_areas))
fig, ax = plt.subplots(figsize=(10, 10))
buildloc.plot(ax=ax, color="grey")
pharmacy.plot(ax=ax, color="purple", markersize=5)
hospital.plot(ax=ax, color="red", markersize=5)
green_areas.plot(ax=ax, color="green")
ox.plot_graph(graph, ax=ax, edge_color="black", node_color="none")
plt.tight_layout()
plt.show()

#Centroid Point
place_boundary = ox.geocode_to_gdf(basak)
neighborhood = place_boundary.geometry.values[0]
centroid = neighborhood.centroid
centroidx = centroid.x
centroidy = centroid.y
print("Centroid point coordinates:", centroidx,centroidy)

#Nearest Green_Area
centroid_node_id = ox.distance.nearest_nodes(graph, centroidx, centroidy)
green_areas_projected = green_areas.to_crs(epsg=32635)
green_x = float(green_areas_projected.geometry.centroid.x[0])
green_y = float(green_areas_projected.geometry.centroid.y[0])

close_green = None
close_distance = float('inf')

for road in graph.nodes():
    x_coordinate = graph.nodes[road]['x']
    y_coordinate = graph.nodes[road]['y']
    
    equation = math.dist((green_x,green_y),(x_coordinate,y_coordinate))
    distance = equation
    if distance < close_distance:
        closest_distance = distance
        close_green = road
    else:
        pass
route = nx.shortest_path(G=graph, source=centroid_node_id, target=close_green, weight='length')
fig, ax = ox.plot_graph_route(graph, route)

#Nearest Hospital
hospitals_projected = hospital.to_crs(epsg=32635)
hospital_x = float(hospitals_projected.geometry.centroid.x[0])
hospital_y = float(hospitals_projected.geometry.centroid.y[0])
closest_hospital = None
closest_distance = float('inf')
for road in graph.nodes():
    road_x = float(graph.nodes[road]['x'])
    road_y = float(graph.nodes[road]['y'])
    equaiton = math.dist((hospital_x,hospital_y),(road_x,road_y))
    distance = equaiton
    if distance < closest_distance:
        closest_hospital = road
        closest_distance = distance
    else:
        pass
route2 = nx.shortest_path(G=graph, source=centroid_node_id, target=closest_hospital, weight='length')
fig, ax = ox.plot_graph_route(graph, route2)
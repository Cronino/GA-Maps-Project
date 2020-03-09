
import pandas as pd
import requests
import datetime
import math
import polyline


def distance_api(start_lat, start_lon, travel_mode, end_lat, end_lon, rebuild_table):
    global logging_table
    global Origin
    global Destination

    # read in API key from local directory
    API_KEY = open('API_key.txt', 'r').read()

    Origin = str(str(start_lat) + ', ' + str(start_lon))
    Destination = str(str(end_lat) + ', ' + str(end_lon))

    # convert coordinates to encoded polyline to make url easier to parse
    origin_polyline = 'enc:' + polyline.encode([(start_lat, start_lon)], 5) + ':'
    destination_polyline = 'enc:' + polyline.encode([(end_lat, end_lon)], 5) + ':'

    google_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=' + origin_polyline + '&destinations=' + destination_polyline + '&key=' + API_KEY + '&mode=' + travel_mode

    google_request = requests.get(google_url)

    google_json = google_request.json()

    try:
        distance_text = google_json['rows'][0]['elements'][0]['distance']['text']


    except:
        distance_text = 'API ERROR'
        duration_text = 'API ERROR'
        duration_value = 0

    else:
        distance_text = google_json['rows'][0]['elements'][0]['distance']['text']
        duration_text = google_json['rows'][0]['elements'][0]['duration']['text']

        duration_value = google_json['rows'][0]['elements'][0]['duration']['value']

    result_list = [datetime.datetime.now(), Origin, Destination, distance_text, duration_text, duration_value,
                   travel_mode]

    if rebuild_table == 1:
        print('rebuilding logging_table')
        column_labels = ['runtime', 'Origin', 'Destination', 'distance', 'travel_time', 'duration_value', 'travel_mode']
        logging_table = pd.DataFrame(columns=column_labels)
        logging_table = logging_table.append(pd.Series(result_list, index=logging_table.columns), ignore_index=True)
    else:

        logging_table = logging_table.append(pd.Series(result_list, index=logging_table.columns), ignore_index=True)

    return (logging_table)


def circle_coords(start_lat, start_lon, distance, n_points):
    global coordinates_df

    R = 6378.1  # Radius of the Earth

    # create a dataframe to populate
    column_labels = ['i', 'bearing', 'distance', 'start_lat', 'start_lon', 'end_lat', 'end_lon']
    coordinates_df = pd.DataFrame(columns=column_labels)

    for i in range(0, n_points):
        brng = math.radians(i * (360 / n_points))  # convert bearing to radians
        lat1 = math.radians(start_lat)  # Current lat point converted to radians
        lon1 = math.radians(start_lon)  # Current long point converted to radians

        end_lat = math.degrees(math.asin(
            math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos((brng))))
        end_lon = math.degrees(lon1 + math.atan2(math.sin(brng) * math.sin(distance / R) * math.cos(lat1),
                                                 math.cos(distance / R) - math.sin(lat1) * math.sin(end_lat)))

        coords_list = [i + 1, i * (360 / n_points), distance, start_lat, start_lon, end_lat, end_lon]

        coordinates_df = coordinates_df.append(pd.Series(coords_list, index=coordinates_df.columns), ignore_index=True)

    return (coordinates_df)


def concentric_circles(split, start_latitude, start_longitude, number_points, distance):
    global coordinates_df_conc

    for i in range(1, distance + split):

        if i == 1:
            circle_coords(start_lat=start_latitude, start_lon=start_longitude, distance=i, n_points=number_points)
            coordinates_df_conc = coordinates_df

        else:
            circle_coords(start_lat=start_latitude, start_lon=start_longitude, distance=i, n_points=number_points)
            coordinates_df_conc = pd.concat([coordinates_df_conc, coordinates_df], ignore_index=True)

    return (coordinates_df_conc)


def data_for_map(start_latitude, start_longitude, number_points, distance):
    concentric_circles(split=1, start_latitude=start_latitude, start_longitude=start_longitude,
                       number_points=number_points, distance=distance)

    max_num = (number_points) * distance

    for i in range(1, max_num+1):
        coordinates_df_filtered = coordinates_df_conc[coordinates_df_conc.index == i]
        distance_api(start_lat=coordinates_df_filtered.iloc[0]['start_lat'],
                     start_lon=coordinates_df_filtered.iloc[0]['start_lon'], travel_mode='transit',
                     end_lat=coordinates_df_filtered.iloc[0]['end_lat'],
                     end_lon=coordinates_df_filtered.iloc[0]['end_lon'], rebuild_table=i)

        print(str(i) + ' of ' + str(max_num) + ' done!')

    logging_table.to_csv(str('./data_outputs/map_example_data_' + str(number_points) + '_' + str(distance) + '.csv'), index=False)
    return (logging_table)

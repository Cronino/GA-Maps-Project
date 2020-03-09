import pandas as pd
import numpy as np
import requests
import json
import datetime
from urllib.request import urlretrieve
from urllib.parse import urlencode
import tqdm

#!pip install polyline

import polyline

API_KEY = open('API_key.txt','r').read()

Origin = 'Monzo, Finsbury Square'
Destination = 'Epsom'
travel_mode = 'transit'

google_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=' + Origin + '&destinations=' + Destination + '&key=' + API_KEY + '&mode=' +travel_mode
google_request = requests.get(google_url)

google_json = google_request.json()
print(json.dumps(google_json, indent=2))
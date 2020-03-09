from urllib.request import urlretrieve
from urllib.parse import urlencode

import pandas as pd
import numpy as np
import requests
import json
import datetime
from urllib.request import urlretrieve
from urllib.parse import urlencode
import tqdm
import math

import polyline

API_KEY = open('API_key.txt','r').read()
import pandas as pd
import json
import datetime
import pytz
import numpy as np
import time
import matplotlib.pyplot as plt
import subprocess


def stream_data_coinbase_l2update(fpath, product_id):

	datas = []
	with open(fpath) as f:
		for n, line in enumerate(f):
			received_at, data = line.split("\t",1)
			received_at = datetime.datetime.strptime(received_at, '%Y-%m-%dT%H-%M-%S.%fZ')
			received_at = pytz.utc.localize(received_at)

			# Aux info (open, connect, disconnect, etc.)
			if data[0]!="{": continue

			data = json.loads(data)


			# Not expected product
			if not 'product_id' in data or data['product_id']!=product_id: continue


			if data['type'] == "l2update":
				data['time'] = datetime.datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
				data['time'] = pytz.utc.localize(data['time'])

			elif data['type']== "snapshot": 
				pass

			else:
				continue




			data['received_at'] = received_at

	
		
			yield data 



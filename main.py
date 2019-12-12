from common.dataloader import *
from common.orderbook import *
import datetime
import math

import matplotlib as mpl 
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import os
import pytz



def sym_log(x):
	if x>0:
		return math.log(1+x)
	else:
		return -math.log(1-x)


if __name__=="__main__":

	
	
	INITIAL_TIME = datetime.datetime(2019, 12, 3, 9, 10, 0, 0, tzinfo=pytz.UTC)
	FINAL_TIME   = datetime.datetime(2019, 12, 3, 9, 15, 0, 0, tzinfo=pytz.UTC)


	fpath = "data/raw_socket_capture_sample.json"

	product_id = "BTC-GBP"

	it = stream_data_coinbase_l2update(fpath, product_id = product_id)


	ob = OrderBook(decimal_places_price = 2, decimal_places_volume=8)



	prices = []



	timestamps = []
	idx_x = 0


	for n, elem in enumerate(it):


		# READ ORDERBOOK
		if elem['type'] == "snapshot":
			print("RESETTING")
			ob.reset(bids = elem['bids'], asks = elem['asks'])
			elem['time'] = np.nan
			continue

		elif elem['type']=="l2update":

			for _type, price, volume in elem['changes']:
				if _type=="buy": _type="bids"
				elif _type=="sell": _type="asks"

				ob.update(_type, price, volume)


		# We use 'receved_at' instead of 'time' since not all lines have the 'time' key 
		if elem['received_at']<INITIAL_TIME: 
			print("Skipping",elem['received_at'])
			continue
		if elem['received_at']>FINAL_TIME:
			print("Final timestamp reached")
			break
		###################


		timestamps.append(elem['time'])
		ob.remember_values()

		if n%100==0:
			print("%s" % (elem['time']))



	## Done, organize data in pandas dataframe

	total_depth, bids_mask = ob.get_depth_snapshot()
	total_depth.set_index(np.array(timestamps), inplace=True)
	bids_mask.set_index(np.array(timestamps), inplace=True)


	bids = (total_depth * bids_mask).iloc[:,::-1].cumsum(axis=1).iloc[:,::-1]
	asks = (total_depth * (1-bids_mask)).cumsum(axis=1)

	total_depth = bids+asks


	total_depth = total_depth.sort_index().transpose().sort_index().ffill()



	## Now let's plot total_depth



	# Concatenating colormaps
	# I also corrected the color code (green -> bids, red -> asks)
	top = plt.cm.get_cmap('Reds',2048)
	bottom = plt.cm.get_cmap('Greens',2048)
	newcolors = np.vstack(( top(np.linspace(1, 0, 2048)), bottom(np.linspace(0, 1, 2048))))
	cmap = mpl.colors.ListedColormap(newcolors)


	# Yes, you can apply vector operations here. No, it's not faster. Yes, I benchmarked it.
	# Yes, you can use a logaritmic color scale in pcolor_mesh. No, it won't work since we have negative values.
	# No, we cannot use the absolute value since we'd lose the color information (green/red).
	total_depth = total_depth.applymap(sym_log)


	X = total_depth.columns.tolist()
	Y = np.array(total_depth.index)
	
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)

	myFmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(myFmt)


	ax.pcolormesh(X, Y, np.array(total_depth), cmap = cmap, norm = plt.Normalize(-5,5))
	ax.set_ylim(5610,5660)




	ax.set_xlabel("Time (GMT)")
	ax.set_ylabel("Price")
	plt.show()


			














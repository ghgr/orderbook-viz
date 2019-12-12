import collections
import operator
import sys
import json
import time
import math
import numpy as np
import pandas as pd


class OrderBook:


	def __init__(self, decimal_places_price, decimal_places_volume):
		self.decimal_places_price = decimal_places_price
		self.decimal_places_volume = decimal_places_volume
		self.orderbook = {'bids' : {}, 'asks' : {}}
		self.resetted = False


		self.values = []
		self.bids_mask= []



	def update(self, _type, price, volume):
		assert self.resetted, "Order book not initialized from snapshot"
		price = int(price.replace(".",""))
		volume = int(volume.replace(".",""))
		
		self.orderbook[_type][price] = volume


	def reset(self, bids, asks):
		self.resetted = True
		for p,v in bids:
			self.update("bids",p,v)
		for p,v in asks:
			self.update("asks",p,v)

			
		
	def best_price_for_volume(self, _type, volume):
		if _type=="sell":
			data = sorted(list(self.orderbook['bids'].items()), key = operator.itemgetter(0), reverse=True)

		elif _type=="buy": 
			data = sorted(list(self.orderbook['asks'].items()), key=operator.itemgetter(0))
		else:
			raise Exception("_type must be either buy or sell")

		volume = int(volume*math.pow(10,self.decimal_places_volume))
		idx = np.array(data)[:,1].cumsum().searchsorted(volume)
		

		return data[idx][0]*math.pow(10,-self.decimal_places_price)


	def get_ticker(self, volume=0):
		bid = self.best_price_for_volume("sell", volume)
		ask = self.best_price_for_volume("buy", volume)
		return bid,ask



	def get_depth_snapshot(self):
		df = pd.DataFrame(self.values)
		df = df.transpose().sort_index().transpose()
		df_bids = pd.DataFrame(self.bids_mask)
		df_bids = df_bids.transpose().sort_index().transpose()
		return df, df_bids





	def forget_values(self):
		self.values = []
		self.bids_mask = []


	def remember_values(self):

		tmp = {} 
		bid_mask = {}
		for p,v in self.orderbook['bids'].items():
			tmp[p*math.pow(10,-self.decimal_places_price)] = v*math.pow(10,-self.decimal_places_volume)
			bid_mask[p*math.pow(10,-self.decimal_places_price)] = 1

		for p,v in self.orderbook['asks'].items():
			if p in tmp and tmp[p]>0: continue
			tmp[p*math.pow(10,-self.decimal_places_price)] = -v*math.pow(10,-self.decimal_places_volume)
			bid_mask[p*math.pow(10,-self.decimal_places_price)] = 0



		self.values.append(tmp)
		self.bids_mask.append(bid_mask)
		return True


	def __str__(self):


		asks = sorted(list(self.orderbook['asks'].items()), key=operator.itemgetter(0))
		bids = sorted(list(self.orderbook['bids'].items()), key = operator.itemgetter(0), reverse=True)



		LIM = 10

		for p,v in asks[LIM::-1]:
			print("%10.*f\t%15.*f" % (self.decimal_places_price, p*math.pow(10,-self.decimal_places_price), self.decimal_places_volume, v*math.pow(10,-self.decimal_places_volume)))


		print("""
			---------------
			ASKS
			

			BIDS
			---------------
		""")

		for p,v in bids[:LIM]:
			print("%10.*f\t%15.*f" % (self.decimal_places_price, p*math.pow(10,-self.decimal_places_price), self.decimal_places_volume, v*math.pow(10,-self.decimal_places_volume)))
		return ""



				
			

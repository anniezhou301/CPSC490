import requests
import json
import csv
import time
import re
import math
import datetime
import pandas as pd
from polygon import RESTClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



sub='wallstreetbets'
# before and after dates
# 1 Day = 86400 Seconds
stock_list = dict()
final_stock_list = list()
api_key = '15DVFB5L7UNEYA5R' #"add own api key here" #put your own API key here #
all_stock_jsons = dict()
daily_time_series_key = 'Time Series (Daily)'
blocked = ['MOON', 'HOLD', 'YOLO', 'FUCK', 'GAIN', 'BUY', 'THE', 'PUMP', 'BIG', 'ASAP', 'FOMO', 'BOYS', 'KING', 'CEO', 'IPO', 'ALL', 'ON', 'IT']
sia = SentimentIntensityAnalyzer()

# with open("raw_historical_stock_prices.json", "r") as read_file:
#     all_stock_jsons = json.load(read_file)
# with open("raw_reddit_stock_scraper.json", "r") as read_file:
#     final_stock_list = json.load(read_file)

def getPushshiftData(after, before, sub):
	url = 'https://api.pushshift.io/reddit/search/submission/?size=100&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)+'&sort=desc&sort_type=score'
	r = requests.get(url)
	try:
		data = json.loads(r.text)
		if 'data' not in data.keys():
			return []
		return data['data']
	except:
		print("skipped")
		return []
	

def extract_ticker(text):
	ticker_list = set(re.findall('\$?([A-Z]{2,4})', text))
	return ticker_list

def get_stock_info(date, stock):
	#check dict to see if it contains stock before calling
	if stock in all_stock_jsons.keys():
		#print("found:" + stock)
		if daily_time_series_key not in all_stock_jsons[stock].keys():
			return None
		if date in all_stock_jsons[stock][daily_time_series_key].keys():
			return 100*(float(all_stock_jsons[stock][daily_time_series_key][date]['4. close']) - float(all_stock_jsons[stock][daily_time_series_key][date]['1. open']))/float(all_stock_jsons[stock][daily_time_series_key][date]['1. open'])
		else:
			return None
	url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + str(stock) +'&outputsize=full&apikey=' + api_key
	r = requests.get(url)
	try:
		data = json.loads(r.text)

		# if data doesn't have time series return none
		if daily_time_series_key not in data.keys():
			blocked.append(key)
			return None
		# else 
			# save json in a dict
			# return open-close of the specific date
		#print(stock)
		all_stock_jsons[stock] = data
		if date in data[daily_time_series_key].keys():
			return 100*(float(data[daily_time_series_key][date]['4. close']) - float(data[daily_time_series_key][date]['1. open']))/float(data[daily_time_series_key][date]['1. open'])
		return None
	except:
		#print("skipped stock info part")
		return None

def update_file():
	amt = 0
	filename = 'data.csv'
	fields = ['stock name', 'text_length', 'num_comments', 'score', 'general sentiment', 'open/close percent change']
	with open(filename, 'w') as f:
		writer = csv.DictWriter(f, fieldnames = fields)
		writer.writeheader()
		date = ''
		for stock_dict in final_stock_list:
			for key, value in stock_dict.items():
				if key == 'day':
					date = str(value)
				else:
					if key in blocked:
						continue
					stock_info = get_stock_info(date, key)
					# if stock_info is none, don't write. is none if key is bad.
					if stock_info is None:
						continue
					print(str(amt) + ":" + str(key))
					amt += 1
					[f.write('{0},{1},{2},{3},{4},{5}\n'.format(key, value['text_length'], value['num_comments'], value['score'], 
						value['general_sentiment'], stock_info))]

def write_files():
	reddit_info = open("raw_reddit_stock_scraper.json", "w")
	jsonString = json.dumps(final_stock_list, default=str)
	reddit_info.write(jsonString)
	reddit_info.close()
	stock_info = open("raw_historical_stock_prices.json", "w")
	jsonString = json.dumps(all_stock_jsons, default=str)
	stock_info.write(jsonString)
	stock_info.close()

# record date : count of mentioned stocks each day on wsb
# compare that with open/close price each day of each stock
def scrape_reddit():
	start = "1618891200" # Apr 20 2021
	day = 86400
	for i in range(400): 
		print(i)
		final_stock_list.append({'day': datetime.date.fromtimestamp(int(start)+day)})
		end = str(int(start) + day)
		# print("getting data at start" + start + 'and end' + end)
		data = getPushshiftData(start, end, sub)
		# look at title/self text and parse for stock names
		stock_list = dict()
		for post in data:
			ticker_list = []
			if 'title' in post.keys():
				ticker_list.extend(extract_ticker(post['title']))
			if 'selftext' in post.keys():
				ticker_list.extend(extract_ticker(post['selftext'])) 
			# iterate through all tickers found in each post
			for ticker in ticker_list:
				if ticker[0] == '$':
					ticker = ticker[1:]
				if ticker not in stock_list.keys():
					stock_list[ticker]  = {'text_length': 0, 'num_comments': 0, 'score': 0, 'general_sentiment': 0}
				if 'selftext' in post.keys():
					stock_list[ticker]['text_length'] += len(post['selftext'])
				stock_list[ticker]['num_comments'] += post['num_comments']
				stock_list[ticker]['score'] += post['score']
				if 'selftext' in post.keys():
					# buy indicator - positive sentiment * score
					stock_list[ticker]['general_sentiment'] += (sia.polarity_scores(post['selftext'])['pos']-sia.polarity_scores(post['selftext'])['neg']) * post['score']
		final_stock_list.append(stock_list)
		start = str(int(start) - day)

scrape_reddit()
update_file()
#write_files() # documenting the data sources used
	


		
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

scaler = StandardScaler()  
df = pd.read_csv("data.csv", names=['stock name', 'text_length', 'num_comments', 'score', 'general sentiment', 'open/close percent change'], skiprows = 1, header = None)
features = ['text_length', 'num_comments', 'score', 'general sentiment']

most_discussed = df.iloc[:, 0].value_counts()[:20]
print(most_discussed)

def filter_by_stock(stock):
	# returns (training, target) that only has a certain stock
	x = []
	y = []
	for index, row in df.iterrows():
		if row[0] == stock:
			x.append([row[1], row[2], row[3], row[4]])
			if row[5] > 0:
				y.append(1)
			else:
				y.append(0)
	return np.array(x), np.array(y)

def train_and_score(stock):
	x, y = filter_by_stock(stock)
	x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

	scaler.fit(x_train)  
	x_train = scaler.transform(x_train)
	x_test = scaler.transform(x_test) 

	clf = MLPClassifier(hidden_layer_sizes=100, activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=10000).fit(x_train, y_train)
	print(stock + ':')
	print(clf.score(x_test, y_test))



train_and_score('GME')
train_and_score('AMC')
train_and_score('DD')
train_and_score('PLTR')
train_and_score('BB')
train_and_score('TSLA')
train_and_score('AAPL')
train_and_score('MSFT')
train_and_score('AMZN')


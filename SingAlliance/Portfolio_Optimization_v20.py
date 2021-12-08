# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 15:27:12 2021

@author: rmili
"""
"""
Assumptions and Other Relevant Information:
    1) execution of this .py file has been tested successfully in both Windows 10 and Ubuntu 20.04.2.0 (with Virtual Box)
    2) the timezone for the trades is assumed to be GMT+0
    3) each portfolio's weight is bounded by 0 and 1 and the constraint for optimiation is that weights of all market sum up to one
    4) 1-year Singapore government bond yield is used as the proxy for risk free rate
    5) all returns are expressed in log terms
    6) during the looping over the days between the user-defined start time and end time,
    which is 2021-10-01 0:0:0 to 2021-10-31 23:00:0,
    each hourly interval is represented by the beginning of the time period , i.e.  the hour ending at 23:00:00 is represented by 22:00:00
    7) Outputs are saved in the same directary of this .py file. 
    8) When saving the outputs in point 7), finding the path of the parent directory is expected to work in both Windows and Linux
    9) simulations are used to plot efficient frontiers, and the number of simulation runs is arbitrarily defined as 30000
    10) output of returns and weights for optimization can be found in the same directory in Github
    11) efficient frontier graph is provided can be found in the same directory in Github
  
    
"""


import time
import hmac
from requests import Request
import requests
from urllib.request import urlopen
import json
import time, os
import pandas as pd
import numpy as np
from scipy.optimize import minimize 
import math
import matplotlib.pyplot as plt
import ntpath
import os

#1) connection and authentication

# 2) configuration of parameters


api_endpoint = 'https://ftx.com/api'
lst_market = ['BTC-PERP','ETH-PERP','ADA-PERP']



end_time = '1635721200'#Epoch time for 2021-10-31 23:00:00.000000' 
start_time = '1633046400' # Epoch time for 2021-10-01 00:00:00.000000' ,
#format of the timestamp , to be used to convert the timestamp to epoch time
p = "%Y-%m-%d %H:%M:%S.%f"   
#use the latest 1-year Singapore government bond yield as the risk-free_rate 
#need to convert the publicly available arithmetic return to log returns
#taking logarithm of the arithmatic return
risk_free_rate = 0.00425
risk_free_rate = math.log(risk_free_rate +1)
simulation_runs = 30000
#the following api key and api secret both belongs to Hillary's account 
api_key = 'Q_3Y2JNEb1JJjLz5cCGe8gKon1kl4XGp4qrMVNKC'
api_secret = 'kY_qDn4dXGUt96iJPCmIcsKRZ6tCKq7RshslrocV'

ts = int(time.time() * 1000)

request = Request('GET', api_endpoint)
prepared = request.prepare()
signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
signature = hmac.new(api_secret.encode(), signature_payload, 'sha256').hexdigest()

request.headers['FTX-KEY'] = api_key
request.headers['FTX-SIGN'] = signature
request.headers['FTX-TS'] = str(ts)




def convert_time_to_epoch(time_to_convert):
    epoch_time = int(time.mktime(time.strptime(time_to_convert,p)))
    return epoch_time


def retrieve_json_data(a_market, the_end_time, the_start_time):
    url = f'https://ftx.com/api/markets/{a_market}/trades'
    params_time_frame = {
                    'end_time': the_end_time,
                    'start_time': the_start_time,
                }
    response = requests.get(url, params=params_time_frame)
    json_obj = response.json()
    
    return json_obj


def extract_data_from_dictionary(a_dictionary):
    #extract the only two useful information: 'price' and 'time'
    return a_dictionary['time'], a_dictionary['price']
    
    
    
def transform_time_data_string(time_string):

    return time_string[0:14] +"00:00.000000"
    
    
    
list_all_market_data = []     
for m in lst_market:  
    
    list_each_market_data = []
    #for each market, retreive the data over the period starting from the start date and end date
    #step is 3600 seconds to account for one-hour interval
    # adding 1 inside (int(end_time)-3600 + 1 => reason is to make sure the end_time wont be skipped in the for loop
    for epoch in range(int(start_time), (int(end_time)-3600 + 1), 3600):
        #epoch below is to be parsed to retrieve_json_data() as the end time
        #iteration of epochs starts from the beginning of all hourly interval starting from Oct 1 0am
        #given the above two points, epoch needs to be added with 3600
        epoch += 3600
        #convert epoch into human-readable time in GMT
        
        human_epoch = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(epoch))
        #as epoch is iteraing, using the dummy_end_time variable to extract data from the latest one hour ending at the epoch 
        calculated_start_time = epoch - 3600
       
        list_result = retrieve_json_data(m, str(epoch), str(calculated_start_time))
        list_result = list_result.get('result')
         # loop through all dictionary in the list for 'result'
        time_data = []
        price_data = []
        
            
        for a_dictionary in list_result:
            a_time_data, a_price_data = extract_data_from_dictionary(a_dictionary)
            # the output will be appended as a list
            # the output will apply to both 'time' and 'price'
            time_data.append(a_time_data)
            price_data.append(a_price_data)
    
            #get the last price and timestamp from each one hour interval, similar to studying closing price for each trade dya
            #however, for some reason, the last price is the first element of the retrieved time series
        last_time_data = time_data[0]
        last_price_data = price_data[0]
    
        #for each epoch, there is only one data point representing the last traded time and price
        time_price_data_combined = {"time": last_time_data, f"price_{m}": last_price_data}
        list_each_market_data.append(time_price_data_combined)
        #convert the list into a dataframe
        #as dataframe is easier to be merged in subsequent steps
        df_each_market_data = pd.DataFrame(list_each_market_data)
        
        #convert each timestamp in the time column into the format that shows 0 for minute, seconds and microseconds
        #the purpose is to allowe for easier merging across markets later
        df_each_market_data['time'] = df_each_market_data['time'].map(transform_time_data_string)
        #set the time column as index
        df_each_market_data.set_index('time',inplace = True)
        
        #note that due to slight differences in the trade time,which is on a magni ude of microseconds
#to represent the hourly trade data, only date, and hour information is extracted
#the objective is to allow for easier merging of the time series for the 3 different markets
               
        
    #compile the hourly closing price for each market into one list with a length of 3    
    list_all_market_data.append(df_each_market_data)            
    
            
    
#merge twice
pd_merged_1_2 = pd.merge(list_all_market_data[0], list_all_market_data[1], left_index=True, right_index=True)
pd_all_markets = pd.merge(list_all_market_data[2], pd_merged_1_2,  left_index=True, right_index=True)


#Calculate hourly log return
pd_all_markets_returns = np.log(pd_all_markets).diff()
#calculate volatility based on the  1-hour data for each market over the user-specified time frame
series_all_markets_std_deviation = pd_all_markets_returns.std()

#calculate varaiancde-covariance matrix for the 3 markets
cov_matrix = pd_all_markets_returns.cov()
#formulate the covraince of the portfolio based on the cov_matrix and weights of each market
    
def objective_maximization(weights):
    #double summing of  cov_matrix_weighted so that  all elements are summed up
    std_weighted = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) 
      
     #calculate mean return based on the  1-hour data for each market over the user-specified time frame
    series_all_markets_average_returns = pd_all_markets_returns.mean()
    
     #weighted_average_return is the element-wise multiplication of weighjts and returns of each market
    weighted_average_return = sum(weights* series_all_markets_average_returns)
#     
     #find out the weights for each of the 3 markets to optimise portfolio performance on a risk-adjusted return basis
#     
     #ultimiate goal is to maxmize weighted_average_return/std_weighted or alternatively minize the negative of weighted_average_return/std_weighted
    ultimate_goal = -weighted_average_return/std_weighted
#     
#     
    return ultimate_goal

#constriants for optimizing portfolios is that the sum of respective weights is one
def constraints1(weights):
    return weights[0]+weights[1]+weights[2] - 1
    
#while in theory short positions should be allowed, it might be better to constrain the weights to between 0 and 1
bnds = ((0,1),(0,1),(0,1))


#portfolio perforemance is annualized
def calculate_portfolio_performance(weights):

    # 252 needs to be multipled with 24 since every year has 252 trading days and each day has 24 hours
    # and the ttrading data is on hourly interval
    std_weighted = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252*24)
    
    
     #calculate mean return based on the  1-hour data for each market over the user-specified time frame
    series_all_markets_average_returns = pd_all_markets_returns.mean()
     #weighted_average_return is the element-wise multiplication of weighjts and returns of each market
    weighted_average_return = np.sum(weights* series_all_markets_average_returns)*252*24

    
    
      
    return std_weighted,weighted_average_return

def random_portfolios():
    #the first dimension is 3 because 3 elements will be calculated for the results
    #namely portofolio standard deviation, portfolio return, and portfolio Sharpe ratio
    results = np.zeros((len(lst_market),simulation_runs))
    weights_record = []
    for i in range(simulation_runs):
        #use random function to randomly generate a set of weights for each of the market
        weights = np.random.random(len(lst_market))
        #need to make sure each market's weight sums up to one
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_std_dev, portfolio_return = calculate_portfolio_performance(weights)
        results[0,i] = portfolio_std_dev
        results[1,i] = portfolio_return
        results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
    return results, weights_record

#draw the efficient frontier
def display_efficient_frontier_with_random(lst_weights_for_optimiation,filename_graph_efficient_frontier):
    results, weights_record = random_portfolios()
        
    plt.figure(figsize=(10, 7))
    plt.scatter(results[0,:],results[1,:],c=results[2,:],cmap='YlGnBu', marker='o', s=10, alpha=0.3)
    plt.colorbar()
    plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
    plt.xlabel('annualised volatility')
    plt.ylabel('annualised returns')
    plt.legend(labelspacing=0.8)
    #save the plot to a  png file in the relative path
    plt.savefig(filename_graph_efficient_frontier)

# intialize weights for weight_ADA , weight_BTC , weight_ETH in the same order
initial_values = [0.1,0.3,0.6]
#solution is the list of weights that maxmize the objective
cons = {'type':'eq', 'fun': constraints1}
solution = minimize(objective_maximization,initial_values, \
                    method = 'SLSQP',\
                    constraints = cons,\
                    bounds = bnds)
weights_for_optimiation = {"ADA-PERP": solution.x[0], 
                           "BTC-PERP": solution.x[1] , 
                           "ETH-PERP": solution.x[2],                            
                           }
pd_weights_for_optimiation = pd.DataFrame(weights_for_optimiation.items())
#draw efficient frontier with randomly generated portfolio weights
#convert the dictionary to a list of values for parsing to the  function below
values = weights_for_optimiation.values()
lst_weights_for_optimiation = list(values)


#get the path of the parent directory, expected to work with both Windoes and Linux
dirname = ntpath.dirname(__file__)
filename_prices = os.path.join(dirname, 'all-prices-Oct21.csv')
filename_returns = os.path.join(dirname, 'all-returns-Oct21.csv')
filename_weights_for_optimization = os.path.join(dirname, 'weights-optimization-Oct21.csv')
filename_graph_efficient_frontier = os.path.join(dirname, 'efficient_frontier-Oct21.png')

#draw efficient frontier
display_efficient_frontier_with_random(lst_weights_for_optimiation, filename_graph_efficient_frontier)


#output the compiled price data, calculated returns, as well as weight for optimization for each of the 3 markets into  CSV files    
pd_all_markets.to_csv(filename_prices)
pd_all_markets_returns.to_csv(filename_returns)
pd_weights_for_optimiation.to_csv(filename_weights_for_optimization)

#output weights_for_optimiation in csv file as well
#use relative path

    

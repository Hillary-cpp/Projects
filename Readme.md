Project: 
Portfolio Optimization for a 3 digital asset portfolio - Coding challenge for the role of research/trading engineer at SingAlliance 

Author: Zhang Liming (Hillary)

Description:
1. This projects sets out to construct an optimal portfolio of 3 digital assets, namely perpetual futures in BTC, ETH, and ADA. Following are the corresponding terms used: 'BTC-PERP','ETH-PERP','ADA-PERP'.

2. The appraoch taken to achieve the optimization is as follows:
   1) retrieve historical hourly price data from Oct 1 0am to Oct 31 23pm from  'https://ftx.com/api'.
   2) calculate mean returns and hourly standard deviation for each of the aforementioned assets. 
   3) use sci-py optimizer to find out the weights that should be assigned to each assets in order to achieve a maximum ratio of portfolio return to portfolio standard deviation. 
   4) variance-covariance matrix is used in the calculation
   5) when attempting to draw efficient frontier, 30000 simulation runs have been executed. 
   5) interim and final outputs were generated, including:
       i. output of hourly closing prices, and log returns for the aformentioned period as a CSV file 
       ii. output of the weights to be used to achieve an optimum portfolio as a CSV vile
       iii. output of the efficient frontier as a png file.

3. Assumptions and Other Relevant Information:
    1) both the execution of the.py file (Portfolio_Optimization_v20) and its output has been tested successfully in both Windows 10 Home edition (Python version: 3.8) and Ubuntu 20.04.2.0 (with Virtual Box) (Python version: 3.8.10)
    2) the timezone for the trades is assumed to be GMT+0
    3) each portfolio's weight is bounded by 0 and 1 and the constraint for optimiation is that weights of all market sum up to one
    4) 1-year Singapore government bond yield is used as the proxy for risk free rate
    5) all returns are expressed in log terms
    6) during the looping over the days between the user-defined start time and end time,
    which is 2021-10-01 0:0:0 to 2021-10-31 23:00:0, each hourly interval is represented by the beginning of the time period , i.e.  the hour ending at 23:00:00 is represented by 22:00:00
    7) Outputs are saved in the same directary of this .py file. 
    8) When saving the outputs in point 7), finding the path of the parent directory could work in both Windows and Linux
    9) simulations are used to plot efficient frontiers, and the number of simulation runs is arbitrarily defined as 30000
    10) output of returns and weights for optimization can be found in the same directory in Github
    11) efficient frontier graph is provided can be found in the same directory in Github
  
  

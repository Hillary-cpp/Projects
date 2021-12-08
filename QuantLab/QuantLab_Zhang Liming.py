import pandas as pd
import numpy as np
import os.path


#the following various methods will do all necessary data processing for a given ticker
def process_trade_data(df, the_ticker): 

    def find_max_time_gap_for_ticker(df, ticker_name):
        
        lst_indx = np.where(df["Symbol"]==ticker_name)[0].tolist()
        
        if len(lst_indx) <= 1:
            #if there is only one trade for the given ticket
            max_time_gap = 0
        else:
            lst_all_values = []
            #if there are multiple trades  for the given ticket
            for i in range(0, len(lst_indx)-1):
                
                start_indx = lst_indx[i]
                end_indx = lst_indx[i+1]
                
                start_value = df.iloc[start_indx,0]
                end_value = df.iloc[end_indx,0]
                difference_value = end_value - start_value
                
                lst_all_values.append(difference_value)
            max_time_gap = max(lst_all_values)
            
        print("maximum time gap is" + str(max_time_gap))
        return max_time_gap
     
    def find_total_volume(df,ticker):
        #df.groupby([ticker])['Age'].sum().reset_index()    
        return df.loc[df["Symbol"] == ticker, 'Quantity'].sum()
        
    def find_max_price(df,ticker):
        #df.groupby([ticker])['Age'].sum().reset_index()    
        return df.loc[df["Symbol"] == ticker, 'Price'].max()
        
    def find_weighted_avg_price_for_ticker(df, ticker_name):
          
        lst_indx = np.where(df["Symbol"]==ticker_name)[0].tolist()
        
        if len(lst_indx) <= 0:
            #if there is only one trade for the given ticket
            weighted_avg_price = 0
        else:
            lst_all_numerator = []
            lst_all_denominator = []
            #if there are multiple trades  for the given ticket
            for i in range(0, len(lst_indx)):
                
                the_indx = lst_indx[i]
                
                
                quantity_value = df.loc[the_indx,'Quantity']
                price_value = df.loc[the_indx,'Price']
                numerator = quantity_value*price_value
                
                lst_all_numerator.append(numerator)
                lst_all_denominator.append(quantity_value)
            sum_numerator = sum(lst_all_numerator)
            sum_denominator = sum(lst_all_denominator)
            weighted_avg_price = sum_numerator/sum_denominator
        print("weighted average price is" + str(weighted_avg_price))
    
        return weighted_avg_price  
       
    
    
    
    max_time_gap = find_max_time_gap_for_ticker(df, the_ticker)
    total_volume = find_total_volume(df, the_ticker)
    max_price = find_max_price(df, the_ticker)
    weighted_avg_price = find_weighted_avg_price_for_ticker(df, the_ticker)
    
    return max_time_gap, int(total_volume), int(max_price), int(weighted_avg_price)




#this secion is for reading input, processing the input in a loop over all unique symbols, 
#and write the output

#assuming input is under the same parent folder
dirname = os.path.dirname(__file__)
filepath_input = os.path.join(dirname, 'input.csv')
df = pd.read_csv(filepath_input)
#assign column names to the raw df
#<TimeStamp>,<Symbol>,<Quantity>,<Price>
df.columns = ["TimeStamp", "Symbol", "Quantity","Price"]



list_unique_tickers = df["Symbol"].unique()
list_dict_all_tickers = []
#build output as dictionaries, list of dictionaries, and then dataframe
for the_ticker in list_unique_tickers:
    row_string =""
    max_time_gap, total_volume, max_price, weighted_avg_price = process_trade_data(df, the_ticker)
    dicts = {}
    keys = range(5)
    titles = ["symbol", "MaxTimeGap","Volume","WeightedAveragePrice","MaxPrice"] 
    values = [the_ticker, max_time_gap, total_volume,  weighted_avg_price,max_price]
    for i in keys:
        dicts[titles[i]] = values[i]
    #print(dicts)
    #list_dict_all_tickers is a list of dictionaries, where each row is represented by a dictionary which will be mapped to multiple columns in the output csv file
    list_dict_all_tickers.append(dicts)
    
df_output_dict = pd.DataFrame(list_dict_all_tickers)

#output to the same parent folder
filepath = os.path.join(dirname, 'output.csv')
df_output_dict.sort_values('symbol', inplace= True)
df_output_dict.reset_index(drop=True, inplace=True)

def concat_each_row(row):
    to_return = row['symbol'] + "," + str(row["MaxTimeGap"]) + "," +\
            str(row["Volume"]) + "," + str(row["WeightedAveragePrice"]) + ","+ \
            str(row["MaxPrice"] )
    print(to_return)
    return to_return

#apply the required format on the output
#which is a long string that are comma-seperated
df_output = df_output_dict.apply(lambda row: concat_each_row(row) , axis = 1)
#remove index and save the output
df_output.to_csv(filepath,index=False,header= False)        

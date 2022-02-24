'''
Purpose: This script will loop through various averages (short_moving_averages and long_moving_averages) in an array
        to run tests against the moving average cross strategy and calculate the outcome if this strategy is used to trade.

API: The API used is here: https://www.coingecko.com/en/api/documentation using the "market_chart" endpoint

'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import math
import datetime
import time

#
#   Adjustable vars
#
'''
Adjustable Vars Desc:

trend_ma_length                 - used to calculate a trend direction
stop_loss_percent               - used to set a stoploss for a transaction to get out of the trade if it goes too far in the wrong direction
ma_split_percent_setting        - used to use a specific distance between two moving averages before entering a trade. Used to prevent trading when price action is flat
prev_trade_price_adj            - used to not allow a trade if a trade in one direction was closed but a signal to open a new trade in the same direction unless the price has changed enough since the inital trade
detailed_output                 - flag used to switch text output to show each transaction versus a summary of the trades (0 = details, 1 = summary)
short_moving_averages           - used in conjunction with long_moving_averages. The short, or fast, moving average is an averge of x number of days. IE short 9 and long 50. 
long_moving_averages            - used in conjunction with short_moving_averages. The long, or slow, moving average is an averge of x number of days. IE short 9 and long 50. 
symbol                          - crypto symbol used for the API. Check documentation for symbols available at the "/coins/list" endpoint.
no_of_interval                  - how far back the process should go based on the interval. IE if  no_of_interval = 50 and interval = 'daily', then it goes back 50 days from current date.
                                     no_of_interval note from API documentation:
                                    * Minutely data will be used for duration within 1 day, Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
interval                        - The time frame used in query (Values available: Minutely, Hourly, Daily)
currency                        - national currency.

'''
'''
ma_split_percent_setting_arr = [.01, .02, .03]
stop_loss_percent_arr = [.03, .04, .05, .06, .07]
trend_ma_length = [3, 6, 9]
short_moving_averages = [5, 8, 9, 13, 21, 34]
long_moving_averages = [21, 34, 50, 55, 89, 144]

'''

ma_split_percent_setting_arr = [.01]
stop_loss_percent_arr = [.05]
trend_ma_length = [2]
short_moving_averages = [9]
long_moving_averages = [50]


prev_trade_price_adj = 0.01
detailed_output = 1
symbol = 'bitcoin'
no_of_interval  = '420'
interval = 'daily'
currency = 'usd'
max_profit = 0.0
# 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377 
#
#   API call
#
api_url = 'https://api.coingecko.com/api/v3/coins/' + symbol + '/market_chart?vs_currency=' + currency + '&days=' + no_of_interval + '&interval=' + interval
price_data_array = requests.get(api_url).json()

per_setting_arr_len = len(ma_split_percent_setting_arr) - 1
per_setting_ctr = 0

while per_setting_ctr <= per_setting_arr_len:

    ma_split_percent_setting = ma_split_percent_setting_arr[per_setting_ctr]

    sl_arr_len = len(stop_loss_percent_arr) - 1
    sl_arr_ctr = 0

    while sl_arr_ctr <= sl_arr_len:

        stop_loss_percent = stop_loss_percent_arr[sl_arr_ctr]

        tml = len(trend_ma_length) - 1
        ctr = 0

        while ctr <= tml:

            cnt = 0
            ma_cnt = len(short_moving_averages) - 1

            while cnt <= ma_cnt:

                # reset vars
                long_ma_length = long_moving_averages[cnt]
                short_ma_length = short_moving_averages[cnt]
                investment_amt = 10000.00
                inital_investment_amt = investment_amt
                trade_cnt = 0
                buy_cnt = 0
                short_cnt = 0
                buy_stoploss_cnt = 0
                short_stoploss_cnt = 0
                buy_exit_cnt = 0
                short_exit_cnt = 0
                stop_loss_price = 0.00
                bought_price = 0.00
                first_bought_price = 0.00
                ma_split_percent = 0.00
                no_of_units = 0.00
                prev_trade_signal = ""
                prev_trade_price = 0.00
                ma_slow = []
                ma_fast = []
                trend_ma = []
                trend  = ""

                #
                #   Loop throught data
                #
                for prices in price_data_array['prices']:

                    trend_ma_total = 0
                    trend_ma_avg = 0
                    trend_ma_base = 0
                    trend_percent = 0.0
                    ma_slow_avg = 0
                    ma_fast_avg = 0
                    curr_price = prices[1]
                    price_date = prices[0]
                    ma_fast_total = 0
                    ma_slow_total = 0
                    
                    # below will show the file date and time formate like: 06 Feb 2022
                    epoch_date = str(price_date)
                    epoch_date = epoch_date[:10]
                    time_formatted = time.strftime('%d %b %Y', time.localtime(int(epoch_date)))

                    #
                    # calculate TREND moving avg
                    #
                    if len(trend_ma) == trend_ma_length[ctr]:
                        # remove first element
                        trend_ma.pop(0)

                    # add new value to end of array
                    trend_ma.append(curr_price)

                    if  len(trend_ma) == trend_ma_length[ctr]:
                        trend_ma_base = trend_ma[0]
                        for i in trend_ma:
                            trend_ma_total = trend_ma_total + i

                        trend_ma_avg = trend_ma_total / trend_ma_length[ctr]
                        trend_percent = trend_ma_avg / trend_ma_base 

                    #
                    # calculate SLOW MA
                    #
                    if len(ma_slow) == long_ma_length:
                        # remove first element
                        ma_slow.pop(0)

                    # add new value to end of array
                    ma_slow.append(curr_price)
                    
                    if  len(ma_slow) == long_ma_length:
                        for i in ma_slow:
                            ma_slow_total = ma_slow_total + i

                        ma_slow_avg = ma_slow_total / long_ma_length

                    #
                    # calculate FAST MA
                    #
                    if len(ma_fast) == short_ma_length:
                        # remove first element
                        ma_fast.pop(0)

                    # add new value to end of array
                    ma_fast.append(curr_price)

                    if len(ma_fast) == short_ma_length:
                        for i in ma_fast:
                            ma_fast_total = ma_fast_total + i

                        ma_fast_avg = ma_fast_total / short_ma_length 

                    #
                    # wait until averages have values. Once we have enough data to calc moving averages then 
                    # review the data for signals
                    #
                    if ma_fast_avg > 0.00000000000000000001 and ma_slow_avg > 0.00000000000000000001:
                        #
                        #   Calculate MA separation distance percent
                        #
                        if ma_slow_avg > ma_fast_avg :
                            ma_split_percent = (ma_slow_avg - ma_fast_avg) / ma_slow_avg
                        else:
                            ma_split_percent = (ma_fast_avg - ma_slow_avg) / ma_fast_avg
                        
                        #
                        #   Exit postions
                        #
                        # Exit LONG positions
                        if (trend == "LONG" and ((curr_price < stop_loss_price) or (curr_price < ma_slow_avg)) and stop_loss_price != 0.00):
                            if (curr_price <= stop_loss_price):
                            # stop loss triggered
                                trend = "LONG - STOP LOSS"
                                investment_amt = no_of_units * stop_loss_price
                                buy_stoploss_cnt += 1

                            elif (curr_price <= ma_slow_avg):
                            # exit long signal
                                trend = "EXIT LONG"
                                investment_amt = no_of_units * curr_price
                                buy_exit_cnt += 1

                            prev_trade_signal = trend
                            prev_trade_price = curr_price
                            stop_loss_price = 0.00

                            if detailed_output == 1:
                                print(print(str(time_formatted), " Curr Price: ", str(curr_price),  "Investment Amt: ", investment_amt, "-", trend))

                        # Exit SHORT positions
                        elif (trend == "SHORT" and ((curr_price > stop_loss_price) or (curr_price > ma_slow_avg)) and stop_loss_price != 0.00):
                            if (curr_price >= stop_loss_price):
                            # stop loss triggered
                                trend = "SHORT - STOP LOSS"
                                investment_amt = (no_of_units * (bought_price - stop_loss_price)) + investment_amt
                                short_stoploss_cnt += 1 

                            elif (curr_price >= ma_slow_avg):
                            # short exit
                                trend = "SHORT EXIT"
                                investment_amt = (no_of_units * (bought_price - curr_price)) + investment_amt
                                short_exit_cnt += 1

                            prev_trade_signal = trend
                            prev_trade_price = curr_price
                            stop_loss_price = 0.00

                            if detailed_output == 1:
                                print(str(time_formatted), " Curr Price: ", str(curr_price),  "Investment Amt: ", investment_amt, "-", trend)

                        #
                        #    Enter positions
                        #
                        if ((ma_fast_avg > ma_slow_avg and curr_price > ma_slow_avg and trend != "LONG" and trend != "SHORT")  and trend_percent >= 1 and ma_split_percent >= ma_split_percent_setting):
                        # LONG price moved above slow avg

                            prev_trade_price =  prev_trade_price + (prev_trade_price * prev_trade_price_adj)
                            if ((prev_trade_signal == "LONG - STOP LOSS" or prev_trade_signal == "EXIT LONG") and curr_price > prev_trade_price) or (prev_trade_signal != "LONG - STOP LOSS" and prev_trade_signal != "EXIT LONG"):
                                bought_price = curr_price
                                stop_loss_price = curr_price - (curr_price * stop_loss_percent) 
                                trend = "LONG"
                                
                                # get number of units (shares/coin) bought
                                no_of_units = investment_amt / curr_price
                                buy_cnt += 1
                            
                                if detailed_output == 1:
                                    print (time_formatted, 
                                    "Curr Price: ", curr_price,
                                    trend)                  

                        elif ((ma_fast_avg < ma_slow_avg and curr_price < ma_slow_avg and trend != "SHORT" and trend != "LONG") and trend_percent < 1 and ma_split_percent >= ma_split_percent_setting):
                        # SHORT price moved below slow avg

                            prev_trade_price =  prev_trade_price - (prev_trade_price * prev_trade_price_adj)
                            if ((prev_trade_signal == "SHORT - STOP LOSS" or prev_trade_signal == "SHORT EXIT") and curr_price < prev_trade_price) or (prev_trade_signal != "SHORT - STOP LOSS" and prev_trade_signal != "SHORT EXIT"):
                                bought_price = curr_price
                                stop_loss_price = curr_price + (curr_price * stop_loss_percent)
                                trend = "SHORT"

                                # get number of units (shares/coin) shorted
                                no_of_units = investment_amt / curr_price
                                short_cnt +=1

                                if detailed_output == 1:
                                    print (time_formatted, 
                                    "Curr Price: ", curr_price,
                                    trend) 


                # print totals
                if detailed_output == 0:
                    if max_profit < investment_amt:
                        max_profit = investment_amt

                    trade_cnt = buy_cnt + short_cnt + buy_stoploss_cnt + short_stoploss_cnt + buy_exit_cnt + short_exit_cnt
                    print("Symbol:", symbol )
                    print("Time back:", no_of_interval, interval, "iterations")
                    print("Moving Avg:", short_ma_length, "/", long_ma_length )
                    print("trend_ma_length:", trend_ma_length[ctr])
                    print("stop_loss_percent", stop_loss_percent_arr[sl_arr_ctr])
                    print("ma_split_percent_setting: ", ma_split_percent_setting)
                    print("Inital_investment_amt:", '{0:.2f}'.format(inital_investment_amt), "  Final Investment Amt:", '{0:.2f}'.format(investment_amt), "  Investment Growth:", '{0:.2f}'.format((investment_amt / inital_investment_amt) * 100), "%")
                    print("Total Trades:", trade_cnt )
                    print("buy_cnt:", buy_cnt, " short_cnt:", short_cnt, " buy_stoploss_cnt:", buy_stoploss_cnt,
                    " short_stoploss_cnt:", short_stoploss_cnt, " buy_exit_cnt:", buy_exit_cnt, " short_exit_cnt:", short_exit_cnt)
                    print("")

                # inc loop cnt
                cnt += 1
            ctr += 1
        sl_arr_ctr += 1
    per_setting_ctr += 1



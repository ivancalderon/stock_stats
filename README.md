# stock_stats
Stock's price data mining application<br>
This script aims to download stocks price data and render an interactive dashboard with
useful trading information such as probability of getting a high or a low in the first 15, 30 or 60 minutes of action,
expected range in each day of the week, and alike.<br>
The data source is www.alphavantage.co As is stated in that website, you need to get  your own  free API key.<br>
The requierments are Python 3.5+, numpy, pandas, requests, plotly and dash, as well as other packages included in the
standard library such as os, asyncio, datetime, json and subprocess.<br>
To get the script working, please replace "YOURKEY" in line 27 of the get_data.py file with your own API key.<br>
Please read the license before using the script. You can contact me at ivancalderonrodriguez@gmail.com<br>

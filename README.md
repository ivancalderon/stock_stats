# stock_stats
Stock's price data mining application
This scripts aims to download stocks price data and render an interactive dashboard with
useful trading information such as probability of getting a high or a low in the first 15, 30 or 60 minutes of action,
expected range in each day of the week, and alike.
The data source is www.alphavantage.co As is stated in the website, you need to get a free API key.
The requierments are Python 3.5+, numpy, pandas, requests, plotly and dash, as well as other packages included in the
standard library such as os, asyncio, datetime, json and subprocess.
To get the script working, please replace "YOUR API KEY" in the 5 line of the get_data.py file with your own API key
Please read the license before using the script.

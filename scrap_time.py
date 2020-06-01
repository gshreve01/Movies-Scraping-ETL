import datetime
your_timestamp = 851866703
date = datetime.datetime.fromtimestamp(your_timestamp / 1e3)
print(date)


timestamp = "1331380058000"
your_dt = datetime.datetime.fromtimestamp(int(timestamp)/1000)  # using the local timezone
print(your_dt.strftime("%Y-%m-%d %H:%M:%S"))  # 2018-04-07 20:48:08, YMMV
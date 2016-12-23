import pandas as pd
import datetime
import matplotlib.pyplot as plt
import forecastio
from pvlib.forecast import GFS

#latitude, longitude = 32.2, -110.9

latitude = -31.601
longitude = -56.813
altitude = 160
timezone = 'Etc/GMT+3'
#timezone = 'US/Arizona'

start = pd.Timestamp(datetime.date.today(), tz=timezone)
end = start + pd.Timedelta(days=7)

model=GFS()
raw_data = model.get_data(latitude, longitude, start, end)


data = model.process_data(raw_data)

cloud_vars = ['total_clouds', 'low_clouds','mid_clouds', 'high_clouds']
print(data['total_clouds'])
#data[cloud_vars].plot();
#plt.show();


#download API_KEY from file to keep it private.
#with open('darksky_apikey', 'r') as f:
#	API_KEY = f.read()
#f.closed
#API_KEY = API_KEY.rstrip()
#LOCATION_ID = "CerrosDeVera";
#LAT = -31.601354;
#LNG = -56.812431;

#d=datetime.datetime.now();
#forecast = forecastio.load_forecast(API_KEY, LAT, LNG,time=d,units='si')

#datos2 = pd.DataFrame();
#aux1=pd.Series();
#aux2=pd.Series();


irrad_data_1 = model.cloud_cover_to_irradiance(data['total_clouds'], how='clearsky_scaling')

irrad_data_1.plot()

plt.show()

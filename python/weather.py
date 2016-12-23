import forecastio
import datetime
#import MySQLdb

#static constants
API_KEY = "3b12723f8ad8d1ba690886e190a5977c";
LOCATION_ID = "CerrosDeVera";
LAT = -31.601354;
LNG = -56.812431;

d=datetime.datetime.now();
forecast = forecastio.load_forecast(API_KEY, LAT, LNG,time=d)

h = forecast.hourly();

for d in h.data:
	timestamp = d.time;
	temperature = d.temperature;
	humidity = d.humidity;
	precipProbability = d.precipProbability;
	precipIntensity = d.precipIntensity;
	windBearing = d.windBearing;
	windSpeed = d.windSpeed;
	cloudCover = d.cloudCover;
	print "'%s' \t %f \t %f \t %f \t %f \t %d \t %f \t %f" % \
	(timestamp,temperature,humidity,precipProbability,precipIntensity,windBearing,windSpeed,cloudCover);

print(forecast.currently())

#!/usr/bin/python

print "Calculador de panel solar de cerros de vera"

import pvlib
from pvlib.pvsystem import LocalizedPVSystem
import datetime
import pandas as pd
import scipy
#import matplotlib
import matplotlib.pyplot as plt
import math
import csv
from os import listdir
import sys
from os.path import isfile, join
import time
import forecastio

import boto
import boto.s3
from boto.s3.key import Key

def horas(hora):
  hora = hora.split(':')
  if(len(hora) == 2 and hora[0].isdigit() and hora[1].isdigit()):
    hora = datetime.time(int(hora[0]),int(hora[1]),0)
    return hora

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def fieldnamess(archivo):
  with open(str(archivo), 'rb') as csvfile:
    #csvfile.seek(4)
    reader = csv.reader(csvfile, delimiter=';')
    rows = []
    fieldnames = []
    i = 0
    j = 0
    for row in reader:
      if(i==4):
        for fieldname in row:
          if fieldname[:3] == 'Pac':
            j = j+1
            print j
            fieldname = 'Pac' + str(j)

          fieldnames.append(fieldname)
        rows.append(fieldnames)
      else:
        #print row
        rows.append(row)
      i = i+1
    #print fieldnames
    if j==5:
      #print rows
      return rows

def reescribir(archivo,rows):
  with open(str(archivo), 'w') as csvfile:
    writer = csv.writer(csvfile,delimiter=';')
    for row in rows:
      writer.writerow(row)

'''
rows = fieldnamess('Buenos_dias.csv')
#print rows
if rows is not None:
  reescribir('Buenos_dias.csv',rows)
  #print str(archivo)
  #print "aa"
  fieldnames = rows[4]
  #print fieldnames
temps = []
potencias = []
irradiancias = []
with open('Buenos_dias.csv', 'rb') as csvfile:
            #j = j+1

            reader = csv.DictReader(csvfile, delimiter=';',fieldnames =fieldnames)
            i=0
            for row in reader:
              #print row
              if(i>5):
                try:
                  inv1 = float(row['Pac3'].replace(',','.'))
                except:
                  inv1 = 0
                try:
                  inv2 = float(row['Pac4'].replace(',','.'))
                except:
                  inv2 = 0
                try:
                  inv3 = float(row['Pac5'].replace(',','.'))
                except:
                  inv3 = 0
                potencias.append((inv1+inv2+inv3)/1000)
                temps.append(float(row['TmpAmb C'].replace(',','.')))
                irradiancias.append(float(row['IntSolIrr'].replace(',','.')))
                #try:
                #temps[-1]=float(temps[-1])
                #except:
                  #pass
              i = i+1
            print temps[1]
inicio = 0
temps2 = []
potencias2 = []
irradiancias2 = []
for i in range(8):
  temps2.append(temps[inicio+288*i:inicio+288*(i+1)])
  temps2[i].append(temps2[i][-1])

  potencias2.append(potencias[inicio+288*i:inicio+288*(i+1)])
  potencias2[i].append(potencias2[i][-1])

  irradiancias2.append(irradiancias[inicio+288*i:inicio+288*(i+1)])
  irradiancias2[i].append(irradiancias2[i][-1])


temps2[7].append(temps2[7][-1])
irradiancias2[7].append(irradiancias2[7][-1])
potencias2[7].append(potencias2[7][-1])
'''

latitude = -31.601
longitude = -56.813
altitude = 160
timezone = 'Etc/GMT+3'
#SMA America: STP15000TL-US-10 (480V) 480V [CEC 2013]
sandia_modules = pvlib.pvsystem.retrieve_sam('CECMod')
sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
module = sandia_modules['Suntech_Power_STP290_24_Vd']
inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
#inverter = sapm_inverters['SMA_America__STP15000TL_US_10__480V__480V__CEC_2013_']
module['EgRef'] = 1.121
module['dEgdT'] = 0
print(sandia_modules)

localized_system = LocalizedPVSystem(module_parameters=module,
				     inverter_parameters=inverter,
				     surface_tilt=30,
                                     surface_azimuth=0,
                                     latitude=latitude,
                                     longitude=longitude,
                                     name="Cerros de Vera",
                                     altitude=altitude,
                                     tz=timezone)



fecha_correcta = True
dia_inicial = ""
mes_inicial = ""
dia_final = ""
mes_final = ""

dias = 7
try:
  dias = int(sys.argv[2])
except:
  print "la cantidad de dias debe ser un numero"

numero_dia = 6

try:
  fecha = sys.argv[1]
  fecha = fecha.split(':')
  print fecha[2]
  print fecha[1]
  print fecha[0]
  fecha = datetime.datetime(int(fecha[2]),int(fecha[1]),int(fecha[0]))  # ejemplo sudo python nombre_archivo.py dia:mes:ano dias_a_evaluar
  delta = datetime.timedelta(days = dias)
  fecha2 = fecha + delta
  print fecha
except:
  fecha_correcta = False
  fecha = datetime.datetime.today()
  fecha = fecha.replace(hour = 0, minute = 0,second = 0,microsecond = 0)
  delta = datetime.timedelta(days = dias)
  fecha2 = fecha + delta
  print "formato incorrecto de fecha"
print fecha
api_key = "e1b77ea6bd1ea54b1ba94e38fa9087c8"
cerros_de_vera = [-31.601,-56.813]
#cerros_de_vera = [40,-90]
#a = 3/0

temperaturas = []
nubosidad = []

for i in range(dias):

  delta = datetime.timedelta(days = i)
  date = fecha + delta
  #try:
  forecast = forecastio.load_forecast(api_key, cerros_de_vera[0], cerros_de_vera[1],units="si",time =date)

  byHour = forecast.hourly()
  print byHour.summary
  print byHour.icon



  for hourlyData in byHour.data:
    #print hourlyData.cloudCover

    temperaturas.append(hourlyData.temperature)
    nubosidad.append(hourlyData.cloudCover)
    if len(temperaturas) > 1:
      temp1 = temperaturas[-2]
      temp2 = temperaturas[-1]
      nub1 = nubosidad[-2]
      nub2 = nubosidad[-1]
      for j in range(1,12):
        t = temp1+(temp2-temp1)*(j)/12
        n = nub1+(nub2-nub1)*(j)/12
        temperaturas.insert(len(temperaturas)-1,t)
        nubosidad.insert(len(nubosidad)-1,n)


#a=3/0
  #except:
    #print "no hay datos de clima solicitados"
temperaturas.append(temperaturas[-1])
nubosidad.append(nubosidad[-1])
temp1 = temperaturas[-2]
temp2 = temperaturas[-1]
nub1 = nubosidad[-2]
nub2 = nubosidad[-1]
for j in range(1,12):
  t = temp1+(temp2-temp1)*(j)/12
  n = nub1+(nub2-nub1)*(j)/12
  temperaturas.insert(len(temperaturas)-1,t)
  nubosidad.insert(len(nubosidad)-1,n)
print temperaturas
print nubosidad
print len(temperaturas)
print len(nubosidad)

if fecha.day < 10:
  dia_inicial = "0" + str(fecha.day)
else:
  dia_inicial = str(fecha.day)
if fecha.month < 10:
  mes_inicial = "0" + str(fecha.month)
else:
  mes_inicial = str(fecha.month)

if fecha2.day < 10:
  dia_final = "0" + str(fecha2.day)
else:
  dia_final = str(fecha2.day)
if fecha2.month < 10:
  mes_final = "0" + str(fecha2.month)
else:
  mes_final = str(fecha2.month)

fecha_inicial = str(fecha.year) + mes_inicial + dia_inicial
fecha_final = str(fecha2.year) + mes_final + dia_final


print fecha_inicial
print fecha_final
#naive_times = pd.DatetimeIndex(start='20150727', end='20150728', freq='5min')
#naive_times = pd.DatetimeIndex(start='20150727', end='20150728', freq='1h')
#naive_times = pd.DatetimeIndex(start='20150726', end='20150727', freq='5min')
naive_times = pd.DatetimeIndex(start=fecha_inicial, end=fecha_final, freq='5min')
times = naive_times.tz_localize(timezone)
#for fech in times:
  #print fech
#a = 3/0
clearsky = localized_system.get_clearsky(times)

print("Clearsky radiation:")
print(clearsky)
print("-----------------------------------")

solar_position = localized_system.get_solarposition(times)

print("Solar Position:")
print(solar_position)
print("-----------------------------------")


total_irrad = localized_system.get_irradiance(solar_position['apparent_zenith'],
                                              solar_position['azimuth'],
                                              clearsky['dni'],
                                              clearsky['ghi'],
                                              clearsky['dhi'])

print("Total irradiance:")
print(total_irrad)
print("-----------------------------------")


#for i in range(len(irradiancias2[numero_dia])):
  #total_irrad['poa_global'][i] = irradiancias2[numero_dia][i]

for i in range(len(total_irrad['poa_global'])):
  total_irrad['poa_global'][i] = ((1-nubosidad[i])*0.65+0.35)*total_irrad['poa_global'][i]

#print ""

#for irra in total_irrad['poa_global']:
  #print irra

#a = 3/0


#lista= [19.2,18.98,19,18.26,17.53,16.21,15.81,15.83,18.41,20.91,23.03,25.48,28.49,30.08,31.21,32.15,31.49,31.3,29.33,26.27,22.69,21.15,19.38,20.55,19.51]

temps = localized_system.sapm_celltemp(total_irrad['poa_global'],0, temperaturas)
#temps = localized_system.sapm_celltemp(irradiancias2[7],0, temps2[7])
#temps = localized_system.sapm_celltemp(total_irrad['poa_global'],0, lista)


print len(temps)
print("Temps:")
print(temps)
print("-----------------------------------")

aoi = localized_system.get_aoi(solar_position['apparent_zenith'],
                               solar_position['azimuth'])
print("AOI:")
print(aoi)
print("-----------------------------------")

airmass = localized_system.get_airmass(solar_position=solar_position)

print("Air masses:")
print(airmass)
print("-----------------------------------")


#ajuste_parametros=pvlib.pvsystem.calcparams_desoto(total_irrad['poa_global'],temps['temp_cell'],module['alpha_sc'],module,1.121,-0.0002677,airmass, irrad_ref=1000, temp_ref=25)
ajuste_parametros=pvlib.pvsystem.calcparams_desoto(total_irrad['poa_global'],temps['temp_cell'],module['alpha_sc'],module,EgRef = 1.121,dEgdT = -0.0002677,M=1, irrad_ref=1000, temp_ref=25)
#ajuste_parametros=pvlib.pvsystem.calcparams_desoto(irradiancias2[7],temps['temp_cell'],module['alpha_sc'],module,EgRef = 1.121,dEgdT = -0.0002677,M=1, irrad_ref=1000, temp_ref=25)
#ajuste_parametros[0] = Il
#ajuste_parametros[1] = Io
#ajuste_parametros[2] = Rs
#ajuste_parametros[3] = Rsh
#ajuste_parametros[4] = a

#ivcurve_pnts=1000
#single_diode = localized_system.singlediode(module['I_L_ref'],module['I_o_ref'],module['R_s'],module['R_sh_ref'],module['a_ref'])
single_diode = localized_system.singlediode(ajuste_parametros[0],ajuste_parametros[1],ajuste_parametros[2],ajuste_parametros[3],ajuste_parametros[4])
print single_diode['p_mp']

"""
suma = 0
for i in range(25):
  if not(math.isnan(single_diode['p_mp'][i])):
    suma = suma +single_diode['p_mp'][i]
print ((suma/1000)*180)*0.98*0.95
"""




"""
potencias = []
for i in range(len(single_diode['i'])):
  potencias.append(single_diode['i'][i]*single_diode['v'][i])
print max(potencias)
plt.figure()
plt.plot(single_diode['v'],single_diode['i'])
plt.xlabel(r"$V$", fontsize = 24, color = (1,0,0))
plt.ylabel(r"$I$", fontsize = 24, color = 'blue')
#plt.show()
#print total_irrad
"""

#a_ref I_L_ref I_o_ref R_s R_sh_ref


#single_diode_values = localized_system.calcparams_desoto(total_irrad,temps['temp_cell'])
#print single_diode_values
#single_diode_values = pvlib.pvsystem.calcparams_desoto(total_irrad,temps['temp_cell'])


#effective_irradiance = localized_system.sapm_effective_irradiance(total_irrad['poa_direct'],total_irrad['poa_diffuse'],airmass['airmass_absolute'], aoi)

#print("Eff. irradiance:")
#print(effective_irradiance)
#print("-----------------------------------")

#dc = localized_system.sapm(effective_irradiance, temps['temp_cell'])

ac = localized_system.snlinverter(single_diode['v_mp']*20, single_diode['p_mp']*60)
ac = localized_system.snlinverter(single_diode['v_mp'], single_diode['p_mp'])
for i in range(len(ac)):
  if math.isnan(ac[i]):
    ac[i] = 0
  else:
    ac[i] = ac[i]*180/1000
    #ac[i] = ac[i]*3/1000
  #print (ac[i]*0.98*180)/1000

'''
total = 0
for potencia in potencias2[numero_dia]:
  total = total+(potencia/12)
print("Total del dia empirico: %f" % total)
'''

day_energy = ac.sum()/12
print("Total del dia predecido: %f" % day_energy)

#print total_irrad['poa_global']

minuto_del_dia = times.hour*60 + times.minute
minuto_del_dia2 = range(0,(60*24)+1,5)

#for i in range(len(nubosidad)):
  #if i > 120:
    #print nubosidad[i]
'''
plt.figure()
plt.plot(minuto_del_dia,ac)
print len(minuto_del_dia2)
print len(potencias2[numero_dia])
plt.plot(minuto_del_dia2,potencias2[numero_dia])
#plt.plot(minuto_del_dia,total_irrad['poa_global'])
#plt.plot(minuto_del_dia,(single_diode['p_mp']*180)/1000)
plt.xlabel(r"$Minutos$", fontsize = 24, color = (1,0,0))
plt.ylabel(r"$KW$", fontsize = 24, color = 'blue')
plt.show()
'''
#for key in sapm_inverters.keys():
  #print key
print nubosidad
print fecha_inicial
print fecha_final

with open('Potencia generada del ' +str(fecha.day)+'-'+ str(fecha.month)+'-'+str(fecha.year)+' al ' + str(fecha2.day)+'-'+ str(fecha2.month)+'-'+str(fecha2.year) + '.csv', 'w') as csvfile:
  fieldnames = ['Fecha y Hora','Potencia generada(kW)']
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
  writer.writeheader()
  for i in range(0,len(ac)):
    writer.writerow({'Fecha y Hora':times[i],'Potencia generada(kW)':ac[i]})

#nombre = 'Datos para ML del ' +str(fecha.day)+'-'+ str(fecha.month)+'-'+str(fecha.year)+' al ' + str(fecha2.day)+'-'+ str(fecha2.month)+'-'+str(fecha2.year) + '.csv'
nombre = 'Datos para ML del ' +str(fecha.day)+'-'+ str(fecha.month)+'-'+str(fecha.year)+ '.csv'
with open(nombre, 'w') as csvfile:
  fieldnames = ['Dia del ano','Minuto','Temperatura','Dia de la semana','Radiacion']
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
  writer.writeheader()

  for i in range(0,len(times)):
    f = times[i]
    a = pd.to_datetime(f)
    writer.writerow({'Dia del ano':a.timetuple().tm_yday,'Minuto':a.minute + a.hour*60,'Temperatura':temperaturas[i],'Dia de la semana':a.weekday(),'Radiacion':total_irrad['poa_global'][i]})

AWS_ACCESS_KEY_ID = 'AKIAJ5J4DPSLMJXM3RVQ'
AWS_SECRET_ACCESS_KEY = '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'

conn = boto.connect_s3(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


bucket = bucket = conn.get_bucket('predictions')

testfile = nombre


k = Key(bucket)
k.key = nombre
k.set_contents_from_filename(testfile,
    cb=percent_cb, num_cb=10)
  #print f.date().day
  #print f.date().minute
  #print f.date().timetuple().tm_yday
  #f.index.hour
  #a = pd.to_datetime(f)
  #print a.day
  #print a.minute
  #print a.timetuple().tm_yday

#for irra in total_irrad['poa_global']:
  #print irra
#print total_irrad['poa_global']
#for irr in total_irrad['poa_global']:
  #print irr
"""
try:
  fecha = sys.argv[1]
  fecha = fecha.split(':')
  fecha = datetime.datetime(int(fecha[2]),int(fecha[1]),int(fecha[0]))
  print fecha
except:
  print "formato incorrecto de fecha"
"""
#annual_energy = ac.sum()
#energies[name] = annual_energy

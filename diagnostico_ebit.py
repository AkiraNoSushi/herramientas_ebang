# config

theoretical_hashrate = 9000 # GHs
theoretical_rpm = 6000 # RPM
connection_timeout = 5.0 # 5 secs

hashrate_threshold = theoretical_hashrate-(theoretical_hashrate*0.4) # -40%
rpm_threshold = theoretical_rpm-(theoretical_rpm*0.15) # -15%

import multiprocessing
import ipaddress
import requests
import sys
import json
import statistics

# disable self-signed certificate warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def worker(ip):
   try:
      ip = ipaddress.IPv4Address(ip)
      result = ()
      session = requests.Session()
      session.verify = False
      session.timeout = connection_timeout
      try:
         session.post(f"https://{ip}/user/login", data={
            "username": "admin", 
            "word": "admin",
            "yuyan": 1 ,
            "login": "Login",
            "get_password": ""
         })
      except requests.RequestException:
         result = {
            "ip": ip,
            "available": False
         }
      else:
         operation_info = json.loads(session.post(f"https://{ip}/alarm/GetAlarmLoop").text)
         system_status = json.loads(session.post(f"http://{ip}/Status/getsystemstatus").text)
         result = {
            "ip": ip,
            "available": True,
            "hashrate": operation_info["feedback"]["calValue"],
            "median_temp": operation_info["feedback"]["tmpValue"],
            "hashboards_temp": [
               system_status["feedback"]["device1temp"],
               system_status["feedback"]["device2temp"],
               system_status["feedback"]["device3temp"]
            ],
            "fans_speed": [
               system_status["feedback"]["devicefan"],
               system_status["feedback"]["devicefan2"],
            ]
         }
      finally:
         session.close()
      return result
   except KeyboardInterrupt:
      pass

if __name__ == "__main__":
   try:
      with multiprocessing.Pool(4) as pool:
         start_ip = ipaddress.IPv4Address(sys.argv[1])
         end_ip = ipaddress.IPv4Address(sys.argv[2])
         print("Escaneando...")
         print()
         total = int(end_ip)-int(start_ip)+1
         error = 0
         unavailable = 0
         broken_fans = 0
         farm_temps = []
         total_hashrate = 0
         for result in pool.imap(worker, range(int(start_ip), int(end_ip)+1)):
            if result["available"]:
               if (result["hashrate"] < hashrate_threshold
                     or any(rpm < rpm_threshold for rpm in result["fans_speed"])):
                  print(f"IP: {result['ip']}")
                  print(f"├ Hashrate: {result['hashrate']}")
                  print(f"├ Temperaturas:")
                  for index, temps in enumerate(result["hashboards_temp"]):
                     print(f"│ {'└' if len(result['hashboards_temp'])==index+1 else '├'} Board {index+1}: {temps} (ºC)")
                  print(f"└ Ventiladores:")
                  for index, rpm in enumerate(result["fans_speed"]):
                     if rpm < rpm_threshold:
                        broken_fans += 1
                     print(f"  {'└' if len(result['fans_speed'])==index+1 else '├'} Ventilador {index+1}: {rpm} RPM")
                  print()
                  error += 1
               total_hashrate += result["hashrate"]
               farm_temps.append(result["median_temp"])
            else:
               print(f"IP: {result['ip']}")
               print("NO DISPONIBLE")
               print()
               error += 1
               unavailable += 1
         print(f"Total de miners: {total}")
         print(f"Hashrate total: {round(total_hashrate/1000, 2)} TH/s")
         print(f"Temperatura de la granja: {statistics.median(farm_temps)} ºC")
         print()
         print(f"Miners fallando: {error} ({round((error/total)*100, 2)}%)")
         print(f"Miners no disponibles: {unavailable} ({round((unavailable/total)*100, 2)}%)")
         print(f"Ventiladores defectuosos: {broken_fans}")
   except KeyboardInterrupt:
      pass

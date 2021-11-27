# config

theoretical_hashrate = 9000 # GHs
threshold = theoretical_hashrate-(theoretical_hashrate*0.4) # -40%
connection_timeout = 5.0 # 5 secs

import multiprocessing
import ipaddress
import requests
import sys
import json

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
         result = (False, {
            "ip": ip,
            "available": False
         })
      else:
         operation_info = json.loads(session.post(f"https://{ip}/alarm/GetAlarmLoop").text)
         if operation_info["feedback"]["calValue"] < threshold:
            system_status = json.loads(session.post(f"http://{ip}/Status/getsystemstatus").text)
            result = (False, {
               "ip": ip,
               "available": True,
               "hashrate": operation_info["feedback"]["calValue"],
               "hashboards_temp": [
                  system_status["feedback"]["device1temp"],
                  system_status["feedback"]["device2temp"],
                  system_status["feedback"]["device3temp"]
               ],
               "fans_speed": [
                  system_status["feedback"]["devicefan"],
                  system_status["feedback"]["devicefan2"],
               ]
            })
         else:
            result = (True, {})
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
         for result in pool.imap(worker, range(int(start_ip), int(end_ip)+1)):
            if not result[0]:
               if error == 0:
                  print("MINERS FALLANDO:")
                  print()
               print(f"IP: {result[1]['ip']}")
               if result[1]["available"]:
                  print(f"├ Hashrate: {result[1]['hashrate']}")
                  print(f"├ Temperaturas:")
                  for index, temps in enumerate(result[1]["hashboards_temp"]):
                     print(f"├ {'└' if len(result[1]['hashboards_temp'])==index+1 else '├'} Board {index+1}: {temps} (ºC)")
                  print(f"└ Ventiladores:")
                  for index, rpm in enumerate(result[1]["fans_speed"]):
                     print(f"  {'└' if len(result[1]['fans_speed'])==index+1 else '├'} Ventilador {index+1}: {rpm} RPM")
               else:
                  print("NO DISPONIBLE")
                  unavailable += 1
               print()
               error += 1
         print(f"Total de miners: {total}")
         print(f"Miners fallando: {error} ({round((error/total)*100, 2)}%)")
         print(f"Miners no disponibles: {unavailable} ({round((unavailable/total)*100, 2)}%)")
   except KeyboardInterrupt:
      pass

import multiprocessing
import ipaddress
import requests
import sys
import json
import threading

# disable self-signed certificate warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def worker(ip):
   try:
      ip = ipaddress.IPv4Address(ip)
      result = ()
      session = requests.Session()
      session.verify = False
      session.timeout = 5
      try:
         session.post(f"https://{ip}/user/login", data={
            "username": "admin", 
            "word": "admin",
            "yuyan": 1 ,
            "login": "Login",
            "get_password": ""
         })
      except requests.RequestException:
         result = (False, ip)
      else:
         pool_user = f"{sys.argv[5]}.{str(ip)[str(ip).rindex('.')+1:].zfill(3)}"
         desired_ports = sys.argv[4].split(",")
         session.post(f"https://{ip}/Cgminer/CgminerConfig", data={
            "mip1": f"stratum+tcp://{sys.argv[3]}:{desired_ports[0]}",
            "mwork1": pool_user,
            "mpassword1": "",
            "mip2": f"stratum+tcp://{sys.argv[3]}:{desired_ports[1]}",
            "mwork2": pool_user,
            "mpassword2": "",
            "mip3": f"stratum+tcp://{sys.argv[3]}:{desired_ports[2]}",
            "mwork3": pool_user,
            "mpassword3": ""
         })
         threading.Thread(target=session.post, args=(f"https://{ip}/update/resetcgminer",)).start() # reboot async
         result = (True, ip)
      return result
   except KeyboardInterrupt:
      pass

if __name__ == "__main__":
   try:
      with multiprocessing.Pool(4) as pool:
         start_ip = ipaddress.IPv4Address(sys.argv[1])
         end_ip = ipaddress.IPv4Address(sys.argv[2])
         print(f"Cambiando a la pool {sys.argv[3]}...")
         print()
         total = int(end_ip)-int(start_ip)+1
         unavailable = 0
         for result in pool.imap(worker, range(int(start_ip), int(end_ip)+1)):
            if not result[0]:
               if unavailable == 0:
                  print("MINERS NO DISPONIBLES:")
               print(f"{result[1]}")
               unavailable += 1
         print()
         print(f"Total de miners: {total}")
         print(f"Miners no disponibles: {unavailable} ({round((unavailable/total)*100, 2)}%)")
         print()
         print("[i] Recuerde que los cambios están tomando efecto y debe esperar unos minutos a que se reinicie el total de máquinas")
         print()
   except KeyboardInterrupt:
      pass

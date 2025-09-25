import subprocess
import time
from datetime import datetime, timedelta

SCRIPT_PATH = "main.py"
INTERVAL_SECONDS = 200 # 5 minutos
DURATION_HOURS = 1

end_time = datetime.now() + timedelta(hours=DURATION_HOURS)

while datetime.now() < end_time:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Ejecutando descarga")
    subprocess.run(["python", SCRIPT_PATH])
    
    if datetime.now() < end_time:
        print(f"Esperando {INTERVAL_SECONDS}s...")
        time.sleep(INTERVAL_SECONDS)

print("Finalizado")
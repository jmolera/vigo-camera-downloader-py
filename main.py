#!/usr/bin/env python3

import requests
import time
import re
from pathlib import Path
from datetime import datetime

CAMARAS_JSON_URL = "https://datos.vigo.org/data/trafico/camaras-trafico.json"
OUTPUT_PATH = "./imagenes_vigo"

def sanitize_filename(name):
    sanitized = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    sanitized = re.sub(r'[<>:"|?*]', '_', sanitized)
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '_-.')
    return sanitized[:50]

def fetch_cameras_data():
    try:
        response = requests.get(CAMARAS_JSON_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return []

def process_camera_data(cameras):
    processed = []
    for i, camera in enumerate(cameras):
        try:
            camera_id = camera.get('id', f'cam_{i:03d}')
            nombre = camera.get('nombre', f'Camara_{i:03d}')
            url_original = camera.get('url', '')
            
            url_imagen = url_original.replace('camv2.php', 'cam.php') if 'camv2.php' in url_original else url_original
            
            processed.append({
                'id': camera_id,
                'nombre': nombre,
                'url_imagen': url_imagen,
                'filename_base': sanitize_filename(f"CAM_{camera_id}_{nombre}")
            })
            
        except Exception as e:
            print(f"Error procesando cámara {i}: {e}")
    
    return processed

def download_cameras():
    cameras_raw = fetch_cameras_data()
    if not cameras_raw:
        return
    
    cameras = process_camera_data(cameras_raw)
    
    current_time = datetime.now()
    date_dir = current_time.strftime('%Y%m%d')
    timestamp = current_time.strftime('%Y%m%d_%H%M')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://hoxe.vigo.org/'
    }
    
    successful = 0
    for camera in cameras:
        camera_dir = Path(OUTPUT_PATH) / camera['filename_base'] / date_dir
        camera_dir.mkdir(parents=True, exist_ok=True)
        filepath = camera_dir / f"{timestamp}.jpg"
        
        try:
            response = requests.get(camera['url_imagen'], timeout=15, headers=headers)
            response.raise_for_status()
            
            if len(response.content) < 1000 or not response.content.startswith(b'\xff\xd8\xff'):
                print(f"Imagen inválida para {camera['id']}")
                continue
            
            filepath.write_bytes(response.content)
            print(f"Descargada {camera['nombre']} ({camera['id']})")
            successful += 1
            
        except Exception as e:
            print(f"Error descargando {camera['id']}: {e}")
        
        time.sleep(1)
    
    print(f"Completado: {successful}/{len(cameras)} exitosas")

if __name__ == "__main__":
    download_cameras()
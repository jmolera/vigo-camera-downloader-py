#!/usr/bin/env python3

import requests
import time
import re
import json
import os
from pathlib import Path
from datetime import datetime

# Obtener directorio del script
SCRIPT_DIR = Path(__file__).parent.absolute()

CAMARAS_JSON_URL = "https://datos.vigo.org/data/trafico/camaras-trafico.json"
OUTPUT_PATH = SCRIPT_DIR / "imagenes"

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
                'filename_base': sanitize_filename(f"{camera_id}_{nombre}")
            })
            
        except Exception as e:
            print(f"Error procesando cámara {i}: {e}")
    
    return processed

def fetch_and_save_cameras(json_file):
    cameras_raw = fetch_cameras_data()
    if not cameras_raw:
        return []
    
    cameras = process_camera_data(cameras_raw)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(cameras, f, ensure_ascii=False, indent=2)
    
    print("Cache actualizado desde API")
    return cameras

def download_cameras():
    json_file = SCRIPT_DIR / 'cameras.json'
    
    # Usar cache si existe y tiene menos de 24 horas
    if json_file.exists():
        age_hours = (time.time() - json_file.stat().st_mtime) / 3600
        if age_hours < 24:
            with open(json_file, 'r', encoding='utf-8') as f:
                cameras = json.load(f)
            print(f"Usando cache (antigüedad: {age_hours:.1f}h)")
        else:
            cameras = fetch_and_save_cameras(json_file)
    else:
        cameras = fetch_and_save_cameras(json_file)
    
    if not cameras:
        print("NO HAY DATOS DISPONIBLES")
        return
    
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
        camera_dir = OUTPUT_PATH / camera['filename_base'] / date_dir
        camera_dir.mkdir(parents=True, exist_ok=True)
        filepath = camera_dir / f"{timestamp}.jpg"
        
        try:
            response = requests.get(camera['url_imagen'], timeout=15, headers=headers)
            response.raise_for_status()
            
            if len(response.content) < 1000 or not response.content.startswith(b'\xff\xd8\xff'):
                continue
            
            filepath.write_bytes(response.content)
            successful += 1
            
        except Exception as e:
            print(f"Error descargando {camera['id']}: {e}")
        
        time.sleep(1)
    
    print(f"Completado: {successful}/{len(cameras)} exitosas")

def main():
    try:
        download_cameras()
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Tiempo total: {time.time() - start_time:.2f}s")
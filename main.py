#!/usr/bin/env python3

import json
import os
import requests
import csv
import argparse
from datetime import datetime
from pathlib import Path
import logging
import time
import re

CAMARAS_JSON_URL = "https://datos.vigo.org/data/trafico/camaras-trafico.json"
OUTPUT_PATH = "./imagenes_vigo"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize_filename(name):
    sanitized = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    sanitized = re.sub(r'[<>:"|?*]', '_', sanitized)
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '_-.')
    return sanitized[:50]

def fetch_cameras_data():
    try:
        logger.info("Obteniendo datos de cámaras desde la API de Vigo...")
        response = requests.get(CAMARAS_JSON_URL, timeout=10)
        response.raise_for_status()
        cameras = response.json()
        logger.info(f"Encontradas {len(cameras)} cámaras")
        return cameras
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}")
        return []

def process_camera_data(cameras):
    processed = []
    for i, camera in enumerate(cameras):
        try:
            camera_id = camera.get('id', f'cam_{i:03d}')
            nombre = camera.get('nombre', f'Camara_{i:03d}')
            url_original = camera.get('url', '')
            
            if 'camv2.php' in url_original:
                url_imagen = url_original.replace('camv2.php', 'cam.php')
            else:
                url_imagen = url_original
            
            lat = float(camera.get('lat', 0))
            lon = float(camera.get('lon', 0))
            
            processed_camera = {
                'id': camera_id,
                'nombre': nombre,
                'url_imagen': url_imagen,
                'url_original': url_original,
                'latitud': lat,
                'longitud': lon,
                'ubicacion': nombre,
                'descripcion': f'Cámara de tráfico en {nombre}, Vigo',
                'filename_base': sanitize_filename(f"CAM_{camera_id}_{nombre}")
            }
            processed.append(processed_camera)
            
        except Exception as e:
            logger.error(f"Error procesando cámara {i}: {e}")
    
    return processed

def download_single_camera(camera, date_dir, timestamp, output_path):
    camera_dir = Path(output_path) / camera['filename_base'] / date_dir
    camera_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{timestamp}.jpg"
    filepath = camera_dir / filename
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://hoxe.vigo.org/'
    }
    
    try:
        response = requests.get(camera['url_imagen'], timeout=15, headers=headers)
        response.raise_for_status()
        
        if len(response.content) < 1000:
            logger.warning(f"Imagen muy pequeña para cámara {camera['id']}: {len(response.content)} bytes")
            return False
        
        if not response.content.startswith(b'\xff\xd8\xff'):
            logger.warning(f"No es JPEG válido para cámara {camera['id']}")
            return False
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Descargada {camera['nombre']} ({camera['id']}) - {len(response.content)} bytes")
        return True
        
    except Exception as e:
        logger.error(f"Error descargando cámara {camera['id']}: {e}")
        return False

def download_cameras(cameras, max_cameras=None, output_path=OUTPUT_PATH):
    if max_cameras:
        cameras = cameras[:max_cameras]
    
    current_time = datetime.now()
    date_dir = current_time.strftime('%Y%m%d')
    timestamp = current_time.strftime('%Y%m%d_%H%M')
    
    logger.info(f"Descargando imágenes de {len(cameras)} cámaras...")
    
    successful = 0
    for camera in cameras:
        if download_single_camera(camera, date_dir, timestamp, output_path):
            successful += 1
        time.sleep(1)
    
    logger.info(f"Descarga completada: {successful}/{len(cameras)} exitosas")

def save_cameras_data(cameras):
    with open('camaras.json', 'w', encoding='utf-8') as f:
        json.dump(cameras, f, ensure_ascii=False, indent=2)
    
    if cameras:
        with open('camaras.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=cameras[0].keys())
            writer.writeheader()
            writer.writerows(cameras)
    
    logger.info("Datos guardados en camaras.json y camaras.csv")

def test_single_camera(camera_id):
    cameras = fetch_cameras_data()
    if not cameras:
        return
    
    target_camera = None
    for camera in cameras:
        if camera.get('id') == camera_id:
            target_camera = camera
            break
    
    if not target_camera:
        logger.error(f"No se encontró cámara con ID: {camera_id}")
        return
    
    logger.info(f"Probando cámara: {target_camera['nombre']} (ID: {camera_id})")
    
    processed = process_camera_data([target_camera])
    if processed:
        download_cameras(processed, max_cameras=1)

def main():
    parser = argparse.ArgumentParser(description='Descargador de cámaras de Vigo')
    parser.add_argument('--max-camaras', type=int, help='Máximo número de cámaras a descargar')
    parser.add_argument('--test-camara', type=str, help='ID de cámara específica a probar')
    parser.add_argument('--solo-metadatos', action='store_true', help='Solo generar metadatos')
    parser.add_argument('--output-dir', default=OUTPUT_PATH, help='Directorio de salida')
    
    args = parser.parse_args()
    
    Path(args.output_dir).mkdir(exist_ok=True)
    
    if args.test_camara:
        test_single_camera(args.test_camara)
        return
    
    cameras_raw = fetch_cameras_data()
    if not cameras_raw:
        logger.error("No se pudieron obtener datos de cámaras")
        return
    
    cameras = process_camera_data(cameras_raw)
    save_cameras_data(cameras)
    
    if not args.solo_metadatos:
        download_cameras(cameras, args.max_camaras, args.output_dir)
    
    logger.info("Proceso completado")

if __name__ == "__main__":
    main()

# Vigo Camera Downloader (Python 🐍)

Sistema automatizado para descargar, comprimir y archivar imágenes de las cámaras de tráfico de Vigo.

## Requisitos del Sistema

- Python 3.8+
- ffmpeg
- zip
- rclone

### Instalación de Dependencias

```bash
sudo apt update
sudo apt install python3 python3-pip ffmpeg zip rclone
pip3 install -r requirements.txt
```

## Configuración

### 1. Configurar Google Drive con rclone

```bash
rclone config
```

- Nombre del remote: `drive-vigo`
- Storage type: `drive` (Google Drive)
- Root folder ID: `1ilkJpT3gLp1BE9gXcZKDeo-qT91J_PyP`
- Configure as Shared Drive: `Yes`

### 2. Dar permisos de ejecución a los scripts

```bash
chmod +x download.sh sync.sh pack_month.sh
```

### 3. Configurar timezone (opcional)

```bash
sudo timedatectl set-timezone Europe/Madrid
```

## Uso

### Ejecución Manual

```bash
# Descargar imágenes una vez
./download.sh

# Procesar día anterior (comprimir + video + subir)
./sync.sh

# Empaquetar mes anterior
./pack_month.sh
```

### Automatización con Cron

```bash
crontab -e
```

Añadir:

```cron
# Descargar imágenes cada 5 minutos
*/5 * * * * /ruta/completa/vigo-camera-downloader-py/download.sh >> /tmp/download.log 2>&1

# Procesar día anterior diariamente a las 3 AM
0 3 * * * /ruta/completa/vigo-camera-downloader-py/sync.sh >> /tmp/sync.log 2>&1

# Empaquetar mes anterior el día 1 de cada mes a las 7 AM
0 7 1 * * /ruta/completa/vigo-camera-downloader-py/pack_month.sh >> /tmp/pack_month.log 2>&1
```

Reemplazar `/ruta/completa/` con la ruta real del proyecto.

## Estructura del Proyecto

```
vigo-camera-downloader-py/
├── main.py                 # Script principal de descarga
├── download.sh             # Ejecuta main.py con timezone correcto
├── sync.sh                 # Procesa día anterior: comprime, genera video y sube
├── pack_month.sh           # Empaqueta archivos mensuales en Drive
├── requirements.txt        # Dependencias Python
├── cameras.json            # Cache de metadatos de cámaras (generado automáticamente)
├── imagenes/               # Carpeta local de imágenes (generada automáticamente)
│   └── [CAMARA]/
│       └── [YYYYMMDD]/
│           └── [YYYYMMDD_HHMM].jpg
└── last_month/             # Carpeta temporal para empaquetado mensual
```

## Funcionamiento

### Descarga (cada 5 minutos)
- Consulta API de Vigo para obtener lista de cámaras
- Usa cache local (válido 24h) para evitar consultas innecesarias
- Descarga imágenes JPG de cada cámara
- Organiza por cámara y fecha: `imagenes/CAM_ID_NOMBRE/YYYYMMDD/YYYYMMDD_HHMM.jpg`

### Sincronización Diaria (3 AM)
- Procesa imágenes del día anterior
- Genera video MKV (2 fps) con ffmpeg
- Comprime imágenes en ZIP
- Sube ZIP y MKV a Google Drive
- Elimina archivos locales y directorios vacíos

### Empaquetado Mensual (día 1, 7 AM)
- Descarga todos los ZIP y MKV del mes anterior desde Drive
- Los empaqueta en un único ZIP mensual por cámara
- Elimina archivos diarios de Drive
- Sube archivo mensual consolidado

## API de Datos

Fuente: [Datos Abiertos Vigo - Cámaras de Tráfico](https://datos.vigo.org/data/trafico/camaras-trafico.json)

## Logs

Los logs se guardan en `/tmp/`:
- `/tmp/download.log` - Registro de descargas
- `/tmp/sync.log` - Registro de sincronización diaria
- `/tmp/pack_month.log` - Registro de empaquetado mensual

## Troubleshooting

### Las imágenes no se descargan
```bash
# Verificar ejecución manual
python3 main.py

# Revisar logs de cron
tail -f /tmp/download.log
```

### No se sube nada a Drive
```bash
# Verificar configuración de rclone
rclone lsd drive-vigo:/Vigo

# Probar subida manual
rclone ls drive-vigo:/Vigo
```

### Cron no ejecuta los scripts
```bash
# Verificar permisos
ls -la *.sh

# Verificar crontab
crontab -l

# Ver logs del sistema
grep CRON /var/log/syslog | tail -20
```
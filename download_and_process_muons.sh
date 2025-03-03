#!/bin/bash

# Configuración inicial
ROOT_DIR="root_files"
INPUT_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/root_files/"
OUTPUT_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/processed_files/"
LOG_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/logs/"
ROOT_URLS=(
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/002104A5-2A44-E311-B69F-00304867918A.root"
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/0027F2FC-2E44-E311-B491-003048678E52.root"
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/005D3B00-2F44-E311-A0D5-002618FDA279.root"
    # Agrega más enlaces ROOT aquí según sea necesario
)

# Lista de nombres personalizados para los archivos descargados
ROOT_NAMES=(
    "muonia_1_1.root"
    "muonia_1_2.root"
    "muonia_1_3.root"
    # Agrega más nombres correspondientes a los enlaces
)

# Validar que el número de enlaces y nombres coincidan
if [ "${#ROOT_URLS[@]}" -ne "${#ROOT_NAMES[@]}" ]; then
    echo "Error: El número de enlaces ROOT no coincide con el número de nombres personalizados."
    exit 1
fi

# Crear los directorios para los archivos ROOT y los logs
#mkdir -p "$ROOT_DIR" "$OUTPUT_DIR" "$LOG_DIR"

# Descargar cada archivo ROOT con el nombre personalizado
for i in "${!ROOT_URLS[@]}"; do
    url="${ROOT_URLS[$i]}"
    custom_name="${ROOT_NAMES[$i]}"
    target_path="$ROOT_DIR/$custom_name"

    # Verificar si el archivo ya existe
    if [ ! -f "$target_path" ]; then
        echo "Descargando $custom_name desde $url..."
        xrdcp "$url" "$target_path"
        if [ $? -ne 0 ]; then
            echo "Error al descargar $custom_name desde $url. Verifica la URL o tu conectividad."
            continue
        fi
        echo "Archivo descargado y guardado como: $target_path"
    else
        echo "El archivo $custom_name ya existe. Saltando descarga."
    fi
done

# Procesar los archivos ROOT descargados
for ROOT_FILE in "$INPUT_DIR"/*.root; do
    # Verificar si el archivo ROOT existe (comodín vacío)
    if [ ! -e "$ROOT_FILE" ]; then
        echo "No se encontraron archivos ROOT en $iNPUT_DIR. Saliendo."
        exit 1
    fi

    # Obtener el nombre base del archivo (sin la ruta completa)
    BASENAME=$(basename "$ROOT_FILE" .root)

    # Definir el archivo de salida
    OUTPUT_FILE="${OUTPUT_DIR}/${BASENAME}_output.root"
    LOG_FILE="${LOG_DIR}/${BASENAME}_processing.log"

    # Ejecutar poet_cfg.py con el archivo de entrada y salida
    echo "Procesando $ROOT_FILE -> $OUTPUT_FILE"
    cmsRun python/poet_cfg_n.py True "$ROOT_FILE" "$OUTPUT_FILE" > "$LOG_FILE" 2>&1

    # Verificar si ocurrió un error en cmsRun
    if [ $? -ne 0 ]; then
        echo "Error al procesar $ROOT_FILE. Revisa el log para más detalles: $LOG_FILE"
        continue
    fi

    # Eliminar el archivo ROOT original después de procesarlo
    rm "$ROOT_FILE"
    echo "Archivo $ROOT_FILE eliminado."
done

# Ejecutar analyzer1.py para analizar los archivos procesados
echo "Ejecutando analyzer1.py para analizar los archivos procesados..."
python analyzer1.py

echo "Procesamiento y análisis completo."

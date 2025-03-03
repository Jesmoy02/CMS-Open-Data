#!/bin/bash

# Configuración de directorios
ROOT_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/root_files/"
OUTPUT_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/processed_files/"
LOG_DIR="/code/CMSSW_5_3_32/src/PhysObjectExtractorTool/PhysObjectExtractor/logs/"

# Crear los directorios si no existen
mkdir -p "$ROOT_DIR" "$OUTPUT_DIR" "$LOG_DIR"

# Lista de archivos ROOT en CERN Open Data
ROOT_URLS=(
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/002104A5-2A44-E311-B69F-00304867918A.root"
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/0027F2FC-2E44-E311-B491-003048678E52.root"
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/MuOnia/AOD/12Oct2013-v1/00000/005D3B00-2F44-E311-A0D5-002618FDA279.root"
)

# Nombres personalizados para los archivos descargados
ROOT_NAMES=(
    "muonia_1_1.root"
    "muonia_1_2.root"
    "muonia_1_3.root"
)

# Validar que el número de enlaces y nombres coincidan
if [ "${#ROOT_URLS[@]}" -ne "${#ROOT_NAMES[@]}" ]; then
    echo "Error: Diferente número de URLs y nombres."
    exit 1
fi

# Descargar archivos ROOT si no existen
for i in "${!ROOT_URLS[@]}"; do
    url="${ROOT_URLS[$i]}"
    custom_name="${ROOT_NAMES[$i]}"
    target_path="$ROOT_DIR/$custom_name"

    if [ ! -f "$target_path" ]; then
        echo "Descargando $custom_name..."
        xrdcp "$url" "$target_path"
        if [ $? -ne 0 ]; then
            echo "Error descargando $custom_name. Verifica la URL."
            continue
        fi
    else
        echo "$custom_name ya existe. Saltando descarga."
    fi
done

# Procesar archivos ROOT descargados con analyzer_mu_tr.py
echo "Ejecutando analyzer_mu_tr.py..."
for ROOT_FILE in "$ROOT_DIR"/*.root; do
    if [ ! -e "$ROOT_FILE" ]; then
        echo "No se encontraron archivos ROOT en $ROOT_DIR."
        exit 1
    fi

    # Registrar logs de la ejecución
    BASENAME=$(basename "$ROOT_FILE" .root)
    LOG_FILE="$LOG_DIR/${BASENAME}_analysis.log"

    echo "Analizando $ROOT_FILE..."
    python analyzer_mu_tr_1.py "$ROOT_FILE" > "$LOG_FILE" 2>&1

    if [ $? -ne 0 ]; then
        echo "Error en analyzer_mu_tr.py con $ROOT_FILE. Revisa el log: $LOG_FILE"
    else
        echo "Análisis de $ROOT_FILE completado. Log: $LOG_FILE"
    fi
done

echo "Proceso completo."


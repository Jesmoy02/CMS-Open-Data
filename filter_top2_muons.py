# -*- coding: utf-8 -*-
import csv
import ROOT
import os
from array import array

# Crear carpetas si no existen
if not os.path.exists('root'):
    os.makedirs('root')
if not os.path.exists('csv'):
    os.makedirs('csv')

# Archivos de entrada y salida
input_csv = 'csv/sorted_muons.csv'
output_csv = 'csv/filtered_top2_muons.csv'
output_root = 'root/filtered_top2_muons.root'

# Leer el archivo CSV
with open(input_csv, 'r') as infile:
    reader = csv.reader(infile)
    header = next(reader)  # Leer la cabecera
    filtered_data = []

    # Obtener las variables muon_XX del encabezado
    unique_variables = []
    for col in header:
        parts = col.split('_')
        if len(parts) == 3 and parts[0] == "muon":
            if parts[2] not in unique_variables:
                unique_variables.append(parts[2])

    # Procesar cada evento
    for row in reader:
        event_id = int(row[0])  # Primer elemento es el event_id
        muons = []

        # Extraer la información de cada muón
        for i in range(10):  # Hasta 10 muones por evento
            muon_data = {}
            for var in unique_variables:
                index = header.index("muon_{0}_{1}".format(i + 1, var)) if "muon_{0}_{1}".format(i + 1, var) in header else None
                if index is not None:
                    try:
                        muon_data[var] = float(row[index]) if row[index] else None
                    except ValueError:
                        muon_data[var] = None
            if "pt" in muon_data and muon_data["pt"] is not None:
                muons.append(muon_data)

        # Filtrar solo eventos con al menos 2 muones
        if len(muons) >= 2:
            # Ordenar por pt (de mayor a menor) y seleccionar los dos primeros
            muons_sorted = sorted(muons, key=lambda x: x["pt"], reverse=True)[:2]
            filtered_data.append([event_id] + [muons_sorted[0][var] for var in unique_variables] +
                                 [muons_sorted[1][var] for var in unique_variables])

# Guardar los datos filtrados en un nuevo archivo CSV
with open(output_csv, 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Event'] + ["Muon1_{0}".format(var) for var in unique_variables] +
                    ["Muon2_{0}".format(var) for var in unique_variables])
    writer.writerows(filtered_data)

# Guardar los datos filtrados en un archivo ROOT
root_file = ROOT.TFile(output_root, 'RECREATE')
tree = ROOT.TTree('Events', 'Eventos con los 2 muones con mayor pt')

# Definir estructuras para almacenar datos
event_id = array('i', [0])
branches = {}

for var in unique_variables:
    branches["Muon1_" + var] = array('f', [0.0])
    branches["Muon2_" + var] = array('f', [0.0])

tree.Branch('Event', event_id, 'Event/I')
for var in unique_variables:
    tree.Branch("Muon1_" + var, branches["Muon1_" + var], "Muon1_{0}/F".format(var))
    tree.Branch("Muon2_" + var, branches["Muon2_" + var], "Muon2_{0}/F".format(var))

# Llenar el árbol con los datos
for data in filtered_data:
    event_id[0] = data[0]  # ID del evento
    for i, var in enumerate(unique_variables):
        branches["Muon1_" + var][0] = float(data[i + 1]) if data[i + 1] is not None else 0.0
        branches["Muon2_" + var][0] = float(data[i + 1 + len(unique_variables)]) if data[i + 1 + len(unique_variables)] is not None else 0.0
    tree.Fill()

# Guardar y cerrar el archivo ROOT
root_file.Write()
root_file.Close()

# Mensaje de finalización
print("Proceso completado. Se guardaron los archivos filtered_top2_muons.root y filtered_top2_muons.csv en las carpetas 'root' y 'csv'.")

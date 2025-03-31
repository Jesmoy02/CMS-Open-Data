# -*- coding: utf-8 -*-

import ROOT
import csv
import os
from array import array

# Crear carpetas si no existen
if not os.path.exists("csv"):
    os.makedirs("csv")
if not os.path.exists("root"):
    os.makedirs("root")

# Abrir el archivo ROOT de entrada
input_file = ROOT.TFile("muonia_1_1_output.root", "READ")
tree = input_file.Get("mymuons/Events")

# Verificar si el árbol tiene eventos
n_entries = tree.GetEntries()
print("Número de eventos en el árbol: {0}".format(n_entries))
if n_entries == 0:
    print("El árbol está vacío. Verifica el archivo ROOT.")
    exit()

# Obtener lista de ramas disponibles en el árbol
branches = [branch.GetName() for branch in tree.GetListOfBranches()]
print("Ramas disponibles en el árbol:")
for branch in branches:
    print(branch)

# Variables esperadas en el árbol
variables = ["e", "pt", "px", "py", "pz", "eta", "phi", "ch", "mass", "pfreliso03all", "pfreliso04all", 
             "tightid", "softid", "dxy", "dxyErr", "dxybs", "dz", "dzErr", "jetidx", "genpartidx"]

detected_variables = [var for var in variables if "muon_" + var in branches]
print("('Variables detectadas en el árbol:', {0})".format(detected_variables))

# Crear un nuevo archivo ROOT de salida en la carpeta correspondiente
output_root_path = os.path.join("root", "sorted_muons.root")
output_file = ROOT.TFile(output_root_path, "RECREATE")
new_tree = ROOT.TTree("Events", "Sorted muons")

# Definir estructuras para almacenar variables de salida
n_muons = array('i', [0])
data_arrays = {}

for var in detected_variables:
    data_arrays[var] = ROOT.std.vector('float')()

new_tree.Branch("numbermuon", n_muons, "numbermuon/I")
for var in detected_variables:
    new_tree.Branch("muon_" + var, data_arrays[var])

# Crear archivo CSV en la carpeta correspondiente
output_csv_path = os.path.join("csv", "sorted_muons.csv")
csv_file = open(output_csv_path, "wb")  # 'wb' en Python 2 para evitar líneas en blanco
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["event"] + ["muon_{0}_".format(i+1) + var for i in range(6) for var in detected_variables])  # Hasta 6 muones por evento

# Recorrer los eventos del árbol original
event_number = 1
for event in tree:
    if not hasattr(event, 'numbermuon'):
        print("La variable numbermuon no existe en el árbol.")
        exit()
    
    n_muons[0] = event.numbermuon
    muon_data = {}
    for var in detected_variables:
        muon_data[var] = [getattr(event, "muon_" + var)[i] for i in range(event.numbermuon)]
    
    sorted_indices = sorted(range(event.numbermuon), key=lambda i: muon_data["pt"][i], reverse=True)
    
    for var in detected_variables:
        data_arrays[var].clear()
        for i in sorted_indices:
            data_arrays[var].push_back(muon_data[var][i])
    
    new_tree.Fill()
    
    # Escribir en CSV
    row = [event_number]
    for i in range(6):
        if i < event.numbermuon:
            row.extend([muon_data[var][sorted_indices[i]] for var in detected_variables])
        else:
            row.extend([None] * len(detected_variables))
    csv_writer.writerow(row)
    
    event_number += 1

# Guardar y cerrar archivos
output_file.Write()
output_file.Close()
input_file.Close()
csv_file.close()

print("Proceso completado. Se guardaron los archivos sorted_muons.root y sorted_muons.csv en las carpetas 'root' y 'csv'.")

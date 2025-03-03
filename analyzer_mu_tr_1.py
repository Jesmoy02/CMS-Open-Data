# -*- coding: utf-8 -*-

import ROOT
import math
import sys

# Verificar si se proporcionó un archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python analyzer_mu_tr.py <archivo_ROOT>")
    sys.exit(1)

file_name = sys.argv[1]  # Obtener el nombre del archivo desde el argumento
tree_muons_name = "mymuons/Events"
tree_tracks_name = "mytracks/Events"

file = ROOT.TFile.Open(file_name)
if not file or file.IsZombie():
    print(f"Error: No se pudo abrir el archivo {file_name}")
    sys.exit(1)

tree_muons = file.Get(tree_muons_name)
tree_tracks = file.Get(tree_tracks_name)

if not tree_muons or not tree_tracks:
    print(f"Error: No se encontraron los árboles en el archivo {file_name}")
    sys.exit(1)

# Definir masas (en GeV/c²)
mass_muon = 0.1057
mass_kaon = 0.493677

# Listas para almacenar masas invariantes
masses_muons = []
masses_tracks = []

# Recorrer los eventos
for event_muons, event_tracks in zip(tree_muons, tree_tracks):
    if event_muons.numbermuon != 5:
        continue
    if event_muons.numbermuon < 2 or event_tracks.numtracks < 2:
        continue
    
    # Selección de muones
    px1_mu, py1_mu, pz1_mu = event_muons.muon_px[0], event_muons.muon_py[0], event_muons.muon_pz[0]
    px2_mu, py2_mu, pz2_mu = event_muons.muon_px[1], event_muons.muon_py[1], event_muons.muon_pz[1]
    E1_mu = math.sqrt(px1_mu**2 + py1_mu**2 + pz1_mu**2 + mass_muon**2)
    E2_mu = math.sqrt(px2_mu**2 + py2_mu**2 + pz2_mu**2 + mass_muon**2)
    masses_muons.append(math.sqrt((E1_mu + E2_mu)**2 - ((px1_mu + px2_mu)**2 + (py1_mu + py2_mu)**2 + (pz1_mu + pz2_mu)**2)))
    
    # Selección de tracks
    px1_tr, py1_tr, pz1_tr = event_tracks.track_px[0], event_tracks.track_py[0], event_tracks.track_pz[0]
    px2_tr, py2_tr, pz2_tr = event_tracks.track_px[1], event_tracks.track_py[1], event_tracks.track_pz[1]
    E1_tr = math.sqrt(px1_tr**2 + py1_tr**2 + pz1_tr**2 + mass_kaon**2)
    E2_tr = math.sqrt(px2_tr**2 + py2_tr**2 + pz2_tr**2 + mass_kaon**2)
    masses_tracks.append(math.sqrt((E1_tr + E2_tr)**2 - ((px1_tr + px2_tr)**2 + (py1_tr + py2_tr)**2 + (pz1_tr + pz2_tr)**2)))

# Guardar histogramas
hist_muons = ROOT.TH1F("mass_hist_muons", "Masa Invariante de Muones", 50, 2.8, 3.3)
hist_tracks = ROOT.TH1F("mass_hist_tracks", "Masa Invariante de Tracks", 50, 0.9, 1.5)

for mass in masses_muons:
    hist_muons.Fill(mass)
for mass in masses_tracks:
    hist_tracks.Fill(mass)

canvas = ROOT.TCanvas("canvas", "Canvas", 1200, 600)
canvas.Divide(2, 1)
canvas.cd(1)
hist_muons.Draw()
canvas.cd(2)
hist_tracks.Draw()
canvas.SaveAs(f"mass_invariant_{file_name}.png")

print(f"Análisis completado para {file_name}")


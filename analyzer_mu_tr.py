# -*- coding: utf-8 -*-

import ROOT
import math

# Abrir el archivo ROOT
file_name = "muonia_1_1_output.root"  # Ajusta el nombre del archivo si es necesario
tree_muons_name = "mymuons/Events"
tree_tracks_name = "mytracks/Events"

file = ROOT.TFile.Open(file_name)
tree_muons = file.Get(tree_muons_name)
tree_tracks = file.Get(tree_tracks_name)

# Definir masas (en GeV/c²)
mass_muon = 0.1057
mass_kaon = 0.493677

# Listas para almacenar masas invariantes
masses_muons = []
masses_tracks = []

# Recorrer los eventos
for event_muons, event_tracks in zip(tree_muons, tree_tracks):
    # Filtrar eventos con exactamente 5 muones
    if event_muons.numbermuon != 5:
        continue
    
    # Verificar que haya al menos 2 muones y 2 tracks
    if event_muons.numbermuon < 2 or event_tracks.numtracks < 2:
        continue
    
    # Seleccionar los dos primeros muones
    px1_mu, py1_mu, pz1_mu = event_muons.muon_px[0], event_muons.muon_py[0], event_muons.muon_pz[0]
    px2_mu, py2_mu, pz2_mu = event_muons.muon_px[1], event_muons.muon_py[1], event_muons.muon_pz[1]
    
    # Energía de cada muón
    E1_mu = math.sqrt(px1_mu**2 + py1_mu**2 + pz1_mu**2 + mass_muon**2)
    E2_mu = math.sqrt(px2_mu**2 + py2_mu**2 + pz2_mu**2 + mass_muon**2)
    
    # Momento total y masa invariante
    Px_mu = px1_mu + px2_mu
    Py_mu = py1_mu + py2_mu
    Pz_mu = pz1_mu + pz2_mu
    E_total_mu = E1_mu + E2_mu
    M_inv_mu = math.sqrt(E_total_mu**2 - (Px_mu**2 + Py_mu**2 + Pz_mu**2))
    masses_muons.append(M_inv_mu)
    
    # Seleccionar los dos primeros tracks
    px1_tr, py1_tr, pz1_tr = event_tracks.track_px[0], event_tracks.track_py[0], event_tracks.track_pz[0]
    px2_tr, py2_tr, pz2_tr = event_tracks.track_px[1], event_tracks.track_py[1], event_tracks.track_pz[1]
    
    # Energía de cada kaón
    E1_tr = math.sqrt(px1_tr**2 + py1_tr**2 + pz1_tr**2 + mass_kaon**2)
    E2_tr = math.sqrt(px2_tr**2 + py2_tr**2 + pz2_tr**2 + mass_kaon**2)
    
    # Momento total y masa invariante
    Px_tr = px1_tr + px2_tr
    Py_tr = py1_tr + py2_tr
    Pz_tr = pz1_tr + pz2_tr
    E_total_tr = E1_tr + E2_tr
    M_inv_tr = math.sqrt(E_total_tr**2 - (Px_tr**2 + Py_tr**2 + Pz_tr**2))
    masses_tracks.append(M_inv_tr)

# Crear histogramas ROOT
hist_muons = ROOT.TH1F("mass_hist_muons", "Masa Invariante de Muones;Masa [GeV/c^2];Eventos", 50, 2.8, 3.3)
hist_tracks = ROOT.TH1F("mass_hist_tracks", "Masa Invariante de Tracks;Masa [GeV/c^2];Eventos", 50, 0.9, 1.5)

# Llenar histogramas
for mass in masses_muons:
    hist_muons.Fill(mass)
for mass in masses_tracks:
    hist_tracks.Fill(mass)

# Dibujar y guardar las distribuciones
canvas = ROOT.TCanvas("canvas", "Canvas", 1200, 600)
canvas.Divide(2, 1)

canvas.cd(1)
hist_muons.SetLineColor(ROOT.kBlue)
hist_muons.Draw("E")

canvas.cd(2)
hist_tracks.SetLineColor(ROOT.kRed)
hist_tracks.Draw("E")

canvas.SaveAs("mass_invariant_muons_tracks.png")

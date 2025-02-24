import ROOT
import numpy as np
from itertools import combinations

# Cargar el archivo ROOT
file = ROOT.TFile("muonia_1_1_output.root")
tree_tracks = file.Get("mytracks/Events")  # Árbol con tracks (kaones)
tree_muons = file.Get("mymuons/Events")  # Árbol con muones

# Constantes físicas
M_K = 0.493677  # Masa del kaón (GeV)
M_JPSI = 3.0969  # Masa del J/psi (GeV)

# Lista para almacenar masas del B+
b_masses = []

# Recorrer eventos
for event in range(tree_tracks.GetEntries()):
    tree_tracks.GetEntry(event)
    tree_muons.GetEntry(event)

    # --- SELECCIÓN DE MUONES PARA J/ψ ---
    muons = []
    for i in range(tree_muons.numbermuon):
        px = tree_muons.muon_px[i]
        py = tree_muons.muon_py[i]
        pz = tree_muons.muon_pz[i]
        charge = tree_muons.muon_ch[i]
        muons.append((charge, px, py, pz))

    jpsi_candidates = []
    for mu1, mu2 in combinations(muons, 2):
        if mu1[0] + mu2[0] == 0:  # Cargas opuestas
            px = mu1[1] + mu2[1]
            py = mu1[2] + mu2[2]
            pz = mu1[3] + mu2[3]
            E1 = np.sqrt(mu1[1]**2 + mu1[2]**2 + mu1[3]**2 + 0.1057**2)
            E2 = np.sqrt(mu2[1]**2 + mu2[2]**2 + mu2[3]**2 + 0.1057**2)
            E = E1 + E2
            mass = np.sqrt(E**2 - (px**2 + py**2 + pz**2))

            if abs(mass - M_JPSI) < 0.05:  # Selección de J/psi
                jpsi_candidates.append((px, py, pz, E))

    if not jpsi_candidates:
        continue  # Si no hay J/psi, pasar al siguiente evento

    # --- SELECCIÓN DE KAONES ---
    num_tracks = tree_tracks.numtracks
    tracks = []
    
    for i in range(num_tracks):
        pt = tree_tracks.track_pt[i]
        charge = tree_tracks.track_charge[i]
        px = tree_tracks.track_px[i]
        py = tree_tracks.track_py[i]
        pz = tree_tracks.track_pz[i]

        if pt > 1.0:  # Selección de kaones (pT > 1 GeV)
            tracks.append((charge, px, py, pz))

    # Buscar combinaciones de 3 tracks con carga total ±1
    for k1, k2, k3 in combinations(tracks, 3):
        if k1[0] + k2[0] + k3[0] == 1 or k1[0] + k2[0] + k3[0] == -1:
            
            # Calcular masas invariante de pares K+K- y seleccionar la de menor masa
            def invariant_mass(p1, p2, mass=M_K):
                E1 = np.sqrt(p1[1]**2 + p1[2]**2 + p1[3]**2 + mass**2)
                E2 = np.sqrt(p2[1]**2 + p2[2]**2 + p2[3]**2 + mass**2)
                px = p1[1] + p2[1]
                py = p1[2] + p2[2]
                pz = p1[3] + p2[3]
                E = E1 + E2
                return np.sqrt(E**2 - (px**2 + py**2 + pz**2))

            mKK1 = invariant_mass(k1, k2)
            mKK2 = invariant_mass(k2, k3)
            mKK3 = invariant_mass(k1, k3)

            # Seleccionar la menor masa invariante
            phi_cand = min([mKK1, mKK2, mKK3])
            if 1.008 < phi_cand < 1.035:  # Criterio del paper
                
                # --- RECONSTRUCCIÓN DEL B+ ---
                for jpsi in jpsi_candidates:
                    px_B = jpsi[0] + k1[1] + k2[1] + k3[1]
                    py_B = jpsi[1] + k1[2] + k2[2] + k3[2]
                    pz_B = jpsi[2] + k1[3] + k2[3] + k3[3]
                    E_B = jpsi[3] + np.sqrt(k1[1]**2 + k1[2]**2 + k1[3]**2 + M_K**2) \
                                  + np.sqrt(k2[1]**2 + k2[2]**2 + k2[3]**2 + M_K**2) \
                                  + np.sqrt(k3[1]**2 + k3[2]**2 + k3[3]**2 + M_K**2)

                    mass_B = np.sqrt(E_B**2 - (px_B**2 + py_B**2 + pz_B**2))
                    b_masses.append(mass_B)

# --- GRAFICAR LA DISTRIBUCIÓN DE MASA DEL B+ ---
if len(b_masses) > 0:
    c = ROOT.TCanvas("c", "Masa Invariante del B+")
    h = ROOT.TH1F("h", "Masa Invariante de J/psi K+K-K+", 50, 5.15, 5.45)
    
    for mass in b_masses:
        h.Fill(mass)
    
    h.SetXTitle("m(J/ψ K+ K- K+) [GeV]")
    h.SetYTitle("Candidates / 5 MeV")
    h.SetLineColor(ROOT.kBlue)
    h.SetLineWidth(2)
    
    h.Draw()
    c.SaveAs("Bplus_mass_distribution.png")
else:
    print("No se encontraron candidatos a B+ en los eventos seleccionados.")


#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Candidate/interface/VertexCompositeCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/VertexReco/interface/Vertex.h"

#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"

class BplusAnalyzer : public edm::EDAnalyzer {
public:
    explicit BplusAnalyzer(const edm::ParameterSet&);
    ~BplusAnalyzer();

    virtual void beginJob();
    virtual void analyze(const edm::Event&, const edm::EventSetup&);
    virtual void endJob();

private:
    edm::InputTag vtxTag_;
    edm::InputTag beamSpotTag_;
    edm::InputTag muonTag_;
    edm::InputTag trackTag_;
};

BplusAnalyzer::BplusAnalyzer(const edm::ParameterSet& iConfig)
    : vtxTag_(iConfig.getParameter<edm::InputTag>("vertices")),
      beamSpotTag_(iConfig.getParameter<edm::InputTag>("beamSpot")),
      muonTag_(iConfig.getParameter<edm::InputTag>("muons")),
      trackTag_(iConfig.getParameter<edm::InputTag>("tracks")) {}

void BplusAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
    edm::Handle<reco::BeamSpot> beamSpot;
    iEvent.getByLabel(beamSpotTag_, beamSpot);

    edm::Handle<reco::VertexCollection> vertices;
    iEvent.getByLabel(vtxTag_, vertices);

    edm::Handle<std::vector<reco::Muon>> muons;
    iEvent.getByLabel(muonTag_, muons);

    edm::Handle<std::vector<reco::Track>> tracks;
    iEvent.getByLabel(trackTag_, tracks);

    if (!vertices.isValid() || !beamSpot.isValid() || !muons.isValid() || !tracks.isValid()) return;

    for (size_t i = 0; i < muons->size(); i++) {
        for (size_t j = i + 1; j < muons->size(); j++) {
            const reco::Muon& mu1 = (*muons)[i];
            const reco::Muon& mu2 = (*muons)[j];

            if (mu1.charge() + mu2.charge() != 0) continue;

            LorentzVector jpsiP4 = mu1.p4() + mu2.p4();
            double m_jpsi = jpsiP4.mass();

            if (fabs(m_jpsi - 3.097) > 0.15) continue;
            if (jpsiP4.pt() < 6.9) continue;

            KalmanVertexFitter fitter;
            std::vector<reco::TransientTrack> tracksVec;
            tracksVec.push_back(reco::TransientTrack(mu1.track(), nullptr));
            tracksVec.push_back(reco::TransientTrack(mu2.track(), nullptr));

            TransientVertex jpsiVertex = fitter.vertex(tracksVec);

            if (!jpsiVertex.isValid()) continue;

            double chi2Prob = TMath::Prob(jpsiVertex.totalChiSquared(), jpsiVertex.degreesOfFreedom());
            if (chi2Prob < 0.005) continue;

            double dx = jpsiVertex.position().x() - beamSpot->position().x();
            double dy = jpsiVertex.position().y() - beamSpot->position().y();
            double Lxy = sqrt(dx * dx + dy * dy);
            double sigmaLxy = sqrt(pow(jpsiVertex.positionError().r(), 2) + pow(beamSpot->BeamWidthX(), 2));

            if (Lxy / sigmaLxy < 3.0) continue;

            double px = jpsiP4.px();
            double py = jpsiP4.py();
            double dotProduct = (px * dx + py * dy) / (sqrt(px*px + py*py) * sqrt(dx*dx + dy*dy));

            if (dotProduct < 0.9) continue;

            edm::LogInfo("BplusAnalyzer") << "J/ψ encontrado con masa " << m_jpsi;
        }
    }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(BplusAnalyzer);

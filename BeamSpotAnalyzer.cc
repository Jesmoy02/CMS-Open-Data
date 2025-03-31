// -*- C++ -*-
//
// Package:    BeamSpotAnalyzer
// Class:      BeamSpotAnalyzer
// 
/**\class BeamSpotAnalyzer BeamSpotAnalyzer.cc PhysObjectExtractorTool/BeamSpotAnalyzer/src/BeamSpotAnalyzer.cc

 Description: Accesses and prints the beam spot information from the event

 Implementation:
     This analyzer fetches the beam spot information for each event
     and prints the values of x0, y0, z0, sigmaZ, etc.
*/
//
// Original Author:  
//         Created:  Sat Mar 22 23:34:23 CET 2025
// $Id$
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"

//
// class declaration
//

class BeamSpotAnalyzer : public edm::EDAnalyzer {
   public:
      explicit BeamSpotAnalyzer(const edm::ParameterSet&);
      ~BeamSpotAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob();
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob();

      // ----------member data ---------------------------
      edm::InputTag beamSpotTag_;
      TTree *mtree;

      float x0_, y0_, z0_;
      float sigmaz_;
      float dxdz_;
      float BeamWidthX_;
      float BeamWidthY_;
};

//
// constructors and destructor
//
BeamSpotAnalyzer::BeamSpotAnalyzer(const edm::ParameterSet& iConfig)
: beamSpotTag_(iConfig.getParameter<edm::InputTag>("beamSpot"))
{
   edm::Service<TFileService> fs;
   mtree = fs->make<TTree>("Events", "Beam Spot Data");

   mtree->Branch("x0", &x0_, "x0/F");
   mtree->Branch("y0", &y0_, "y0/F");
   mtree->Branch("z0", &z0_, "z0/F");
   mtree->Branch("sigmaZ", &sigmaz_, "sigmaZ/F");
   mtree->Branch("dxdz", &dxdz_, "dxdz/F");
   mtree->Branch("BeamWidthX", &BeamWidthX_, "BeamWidthX/F");
   mtree->Branch("BeamWidthY", &BeamWidthY_, "BeamWidthY/F");
}

BeamSpotAnalyzer::~BeamSpotAnalyzer() {}

//
// member functions
//

// ------------ method called for each event  ------------
void BeamSpotAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   edm::Handle<reco::BeamSpot> beamSpotHandle;
   iEvent.getByLabel(beamSpotTag_, beamSpotHandle); // <-- Volvemos a usar getByLabel()

   if (beamSpotHandle.isValid()) {
      const reco::BeamSpot& beamSpot = *beamSpotHandle;

      x0_ = beamSpot.x0();
      y0_ = beamSpot.y0();
      z0_ = beamSpot.z0();
      sigmaz_ = beamSpot.sigmaZ();
      dxdz_ = beamSpot.dxdz();
      BeamWidthX_ = beamSpot.BeamWidthX();
      BeamWidthY_ = beamSpot.BeamWidthY();

      mtree->Fill();
   }
}

// ------------ method called once each job just before starting event loop  ------------
void BeamSpotAnalyzer::beginJob() {}

// ------------ method called once each job just after ending the event loop  ------------
void BeamSpotAnalyzer::endJob() {}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void BeamSpotAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
   edm::ParameterSetDescription desc;
   desc.add<edm::InputTag>("beamSpot", edm::InputTag("offlineBeamSpot"));
   descriptions.add("beamSpotAnalyzer", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BeamSpotAnalyzer);

#include <iostream>
#include <vector>
#include <TSystem.h>

#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDFHelpers.hxx"
#include "ROOT/RVec.hxx"
#include "Math/LorentzVector.h"
#include "Math/Vector4D.h"

using namespace ROOT::VecOps;
using ROOT::RDF::RSampleInfo;
using namespace ROOT::RDF::Experimental;
using PtEtaPhiMVectorD = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

template <typename T>
RVec<T> dimuonKinematic(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi)
{
   T muonRestMass = 0.1056583715;
   PtEtaPhiMVectorD P(0.,0.,0.,0.);
   PtEtaPhiMVectorD p1(pt[0], eta[0], phi[0],  muonRestMass);
   PtEtaPhiMVectorD p2(pt[1], eta[1], phi[1], muonRestMass);

  P = p1 + p2;
  T Pt = P.Pt();
  T Pz = P.Pz();
  T M = P.M();
  T E = P.E();
  T Eta = P.Eta();
  T Y = P.Rapidity();
  T Phi = P.Phi();
  RVec<T> dimuon {Pt, Eta, Phi, M, Y};

   return dimuon;
}

void Cut(std::string inf, std::string type)
{
  ROOT::RDataFrame d("Events", inf);  
  ROOT::RDF::Experimental::AddProgressBar(d);
  auto d1 = d
    .Define("dimuonKinematic", dimuonKinematic<float_t>, {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_eta", "ScoutingMuonVtx_phi"} )
    .Define("ScoutingMuonVtxPair_mass", [](RVec<float_t> P){return P[3];}, {"dimuonKinematic"})
    .Define("ScoutingMuonVtxPair_pt", [](RVec<float_t> P){return P[0];}, {"dimuonKinematic"})
    .Define("ScoutingMuonVtxPair_eta", [](RVec<float_t> P){return P[1];}, {"dimuonKinematic"})
    .Define("ScoutingMuonVtxPair_y", [](RVec<float_t> P){return P[4];}, {"dimuonKinematic"})
    .Define("ScoutingMuonVtxPair_phi", [](RVec<float_t> P){return P[2];}, {"dimuonKinematic"})
    .Define("rTrkIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuonVtx_trackIso", "ScoutingMuonVtx_pt"})
    .Define("rECalIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuonVtx_ecalIso", "ScoutingMuonVtx_pt"})
    .Define("rHCalIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuonVtx_hcalIso", "ScoutingMuonVtx_pt"})
    // Skimming
    // Should not be asked for trigger efficiency, biasing the computation.
    .Filter([](Int_t n){ return n == 2;}, {"nScoutingMuonVtx"}, "Exactly two muons")
    .Filter([](RVec<float_t> eta, RVec<float_t> pt){return All(abs(eta) < 2.4) && All(pt > 5.0) ;}, {"ScoutingMuonVtx_eta", "ScoutingMuonVtx_pt"}, "In Eta and Pt Range")
    .Filter([](float_t M){ return (M > 5 && M < 120); }, {"ScoutingMuonVtxPair_mass"}, "Dimuon Mass in the analysis range")
    ;


  std::string var =  "^run$|^event$|^luminosityBlock$|^(.|)ScoutingMuonVtx_.*$|^n.*$|^L1_DoubleMu.*$|^DST.*$|^genWeight$|^GenPart_.*$|^(.|)ScoutingPFJet.*$";

  if ( !type.compare("Data") ) {
    auto d2 = d1.Define("genWeight", [](){return 1.0f;});

  d2.Snapshot("Events", "output.root", var);
  d2.Report()->Print();
  }
  else {
    auto d2 = d1;

  d2.Snapshot("Events", "output.root", var);
  d2.Report()->Print();
  }
}

int main(int argc, char *argv[])
{
  Cut(argv[1], argv[2]);
}

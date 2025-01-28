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
  T Y = log( (E + Pz) / pow( pow(M, 2) + pow(Pt, 2) , 1/2) );
  T Phi = P.Phi();
  RVec<T> dimuon {Pt, Eta, Phi, M, Y};
   
   return dimuon;
}

void Cut(std::string inf, std::string type)
{
  ROOT::RDataFrame d("Events", inf);
  auto d1 = d
    .Define("dimuonKinematic", dimuonKinematic<float_t>, {"ScoutingMuon_pt", "ScoutingMuon_eta", "ScoutingMuon_phi"} )
    .Define("ScoutingMuon_diMass", [](RVec<float_t> P){return P[3];}, {"dimuonKinematic"})
    .Define("ScoutingMuon_diPt", [](RVec<float_t> P){return P[0];}, {"dimuonKinematic"})
    .Define("ScoutingMuon_diEta", [](RVec<float_t> P){return P[1];}, {"dimuonKinematic"})
    .Define("ScoutingMuon_diY", [](RVec<float_t> P){return P[4];}, {"dimuonKinematic"})
    .Define("ScoutingMuon_diPhi", [](RVec<float_t> P){return P[2];}, {"dimuonKinematic"})
    .Define("rTrkIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuon_trackIso", "ScoutingMuon_pt"})
    .Define("rECalIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuon_ecalIso", "ScoutingMuon_pt"})
    .Define("rHCalIso", [](RVec<float> i, RVec<float> pt){ return i/pt ;}, {"ScoutingMuon_hcalIso", "ScoutingMuon_pt"})
    // Skimming
    // Should not be asked for trigger efficiency, biasing the computation.
    .Filter([](Int_t n){ return n == 2;}, {"nScoutingMuon"}, "Exactly two muons")
    .Filter([](RVec<float_t> eta, RVec<float_t> pt){return All(abs(eta) < 2.4) && All(pt > 5.0) ;}, {"ScoutingMuon_eta", "ScoutingMuon_pt"}, "In Eta and Pt Range")
    .Filter([](float_t M){ return M > 10 ; }, {"ScoutingMuon_diMass"}, "Dimuon Mass > 10 Gev")
    ;


  std::string var =  "^run$|^event$|^luminosityBlock$|^(.|)L1Mu.*$|^(.|)ScoutingMuon.*$| \
          nScoutingDisplacedVertex|^L1_DoubleMu.*$|^DST.*$|genWeight|^Gen.*$";
  
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
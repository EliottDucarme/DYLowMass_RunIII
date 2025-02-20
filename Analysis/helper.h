#include "ROOT/RVec.hxx"
using namespace ROOT::VecOps;


RVec<float> dimuonKinematics(RVec<float>pt , RVec<float> eta, RVec<float> phi)
{
    using PtEtaPhiMVectorD = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;
    float muonRestMass = 0.1056583715;
    if (pt.size() != 2){
      return {-100, -100, -100, -100, -100};
    }
    else{
    PtEtaPhiMVectorD P(0.,0.,0.,0.);

    PtEtaPhiMVectorD p1(pt[0], eta[0], phi[0], muonRestMass);
    PtEtaPhiMVectorD p2(pt[1], eta[1], phi[1], muonRestMass);

    P = p1 + p2;
    float Pt = P.Pt();
    float Pz = P.Pz();
    float M = P.M();
    float E = P.E();
    float Eta = P.Eta();
    float Y = 0.5*log((E + Pz)/(E - Pz));
    float Phi = P.Phi();

    RVec<float> dimuon {Pt, Eta, Phi, M, Y};

    return dimuon;

    }

 };

RVec<int> findGenMuons(RVec<int> Ids, RVec<int> status, RVec<int> flags)
{
  int n = Ids.size();
  RVec<int> genMu_indices;
  for (int i=0; i < n; i++){
    // Is a gen-level muon
    if ( !(std::abs(Ids[i]) == 13) ) continue;

    // is a stable particle
    if ( status[i] != 1 ) continue;

    // select a true DY pair looking at status flag
    // -- flags to select true DY pairs
    // -- 1: isPrompt
    // -- 256: fromHardProcess
    // -- 8192: isLastCopy
    if (!(flags[i] & 1 )) continue;
    if (!(flags[i] & 256)) continue;
    if (!(flags[i] & 8192)) continue;
    genMu_indices.push_back(i);
  }

  return genMu_indices;
};

double reweighting(double xsec, double sumws, double weight, std::string type){
  // lumi is in /pb
  // double lumi = 3069.910729; // following brilcalc
  double lumi = 3082.8; // following GoldenJSON
  if (type.find("MC") != std::string::npos){
  double sign = weight/abs(weight);
  return lumi*xsec*sign/sumws;
  }
  else return 1.0;
};

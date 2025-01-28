#include "ROOT/RVec.hxx"
using namespace ROOT::VecOps;

RVec<float> dimuonKinematics(RVec<float>pt , RVec<float> eta, RVec<float> phi)
{
    using PtEtaPhiMVectorD = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;
    float muonRestMass = 0.1056583715;

    PtEtaPhiMVectorD P(0.,0.,0.,0.);
    
    PtEtaPhiMVectorD p1(pt[0], eta[0], phi[0], muonRestMass);
    PtEtaPhiMVectorD p2(pt[1], eta[1], phi[1], muonRestMass);

    P = p1 + p2;
    float Pt = P.Pt();
    float Pz = P.Pz();
    float M = P.M();
    float E = P.E();
    float Eta = P.Eta();
    float Y = log( (E + Pz) / pow( pow(M, 2) + pow(Pt, 2) , 1/2) );
    float Phi = P.Phi();
        
    RVec<float> dimuon {Pt, Eta, Phi, M, Y};
    
    return dimuon;
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
    // -- 4096: isFirstCopy
    // -- 8192: isLastCopy
    if (!(flags[i] & 1 )) continue;
    if (!(flags[i] & 256)) continue;
    if (!(flags[i] & 4096)) continue;
    if (!(flags[i] & 8192)) continue;
    genMu_indices.push_back(i);
  }
  if (genMu_indices.size() > 2) std::cout << "mamma mia !" << std::endl;
  
  return genMu_indices;
};

double reweighting(double xsec, double sumws, double weight, std::string type){
  if (type.find("MC") != std::string::npos){
  double sign = weight/abs(weight);
  return double(3082.8)*xsec*sign/sumws;
  } 
  else return 1.0;
};


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
    float Y = P.Rapidity();
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
    // -- 8192: isLastCopy
    if (!(flags[i] & 1 )) continue;
    if (!(flags[i] & 256)) continue;
    if (!(flags[i] & 8192)) continue;
    genMu_indices.push_back(i);
  }

  return genMu_indices;
};

double reweighting(double xsec, double sumws, Float_t weight, string isMC, double lumi){
  // lumi is in /pb
  // double lumi = 11417.484664139 ; // 2024 following PDMV report
  // double lumi = 3079; // 2022 follozing trust-me-bro
  if ( isMC == "True"){
    Float_t sign = weight/abs(weight);
    return lumi*xsec*sign/sumws;
  }
  else return 1.0;
};

RVec<int> TruePFJet(RVec<float_t> Jet_pt, RVec<float_t> Jet_eta, RVec<float_t> Jet_phi, 
                RVec<float_t> Mu_eta, RVec<float_t> Mu_phi ){

  int n_jet = Jet_eta.size();
  int n_mu = Mu_eta.size();
  bool veto = 1;
  RVec<int> Jet_ind;
  
  // cout << "N Jet : " << n_jet << endl;
  for (int i=0; i < n_jet; i++){
    veto = 1;
    // cout << "Jet : " << i << " Selected " << Jet_ind << endl;
    // cout << Jet_pt[i] << " " <<  Jet_eta[i] << endl;

    // Jet is in range for analysis
    if ((Jet_pt[i] < 30) || (std::abs(Jet_eta[i]) > 2.5)) {
      Jet_ind.push_back(0);
      veto = 0;
      // cout << "Is not a valid jet !" << endl;
      continue;
    }

    // check if muon is not mistaken for a jet
    for (int j=0; j < n_mu; j++){

      float_t dR = sqrt(pow((Jet_eta[i] - Mu_eta[j]), 2) + pow((Jet_phi[i] - Mu_phi[j]), 2));
      // cout << "Muon : " << j << " Delta R " << dR << endl;

      if (dR < 0.1) {
        Jet_ind.push_back(0);
        veto = 0;
        // cout << "Is a muon !" << endl;
        break;
      }
    }

    // wooh is a jet
    if (veto == 1){ 
      Jet_ind.push_back(1);
      // cout << "Is a Jet !" << endl ;
    }
  }
  // cout << "TruePFJet Indices : " << Jet_ind.size() << endl;
  return Jet_ind;
};

Float_t Sum(RVec<Float_t> col){
  Float_t sum = 0;
  for(int i; i < col.size(); i++){
    sum += col[i];
  }
  return sum;
}

Float_t cosThetaCS(RVec<Float_t> pt_mu, RVec<Float_t> eta_mu, RVec<Float_t> phi_mu , RVec<Float_t> m_mu, 
                    Float_t pt_pair, Float_t mass_pair, Float_t rapidity_pair)
{
  using PtEtaPhiMVectorD = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

  PtEtaPhiMVectorD mu1(pt_mu[0], eta_mu[0], phi_mu[0], m_mu[0]);
  PtEtaPhiMVectorD mu2(pt_mu[1], eta_mu[1], phi_mu[1], m_mu[1]);

  Float_t pp1 = (mu1.E() + mu1.Pz())/sqrt(2);
  Float_t pm1 = (mu1.E() - mu1.Pz())/sqrt(2);

  Float_t pp2 = (mu2.E() + mu2.Pz())/sqrt(2);
  Float_t pm2 = (mu2.E() - mu2.Pz())/sqrt(2);

  Float_t cos = 2 * (pp1 * pm2 - pp2 * pm1)/sqrt(pow(mass_pair, 2) * (pow(mass_pair, 2) + pow(pt_pair, 2))) * rapidity_pair/abs(rapidity_pair);

  return cos;
}

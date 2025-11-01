#!/usr/bin/env python
import ROOT
ROOT.gInterpreter.ProcessLine('#include "helper.h"')

# Declaration of ranges for each histogram type
default_nbins = 100
ranges = {
  "ScoutingMuonNoVtxPair_Pt" : ("ScoutingMuonNoVtxPair_pt", default_nbins, 0.0, 50.0),
  "ScoutingMuonNoVtxPair_PtLow" : ("ScoutingMuonNoVtxPair_pt", default_nbins, 0.0, 15.0),
  "ScoutingMuonNoVtxPair_Y" : ("ScoutingMuonNoVtxPair_Y", default_nbins, -2.5, 2.5),
  "ScoutingMuonNoVtxPair_mass" : ("ScoutingMuonNoVtxPair_mass", default_nbins, 10.0, 110.0),
  "ScoutingMuonNoVtxPair_massZ" : ("ScoutingMuonNoVtxPair_mass", default_nbins, 76.0, 106.0),
  "ScoutingMuonNoVtxPair_eta" : ("ScoutingMuonNoVtxPair_eta", default_nbins, -5.0, 5.0),

  "ScoutingMuonNoVtx_trk_dxy" : ("ScoutingMuonNoVtx_trk_dxy", default_nbins, -20.0, 20.0),
  "ScoutingMuonNoVtx_trk_dxy_short" : ("ScoutingMuonNoVtx_trk_dxy", default_nbins, -5.0, 5.0),
  "ScoutingMuonNoVtx_trk_dz" : ("ScoutingMuonNoVtx_trk_dz", default_nbins, -20.0, 20.0),

  "ScoutingMuonNoVtxLead_pt" : ("ScoutingMuonNoVtxSub_pt", default_nbins, 5.0, 105.0),
  "ScoutingMuonNoVtxSub_pt" : ("ScoutingMuonNoVtxSub_pt", default_nbins, 5.0, 105.0),
  "ScoutingMuonNoVtxSub_eta" : ("ScoutingMuonNoVtxSub_eta", default_nbins, -2.5, 2.5),
  "ScoutingMuonNoVtxLead_eta" : ("ScoutingMuonNoVtxLead_eta", default_nbins, -2.5, 2.5),
  "ScoutingMuonNoVtxLead_phi" : ("ScoutingMuonNoVtxLead_phi",default_nbins, -3.15, 3.15),
  "ScoutingMuonNoVtxSub_phi" : ("ScoutingMuonNoVtxSub_phi",default_nbins, -3.15, 3.15),
  "ScoutingMuonNoVtx_deltaPhi" : ("ScoutingMuonNoVtx_deltaPhi",default_nbins, -6.5, 6.5),
  "ScoutingMuonNoVtx_deltaEta" : ("ScoutingMuonNoVtx_deltaEta",default_nbins, -5, 5),
  "ScoutingMuonNoVtx_deltaR" : ("ScoutingMuonNoVtx_deltaR",default_nbins, 0, 6),

  "HCalIsolation" : ("ScoutingMuonNoVtx_hcalIso", default_nbins, -5.0, 40),
  "ECalIsolation" : ("ScoutingMuonNoVtx_ecalIso", default_nbins, -5.0, 40),
  "trkIsolation" : ("ScoutingMuonNoVtx_trackIso", default_nbins, 0.0, 50),
  "relTrkIso" : ("rTrkIso", default_nbins, 0, 1),
  "relHcalIso" : ("rHcalIso", default_nbins, 0.0, 1),
  "relEcalIso" : ("rEcalIso", default_nbins, 0.0, 1),

  "nTruePFJet" : ("nTruePFJet", default_nbins, 0.0, 100.0),
  "nScoutingPFJet" : ("nScoutingPFJet", default_nbins, 0.0, 100.0),
  "TruePFJet_HT" : ("TruePFJet_HT", default_nbins, 0.0, 1000.0),
  "TruePFJet_pt" : ("TruePFJet_pt", default_nbins, 0.0, 400.0),

  "nScoutingPrimaryVertex" : ("nScoutingPrimaryVertex", default_nbins, 0.0, 100.0),
  "Strip_Hit" : ("ScoutingMuonNoVtx_nValidStripHits", 25, 0, 25),
  "Pixel_Hit" : ("ScoutingMuonNoVtx_nPixelLayersWithMeasurement", 10, 0, 10),
  "Tracker_Hit" : ("ScoutingMuonNoVtx_nTrackerLayersWithMeasurement", 18, 0, 18),
  "MuonChamber_Hit" : ("ScoutingMuonNoVtx_nRecoMuonChambers", 50, 0, 51),
  "MatchedStation" : ("ScoutingMuonNoVtx_nRecoMuonMatchedStations", 5, 0, 5),
}


def bookHist(d, name, range_): #Histo booking
  return d.Histo1D(ROOT.ROOT.RDF.TH1DModel(name, name, range_[1], range_[2], range_[3]),\
                    range_[0], "norm")


def writeHist(h, name): #Write it !
  h.SetName(name)
  h.Write()

def main():
  # Output file
  outf_name = "Hist/histograms.root"
  outf = ROOT.TFile(outf_name, "RECREATE")

  # Create the dataframe with the .json spec file
  ROOT.EnableImplicitMT(16)
  d = ROOT.RDF.Experimental.FromSpec("samples_2024.json")
  ROOT.RDF.Experimental.ProgressHelper.ProgressHelper(100000, progressBarWidth=5, useColors=True)
  # d = d.Range(1000000)
  ROOT.RDF.Experimental.AddProgressBar(d)

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("nevents")')
  d = d.DefinePerSample("isMC", 'rdfsampleinfo_.GetS("isMC")')
  d = d.DefinePerSample("sample", 'rdfsampleinfo_.GetS("sample")')
  # d = d.DefaultValueFor("genWeight", 1.0) 
  # d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 11417.484664139)', {"xsec", "sumws", "genWeight", "isMC"}) # Full 2024I
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 839.477313932)', {"xsec", "sumws", "genWeight", "isMC"}) # 1 large runs  


  # Define new variables
  d = d.Define("ind", 'ROOT::VecOps::Argsort(ScoutingMuonNoVtx_pt)', {"ScoutingMuonNoVtx_pt"})
  d = d.Define("ScoutingMuonNoVtxLead_pt", "ScoutingMuonNoVtx_pt[ind[1]]").Define("ScoutingMuonNoVtxSub_pt", "ScoutingMuonNoVtx_pt[ind[0]]")
  d = d.Define("ScoutingMuonNoVtxLead_eta", "ScoutingMuonNoVtx_eta[ind[1]]").Define("ScoutingMuonNoVtxSub_eta", "ScoutingMuonNoVtx_eta[ind[0]]")
  d = d.Define("ScoutingMuonNoVtxLead_phi", "ScoutingMuonNoVtx_phi[ind[1]]").Define("ScoutingMuonNoVtxSub_phi", "ScoutingMuonNoVtx_phi[ind[0]]")
  d = d.Define("ScoutingMuonNoVtx_deltaPhi", "ScoutingMuonNoVtxLead_phi - ScoutingMuonNoVtxSub_phi")
  d = d.Define("ScoutingMuonNoVtx_deltaEta", "ScoutingMuonNoVtxLead_eta - ScoutingMuonNoVtxSub_eta")
  d = d.Define("ScoutingMuonNoVtx_deltaR", "sqrt(pow(ScoutingMuonNoVtx_deltaPhi, 2) + pow(ScoutingMuonNoVtx_deltaEta, 2))")

  d = d.Define("dimuonKinematics", 'dimuonKinematics(ScoutingMuonNoVtx_pt, ScoutingMuonNoVtx_eta, ScoutingMuonNoVtx_phi)')
  d = d.Define("ScoutingMuonNoVtxPair_pt", "dimuonKinematics[0]")
  d = d.Define("ScoutingMuonNoVtxPair_eta", "dimuonKinematics[1]")
  d = d.Define("ScoutingMuonNoVtxPair_phi", "dimuonKinematics[2]")
  d = d.Define("ScoutingMuonNoVtxPair_mass", "dimuonKinematics[3]")
  d = d.Define("ScoutingMuonNoVtxPair_Y", "dimuonKinematics[4]")

  d = d.Define("rTrkIso", "ScoutingMuonNoVtx_trackIso/ScoutingMuonNoVtx_pt" , {"ScoutingMuonNoVtx_pt", "ScoutingMuonNoVtx_trackIso"})
  d = d.Define("rEcalIso", "ScoutingMuonNoVtx_ecalIso/ScoutingMuonNoVtx_pt" , {"ScoutingMuonNoVtx_pt", "ScoutingMuonNoVtx_ecalIso"})
  d = d.Define("rHcalIso", "ScoutingMuonNoVtx_hcalIso/ScoutingMuonNoVtx_pt" , {"ScoutingMuonNoVtx_pt", "ScoutingMuonNoVtx_hcalIso"})

  d = d.Define("TruePFJet_ind", 'TruePFJet(ScoutingPFJet_pt, ScoutingPFJet_eta, ScoutingPFJet_phi, ScoutingMuonNoVtx_eta, ScoutingMuonNoVtx_phi)')
  d = d.Define("TruePFJet_pt", 'ScoutingPFJet_pt[TruePFJet_ind]')
  d = d.Define("nTruePFJet", "TruePFJet_pt.size()")
  d = d.Define("TruePFJet_HT", 'Sum(TruePFJet_pt)')

  # # # # d = d.Define("TruePFJetRecluster_ind", 'TruePFJet(ScoutingPFJetRecluster_pt, ScoutingPFJetRecluster_eta, ScoutingPFJetRecluster_phi, ScoutingMuonNoVtx_eta, ScoutingMuonNoVtx_phi)')
  # # # d = d.Define("TruePFJetRecluster_pt", 'ScoutingPFJetRecluster_pt[TruePFJetRecluster_ind]')
  # # d = d.Define("nTruePFJetRecluster", "TruePFJetRecluster_pt.size()")
  # # d = d.Define("TruePFJetRecluster_HT", 'Sum(TruePFJetRecluster_pt)')

  # Filter the events
  d = d.Filter("DST_PFScouting_DoubleMuon", "HLT Scouting Stream")  #2024
  # d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream") #2022
  d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")
  d = d.Filter("nScoutingMuonNoVtx == 2")
  d = d.Filter("ScoutingMuonNoVtx_charge[0]*ScoutingMuonNoVtx_charge[1] == -1", "Opposite charge")
  d = d.Filter("abs(ScoutingMuonNoVtx_eta[0]) < 2.0 && abs(ScoutingMuonNoVtx_eta[1]) < 2.0",\
                "eta-cut")
  d = d.Filter("ScoutingMuonNoVtx_pt[0] > 5.0 && ScoutingMuonNoVtx_pt[1] > 5.0", "pt-cut")
  d = d.Filter('All(rTrkIso < 0.03)', "Muons are isolated in the tracker: ")
  d = d.Filter("All(ScoutingMuonNoVtx_trk_chi2/ScoutingMuonNoVtx_trk_ndof < 10)", "Track of the muons are nicely reconstructed")
  # d = d.Filter('All(rEcalIso < 0.4)', "Muons are isolated in the ECAL: ")
  d = d.Filter('ScoutingMuonNoVtxSub_pt/ScoutingMuonNoVtxPair_mass > 0.25')\
      .Filter('ScoutingMuonNoVtxSub_pt/ScoutingMuonNoVtxPair_mass > 0.45', "leptons are decay products of the original boson")

  # Separate samples and add them to the sample list
  samples = []
  dMC = d.Filter('isMC == "True"', "isMC")
  dDY2Mu = dMC.Filter('sample == "DYto2Mu"', "isDY")
  samples.append(("DYto2Mu", dDY2Mu))
  dQCD = dMC.Filter('sample == "QCD"')
  samples.append(("QCD", dQCD))
  dTT = dMC.Filter('sample == "TTto2l2nu"', "is TT MC")
  samples.append(("TT", dTT))
  dDY2Tau = dMC.Filter(('sample == "DYto2Tau"'))
  samples.append(("DYto2Tau", dDY2Tau))
  dD = d.Filter('isMC != "True"')
  dD = dD.Filter("run == 386604")
  samples.append(("Data", dD))

  # Loop over sample to make histograms for each isolation selection
  plots = ranges.keys()
  hists_s = {} # Declare the dictionary where histograms w ill be stored

  for df_label, df in samples :
    # Separate mass windows
    d_ups = df.Filter("ScoutingMuonNoVtxPair_mass < 20 && ScoutingMuonNoVtxPair_mass > 10", "Under Upsilon influence")
    d_QCD = df.Filter("ScoutingMuonNoVtxPair_mass < 50 && ScoutingMuonNoVtxPair_mass > 20", "Bulk")
    d_W = df.Filter("ScoutingMuonNoVtxPair_mass > 50 && ScoutingMuonNoVtxPair_mass < 76", "Under W influence")
    d_Z = df.Filter("ScoutingMuonNoVtxPair_mass > 76 && ScoutingMuonNoVtxPair_mass < 106", "Under Z influence")
    df_massWindows = [
              ("Incl", df),
              ("Upsilon", d_ups),
              ("QCD", d_QCD),
              ("W", d_W),
              ("Z", d_Z)
              ]
    for label_mass, df_mass in df_massWindows :
      if (df_label == "Data" and label_mass == "Incl") : 
        rep = df_mass.Report()
      # Book Histograms for each variable
      for plot in plots :
        hkey = "{}_{}_{}".format(df_label, plot, label_mass)
        print("Booking : ", hkey)
        hists_s[hkey] = bookHist(df_mass, plot, ranges[plot])

  # Write histograms in the file
  for hkey in hists_s :
    print("Writing : ", hkey)
    writeHist(hists_s[hkey], hkey)

  rep.Print()
  outf.Close()

if __name__ == "__main__" :
  main()

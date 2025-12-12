#!/usr/bin/env python
import sys
import ROOT
from cluster import create_connection


# Declaration of ranges for each histogram type
default_nbins = 100
ranges = {
  "ScoutingMuonVtxPair_Pt" : ("ScoutingMuonVtxPair_pt", default_nbins, 0.0, 50.0),
  "ScoutingMuonVtxPair_PtLow" : ("ScoutingMuonVtxPair_pt", default_nbins, 0.0, 15.0),
  "ScoutingMuonVtxPair_Y" : ("ScoutingMuonVtxPair_y", default_nbins, -2.5, 2.5),
  "ScoutingMuonVtxPair_mass" : ("ScoutingMuonVtxPair_mass", default_nbins, 10.0, 110.0),
  "ScoutingMuonVtxPair_massZ" : ("ScoutingMuonVtxPair_mass", default_nbins, 76.0, 106.0),
  "ScoutingMuonVtxPair_eta" : ("ScoutingMuonVtxPair_eta", default_nbins, -5.0, 5.0),
  "ScoutingMuonVtxPair_deltaxy" : ("ScoutingMuonVtxPair_deltaxy", default_nbins, -2.0, 2.0),
  "ScoutingMuonVtxPair_deltaz" : ("ScoutingMuonVtxPair_deltaz", default_nbins, -2.0, 2.0),

  "ScoutingMuonVtx_trk_dxy" : ("ScoutingMuonVtx_trk_dxy", default_nbins, -1.0, 1.0),
  "ScoutingMuonVtx_trk_dxy_short" : ("ScoutingMuonVtx_trk_dxy", default_nbins, -0.3, 0.3),
  "ScoutingMuonVtx_trk_dz" : ("ScoutingMuonVtx_trk_dz", default_nbins, -20.0, 20.0),

  "ScoutingMuonVtxLead_pt" : ("ScoutingMuonVtxSub_pt", default_nbins, 5.0, 105.0),
  "ScoutingMuonVtxSub_pt" : ("ScoutingMuonVtxSub_pt", default_nbins, 5.0, 105.0),
  "ScoutingMuonVtxSub_eta" : ("ScoutingMuonVtxSub_eta", default_nbins, -2.5, 2.5),
  "ScoutingMuonVtxLead_eta" : ("ScoutingMuonVtxLead_eta", default_nbins, -2.5, 2.5),
  "ScoutingMuonVtxLead_phi" : ("ScoutingMuonVtxLead_phi",default_nbins, -3.15, 3.15),
  "ScoutingMuonVtxSub_phi" : ("ScoutingMuonVtxSub_phi",default_nbins, -3.15, 3.15),
  "ScoutingMuonVtx_deltaPhi" : ("ScoutingMuonVtx_deltaPhi",default_nbins, -6.5, 6.5),
  "ScoutingMuonVtx_deltaEta" : ("ScoutingMuonVtx_deltaEta",default_nbins, -5, 5),
  "ScoutingMuonVtx_deltaR" : ("ScoutingMuonVtx_deltaR",default_nbins, 0, 6),
  "ScoutingMuonVtx_cosThetaCS" : ("ScoutingMuonVtx_cosThetaCS", default_nbins, -1, 1),

  "HCalIsolation" : ("ScoutingMuonVtx_hcalIso", default_nbins, -5.0, 40),
  "ECalIsolation" : ("ScoutingMuonVtx_ecalIso", default_nbins, -5.0, 40),
  "trkIsolation" : ("ScoutingMuonVtx_trackIso", default_nbins, 0.0, 50),
  "relTrkIso" : ("rTrkIso", default_nbins, 0, 1),
  "relHCalIso" : ("rHCalIso", default_nbins, 0.0, 1),
  "relECalIso" : ("rECalIso", default_nbins, 0.0, 1),

  "nTruePFJet" : ("nTruePFJet", default_nbins, 0.0, 100.0),
  "nScoutingPFJet" : ("nScoutingPFJet", default_nbins, 0.0, 100.0),
  "TruePFJet_HT" : ("TruePFJet_HT", default_nbins, 0.0, 1000.0),
  "TruePFJet_pt" : ("TruePFJet_pt", default_nbins, 0.0, 400.0),
  "nTruePFJetRecluster" : ("nTruePFJetRecluster", default_nbins, 0.0, 100.0),
  "nScoutingPFJetRecluster" : ("nScoutingPFJetRecluster", default_nbins, 0.0, 100.0),
  "TruePFJetRecluster_HT" : ("TruePFJetRecluster_HT", default_nbins, 0.0, 1000.0),
  "TruePFJetRecluster_pt" : ("TruePFJetRecluster_pt", default_nbins, 0.0, 400.0),

  "nScoutingPrimaryVertex" : ("nScoutingPrimaryVertex", default_nbins, 0.0, 100.0),
  # "ScoutingPrimaryVertex_MuonVtx_dz" : ("ScoutingPrimaryVertex_MuonVtx_dz", default_nbins, -10.0, 10.0),
  # "ScoutingPrimaryVertex_MuonVtx_dxy" : ("ScoutingPrimaryVertex_MuonVtx_dxy", default_nbins, -1.0, 1.0),

  "Strip_Hit" : ("ScoutingMuonVtx_nValidStripHits", 25, 0, 25),
  "Pixel_Hit" : ("ScoutingMuonVtx_nPixelLayersWithMeasurement", 10, 0, 10),
  "Tracker_Hit" : ("ScoutingMuonVtx_nTrackerLayersWithMeasurement", 18, 0, 18),
  "MuonChamber_Hit" : ("ScoutingMuonVtx_nRecoMuonChambers", 50, 0, 51),
  "MatchedStation" : ("ScoutingMuonVtx_nRecoMuonMatchedStations", 5, 0, 5),
}


def bookHist(d, name, range_): #Histo booking
  return d.Histo1D(ROOT.ROOT.RDF.TH1DModel(name, name, range_[1], range_[2], range_[3]),\
                    range_[0], "norm")


def writeHist(h, name): #Write it !
  h.SetName(name)
  h.Write()

def main(executor):
  # Create the dataframe with the .json spec file
  # chose if dask_jobqueue is used to submit to the cluster

  if (executor == "cluster") : 
    client = create_connection()
    d = ROOT.RDF.Experimental.FromSpec("samples_2024_LowPu.json", executor=client, npartitions=100)
    ROOT.RDF.Distributed.DistributeHeaders("helper.h")
  elif (executor == "local") : 
    ROOT.gInterpreter.Declare('#include "helper.h"') 
    ROOT.EnableImplicitMT(16) 
    d = ROOT.RDF.Experimental.FromSpec("samples_2024_LowPu.json")
    # d = d.Range(1000000)
    ROOT.RDF.Experimental.AddProgressBar(d)
    ROOT.RDF.Experimental.ProgressHelper.ProgressHelper(1000000, progressBarWidth=5, useColors=True)
  else :
    print("Use 'local' or 'cluster' for a direct execution or distributed one")
  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("nevents")')
  d = d.DefinePerSample("isMC", 'rdfsampleinfo_.GetS("isMC")')
  d = d.DefinePerSample("sample", 'rdfsampleinfo_.GetS("sample")')
  # d = d.DefaultValueFor("genWeight", 1.0) 
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 11417.506065)', {"xsec", "sumws", "genWeight", "isMC"}) # Full 2024I
  # d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 839.477313932)', {"xsec", "sumws", "genWeight", "isMC"}) # 1 large runs  
  # d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 95.219164827)', {"xsec", "sumws", "genWeight", "isMC"}) # low PU runs  

  # Define new variables
  d = d.Define("ind", 'ROOT::VecOps::Argsort(ScoutingMuonVtx_pt)', {"ScoutingMuonVtx_pt"})
  d = d.Define("ScoutingMuonVtxLead_pt", "ScoutingMuonVtx_pt[ind[1]]").Define("ScoutingMuonVtxSub_pt", "ScoutingMuonVtx_pt[ind[0]]")
  d = d.Define("ScoutingMuonVtxLead_eta", "ScoutingMuonVtx_eta[ind[1]]").Define("ScoutingMuonVtxSub_eta", "ScoutingMuonVtx_eta[ind[0]]")
  d = d.Define("ScoutingMuonVtxLead_phi", "ScoutingMuonVtx_phi[ind[1]]").Define("ScoutingMuonVtxSub_phi", "ScoutingMuonVtx_phi[ind[0]]")
  d = d.Define("ScoutingMuonVtx_deltaPhi", "ScoutingMuonVtxLead_phi - ScoutingMuonVtxSub_phi")
  d = d.Define("ScoutingMuonVtx_deltaEta", "ScoutingMuonVtxLead_eta - ScoutingMuonVtxSub_eta")
  d = d.Define("ScoutingMuonVtx_deltaR", "sqrt(pow(ScoutingMuonVtx_deltaPhi, 2) + pow(ScoutingMuonVtx_deltaEta, 2))")
  d = d.Define("ScoutingMuonVtx_cosThetaCS", 'cosThetaCS(ScoutingMuonVtx_pt, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi, ScoutingMuonVtx_m, ScoutingMuonVtxPair_pt, ScoutingMuonVtxPair_mass, ScoutingMuonVtxPair_y)')

  # d = d.Define("dimuonKinematics", 'dimuonKinematics(ScoutingMuonVtx_pt, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi)')
  # d = d.Define("ScoutingMuonVtxPair_pt", "dimuonKinematics[0]")
  # d = d.Define("ScoutingMuonVtxPair_eta", "dimuonKinematics[1]")
  # d = d.Define("ScoutingMuonVtxPair_phi", "dimuonKinematics[2]")
  # d = d.Define("ScoutingMuonVtxPair_mass", "dimuonKinematics[3]")
  # d = d.Define("ScoutingMuonVtxPair_Y", "dimuonKinematics[4]")
  d = d.Define("ScoutingMuonVtxPair_deltaxy", "ScoutingMuonVtx_trk_dxy[0] - ScoutingMuonVtx_trk_dxy[1]")
  d = d.Define("ScoutingMuonVtxPair_deltaz", "ScoutingMuonVtx_trk_dz[0] - ScoutingMuonVtx_trk_dz[1]")

  d = d.Define("TruePFJet_ind", 'TruePFJet(ScoutingPFJet_pt, ScoutingPFJet_eta, ScoutingPFJet_phi, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi)')
  d = d.Define("TruePFJet_pt", 'ScoutingPFJet_pt[TruePFJet_ind]')
  d = d.Define("nTruePFJet", "TruePFJet_pt.size()")
  d = d.Define("TruePFJet_HT", 'Sum(TruePFJet_pt)')

  d = d.Define("TruePFJetRecluster_ind", 'TruePFJet(ScoutingPFJetRecluster_pt, ScoutingPFJetRecluster_eta, ScoutingPFJetRecluster_phi, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi)')
  d = d.Define("TruePFJetRecluster_pt", 'ScoutingPFJetRecluster_pt[TruePFJetRecluster_ind]')
  d = d.Define("nTruePFJetRecluster", "TruePFJetRecluster_pt.size()")
  d = d.Define("TruePFJetRecluster_HT", 'Sum(TruePFJetRecluster_pt)')

  # Filter the events
  d = d.Filter("DST_PFScouting_SingleMuon", "HLT Scouting Stream")  #2024
  # d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream") #2022
  d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")
  d = d.Filter("nScoutingMuonVtx == 2")
  d = d.Filter("ScoutingMuonVtx_charge[0]*ScoutingMuonVtx_charge[1] == -1", "Opposite charge")
  d = d.Filter("abs(ScoutingMuonVtx_eta[0]) < 2.0 && abs(ScoutingMuonVtx_eta[1]) < 2.0",\
                "eta-cut")
  d = d.Filter("ScoutingMuonVtx_pt[0] > 5.0 && ScoutingMuonVtx_pt[1] > 5.0", "pt-cut")
  d = d.Filter('All(rTrkIso < 0.03)', "Muons are isolated in the tracker: ")
  d = d.Filter("All(ScoutingMuonVtx_trk_chi2/ScoutingMuonVtx_trk_ndof < 10)", "Track of the muons are nicely reconstructed")
  d = d.Filter('ScoutingMuonVtxSub_pt/ScoutingMuonVtxPair_mass > 0.25')\
      .Filter('ScoutingMuonVtxSub_pt/ScoutingMuonVtxPair_mass > 0.45', "leptons are decay products of the original boson")

  # d = d.Filter('All(rEcalIso < 0.4)', "Muons are isolated in the ECAL: ")
  # d = d.Filter("All(abs(ScoutingMuonVtx_trk_dxy) < 0.2)", "Muons are coming from reco PV ")
  # d = d.Filter("All(abs(ScoutingMuonVtx_trk_dz) < 15)", "Muons are coming from reco PV ")
  # d = d.Filter("ScoutingMuonVtx_deltaR > 2 && ScoutingMuonVtx_deltaR < 4", " leptons are not too close or too separated")

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
  # dD = dD.Filter("run == 386604")
  samples.append(("Data", dD))

  # Loop over sample to make histograms for each isolation selection
  plots = ranges.keys()
  hists_s = {} # Declare the dictionary where histograms w ill be stored

  for df_label, df in samples :
    # Separate mass windows
    d_ups = df.Filter("ScoutingMuonVtxPair_mass < 20 && ScoutingMuonVtxPair_mass > 10", "Under Upsilon influence")
    d_QCD = df.Filter("ScoutingMuonVtxPair_mass < 50 && ScoutingMuonVtxPair_mass > 20", "Bulk")
    d_W = df.Filter("ScoutingMuonVtxPair_mass > 50 && ScoutingMuonVtxPair_mass < 76", "Under W influence")
    d_Z = df.Filter("ScoutingMuonVtxPair_mass > 76 && ScoutingMuonVtxPair_mass < 106", "Under Z influence")
    df_massWindows = [
              ("Incl", df),
              ("Upsilon", d_ups),
              ("QCD", d_QCD),
              ("W", d_W),
              ("Z", d_Z)
              ]
    for label_mass, df_mass in df_massWindows :
      # if (df_label == "Data" and label_mass == "Incl") : 
        # rep = df_mass.Report()
      # Book Histograms for each variable
      for plot in plots :
        hkey = "{}_{}_{}".format(df_label, plot, label_mass)
        # print("Booking : ", hkey)
        hists_s[hkey] = bookHist(df_mass, plot, ranges[plot])

  # Write histograms in the file
  for hkey in hists_s :
    # print("Writing : ", hkey)
    writeHist(hists_s[hkey], hkey)

  # rep.Print()
  outf.Close()

if __name__ == "__main__" :
  # Output file
  outf_name = "Hist/histograms.root"
  outf = ROOT.TFile(outf_name, "RECREATE")
  main(sys.argv[1])
#!/usr/bin/env python
import ROOT
import cmsstyle as CMS
CMS.setCMSStyle()
CMS.SetLumi(11.417)
CMS.SetEnergy(13.6)

import numpy as np
ROOT.gROOT.SetBatch(True)

ROOT.gInterpreter.ProcessLine('#include "helper.h"')

# Declaration of ranges for each histogram type
default_nbins = 1

ranges = {
  "ScoutingMuonVtxPair_mass" : ("ScoutingMuonVtxPair_mass", default_nbins, 10.0, 86.0),
#   # "ScoutingMuonVtxPair_massZ" : ("ScoutingMuonVtxPair_mass", default_nbins, 81.0, 101.0),
#   # "ScoutingMuonVtxPair_massLow" : ("ScoutingMuonVtxPair_mass", default_nbins, 10.0, 60.0)
  }

def bookHist(d, name, range_): #Histo booking
  return d.Histo1D(ROOT.ROOT.RDF.TH1DModel(name, name, range_[1], range_[2], range_[3]),\
                    range_[0], "norm")


def writeHist(h, name): #Write it !
  h.SetName(name)
  h.Write()

# Retrieve histograms based on process, variable and isolation
def getHistogram(inf, sample, type, iso):
    name = "{}_{}_{}".format(sample, type, iso)
    h = inf.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def makeGraphs():
  # Output file
  outf_name = "Hist/efficiencyVsiIso.root"
  outf = ROOT.TFile(outf_name, "RECREATE")

  # Create the dataframe with the .json spec file
  ROOT.EnableImplicitMT(16)
  d = ROOT.RDF.Experimental.FromSpec("samples_MC.json")
  ROOT.RDF.Experimental.AddProgressBar(d)
  # d = d.Range(10000)

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("nevents")')
  d = d.DefinePerSample("isMC", 'rdfsampleinfo_.GetS("isMC")')
  d = d.DefinePerSample("sample", 'rdfsampleinfo_.GetS("sample")')


  # Define new variables
  d = d.Define("dimuonKinematics", 'dimuonKinematics(ScoutingMuonVtx_pt, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi)')
  d = d.Define("ScoutingMuonVtxPair_mass", "dimuonKinematics[3]")
  d = d.Define("rTrkIso", "ScoutingMuonVtx_trackIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_trackIso"})
  d = d.Define("rECALIso", "ScoutingMuonVtx_ecalIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_ecalIso"})
  d = d.Define("rHCALIso", "ScoutingMuonVtx_hcalIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_hcalIso"})
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 1.0)',{"xsec", "sumws", "genWeight", "isMC"})
  d = d.Define("ind", 'ROOT::VecOps::Argsort(ScoutingMuonVtx_pt)', {"ScoutingMuonVtx_pt"})
  d = d.Define("leadpt", "ScoutingMuonVtx_pt[ind[1]]").Define("subpt", "ScoutingMuonVtx_pt[ind[0]]")
  d = d.Filter("nScoutingMuonVtx == 2")
  d = d.Filter("ScoutingMuonVtxPair_mass < 86", "No Z-peak contamination")
  d = d.Filter("All(ScoutingMuonVtx_pt > 5) && All(abs(ScoutingMuonVtx_eta < 2.4))")
  d = d.Filter("ScoutingMuonVtx_charge[0]*ScoutingMuonVtx_charge[1] == -1")
  d = d.Filter("DST_PFScouting_DoubleMuon", "HLT Scouting Stream")  #2024
  # d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream") #2022
  d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")
  d = d.Filter('leadpt/ScoutingMuonVtxPair_mass > 0.45')\
         .Filter('subpt/ScoutingMuonVtxPair_mass > 0.25', "leptons are decay products of the original boson")
  # d.Display({"ScoutingMuonVtx_trackIso", "ScoutingMuonVtx_ecalIso", "ScoutingMuonVtx_hcalIso", "PFIso"}, 128).Print()
  # Separate samples and add them to the sample list
  samples = []
  sig = d.Filter('sample == "DYto2Mu"', "isDY")
  samples.append(("signal", sig))
  bckg = d.Filter('sample == "QCD" or sample == "TTto2l2nu" or sample =="DYto2Tau"')
  samples.append(("bckg", bckg))

  graphs = {}
  signal_trkIso = []
  signal_ECALIso = []
  signal_HCALIso = []
  signal_PFIso = []
  signal_rTrkIso = []
  signal_rECALIso = []
  signal_rHCALIso = []
  signal_rPFIso = []

  bckg_trkIso = []
  bckg_ECALIso = []
  bckg_HCALIso = []
  bckg_PFIso = []
  bckg_rTrkIso = []
  bckg_rECALIso = []
  bckg_rHCALIso = []
  bckg_rPFIso = []

  n = 40
  xs = np.linspace(1, 100, n)
  halfBinWidth = 100/(2*n)
  errors_x = np.full(n, halfBinWidth)
  errors_rx = np.full(n, halfBinWidth/100)
  errors_y = np.full(n, 0.0)
  for l_s, s in samples :
    rxs = []
    ns_all = []
    ns_trkIso = []
    ns_ECALIso = []
    ns_HCALIso = []
    ns_PFIso = []
    ns_rTrkIso = []
    ns_rECALIso = []
    ns_rHCALIso = []
    ns_rPFIso = []

    rs_trkIso = []
    rs_ECALIso = []
    rs_HCALIso = []
    rs_PFIso = []
    rs_rTrkIso = []
    rs_rECALIso = []
    rs_rHCALIso = []
    rs_rPFIso = []
    for x in xs:
      rx = x/100
      n_all = bookHist(s, "all", ranges["ScoutingMuonVtxPair_mass"])
      n_trkIso = bookHist(s.Filter("ScoutingMuonVtx_trackIso[0] < {} && ScoutingMuonVtx_trackIso[1] < {}".format(x,x)), "trkIso", ranges["ScoutingMuonVtxPair_mass"])
      n_ECALIso = bookHist(s.Filter("ScoutingMuonVtx_ecalIso[0] < {} && ScoutingMuonVtx_ecalIso[1] < {}".format(x,x)), "ECALIso", ranges["ScoutingMuonVtxPair_mass"])
      n_HCALIso = bookHist(s.Filter("ScoutingMuonVtx_hcalIso[0] < {} && ScoutingMuonVtx_hcalIso[1] < {}".format(x,x)), "HCALIso", ranges["ScoutingMuonVtxPair_mass"])
      n_PFIso = bookHist(s.Filter("ScoutingMuonVtx_trackIso[0] < {} && ScoutingMuonVtx_trackIso[1] < {}".format(x,x)) \
                          .Filter("ScoutingMuonVtx_ecalIso[0] < {} && ScoutingMuonVtx_ecalIso[1] < {}".format(x,x)) \
                          .Filter("ScoutingMuonVtx_hcalIso[0] < {} && ScoutingMuonVtx_hcalIso[1] < {}".format(x,x)) \
                          , "PFIso", ranges["ScoutingMuonVtxPair_mass"])
      n_rTrkIso = bookHist(s.Filter("rTrkIso[0] < {} && rTrkIso[1] < {}".format(rx,rx)), "tTrkIso", ranges["ScoutingMuonVtxPair_mass"])
      n_rECALIso = bookHist(s.Filter("rECALIso[0] < {} && rECALIso[1] < {}".format(rx,rx)), "rECALISo", ranges["ScoutingMuonVtxPair_mass"])
      n_rHCALIso = bookHist(s.Filter("rHCALIso[0] < {} && rHCALIso[1] < {}".format(rx,rx)), "rHCALIso", ranges["ScoutingMuonVtxPair_mass"])
      n_rPFIso =  bookHist(s.Filter("rTrkIso[0] < {} && rTrkIso[1] < {}".format(rx,rx)) \
                                    .Filter("rECALIso[0] < {} && rECALIso[1] < {}".format(rx,rx)) \
                                    .Filter("rHCALIso[0] < {} && rHCALIso[1] < {}".format(rx,rx)) \
                                    , "rPFIso", ranges["ScoutingMuonVtxPair_mass"])


      rxs.append(rx)
      ns_all.append(n_all)
      ns_trkIso.append(n_trkIso)
      ns_ECALIso.append(n_ECALIso)
      ns_HCALIso.append(n_HCALIso)
      ns_PFIso.append(n_PFIso)
      ns_rTrkIso.append(n_rTrkIso)
      ns_rECALIso.append(n_rECALIso)
      ns_rHCALIso.append(n_rHCALIso)
      ns_rPFIso.append(n_rPFIso)

    for j in range(n) :
      ns_all[j] = ns_all[j].Integral()
      ns_trkIso[j] = ns_trkIso[j].Integral()
      ns_ECALIso[j] = ns_ECALIso[j].Integral()
      ns_HCALIso[j] = ns_HCALIso[j].Integral()
      ns_PFIso[j] = ns_PFIso[j].Integral()
      ns_rTrkIso[j] = ns_rTrkIso[j].Integral()
      ns_rECALIso[j] = ns_rECALIso[j].Integral()
      ns_rHCALIso[j] = ns_rHCALIso[j].Integral()
      ns_rPFIso[j] = ns_rPFIso[j].Integral()

      rs_trkIso.append(ns_trkIso[j]/ns_all[j])
      rs_ECALIso.append(ns_ECALIso[j]/ns_all[j])
      rs_HCALIso.append(ns_HCALIso[j]/ns_all[j])
      rs_PFIso.append(ns_PFIso[j]/ns_all[j])
      rs_rTrkIso.append(ns_rTrkIso[j]/ns_all[j])
      rs_rECALIso.append(ns_rECALIso[j]/ns_all[j])
      rs_rHCALIso.append(ns_rHCALIso[j]/ns_all[j])
      rs_rPFIso.append(ns_rPFIso[j]/ns_all[j])

      if (l_s == "signal") :
        signal_trkIso.append(ns_trkIso[j])
        signal_ECALIso.append(ns_ECALIso[j])
        signal_HCALIso.append(ns_HCALIso[j])
        signal_PFIso.append(ns_PFIso[j])
        signal_rTrkIso.append(ns_rTrkIso[j])
        signal_rECALIso.append(ns_rECALIso[j])
        signal_rHCALIso.append(ns_rHCALIso[j])
        signal_rPFIso.append(ns_rPFIso[j])
      else :
        bckg_trkIso.append(ns_trkIso[j])
        bckg_ECALIso.append(ns_ECALIso[j])
        bckg_HCALIso.append(ns_HCALIso[j])
        bckg_PFIso.append(ns_PFIso[j])
        bckg_rTrkIso.append(ns_rTrkIso[j])
        bckg_rECALIso.append(ns_rECALIso[j])
        bckg_rHCALIso.append(ns_rHCALIso[j])
        bckg_rPFIso.append(ns_rPFIso[j])

    n_trkIso = ROOT.TGraphErrors(n, xs, np.array(ns_trkIso), errors_x, errors_y)
    graphs["{}_n_trkIso".format(l_s)] = n_trkIso
    n_ECALIso = ROOT.TGraphErrors(n, xs, np.array(ns_ECALIso), errors_x, errors_y)
    graphs["{}_n_ECALIso".format(l_s)] = n_ECALIso
    n_HCALIso = ROOT.TGraphErrors(n, xs, np.array(ns_HCALIso), errors_x, errors_y)
    graphs["{}_n_HCALIso".format(l_s)] = n_HCALIso
    n_PFIso = ROOT.TGraphErrors(n, xs, np.array(ns_PFIso), errors_x, errors_y)
    graphs["{}_n_PFIso".format(l_s)] = n_PFIso
    n_rTrkIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(ns_rTrkIso), errors_rx, errors_y)
    graphs["{}_n_rTrkIso".format(l_s)] = n_rTrkIso
    n_rECALIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(ns_rECALIso), errors_rx, errors_y)
    graphs["{}_n_rECALIso".format(l_s)] = n_rECALIso
    n_rHCALIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(ns_rHCALIso), errors_rx, errors_y)
    graphs["{}_n_rHCALIso".format(l_s)] = n_rHCALIso
    n_rPFIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(ns_rPFIso), errors_rx, errors_y)
    graphs["{}_n_rPFIso".format(l_s)] = n_rPFIso

    eff_trkIso = ROOT.TGraphErrors(n, xs, np.array(rs_trkIso), errors_x, errors_y)
    graphs["{}_eff_trkIso".format(l_s)] = eff_trkIso
    eff_ECALIso = ROOT.TGraphErrors(n, xs, np.array(rs_ECALIso), errors_x, errors_y)
    graphs["{}_eff_ECALIso".format(l_s)] = eff_ECALIso
    eff_HCALIso = ROOT.TGraphErrors(n, xs, np.array(rs_HCALIso), errors_x, errors_y)
    graphs["{}_eff_HCALIso".format(l_s)] = eff_HCALIso
    eff_PFIso = ROOT.TGraphErrors(n, xs, np.array(rs_PFIso), errors_x, errors_y)
    graphs["{}_eff_PFIso".format(l_s)] = eff_PFIso
    eff_rTrkIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(rs_rTrkIso), errors_rx, errors_y)
    graphs["{}_eff_rTrkIso".format(l_s)] = eff_rTrkIso
    eff_rECALIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(rs_rECALIso), errors_rx, errors_y)
    graphs["{}_eff_rECALIso".format(l_s)] = eff_rECALIso
    eff_rHCALIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(rs_rHCALIso), errors_rx, errors_y)
    graphs["{}_eff_rHCALIso".format(l_s)] = eff_rHCALIso
    eff_rPFIso = ROOT.TGraphErrors(n, np.array(rxs), np.array(rs_rPFIso), errors_rx, errors_y)
    graphs["{}_eff_rPFIso".format(l_s)] = eff_rPFIso

  for g in graphs :
    writeHist(graphs[g], g)

def plotGraphs() :
  inf = ROOT.TFile("Hist/efficiencyVsiIso.root", "READ")

  signal_trkIso = getHistogram(inf, "signal", "eff", "trkIso")
  bckg_trkIso = getHistogram(inf, "bckg", "eff", "trkIso")
  c_trk = CMS.cmsCanvas("Efficiency for Tracker Isolation", 0, 100, 0, 1.0, \
                          "I_{tracker}", "#pass/#total")
  leg_trk = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_trkIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_trk.AddEntry(signal_trkIso, "Signal")
  CMS.cmsObjectDraw(bckg_trkIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_trk.AddEntry(bckg_trkIso, "Background")
  leg_trk.Draw()
  c_trk.SaveAs("Hist/Efficiency/Efficiency_tracker.png")
  c_trk.SaveAs("Hist/Efficiency/Efficiency_tracker.pdf")

  signal_HCALIso = getHistogram(inf, "signal", "eff", "HCALIso")
  bckg_HCALIso = getHistogram(inf, "bckg", "eff","HCALIso")
  c_HCAL = CMS.cmsCanvas("Efficiency for HCAL Isolation", 0, 100, 0, 1.0, \
                          "I_{HCAL}", "#pass/#total")
  leg_HCAL = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_HCALIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_HCAL.AddEntry(signal_HCALIso, "Signal")
  CMS.cmsObjectDraw(bckg_HCALIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_HCAL.AddEntry(bckg_HCALIso, "Background")
  leg_HCAL.Draw()
  c_HCAL.SaveAs("Hist/Efficiency/Efficiency_HCAL.png")
  c_HCAL.SaveAs("Hist/Efficiency/Efficiency_HCAL.pdf")

  signal_ECALIso = getHistogram(inf, "signal","eff", "ECALIso")
  bckg_ECALIso = getHistogram(inf, "bckg","eff", "ECALIso")
  c_ECAL = CMS.cmsCanvas("Efficiency for ECAL Isolation", 0, 100, 0, 1.0, \
                          "I_{ECAL}", "#pass/#total")
  leg_ECAL = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_ECALIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_ECAL.AddEntry(signal_ECALIso, "Signal")
  CMS.cmsObjectDraw(bckg_ECALIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_ECAL.AddEntry(bckg_ECALIso, "Background")
  leg_ECAL.Draw()
  c_ECAL.SaveAs("Hist/Efficiency/Efficiency_ECAL.png")
  c_ECAL.SaveAs("Hist/Efficiency/Efficiency_ECAL.pdf")

  signal_PFIso = getHistogram(inf, "signal", "eff","PFIso")
  bckg_PFIso = getHistogram(inf, "bckg", "eff","PFIso")
  c_PF = CMS.cmsCanvas("Efficiency for PF Isolation", 0, 90, 0, 1.0, \
                          "I_{PF}", "#pass/#total")
  leg_PF = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_PFIso, "P", MarkerColor=CMS.p6.kRed)
  leg_PF.AddEntry(signal_PFIso, "Signal")
  CMS.cmsObjectDraw(bckg_PFIso, "SAME P", MarkerColor=CMS.p6.kBlue)
  leg_PF.AddEntry(bckg_PFIso, "Background")
  leg_PF.Draw()
  c_PF.SaveAs("Hist/Efficiency/Efficiency_PF.png")
  c_PF.SaveAs("Hist/Efficiency/Efficiency_PF.pdf")

  signal_rTrkIso = getHistogram(inf, "signal", "eff","rTrkIso")
  bckg_rTrkIso = getHistogram(inf, "bckg", "eff","rTrkIso")
  c_rtrk = CMS.cmsCanvas("Efficiency for relative Tracker Isolation", 0, 1.0, 0, 1.0, \
                          "I_{tracker}/p_{\mu}", "#pass/#total")
  leg_rtrk = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_rTrkIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_rtrk.AddEntry(signal_rTrkIso, "Signal")
  CMS.cmsObjectDraw(bckg_rTrkIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_rtrk.AddEntry(bckg_rTrkIso, "Background")
  leg_rtrk.Draw()
  c_rtrk.SaveAs("Hist/Efficiency/Efficiency_rTracker.png")
  c_rtrk.SaveAs("Hist/Efficiency/Efficiency_rTracker.pdf")

  signal_rHCALIso = getHistogram(inf, "signal", "eff","rHCALIso")
  bckg_rHCALIso = getHistogram(inf, "bckg", "eff","rHCALIso")
  c_rHCAL = CMS.cmsCanvas("Efficiency for relative HCAL Isolation", 0, 1.0, 0, 1.0, \
                          "I_{HCAL}/p_{\mu}", "#pass/#total")
  leg_rHCAL = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_rHCALIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_rHCAL.AddEntry(signal_rHCALIso, "Signal")
  CMS.cmsObjectDraw(bckg_rHCALIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_rHCAL.AddEntry(bckg_rHCALIso, "Background")
  leg_rHCAL.Draw()
  c_rHCAL.SaveAs("Hist/Efficiency/Efficiency_rHCAL.png")
  c_rHCAL.SaveAs("Hist/Efficiency/Efficiency_rHCAL.pdf")

  signal_rECALIso = getHistogram(inf, "signal", "eff","rECALIso")
  bckg_rECALIso = getHistogram(inf, "bckg", "eff","rECALIso")
  c_rECAL = CMS.cmsCanvas("Efficiency for relative ECAL Isolation", 0, 1.0, 0, 1.0, \
                          "I_{ECAL}/p_{\mu}", "#pass/#total")
  leg_rECAL = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_rECALIso, "PE", MarkerColor=CMS.p6.kRed)
  leg_rECAL.AddEntry(signal_rECALIso, "Signal")
  CMS.cmsObjectDraw(bckg_rECALIso, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_rECAL.AddEntry(bckg_rECALIso, "Background")
  leg_rECAL.Draw()
  c_rECAL.SaveAs("Hist/Efficiency/Efficiency_rECAL.png")
  c_rECAL.SaveAs("Hist/Efficiency/Efficiency_rECAL.pdf")

  signal_rPFIso = getHistogram(inf, "signal", "eff","rPFIso")
  bckg_rPFIso = getHistogram(inf, "bckg", "eff","rPFIso")
  c_rPF = CMS.cmsCanvas("Efficiency for relative PF Isolation", 0, 1.0, 0, 1.0, \
                          "I_{PF}/p_{\mu}", "#pass/#total")
  leg_rPF = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal_rPFIso, "P", MarkerColor=CMS.p6.kRed)
  leg_rPF.AddEntry(signal_rPFIso, "Signal")
  CMS.cmsObjectDraw(bckg_rPFIso, "SAME P", MarkerColor=CMS.p6.kBlue)
  leg_rPF.AddEntry(bckg_rPFIso, "Background")
  leg_rPF.Draw()
  c_rPF.SaveAs("Hist/Efficiency/Efficiency_rPF.png")
  c_rPF.SaveAs("Hist/Efficiency/Efficiency_rPF.pdf")

  signal_trkIso = getHistogram(inf, "signal", "n", "trkIso")
  bckg_trkIso = getHistogram(inf, "bckg", "n", "trkIso")
  signal_HCALIso = getHistogram(inf, "signal", "n", "HCALIso")
  bckg_HCALIso = getHistogram(inf, "bckg", "n","HCALIso")
  signal_ECALIso = getHistogram(inf, "signal","n", "ECALIso")
  bckg_ECALIso = getHistogram(inf, "bckg","n", "ECALIso")
  signal_PFIso = getHistogram(inf, "signal", "n","PFIso")
  bckg_PFIso = getHistogram(inf, "bckg", "n","PFIso")
  signal_rTrkIso = getHistogram(inf, "signal", "n","rTrkIso")
  bckg_rTrkIso = getHistogram(inf, "bckg", "n","rTrkIso")
  signal_rHCALIso = getHistogram(inf, "signal", "n","rHCALIso")
  bckg_rHCALIso = getHistogram(inf, "bckg", "n","rHCALIso")
  signal_rECALIso = getHistogram(inf, "signal", "n","rECALIso")
  bckg_rECALIso = getHistogram(inf, "bckg", "n","rECALIso")
  signal_rPFIso = getHistogram(inf, "signal", "n","rPFIso")
  bckg_rPFIso = getHistogram(inf, "bckg", "n","rPFIso")

  pure_trk = []
  pure_ECAL = []
  pure_HCAL = []
  pure_PF = []

  pure_rtrk = []
  pure_rECAL = []
  pure_rHCAL = []
  pure_rPF = []
  
  n = signal_trkIso.GetN()
  xs = signal_trkIso.GetX()
  rxs = signal_rTrkIso.GetX()
  halfBinWidth = 100/(2*n)
  errors_x = np.full(n, halfBinWidth)
  errors_rx = np.full(n, halfBinWidth/100)
  errors_y = np.full(n, 0.0)

  for i in range(n) :
    p_trk = signal_trkIso.GetPointY(i)/(signal_trkIso.GetPointY(i) + bckg_trkIso.GetPointY(i))
    p_ECAL = signal_ECALIso.GetPointY(i)/(signal_ECALIso.GetPointY(i) + bckg_ECALIso.GetPointY(i))
    p_HCAL = signal_HCALIso.GetPointY(i)/(signal_HCALIso.GetPointY(i) + bckg_HCALIso.GetPointY(i))
    p_PF = signal_PFIso.GetPointY(i)/(signal_PFIso.GetPointY(i) + bckg_PFIso.GetPointY(i))
    pure_trk.append(p_trk)
    pure_ECAL.append(p_ECAL)
    pure_HCAL.append(p_HCAL)
    pure_PF.append(p_PF)

    p_rtrk = signal_rTrkIso.GetPointY(i)/(signal_rTrkIso.GetPointY(i) + bckg_rTrkIso.GetPointY(i))
    p_rECAL = signal_rECALIso.GetPointY(i)/(signal_rECALIso.GetPointY(i) + bckg_rECALIso.GetPointY(i))
    p_rHCAL = signal_rHCALIso.GetPointY(i)/(signal_rHCALIso.GetPointY(i) + bckg_rHCALIso.GetPointY(i))
    p_rPF = signal_rPFIso.GetPointY(i)/(signal_rPFIso.GetPointY(i) + bckg_rPFIso.GetPointY(i))
    pure_rtrk.append(p_rtrk)
    pure_rECAL.append(p_rECAL)
    pure_rHCAL.append(p_HCAL)
    pure_rPF.append(p_PF)
  
  graph_pure_trk = ROOT.TGraphErrors(n, xs, np.array(pure_trk), errors_x, errors_y)
  graph_pure_ECAL = ROOT.TGraphErrors(n, xs, np.array(pure_ECAL), errors_x, errors_y)
  graph_pure_HCAL = ROOT.TGraphErrors(n, xs, np.array(pure_HCAL), errors_x, errors_y)
  graph_pure_PF = ROOT.TGraphErrors(n, xs, np.array(pure_PF), errors_x, errors_y)

  c_pure = CMS.cmsCanvas("Purity regarding Isolation Method", 0, 100, 0.0, 0.2, \
                          "I", "#sig/(#sig+#bkg)")
  leg_pure = CMS.cmsLeg(0.5, 0.6, 0.6, 0.8)
  CMS.cmsObjectDraw(graph_pure_trk, "PEZ", MarkerColor=CMS.p6.kRed)
  leg_pure.AddEntry(graph_pure_trk, "tracker")
  CMS.cmsObjectDraw(graph_pure_ECAL, "SAME PEZ", MarkerColor=CMS.p6.kBlue)
  leg_pure.AddEntry(graph_pure_ECAL, "ECAL")
  CMS.cmsObjectDraw(graph_pure_HCAL, "SAME PEZ", MarkerColor=CMS.p6.kYellow)
  leg_pure.AddEntry(graph_pure_HCAL, "HCAL")
  CMS.cmsObjectDraw(graph_pure_PF, "SAME PEZ", MarkerColor=CMS.p6.kViolet)
  leg_pure.AddEntry(graph_pure_PF, "PF")
  leg_pure.Draw()
  c_pure.SaveAs("Hist/Efficiency/Purity_abs.png")
  c_pure.SaveAs("Hist/Efficiency/Purity_abs.pdf")

  graph_pure_rtrk = ROOT.TGraphErrors(n, rxs, np.array(pure_rtrk), errors_rx, errors_y)
  graph_pure_rECAL = ROOT.TGraphErrors(n, rxs, np.array(pure_rECAL), errors_rx, errors_y)
  graph_pure_rHCAL = ROOT.TGraphErrors(n, rxs, np.array(pure_rHCAL), errors_rx, errors_y)
  graph_pure_rPF = ROOT.TGraphErrors(n, rxs, np.array(pure_rPF), errors_rx, errors_y)

  c_pure_r = CMS.cmsCanvas("Purity regarding relative Isolation Method", 0, 1.0, 0.0, 0.2, \
                          "I/p_{\mu}", "#sig/(#sig+#bkg)")
  leg_pure = CMS.cmsLeg(0.5, 0.6, 0.6, 0.8)
  CMS.cmsObjectDraw(graph_pure_rtrk, "PEZ", MarkerColor=CMS.p6.kRed)
  leg_pure.AddEntry(graph_pure_rtrk, "tracker")
  CMS.cmsObjectDraw(graph_pure_rECAL, "SAME PEZ", MarkerColor=CMS.p6.kBlue)
  leg_pure.AddEntry(graph_pure_rECAL, "ECAL")
  CMS.cmsObjectDraw(graph_pure_rHCAL, "SAME PEZ", MarkerColor=CMS.p6.kYellow)
  leg_pure.AddEntry(graph_pure_rHCAL, "HCAL")
  CMS.cmsObjectDraw(graph_pure_rPF, "SAME PEZ", MarkerColor=CMS.p6.kViolet)
  leg_pure.AddEntry(graph_pure_rPF, "PF")
  leg_pure.Draw()
  c_pure_r.SaveAs("Hist/Efficiency/Purity_rel.png")
  c_pure_r.SaveAs("Hist/Efficiency/Purity_rel.pdf")

          

if __name__ == "__main__" :
  makeGraphs()
  plotGraphs()

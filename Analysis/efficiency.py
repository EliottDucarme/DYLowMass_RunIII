#!/usr/bin/env python
import ROOT
import sys
import cmsstyle as CMS
CMS.setCMSStyle()
CMS.SetLumi(11.417)
CMS.SetEnergy(13.6)
from cluster import create_connection
import numpy as np
ROOT.gROOT.SetBatch(True)

p10 = [CMS.p10.kBlue,
        CMS.p10.kRed,
        CMS.p10.kYellow,
        CMS.p10.kGray ,
        CMS.p10.kViolet,
        CMS.p10.kBrown,
        CMS.p10.kOrange,
        CMS.p10.kGreen,
        CMS.p10.kAsh ,
        CMS.p10.kCyan
]
# Declaration of ranges for each histogram type
default_nbins = 100

ranges = {
  "ScoutingMuonVtxPair_mass_1bin" : ("ScoutingMuonVtxPair_mass", 1, 10.0, 50.0),  
  "ScoutingMuonVtxPair_mass" : ("ScoutingMuonVtxPair_mass", default_nbins, 10.0, 50.0),  
  "ScoutingMuonVtxLead_pt" : ("ScoutingMuonVtxLead_pt", default_nbins, 5.0, 105.0),
  "ScoutingMuonVtxSub_pt" : ("ScoutingMuonVtxSub_pt", default_nbins, 5.0, 105.0),
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

def makeGraphs(executor, study):
  # Output file
  outf_name = "Hist/efficiency_{}.root".format(study)
  outf = ROOT.TFile(outf_name, "RECREATE")

  if (executor == "cluster") : 
    client = create_connection()
    d = ROOT.RDF.Experimental.FromSpec("samples_MC.json", executor=client, npartitions=100)
    ROOT.RDF.Distributed.DistributeHeaders("helper.h")
  elif (executor == "local") : 
    ROOT.gInterpreter.Declare('#include "helper.h"') 
    # ROOT.EnableImplicitMT(16) 
    d = ROOT.RDF.Experimental.FromSpec("samples_MC.json")
    ROOT.RDF.Experimental.AddProgressBar(d)
    d = d.Range(1000)
    ROOT.RDF.Experimental.ProgressHelper.ProgressHelper(1000000, progressBarWidth=5, useColors=True)
  else :
    print("Use 'local' or 'cluster' for a direct execution or distributed one")

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("nevents")')
  d = d.DefinePerSample("isMC", 'rdfsampleinfo_.GetS("isMC")')
  d = d.DefinePerSample("sample", 'rdfsampleinfo_.GetS("sample")')


  # Define new variables
  # d = d.Define("dimuonKinematics", 'dimuonKinematics(ScoutingMuonVtx_pt, ScoutingMuonVtx_eta, ScoutingMuonVtx_phi)')
  # d = d.Define("ScoutingMuonVtxPair_mass", "dimuonKinematics[3]")
  # d = d.Define("rTrkIso", "ScoutingMuonVtx_trackIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_trackIso"})
  # d = d.Define("rECALIso", "ScoutingMuonVtx_ecalIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_ecalIso"})
  # d = d.Define("rHCALIso", "ScoutingMuonVtx_hcalIso/ScoutingMuonVtx_pt" , {"ScoutingMuonVtx_pt", "ScoutingMuonVtx_hcalIso"})
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, isMC, 1.0)',{"xsec", "sumws", "genWeight", "isMC"})
  d = d.Define("ind", 'ROOT::VecOps::Argsort(ScoutingMuonVtx_pt)', {"ScoutingMuonVtx_pt"})
  d = d.Define("ScoutingMuonVtxLead_pt", "ScoutingMuonVtx_pt[ind[1]]").Define("ScoutingMuonVtxSub_pt", "ScoutingMuonVtx_pt[ind[0]]")
  d = d.Filter("DST_PFScouting_DoubleMuon", "HLT Scouting Stream")  #2024

  d = d.Define("ScoutingMuonVtx_impactParametrs", "computeImpactParameters(ScoutingMuonVtx_trk_vx, ScoutingMuonVtx_trk_vy, ScoutingMuonVtx_trk_dz, ScoutingPrimaryVertex_x, ScoutingPrimaryVertex_y, ScoutingPrimaryVertex_z, ScoutingMuonVtx_trk_vx, ScoutingMuonVtx_trk_vy, ScoutingMuonVtx_trk_vz)")
  d = d.Define("ScoutingMuonVtx_dxy", "ScoutingMuonVtx_impactParametrs[0]")
  d = d.Define("ScoutingMuonVtx_dz", "ScoutingMuonVtx_impactParametrs[1]")

  # d.Display({"ScoutingMuonVtx_trackIso", "ScoutingMuonVtx_ecalIso", "ScoutingMuonVtx_hcalIso", "PFIso"}, 128).Print()
  # Separate samples and add them to the sample list
  samples = []
  sig = d.Filter('sample == "DYto2Mu"', "isDY")
  samples.append(("signal", sig))
  bckg = d.Filter('sample == "QCD" or sample == "TTto2l2nu" or sample =="DYto2Tau"')
  samples.append(("bckg", bckg))

  if (study != "L1s" ) :
    samples_skimmed = []
    for d in samples :
      d = d.Filter("nScoutingMuonVtx == 2")
      d = d.Filter("ScoutingMuonVtxPair_mass < 60", "No Z-peak contamination")
      d = d.Filter("All(ScoutingMuonVtx_pt > 5) && All(abs(ScoutingMuonVtx_eta < 2.4))")
      d = d.Filter("ScoutingMuonVtx_charge[0]*ScoutingMuonVtx_charge[1] == -1")
      # d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream") #2022
      d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")
      d = d.Filter('leadpt/ScoutingMuonVtxPair_mass > 0.45')\
            .Filter('subpt/ScoutingMuonVtxPair_mass > 0.25', "leptons are decay products of the original boson")
      samples_skimmed.append(d)
    if (study == "dis") :
      displacementStudy(samples_skimmed)
    elif (study == "iso") :
      isoStudy(samples_skimmed)
  elif (study == "L1s") :
    l1Study(samples)

def l1Study(samples) :
  hists = {}
  signal_L14p5 = []
  signal_L18 = []

  bckg_L14p5 = []
  bckg_L18 = []
  for l_s, s in samples :
    vars = ranges.keys()
    for v in vars:
      HLT = bookHist(s, "HLT", ranges[v])
      L14p5 = bookHist(s.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7"), "L14p5", ranges[v])
      L18 = bookHist(s.Filter("L1_DoubleMu8_SQ"), "L18", ranges[v])
      
      hists["HLT_{}_{}".format(l_s, v)] = HLT
      hists["L18_{}_{}".format(l_s, v)] = L18
      hists["L14p5_{}_{}".format(l_s, v)] = L14p5

  for l_s, s in samples:
    for v in vars:
      HLT = hists["HLT_{}_{}".format(l_s, v)]
      L14p5 = hists["L14p5_{}_{}".format(l_s, v)]
      L18 = hists["L18_{}_{}".format(l_s, v)]

      den = HLT.Clone()
      eff_L14p5 = L14p5.Clone()
      eff_L14p5.Divide(den)
      eff_L18 = L18.Clone()
      eff_L18.Divide(den)
      
      hists["eff_L14p5_{}_{}".format(l_s, v)] =eff_L14p5
      hists["eff_L18_{}_{}".format(l_s, v)] = eff_L18

  for h in hists :
    writeHist(hists[h], h) 

def displacementStudy(samples):
  graphs = {}
  hists = {}
  signal_dxy = []
  signal_dz = []

  bckg_dxy = []
  bckg_dz = []

  n = 100
  xf = 0.1
  xs = np.linspace(0, xf, n)
  
  halfBinWidth = xf/(2*n)
  errors_rx = np.full(n, halfBinWidth)
  errors_y = np.full(n, 0.0)
  for l_s, s in samples :

    for i in range(n):
      x = xs[i]
      n_all = bookHist(s, "all", ranges["ScoutingMuonVtxPair_mass"])
      n_dxy = bookHist(s.Filter("ScoutingMuonVtx_dxy[0] < {} && ScoutingMuonVtx_dxy[1] < {}".format(x,x)), "dxy", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_dz = bookHist(s.Filter("ScoutingMuonVtx_dz[0] < {} && ScoutingMuonVtx_dz[1] < {}".format(x,x)), "dz", ranges["ScoutingMuonVtxPair_mass_1bin"])
      
      hists["ns_all_{}_{}".format(l_s, i)] = n_all
      hists["ns_dz_{}_{}".format(l_s, i)] = n_dz
      hists["ns_dxy_{}_{}".format(l_s, i)] = n_dxy

  for l_s, s in samples:
    ns_all = []
    ns_dxy = []
    ns_dz = []
    for j in range(n) :
      ns_all.append(hists["ns_all_{}_{}".format(l_s, j)].Integral())
      ns_dxy.append(hists["ns_dxy_{}_{}".format(l_s, j)].Integral())
      ns_dz.append(hists["ns_dz_{}_{}".format(l_s, j)].Integral())
      
      rs_dxy = []
      rs_dz = []
      rs_dxy.append(ns_dxy[j]/ns_all[j])
      rs_dz.append(ns_dz[j]/ns_all[j])

      if (l_s == "signal") :
        signal_dxy.append(ns_dxy[j])
        signal_dz.append(ns_dz[j])
      else :
        bckg_dxy.append(ns_dxy[j])
        bckg_dz.append(ns_dz[j])

    n_dxy = ROOT.TGraphErrors(n, xs, np.array(ns_dxy), errors_rx, errors_y)
    graphs["{}_n_dxy".format(l_s)] = n_dxy
    n_dz = ROOT.TGraphErrors(n, xs, np.array(ns_dz), errors_rx, errors_y)
    graphs["{}_n_dz".format(l_s)] = n_dz

    eff_dxy = ROOT.TGraphErrors(n, xs, np.array(rs_dxy), errors_rx, errors_y)
    graphs["{}_eff_dxy".format(l_s)] = eff_dxy
    eff_dz = ROOT.TGraphErrors(n, xs, np.array(rs_dz), errors_rx, errors_y)
    graphs["{}_eff_dz".format(l_s)] = eff_dz

  for g in graphs :
    writeHist(graphs[g], g) 

def isoStudy(d) :
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
      n_trkIso = bookHist(s.Filter("ScoutingMuonVtx_trackIso[0] < {} && ScoutingMuonVtx_trackIso[1] < {}".format(x,x)), "trkIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_ECALIso = bookHist(s.Filter("ScoutingMuonVtx_ecalIso[0] < {} && ScoutingMuonVtx_ecalIso[1] < {}".format(x,x)), "ECALIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_HCALIso = bookHist(s.Filter("ScoutingMuonVtx_hcalIso[0] < {} && ScoutingMuonVtx_hcalIso[1] < {}".format(x,x)), "HCALIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_PFIso = bookHist(s.Filter("ScoutingMuonVtx_trackIso[0] < {} && ScoutingMuonVtx_trackIso[1] < {}".format(x,x)) \
                          .Filter("ScoutingMuonVtx_ecalIso[0] < {} && ScoutingMuonVtx_ecalIso[1] < {}".format(x,x)) \
                          .Filter("ScoutingMuonVtx_hcalIso[0] < {} && ScoutingMuonVtx_hcalIso[1] < {}".format(x,x)) \
                          , "PFIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_rTrkIso = bookHist(s.Filter("rTrkIso[0] < {} && rTrkIso[1] < {}".format(rx,rx)), "tTrkIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_rECALIso = bookHist(s.Filter("rECALIso[0] < {} && rECALIso[1] < {}".format(rx,rx)), "rECALISo", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_rHCALIso = bookHist(s.Filter("rHCALIso[0] < {} && rHCALIso[1] < {}".format(rx,rx)), "rHCALIso", ranges["ScoutingMuonVtxPair_mass_1bin"])
      n_rPFIso =  bookHist(s.Filter("rTrkIso[0] < {} && rTrkIso[1] < {}".format(rx,rx)) \
                                    .Filter("rECALIso[0] < {} && rECALIso[1] < {}".format(rx,rx)) \
                                    .Filter("rHCALIso[0] < {} && rHCALIso[1] < {}".format(rx,rx)) \
                                    , "rPFIso", ranges["ScoutingMuonVtxPair_mass_1bin"])


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

def plotEffs(var, title, x_label, fname) :
  inf = ROOT.TFile("Hist/efficiency.root", "READ")

  signal = getHistogram(inf, "signal", "eff", var)
  x0 = signal.GetPointX(0)
  xf = signal.GetPointY(signal.GetN()-1)
  print(x0, xf, signal.GetN())
  bckg = getHistogram(inf, "bckg", "eff", var)
  c_trk = CMS.cmsCanvas(title, x0, xf, 0, 1.0, \
                          x_label, "#epsilon")
  leg_trk = CMS.cmsLeg(0.5, 0.2, 0.6, 0.3)
  CMS.cmsObjectDraw(signal, "PE", MarkerColor=CMS.p6.kRed)
  leg_trk.AddEntry(signal, "Signal")
  CMS.cmsObjectDraw(bckg, "SAME PE", MarkerColor=CMS.p6.kBlue)
  leg_trk.AddEntry(bckg, "Background")
  leg_trk.Draw()
  c_trk.SaveAs("Hist/Efficiency/Efficiency_{}.png".format(fname))
  c_trk.SaveAs("Hist/Efficiency/Efficiency_{}.pdf".format(fname))

def plotSigFraction(var, title, x_label, fname):
  inf = ROOT.TFile("Hist/efficiency.root", "READ")
  graphs = {} 
  colors = {}
  for i in range(len(var)):
    signal = getHistogram(inf, "signal", "n", var[i])
    bckg = getHistogram(inf, "bckg", "n", var[i])

    pure = []
    
    n = signal.GetN()
    xs = signal.GetX()
    halfBinWidth = xs[n-1]/(2*n)
    errors_x = np.full(n, halfBinWidth)
    errors_y = np.full(n, 0.0)

    for j in range(n) :
      p = signal.GetPointY(j)/(signal.GetPointY(j) + bckg.GetPointY(j))
      pure.append(p)
    
    graph = ROOT.TGraphErrors(n, xs, np.array(pure), errors_x, errors_y)
    graphs[var[i]] = graph
    colors[var[i]] = p10[i]

  model = graphs[var[0]]
  y0 = model.GetPointY(0)*0.95
  yf = model.GetPointY(model.GetN()-1)*2

  print(y0, yf)
  c = CMS.cmsCanvas(title, xs[0], xs[n-1], y0, yf, \
                          x_label, "sig/tot")
  leg = CMS.cmsLeg(0.5, 0.6, 0.6, 0.8)
  for v in var :
    CMS.cmsObjectDraw(graphs[v], "SAME PEZ", MarkerColor=colors[v])
    leg.AddEntry(graphs[v], v)
  leg.Draw()
  c.SaveAs("Hist/Efficiency/SignalFraction_{}.png".format(fname))
  c.SaveAs("Hist/Efficiency/SignalFraction_{}.pdf".format(fname))

          

if __name__ == "__main__" :
  makeGraphs(sys.argv[1])
  # plotGraphs()

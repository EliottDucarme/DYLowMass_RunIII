import ROOT
import sys
import os
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# Define style
import cmsstyle as CMS
CMS.setCMSStyle()
CMS.SetExtraText("Preliminary")
CMS.SetLumi(11.42)
CMS.SetEnergy(13.6)

# Declare labels
labels = {
  "ScoutingMuonVtxLead_pt" : "p_{T}^{#mu} / GeV",
  "ScoutingMuonVtxSub_pt" : "p_{T}^{#mu} / GeV",
  "ScoutingMuonVtxLead_eta" : "#eta",
  "ScoutingMuonVtxSub_eta" : "#eta",
  "ScoutingMuonVtxLead_phi" : "#phi",
  "ScoutingMuonVtxSub_phi" : "#phi",
  "ScoutingMuonVtx_deltaPhi" : "#Delta #phi",
  "ScoutingMuonVtx_deltaEta" : "#Delta eta",
  "ScoutingMuonVtx_deltaR" : "#Delta R",
  "ScoutingMuonVtx_cosThetaCS" : "cos(#theta_{CS})",

  "ScoutingMuonVtxPair_Pt" : "p_{T}^{#mu#mu} / GeV",
  "ScoutingMuonVtxPair_PtLow" : "p_{T}^{#mu#mu} / GeV",
  "ScoutingMuonVtxPair_Y" : "Y^{#mu #mu}",
  "ScoutingMuonVtxPair_mass" : "M^{#mu#mu} / GeV",
  "ScoutingMuonVtxPair_massZ" : "M^{#mu#mu} / GeV",
  "ScoutingMuonVtxPair_eta"   : "#eta^{#mu#mu}",

  "trkIsolation" : "I^{#mu} / GeV",
  "ECalIsolation" : "I^{#mu} / GeV",
  "HCalIsolation" : "I^{#mu} / GeV",
  "relTrkIso"     : "I^{#mu}/p^{#mu}",
  "relECalIso"    : "I^{#mu}/p^{#mu}",
  "relHCalIso"     : "I^{#mu}/p^{#mu}",
  
  "TruePFJet_HT" : "H_{T} / GeV",
  "TruePFJet_pt" : "p_{T} / GeV",
  "nTruePFJet" : "N_{PFJet}",
  "nScoutingPFJet" : "N_{PFJet}",
  "TruePFJetRecluster_HT" : "H_{T} / GeV",
  "TruePFJetRecluster_pt" : "p_{T} / GeV",
  "nTruePFJetRecluster" : "N_{PFJetRecluster}",
  "nScoutingPFJetRecluster" : "N_{PFJetRecluster}",

  "nScoutingPrimaryVertex" : "N_{Vtx}",
  "ScoutingPrimaryVertex_tracksSize" : "N_{tracks}/Vtx",
  "Strip_Hit" : "# Strip Hit",
  "Pixel_Hit" : "# Pixel Hit",
  "Tracker_Hit" : "# Tracker Layer",
  "MuonChamber_Hit" : "# Muon Chamber Hit",
  "MatchedStation" : "# Matched Station",

  "ScoutingMuonVtx_dxy" : "d_{xy} [cm]",
  "ScoutingMuonVtx_dxy_short" : "d_{xy} [cm]",
  "ScoutingMuonVtx_dz" : "d_{z} [cm]",
  "ScoutingMuonVtx_dz_short" : "d_{z} [cm]",
  "ScoutingMET_pt" : "p_{T}^{MET}",

  }

# Set colors
colors = {
  "DYto2Mu" : CMS.p10.kBlue,
  "DYto2Tau" : CMS.p10.kViolet,
  "QCD" : CMS.p10.kRed,
  "TT" : CMS.p10.kYellow
}

# Declare isolation level
massWindows = [
      "Incl",
      "Upsilon",
      "QCD",
      "W",
      "Z"
   ]

# Retrieve histograms based on process, variable and isolation
def getHistogram(tfile, name, variable, mass, tag=""):
    name = "{}_{}_{}{}".format(name, variable, mass, tag)
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def getScaleFactor() :
  inf_N = "Hist/histograms.root"
  inf = ROOT.TFile(inf_N, "READ")

  # sim
  scaleDY_DY2mu= getHistogram( inf, "DYto2Mu", "ScoutingMuonVtxPair_mass", "Z")
  scaleDY_qcd = getHistogram( inf, "QCD", "ScoutingMuonVtxPair_mass", "Z")
  scaleDY_TT = getHistogram( inf, "TT", "ScoutingMuonVtxPair_mass", "Z")
  scaleDY_DY2tau = getHistogram( inf, "DYto2Tau", "ScoutingMuonVtxPair_mass", "Z")
  dy_DY2mu = scaleDY_DY2mu.Integral()
  dy_qcd = scaleDY_qcd.Integral()
  dy_TT = scaleDY_TT.Integral()
  dy_DY2tau = scaleDY_DY2tau.Integral()

  # scaleQCD_qcd = getHistogram( inf, "QCD", "ScoutingMuonVtxPair_mass", "QCD")
  # scaleQCD_dy = getHistogram( inf, "DYto2Mu", "ScoutingMuonVtxPair_mass", "QCD")
  # scaleQCD_TT = getHistogram( inf, "TT", "ScoutingMuonVtxPair_mass", "QCD")
  # scaleQCD_DY2tau = getHistogram( inf, "DYto2Tau", "ScoutingMuonVtxPair_mass", "QCD")
  # bckg_qcd = scaleQCD_qcd.Integral()
  # bckg_TT = scaleDY_TT.Integral()
  # bckg_DY2tau = scaleDY_DY2tau.Integral()
  # bckg_dy = scaleQCD_dy.Integral()
  # bckg = bckg_qcd + bckg_TT + bckg_DY2tau

  # real stuff
  data_dy = getHistogram( inf, "Data", "ScoutingMuonVtxPair_mass", "Z")
  data_dy = data_dy.Integral()

  # data_bckg = getHistogram( inf, "Data", "ScoutingMuonVtxPair_mass", "QCD")
  # data_bckg = data_bckg.Integral()

  # Substract contribution for the other process
  # and compute scale factor
  # data_dy = data_dy - dy_qcd - dy_DY2tau - dy_TT        #to use on signal
  rdy = data_dy/(dy_DY2mu + dy_qcd + dy_DY2tau +  dy_TT)  # to use on data

  # data_bckg = data_bckg - bckg_dy
  # if data_bckg == 0 :
  #    rqcd = 1
  # else :
  #   rqcd = data_bckg/bckg
  return rdy, 1.0

def main(var, mass, scale):
  inf_n = "Hist/histograms.root"
  inf = ROOT.TFile(inf_n, "READ")

  # # Get simulation
  dyMu = getHistogram( inf, "DYto2Mu", var, mass)
  dyMu.Scale(scale[0])
  dyTau = getHistogram( inf, "DYto2Tau", var, mass)
  dyTau.Scale(scale[0])
  qcd = getHistogram( inf, "QCD", var, mass)
  qcd.Scale(scale[0])
  tt = getHistogram( inf, "TT", var, mass)
  tt.Scale(scale[0])

  # Get the real stuff
  data = getHistogram( inf, "Data", var, mass)
  # data.Scale(1/scale[0])


  # draw a clone of the ratio plot
  # a canvas that is not going to be saved
  tmpc = ROOT.TCanvas("", "", 600, 600)
  mc = dyMu.Clone()
  mc.Add(qcd)
  mc.Add(tt)
  mc.Add(dyTau)
  ratio = ROOT.TRatioPlot(data, mc)
  ratio.Draw()
  r_mean = ratio.GetLowerRefGraph().GetMean(2)
  r_StdDev = ratio.GetLowerRefGraph().GetRMS(2)
  if r_StdDev == 0 or r_StdDev > 0.4 :
     r_StdDev = 0.4
  r_max = r_mean + 2*r_StdDev
  r_min = r_mean - 2*r_StdDev

  # use cmsstyle to define a canvas
  xlow = data.GetBinLowEdge(1)
  xhigh = data.GetBinLowEdge(data.GetNbinsX()+1)
  c = CMS.cmsDiCanvas(var, xlow, xhigh, \
        max((data.GetMaximum())/(10**4),1.0), data.GetMaximum()*100, r_min, r_max, \
          labels[var], "Entries", "Data/MC")

  # Make legend
  legend = CMS.cmsLeg(0.6, 0.73, 0.88, 0.88)

  # Draw
  c.cd(1)
  stack = ROOT.THStack("", "")
  ROOT.gPad.SetLogy()
  for xobj in samples:
      legend.AddEntry(*xobj)
  CMS.cmsObjectDraw(stack, "HIST")
  CMS.cmsDraw(data, "SAME APE")
  data.SetStats(0)
  ROOT.gPad.RedrawAxis()


  # get the ratio from TRatio and draw it on cmsDiCanvas
  #lower pad
  c.cd(2)
  r = ratio.GetLowerRefGraph()
  CMS.cmsDraw(r, "PE")
  if not (r_StdDev == 0 or r_StdDev > 0.4) :
    up_line = ROOT.TLine(xlow, r_mean + r_StdDev, xhigh, r_mean + r_StdDev)
    dn_line = ROOT.TLine(xlow, r_mean - r_StdDev, xhigh, r_mean - r_StdDev)
    mid_line = ROOT.TLine(xlow, r_mean , xhigh, r_mean )
    up_line.SetLineStyle(2)
    dn_line.SetLineStyle(2)
    mid_line.SetLineStyle(2)
    up_line.Draw()
    dn_line.Draw()
    mid_line.Draw()

  # Check if 1 is in range for the reference line to be drawn
  if ( (r_mean + 2*r_StdDev > 1) and (r_mean - 2*r_StdDev < 1)) :
    ROOT.gPad.Update()
    line = ROOT.TLine(xlow, 1, xhigh, 1)
    line.SetLineWidth(1)
    line.Draw()

  # Add title
  latex = ROOT.TLatex()
  latex.SetNDC()
  latex.SetTextSize(0.04)
  latex.SetTextFont(42)

  # Save
  c.SaveAs("Hist/Main/{}/{}.pdf".format(mass, var))
  c.SaveAs("Hist/Main/{}/{}.png".format(mass, var))

# Loop over all variable names and make a plot for each
if __name__ == "__main__":
  ROOT.EnableImplicitMT(16)
  # scale_dyMu, scale_bckg = getScaleFactor()
  # print(scale_dyMu, scale_bckg)
  for variable in labels.keys():
      for mass in massWindows :
        main(variable, mass, (1.0, 1.0))

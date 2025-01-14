import ROOT
import sys
import os
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# Define style 
import cmsstyle as CMS
CMS.SetExtraText("Preliminary")
CMS.SetLumi("3.08")

# Declare labels 
labels = {
  "lead_pt" : "p_{T}^{#mu} / GeV",
  "sub_pt" : "p_{T}^{#mu} / GeV",
  "lead_eta" : "#eta",
  "sub_eta" : "#eta",
  "lead_phi" : "#phi",
  "sub_phi" : "#phi",
  "diPt" : "p_{T}^{#mu#mu} / GeV",
  "diMass" : "M^{#mu#mu} / GeV",
  "diMassZ" : "M^{#mu#mu} / GeV",
  "diMassLow" : "M^{#mu#mu} / GeV",
  "diEta"   : "#eta^{#mu#mu}",
  "dimassQCDscale" : "M^{#mu#mu} / GeV",
  "dimassDYscale" : "M^{#mu#mu} / GeV",
  "trkIsolation" : "I^{#mu}",
  "ECalIsolation" : "I^{#mu}",
  "HCalIsolation" : "I^{#mu}",
  "relTrkIso"     : "I^{#mu}/p^{#mu}",
  "relEcalIso"    : "I^{#mu}/p^{#mu}",
  "relHcalIso"     : "I^{#mu}/p^{#mu}",
  # "Strip_Hit" : "# Strip Hit",
  # "Pixel_Hit" : "# Pixel Hit",
  # "Tracker_Hit" : "# Tracker Layer",
  # "MuonChamber_Hit" : "# Muon Chamber Hit",
  # "MatchedStation" : "# Matched Station",
  }

# Set colors
colors = {
  "DY" : ROOT.TColor.GetColor(155, 152, 204),
  "QCD" : ROOT.TColor.GetColor(222, 90, 106)
}

# Declare isolation level
isos = [
  "NIReq", 
  "Biso", 
  "Siso", 
  "Niso"
   ]

# Retrieve histograms based on process, variable and isolation
def getHistogram(tfile, name, variable, iso, tag=""):
    name = "{}_{}_{}{}".format(name, variable, iso, tag)
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def getScaleFactor() :
  inf_N = "Hist/histograms.root"
  inf = ROOT.TFile(inf_N, "READ")
  # sim
  scaleDY_dy = getHistogram( inf, "DY", "dimassDYscale", "Biso")
  scaleDY_qcd = getHistogram( inf, "QCD", "dimassDYscale", "Biso")
  dy_dy = scaleDY_dy.GetBinContent(1)
  dy_qcd = scaleDY_qcd.GetBinContent(1)

  scaleQCD_qcd = getHistogram( inf, "QCD", "dimassQCDscale", "Niso")
  scaleQCD_dy = getHistogram( inf, "DY", "dimassQCDscale", "Niso")
  qcd_qcd = scaleQCD_qcd.GetBinContent(1)
  qcd_dy = scaleQCD_dy.GetBinContent(1)

  # real stuff
  DATA_dy = getHistogram( inf, "Data", "dimassDYscale", "Biso")
  data_dy = DATA_dy.GetBinContent(1)

  DATA_qcd = getHistogram( inf, "Data", "dimassQCDscale", "Niso")
  data_qcd = DATA_qcd.GetBinContent(1)

  # Substract contribution for the other process
  # and compute scale factor
  data_dy = data_dy - dy_qcd
  rdy = data_dy/dy_dy

  data_qcd = data_qcd - qcd_dy
  if data_qcd == 0 : 
     rqcd = 1
  else :
    rqcd = data_qcd/qcd_qcd
  return rdy, rqcd

def main(var, iso, scale):
  inf_n = "Hist/histograms.root"
  inf = ROOT.TFile(inf_n, "READ")
  
  # # Get simulation
  dy = getHistogram( inf, "DY", var, iso)
  dy.Scale(scale[0])
  qcd = getHistogram( inf, "QCD", var, iso)
  qcd.Scale(scale[1])

  # Get the real stuff
  data = getHistogram( inf, "Data", var, iso)

  # draw a clone of the ratio plot
  # a canvas that is not going to be saved
  tmpc = ROOT.TCanvas("", "", 600, 600)
  mc = qcd.Clone()
  mc.Add(dy)
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
        data.GetMinimum()/100+1, data.GetMaximum()*100, r_min, r_max, \
          labels[var], "Entries", "Data/MC")
  
  # Make legend
  legend = CMS.cmsLeg(0.6, 0.73, 0.88, 0.88)

  # Draw 
  c.cd(1)
  stack = ROOT.THStack("", "")
  ROOT.gPad.SetLogy()
  samples = { "Drell-Yan"                 : dy, 
              "QCD, p^{#mu}_{T} > 5 GeV"  : qcd}
  CMS.cmsDrawStack(stack, legend, samples, data)
  c.Update()
  data.SetStats(0)

  
  # get the ratio from TRatio and draw it on cmsDiCanvas
  #lower pad
  c.cd(2)
  r = ratio.GetLowerRefGraph()
  CMS.cmsDraw(r, "PE")
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
  c.SaveAs("Hist/{}/{}.pdf".format(iso, var))
  c.SaveAs("Hist/{}/{}.png".format(iso, var))
  
# Loop over all variable names and make a plot for each
if __name__ == "__main__":
  # scale_dy, scale_qcd = getScaleFactor()
  for variable in labels.keys():
      for iso in isos : 
        main(variable, iso, (1.0, 1.0))

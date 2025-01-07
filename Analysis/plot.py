import ROOT
import sys
import os
ROOT.gROOT.SetBatch(True)

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
  "dimassQCDscale" : "M^{#mu#mu} / GeV",
  "dimassDYscale" : "M^{#mu#mu} / GeV",
  "trkIsolation" : "I^{#mu}",
  "ECalIsolation" : "I^{#mu}",
  "HCalIsolation" : "I^{#mu}",
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
  #  "Siso", 
  "Niso"
   ]

# Retrieve histograms based on process, variable and isolation
def getHistogram(tfile, name, variable, iso, tag=""):
    name = "{}_{}_{}{}".format(name, variable, iso, tag)
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def GetScaleFactor() :
  inf_N = "Hist/histograms.root"
  inf = ROOT.TFile(inf_N, "READ")

  # sim
  DY_dy = getHistogram( inf, "DY", "dimassDYscale", "Biso")
  DY_qcd = getHistogram( inf, "QCD", "dimassDYscale", "Biso")
  dy_dy = DY_dy.GetBinContent(1)
  dy_qcd = DY_qcd.GetBinContent(1)

  QCD_qcd = getHistogram( inf, "QCD", "dimassQCDscale", "Niso")
  QCD_dy = getHistogram( inf, "DY", "dimassQCDscale", "Niso")
  qcd_qcd = QCD_qcd.GetBinContent(1)
  qcd_dy = QCD_dy.GetBinContent(1)

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
  DY = getHistogram( inf, "DY", var, iso)
  DY.Scale(scale[0])
  QCD = getHistogram( inf, "QCD", var, iso)
  QCD.Scale(scale[1])

  # Get the real stuff
  Data = getHistogram( inf, "Data", var, iso)
  
  # Stack to compare visually simulation and real stuff
  stack = ROOT.THStack("", "")

  # Ratio to quantify the difference between simulation and real stuff
  MC = DY.Clone()
  MC.Add(QCD)
  ratio = Data/MC

  # Set the ratio plot range to keep interesting values visibles
  r_mean = ratio.GetMean(2)
  r_StdDev = ratio.GetRMS(2)
  print(r_mean, r_StdDev)
  if r_StdDev == 0 or r_StdDev > 0.4 :
     r_StdDev = 0.4
  xlow = Data.GetBinLowEdge(1)
  xhigh = Data.GetBinLowEdge(Data.GetNbinsX()+1)
  # print(labels[var])
  c = CMS.cmsDiCanvas(var, xlow, xhigh, \
        Data.GetMinimum()/1000, Data.GetMaximum()*10+1, 0.5, 1.5, \
          labels[var], "Entries", "Data/MC")
  # ratio.SetGridlines({r_mean-r_StdDev, r_mean, r_mean+r_StdDev})
  
  # # Text with the stat values
  # stat = ROOT.TPaveText(0.01, 0.01, 0.25, 0.03, "NDC")
  # stat.SetTextSize(0.02)
  # stat.SetFillColor(0)
  # text = "Mean : {:.3f} ; RMS : {:.3f}".format(r_mean, r_StdDev)
  # stat.AddText(text)
  # stat.Draw()

  # Check if 1 is in range for the reference line to be drawn
  if ( (r_mean + 2*r_StdDev > 1) and (r_mean - 2*r_StdDev < 1)) :
    ratio.GetLowerPad().cd() 
    ROOT.gPad.Update()
    xmin = ROOT.gPad.GetUxmin()
    xmax = ROOT.gPad.GetUxmax()
    line = ROOT.TLine(xmin, 1, xmax, 1)
    line.SetLineWidth(2)
    line.Draw()
    
  # Make legend
  legend = CMS.cmsLeg(0.6, 0.73, 0.88, 0.88)

  # Draw
  c.cd(1)
  ROOT.gPad.SetLogy()
  samples = {"Drell-Yan"                    : DY, 
              "QCD, p^{#mu}_{T} > 4.5 GeV"  : QCD}
  CMS.cmsDrawStack(stack, legend, samples, Data)
  
  c.cd(2)
  CMS.cmsDraw(ratio, "HIST PE")
  # ratio.Draw("Hist PE")


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
  scale_dy = 1.0
  scale_qcd = 1.0
  # scale_dy, scale_qcd = GetScaleFactor()
  for variable in labels.keys():
      for iso in isos : 
        main(variable, iso, (scale_dy, scale_qcd))

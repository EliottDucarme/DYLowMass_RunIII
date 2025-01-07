#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os
import numpy as np
from array import array

def writeHist(h, name): #Write it !
  h.SetName(name)
  h.Write()

def main():
  # Output file
  outf_name = "Hist/cutStudy.root"
  outf = ROOT.TFile(outf_name, "RECREATE")

  # Create the dataframe with the .json spec file
  ROOT.EnableImplicitMT(12)
  # d = ROOT.RDF.Experimental.FromSpec("samplesData.json")
  # d = ROOT.RDF.Experimental.FromSpec("samplesDY.json")
  d = ROOT.RDF.Experimental.FromSpec("samples.json")
  ROOT.RDF.Experimental.AddProgressBar(d)

  # check if sample provided is MC or not
  # lumi is in fb^-1
  ROOT.gInterpreter.Declare(
    """
    float reweighting(double xsec, double sumws, std::string type){
       if (type.find("MC") != std::string::npos) return 3.0828*xsec/sumws;
       else return 1.0;
    }
    """
  )

  # Extract indice of the leading muon in pt and the sub-leading
  ROOT.gInterpreter.Declare(
    """
    using namespace ROOT::VecOps;
    RVec<float> sorting(const RVec<float> sorter){
      auto sortedIndices = Argsort(sorter);
      return sortedIndices;
    }
    """
  )

  # 

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("sumws")')
  d = d.DefinePerSample("type", 'rdfsampleinfo_.GetS("type")')
  d = d.Define("norm", 'reweighting(xsec, sumws, type)',{"xsec", "sumws",  "type"})

  # Filter the events
  d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream")
  d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")

  # Define new variables
  d = d.Define("ind", 'sorting(ScoutingMuon_pt)', {"ScoutingMuon_pt"})
  d = d.Define("leadpt", "ScoutingMuon_pt[ind[1]]").Define("subpt", "ScoutingMuon_pt[ind[0]]")
  d = d.Define("leadeta", "ScoutingMuon_eta[ind[1]]").Define("subeta", "ScoutingMuon_eta[ind[0]]")
  d = d.Define("leadphi", "ScoutingMuon_phi[ind[1]]").Define("subphi", "ScoutingMuon_phi[ind[0]]")
  d = d.Define("rIso", "ScoutingMuon_trackIso/ScoutingMuon_pt" , {"ScoutingMuon_pt", "ScoutingMuon_trackIso"})
  d = d.Filter('All(rIso < 0.15)', "Isolated muons")
  # d = d.Filter('leadpt/ScoutingMuon_diMass > 0.25').Filter('subpt/ScoutingMuon_diMass> 0.25', "leptons are decay products of the original boson")

  # Separate samples and add them to the sample list
  samples = []
  dD = d.Filter('type == "Data"')
  samples.append(("Data", dD))
  dDY = d.Filter('type == "MC_DY"')
  samples.append(("DY", dDY))
  dQCD = d.Filter('type == "MC_QCD"')
  samples.append(("QCD", dQCD))

  dD.Report().Print()

  # Book hists for each sample
  hists ={}
  nx = 110
  ny = 105
  x_start = 0
  x_end = 110

  for df_label, df in samples :
    hists["subPtvsMll_{}".format(df_label)] = df.Histo2D(("subPtvsMll_{}".format(df_label), "subPtvsMll_{}".format(df_label), nx, x_start, x_end, ny, 0, 105), "ScoutingMuon_diMass","subpt", "norm")
    hists["leadPtvsMll_{}".format(df_label)] = df.Histo2D(("leadPtvsMll_{}".format(df_label), "leadPtvsMll_{}".format(df_label), nx, x_start, x_end, ny, 0, 105), "ScoutingMuon_diMass", "leadpt", "norm")

  for h in hists:
    writeHist(hists[h], h)

  # store bin number
  x = array('d')
  # store bin width
  x_width = np.full(ny, 0.5)

  # store average by bin number
  dataSubAvgs = array('d')
  dySubAvgs = array('d')
  qcdSubAvgs = array('d')
  dataLeadAvgs = array('d')
  dyLeadAvgs = array('d')
  qcdLeadAvgs = array('d')

  # store RMS by bin number
  dataSubRMSs = array('d')
  dySubRMSs = array('d')
  qcdSubRMSs = array('d')
  dataLeadRMSs = array('d')
  dyLeadRMSs = array('d')
  qcdLeadRMSs = array('d')


  for i in range(nx) : 
    x_i = i + x_start
    print(x_i)
    x.append(x_i)

    hSubData = hists["subPtvsMll_Data"].Clone() 
    hSubData.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    dataSubAvg = hSubData.GetMean(2)
    dataSubAvgs.append(dataSubAvg)
    dataSubRMS = hSubData.GetRMS(2)
    dataSubRMSs.append(dataSubRMS)

    hSubDy = hists["subPtvsMll_DY"].Clone()
    hSubDy.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    dySubAvg = hSubDy.GetMean(2)
    dySubAvgs.append(dySubAvg)
    dySubRMS = hSubDy.GetRMS(2)
    dySubRMSs.append(dySubRMS)

    hSubQcd = hists["subPtvsMll_QCD"].Clone()
    hSubQcd.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    qcdSubAvg = hSubQcd.GetMean(2)
    qcdSubAvgs.append(qcdSubAvg)
    qcdSubRMS = hSubQcd.GetRMS(2)
    qcdSubRMSs.append(qcdSubRMS)

    hLeadData = hists["leadPtvsMll_Data"].Clone() 
    hLeadData.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    dataLeadAvg = hLeadData.GetMean(2)
    dataLeadAvgs.append(dataLeadAvg)
    dataLeadRMS = hLeadData.GetRMS(2)
    dataLeadRMSs.append(dataLeadRMS)

    hLeadDy = hists["leadPtvsMll_DY"].Clone()
    hLeadDy.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    dyLeadAvg = hLeadDy.GetMean(2)
    dyLeadAvgs.append(dyLeadAvg)
    dyLeadRMS = hLeadDy.GetRMS(2)
    dyLeadRMSs.append(dyLeadRMS)

    hLeadQcd = hists["leadPtvsMll_QCD"].Clone()
    hLeadQcd.GetXaxis().SetRangeUser(x_start + i, 11 + i)
    qcdLeadAvg = hLeadQcd.GetMean(2)
    qcdLeadAvgs.append(qcdLeadAvg)
    qcdLeadRMS = hLeadQcd.GetRMS(2)
    qcdLeadRMSs.append(qcdLeadRMS)

  dataSubDist = ROOT.TGraphErrors(nx, x, dataSubAvgs, x_width, dataSubRMSs)
  dataSubDist.SetTitle("Data; M^{#mu #mu} (GeV); <P^{s}_{T}>/GeV")
  dataSubDist.SetMarkerStyle(8)
  dataSubDist.SetMarkerColor(ROOT.TColor.GetColor(155, 152, 204))
  dataSubDist.SetLineColor(ROOT.TColor.GetColor(155, 152, 204))

  dySubDist = ROOT.TGraphErrors(nx, x, dySubAvgs, x_width, dySubRMSs)
  dySubDist.SetTitle("DY")
  dySubDist.SetMarkerStyle(8)
  dySubDist.SetMarkerColor(ROOT.TColor.GetColor(222, 90, 106))
  dySubDist.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))

  qcdSubDist = ROOT.TGraphErrors(nx, x, qcdSubAvgs, x_width, qcdSubRMSs)
  qcdSubDist.SetTitle("QCD")
  qcdSubDist.SetMarkerStyle(8)
  qcdSubDist.SetMarkerColor(ROOT.TColor.GetColor(248, 156, 32))
  qcdSubDist.SetLineColor(ROOT.TColor.GetColor(248, 156, 32))

  dataLeadDist = ROOT.TGraphErrors(nx, x, dataLeadAvgs, x_width, dataLeadRMSs)
  dataLeadDist.SetTitle("Data; M^{#mu #mu} (GeV); <P^{l}_{T}>/GeV")
  dataLeadDist.SetMarkerStyle(8)
  dataLeadDist.SetMarkerColor(ROOT.TColor.GetColor(155, 152, 204))
  dataLeadDist.SetLineColor(ROOT.TColor.GetColor(155, 152, 204))

  dyLeadDist = ROOT.TGraphErrors(nx, x, dyLeadAvgs, x_width, dyLeadRMSs)
  dyLeadDist.SetTitle("DY")
  dyLeadDist.SetMarkerStyle(8)
  dyLeadDist.SetMarkerColor(ROOT.TColor.GetColor(222, 90, 106))
  dyLeadDist.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))

  qcdLeadDist = ROOT.TGraphErrors(nx, x, qcdLeadAvgs, x_width, qcdLeadRMSs)
  qcdLeadDist.SetTitle("QCD")
  qcdLeadDist.SetMarkerStyle(8)
  qcdLeadDist.SetMarkerColor(ROOT.TColor.GetColor(248, 156, 32))
  qcdLeadDist.SetLineColor(ROOT.TColor.GetColor(248, 156, 32))

  cs = ROOT.TCanvas("", "", 600, 600)
  cs.SetGrid()
  dataSubDist.Draw("APE")
  dySubDist.Draw("SAME PE")
  qcdSubDist.Draw("SAME PE")
  cs.BuildLegend()
  cs.SaveAs("Hist/ptSubVsMll.pdf")
  cs.SaveAs("Hist/ptSubVsMll.png")

  cl = ROOT.TCanvas("", "", 600, 600)
  cl.SetGrid()
  dataLeadDist.Draw("APE")
  dyLeadDist.Draw("SAME PE")
  qcdLeadDist.Draw("SAME PE")
  cl.BuildLegend()
  cl.SaveAs("Hist/ptLeadVsMll.pdf")
  cl.SaveAs("Hist/ptLeadVsMll.png")
  
if __name__ == "__main__":
  main()
#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os
import cmsstyle as CMS

ROOT.gInterpreter.ProcessLine('#include "helper.h"')

# Declaration of ranges for each histogram type
default_nbins = 100
ranges = {
  "diPt" : ( default_nbins, 0.0, 100.0),
  "diMass" : ( default_nbins, 10.0, 110.0),
  "lead" : ( default_nbins, 5.0, 105.0),
  "sub" : ( default_nbins, 5.0, 105.0),
  "diY" : ( default_nbins, -4.0, 8.0)
}

def bookHist(d, name, range_, inp): #Histo booking
  return d.Histo1D(ROOT.ROOT.RDF.TH1DModel(name, name, range_[0], range_[1], range_[2]),\
                   inp, "norm")

def bookHist2D(d, name, range_, inp): # 2D Histo booking
  return d.Histo2D(ROOT.ROOT.RDF.TH2DModel(name, name, range_[0], range_[1], range_[2], range_[0], range_[1], range_[2]),\
                   "genMuon_" + inp, "ScoutingMuon_" + inp, "norm")

def writeHist(h, name): #Write it !
  h.SetName(name)
  h.Write()
  
# Retrieve histograms based on process, variable and isolation
def getHistogram(tfile, name, variable, tag=""):
    name = "{}_{}{}".format(name, variable, tag)
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def main():
  # ROOT.gInterpreter.ProcessLine('#include "helper.h"')
  # ROOT.gSystem.Load('helper.so')
  # Output file
  outf_name = "Hist/resolutionStudy.root"
  outf = ROOT.TFile(outf_name, "RECREATE")

  # Create the dataframe with the .json spec file
  ROOT.EnableImplicitMT(12)
  d = ROOT.RDF.Experimental.FromSpec("genDySamples.json")
  ROOT.RDF.Experimental.AddProgressBar(d)
  # d = d.Range(10000)

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("sumws")')
  d = d.DefinePerSample("type", 'rdfsampleinfo_.GetS("type")')
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, type)',{"xsec", "sumws", "genWeight", "type"})

  # find pair of generated muon and define associated variables
  # take the findGenMuon from helper files
  d = d.Define("genMu", 'findGenMuons(GenPart_pdgId, GenPart_status, GenPart_statusFlags)')
  d = d.Define("genMuon_pt", "RVec<float> pt; pt.push_back(GenPart_pt[genMu[0]]); pt.push_back(GenPart_pt[genMu[1]]); pt = Reverse(pt); return pt;")
  d = d.Define("genMuon_lead", "genMuon_pt[0]").Define("genMuon_sub", "genMuon_pt[1]")
  d = d.Define("genMuon_eta", "RVec<float> eta; eta.push_back(GenPart_eta[genMu[0]]); eta.push_back(GenPart_eta[genMu[1]]); return eta;")
  d = d.Define("genMuon_phi", "RVec<float> phi; phi.push_back(GenPart_phi[genMu[0]]); phi.push_back(GenPart_phi[genMu[1]]); return phi;")

  d = d.Define("genDimuonKinematic", 'dimuonKinematics(genMuon_pt, genMuon_eta, genMuon_phi)')
  d = d.Define("genMuon_diMass", "genDimuonKinematic[3]")
  d = d.Define("genMuon_diPt", "genDimuonKinematic[0]")
  d = d.Define("genMuon_diEta", "genDimuonKinematic[1]")
  d = d.Define("genMuon_diPhi", "genDimuonKinematic[2]")
  d = d.Define("genMuon_diY", "genDimuonKinematic[4]")
  d = d.Filter("genMu.size() == 2", "two generated muons")
  # d = d.Filter("All(abs(genMuon_eta) < 2.4)", "in detector acceptance")
  # d = d.Filter("genMuon_diMass > 10 && genMuon_diMass < 110", "in scope of the analysis")

  # d = d.Filter("nScoutingMuon == 2", "two reconstructed muons")
  # d = d.Filter("All(abs(ScoutingMuon_eta) < 2.4)", "in detector acceptance")
  d = d.Define("scoutingDimuonKinematic",'dimuonKinematics(ScoutingMuon_pt, ScoutingMuon_eta, ScoutingMuon_phi)')
  d = d.Define("ScoutingMuon_diY", "scoutingDimuonKinematic[4]")
  d = d.Define("ScoutingMuon_lead", "RVec<float> pt =Reverse(ScoutingMuon_pt); return pt[0]")
  d = d.Define("ScoutingMuon_sub", "RVec<float> pt =Reverse(ScoutingMuon_pt); return pt[1]")

  rep = d.Report()
  var = ranges.keys()
  hists = {}
  for v in var:
    hgen = "genMuon_" + v
    hists[hgen] = bookHist(d, v, ranges[v], "genMuon_{}".format(v))
    hrec = "ScoutingMuon_" + v
    hists[hrec] = bookHist(d, v, ranges[v], "ScoutingMuon_{}".format(v))
    h2D = "correlationGenVsRec_" + v
    hists[h2D] = bookHist2D(d, v, ranges[v], v)

  for h in hists :
    writeHist(hists[h], h)

  rep.Print()

  for v in var:
    nGen = "genMuon_" + v
    hGen = getHistogram(outf, "genMuon", v)
    nRec = "ScoutingMuon_" + v
    hRec = getHistogram(outf, "ScoutingMuon", v)
    res = hRec.Clone()
    res.Add(hGen, -1)
    writeHist(res, "min_" + v)
    res.Divide(hGen)
    writeHist(res, "res_" + v)

    absRes = ROOT.TH1D("absRes_" + v, "absRes_" + v, default_nbins, ranges[v][1], ranges[v][2])
    for i in range(1, default_nbins + 1) :
      i_bin = res.GetBinContent(i)
      absI_bin = abs(i_bin)
      absRes.SetBinContent(i, absI_bin)
    writeHist(absRes, "absRes" + v)

    c = CMS.cmsCanvas("Resolution" + v, ranges[v][1], ranges[v][2], res.GetMinimum()-0.2, res.GetMaximum()+0.2, v, "Entries")
    CMS.cmsDraw(res, "PE", mcolor = CMS.p6.kBlue)
    c.SaveAs("Hist/Resolution/res_" + v + ".png")
    c.SaveAs("Hist/Resolution/res_" + v + ".pdf")
    



if __name__ == "__main__":
  main()


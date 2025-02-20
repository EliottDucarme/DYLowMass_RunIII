import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os
import cmsstyle as CMS

CMS.SetExtraText("Preliminary")
CMS.SetLumi("3.08")

ROOT.gInterpreter.ProcessLine('#include "helper.h"')

# Declaration of ranges for each histogram type
default_nbins = 100
ranges = {
  "diPt" : ( default_nbins, 0.0, 100.0),
  "diMass" : ( default_nbins, 10.0, 110.0),
  "lead" : ( default_nbins, 5.0, 105.0),
  "sub" : ( default_nbins, 5.0, 105.0),
  "diY" : ( default_nbins, -3.0, 3.0)
}

var = ranges.keys()

def bookHist(d, name, range_, inp): #Histo booking
  return d.Histo1D(ROOT.ROOT.RDF.TH1DModel(name, name, range_[0], range_[1], range_[2]),\
                   inp, "norm")

def bookHist2D(d, name, range1_, range2_, v1, v2): # 2D Histo booking
  return d.Histo2D(ROOT.ROOT.RDF.TH2DModel(name, name, range1_[0], range1_[1], range1_[2],\
                                             range2_[0], range2_[1], range2_[2]), v1, v2, "norm")

def bookProfile(d, name, range1_, range2_, v1, v2):
    return d.Profile1D(ROOT.ROOT.RDF.TProfile1DModel(name, name, range1_[0], range1_[1], range1_[2],\
                                             range2_[0], range2_[1], range2_[2]), v1, v2, "norm")

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

def makeCorrHist():
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
  d = d.Define("nGenMuon", "genMu.size()")

  d = d.Filter("nGenMuon == 2", "two generated muons")
  d = d.Filter("GenPart_pdgId[genMu[0]]*GenPart_pdgId[genMu[1]] == -169","isOSGenMuons")

  d = d.Filter("DST_Run3_PFScoutingPixelTracking", "HLT Scouting Stream")
  d = d.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1 fired")
  d = d.Filter("nScoutingMuon == 2", "two reconstructed muons")
  d = d.Filter("All(abs(ScoutingMuon_eta) < 2.0)", "in detector acceptance")
  d = d.Filter("All(ScoutingMuon_pt > 5.0)", "above pt threshold")
  d = d.Define("scoutingDimuonKinematic",'dimuonKinematics(ScoutingMuon_pt, ScoutingMuon_eta, ScoutingMuon_phi)')
  d = d.Define("ScoutingMuon_diY", "scoutingDimuonKinematic[4]")
  d = d.Define("ScoutingMuon_lead", "RVec<float> pt =Reverse(ScoutingMuon_pt); return pt[0]")
  d = d.Define("ScoutingMuon_sub", "RVec<float> pt =Reverse(ScoutingMuon_pt); return pt[1]")


  ROOT.gInterpreter.Declare(
    """
    float_t relativDiff(const float_t& rec, const float_t& gen)
    {
      auto res = (gen-rec)/gen;
      return res;
    }
    """
  )

  d = d.Define("relDiff_diMass", 'relativDiff(ScoutingMuon_diMass, genMuon_diMass)')
  d = d.Define("relDiff_diPt", 'relativDiff(ScoutingMuon_diPt, genMuon_diPt)')
  d = d.Define("relDiff_diY", 'relativDiff(ScoutingMuon_diY, genMuon_diY)')
  d = d.Define("relDiff_lead", 'relativDiff(ScoutingMuon_lead, genMuon_lead)')
  d = d.Define("relDiff_sub", 'relativDiff(ScoutingMuon_sub, genMuon_sub)')


  rep = d.Report()
  # dis = d.Display({"genMu", "nGenMuon"}, 100)
  hists = {}
  for v in var:
    GenName = "GenMuon_" + v
    hists[GenName] = bookHist(d, GenName, ranges[v], "genMuon_" + v)
    ScoutingName = "ScoutingMuon_" + v
    hists[ScoutingName] = bookHist(d, ScoutingName, ranges[v], "ScoutingMuon_" + v)
    RelDName = "relDiff" + v + "Vs" + v
    hists[RelDName] = bookHist2D(d, RelDName, ranges[v],\
                             (100, -1.0, 1.0), "genMuon_" + v, "relDiff_" + v)
    corrName = "CorrGenRec_" + v
    hists[corrName] = bookHist2D(d, corrName, ranges[v],\
                             ranges[v], "ScoutingMuon_" + v, "genMuon_" + v)

  for h in hists :
    writeHist(hists[h], h)
  rep.Print()
  outf.Close()

def makeProfileHists():
  inf = ROOT.TFile("Hist/resolutionStudy.root", "READ")
  for v in var :
    corrName = "relDiff" + v + "Vs" + v
    h = inf.Get(corrName)
    pr = h.ProfileX("profName", 0, -1, "es")
    h_zoomd = inf.Get(corrName)
    pr_zoomd = h_zoomd.ProfileX("profZoomdName", 30, 70, "es")

    c = CMS.cmsCanvas( "RelDiff_" + v, ranges[v][1], ranges[v][2], -1.0, 1.0,
                            v, v + "_{rec} -" + v + "_{gen}/" + v + "_{rec}")
    CMS.cmsDraw(h, "")
    h.SetMinimum(1.0)
    c.SetLogz()

    c.SaveAs("Hist/Resolution/RelDiff" + v + "Vs" + v + ".png")
    c.SaveAs("Hist/Resolution/RelDiff" + v + "Vs" + v + ".pdf")

    cc = CMS.cmsCanvas( "Res" + v, ranges[v][1], ranges[v][2], \
           pr.GetMinimum() - 0.15, pr.GetMaximum() + 0.15, v, "Entries")
    leg = CMS.cmsLeg(0.6, 0.8, 0.8, 0.95)
    CMS.cmsDraw(pr, "E1", mcolor=ROOT.TColor.GetColor(155, 152, 204))
    leg.AddEntry(pr, "Full range")
    CMS.cmsDraw(pr_zoomd, "SAME E1", mcolor=ROOT.TColor.GetColor(222, 90, 106))
    leg.AddEntry(pr_zoomd, "Zoomed range")
    leg.Draw()

    cc.SaveAs("Hist/Resolution/Res_" + v + ".png")
    cc.SaveAs("Hist/Resolution/Res_" + v + ".pdf")

def corrNorm():
  inf = ROOT.TFile("Hist/resolutionStudy.root", "UPDATE")
  for v in var:
    h = inf.Get( "CorrGenRec_" + v)
    h.SetMinimum(0.0)
    nbinX = h.GetNbinsX()
    nbinY = h.GetNbinsY()
    ySum = 0
    for i in range(nbinY + 1) :
      for j in range(nbinX + 1) :
        ySum = ySum + h.GetBinContent(j, i)
      if (ySum == 0) : continue
      else :
        for k in range(nbinX + 1) :
          b = h.GetBinContent(k, i)
          bNormd = b/ySum
          h.SetBinContent(k, i, bNormd)
        ySum = 0

    c = CMS.cmsCanvas("CorrGenRec_" + v, ranges[v][1], ranges[v][2], ranges[v][1], ranges[v][2], \
                              "rec " + v, "gen " + v)
    CMS.cmsDraw(h, "A")
    c.SaveAs("Hist/Resolution/CorrGenRec_" + v + ".png")
    c.SaveAs("Hist/Resolution/CorrGenRec_" + v + ".pdf")


def main():
  # makeCorrHist()
  corrNorm()
  makeProfileHists()

if __name__ == "__main__":
  main()

#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os

# lumi is defined in 

# Declaration of ranges for each histogram type
default_nbins = 100
ranges = {
  "diPt" : ("ScoutingMuon_diPt", default_nbins, 0.0, 100.0),
  "diMass" : ("ScoutingMuon_diMass", default_nbins, 10.0, 110.0),
  "diMassZ" : ("ScoutingMuon_diMass", default_nbins, 81.0, 101.0),
  "diMassLow" : ("ScoutingMuon_diMass", default_nbins, 10.0, 60.0),
  "diEta" : ("ScoutingMuon_diEta", default_nbins, -5.0, 5.0),
  "lead_pt" : ("leadpt", default_nbins, 5.0, 105.0),
  "sub_pt" : ("subpt", default_nbins, 5.0, 105.0),
  "lead_eta" : ("leadeta", default_nbins, -2.5, 2.5),
  "sub_eta" : ("subeta", default_nbins, -2.5, 2.5),
  "lead_phi" : ("leadphi",default_nbins, -3.15, 3.15),
  "sub_phi" : ("subphi",default_nbins, -3.15, 3.15),
  "dimassQCDscale" :("ScoutingMuon_diMass", 1, 12, 110),
  "dimassDYscale" : ("ScoutingMuon_diMass", 1, 86, 96),
  "HCalIsolation" : ("ScoutingMuon_hcalIso", 15, -5.0, 10),
  "ECalIsolation" : ("ScoutingMuon_ecalIso", 15, -5.0, 10),
  "trkIsolation" : ("ScoutingMuon_trackIso", 10, 0.0, 10),
  "Strip_Hit" : ("ScoutingMuon_nValidStripHits", 25, 0, 25),
  "Pixel_Hit" : ("ScoutingMuon_nPixelLayersWithMeasurement", 10, 0, 10),
  "Tracker_Hit" : ("ScoutingMuon_nTrackerLayersWithMeasurement", 18, 0, 18),
  "MuonChamber_Hit" : ("ScoutingMuon_nRecoMuonChambers", 50, 0, 51),
  "MatchedStation" : ("ScoutingMuon_nRecoMuonMatchedStations", 5, 0, 5)
}


def bookHist1D(d, name, range_): #Histo booking
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
  # d = d.Filter("nScoutingMuon == 2 ", "Exactly two muons")
  # d = d.Filter("ScoutingMuon_eta[0] < 2.4 && ScoutingMuon_eta[1] < 2.4")
  # d = d.Filter("ScoutingMuon_pt[0] > 5.0 && ScoutingMuon_pt[1] > 5.0")
  # d = d.Filter("dimass > 81 && dimass < 101", "Z peak")
  # d = d.Filter("ScoutingMuon_nPixelHit[0] > 0 && ScoutingMuon_nPixelHit[1] > 0")
  # d = d.Filter("ScoutingMuon_nTrackerLayer[0] > 4 && ScoutingMuon_nTrackerLayer[1] > 4")

  # Define new variables
  d = d.Define("ind", 'sorting(ScoutingMuon_pt)', {"ScoutingMuon_pt"})
  d = d.Define("leadpt", "ScoutingMuon_pt[ind[1]]").Define("subpt", "ScoutingMuon_pt[ind[0]]")
  d = d.Define("leadeta", "ScoutingMuon_eta[ind[1]]").Define("subeta", "ScoutingMuon_eta[ind[0]]")
  d = d.Define("leadphi", "ScoutingMuon_phi[ind[1]]").Define("subphi", "ScoutingMuon_phi[ind[0]]")
  d = d.Define("rIso", "ScoutingMuon_trackIso/ScoutingMuon_pt" , {"ScoutingMuon_pt", "ScoutingMuon_trackIso"})

  # Separate samples and add them to the sample list
  samples = []
  dD = d.Filter('type == "Data"')
  samples.append(("Data", dD))
  dDY = d.Filter('type == "MC_DY"')
  samples.append(("DY", dDY))
  dQCD = d.Filter('type == "MC_QCD"')
  samples.append(("QCD", dQCD))

  # Loop over sample to make histograms for each isolation selection
  plots = ranges.keys()
  hists_s = {} # Declare the dictionary where histograms w ill be stored
  
  for df_label, df in samples :    
    # Separate isolation type 
    df_biso  = df.Filter('All(rIso < 0.15)', "Muons are isolated : ")
    # df_siso  = df.Filter('Any(rIso < 0.15) && Any(rIso >= 0.15)', "One muons is isolated : ")
    df_niso  = df.Filter('All(rIso >= 0.15)', "Muons are not isolated")
    df_isos = [
              ("NIReq", df),
              ("Biso", df_biso), 
              # ("Siso", df_siso),
              ("Niso", df_niso)
              ]

    reports_s = []
    for label_iso, df_iso in df_isos :

      # Book Histograms for each variable
      for plot in plots :
        hkey = "{}_{}_{}".format(df_label, plot, label_iso)
        hists_s[hkey] = bookHist1D(df_iso, plot, ranges[plot])
    
    # QCDscale = df_label + "_dimassQCDscale_Niso"
    # hists_s[QCDscale] = bookHist(df_s_niso, "dimassQCDscale", ranges["dimassQCDscale"])
  

  # Write histograms in the file
  for hkey in hists_s : 
    writeHist(hists_s[hkey], hkey)

  d.GetNRuns()
  # Cut-Flow
  outf.Close()

if __name__ == "__main__" :
  main()
import ROOT
import sys
import os 

ROOT.gROOT.SetBatch(True)

def main():

  file = {"/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134853/0000/*",
          "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134853/0001/*",  
          "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134853/0002/*",
          # "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134427/0003/*",
          # "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134427/0004/*",
          # "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134427/0005/*",
          # "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134427/0006/*",
          # "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/crab_QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/241218_134427/0007/*"
          }
  # Initialize i/o 
  ROOT.EnableImplicitMT(12)
  df = ROOT.RDataFrame("Events", file)
  ROOT.RDF.Experimental.AddProgressBar(df)
  df = df.Redefine("genWeight", "genWeight/abs(genWeight)")
  # df.Display("genWeight", 128).Print()
  weight = df.Sum("genWeight").GetValue()
  print(file, weight)

if __name__ == "__main__":
  main()
import ROOT
import sys
import os

ROOT.gROOT.SetBatch(True)

def main():

  file = {
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0000/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0001/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0002/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0003/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0004/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0005/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0006/*",
    "/user/educarme/pnfs/ScoutingNANO_MC2022_v02/TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/crab_TTto2L2Nu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/250128_140458/0007/*"
  }
  # Initialize i/o
  ROOT.EnableImplicitMT(24)
  df = ROOT.RDataFrame("Events", file)
  ROOT.RDF.Experimental.AddProgressBar(df)
  df = df.Define("sgnWght", "genWeight/abs(genWeight)")
  weight = df.Sum("genWeight")
  absW = df.Sum("sgnWght")
  weight_v = weight.GetValue()
  absW_v = absW.GetValue()
  print(file, "sum", weight_v, "sign sum", absW_v)

if __name__ == "__main__":
  main()

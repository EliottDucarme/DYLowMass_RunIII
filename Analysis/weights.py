import ROOT
import sys
import os

ROOT.gROOT.SetBatch(True)

def main():

  file = {
                "/pnfs/iihe/cms/store/user/educarme/ScoutingSkim/2024/TT/250814_again/output_566711.0.root",
                "/pnfs/iihe/cms/store/user/educarme/ScoutingSkim/2024/TT/250814_again/output_566711.1.root"
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

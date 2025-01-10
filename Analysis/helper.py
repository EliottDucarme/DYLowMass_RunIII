#!/usr/bin/env python
import ROOT

def initializeFromJSON(d):
  ROOT.RDF.Experimental.AddProgressBar(d)

  # check if sample provided is MC or not and normalize accordingly
  # lumi is in fb^-1
  ROOT.gInterpreter.Declare(
    """
    double reweighting(double xsec, double sumws, double weight, std::string type){
       if (type.find("MC") != std::string::npos){
        double sign = weight/abs(weight);
        return double(3082.8)*xsec*sign/sumws;
        } 
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

  # Take info from the spec .json file
  d = d.DefinePerSample("xsec", 'rdfsampleinfo_.GetD("xsec")')
  d = d.DefinePerSample("sumws", 'rdfsampleinfo_.GetD("sumws")')
  d = d.DefinePerSample("type", 'rdfsampleinfo_.GetS("type")')
  d = d.Define("norm", 'reweighting(xsec, sumws, genWeight, type)',{"xsec", "sumws", "genWeight", "type"})

  return d

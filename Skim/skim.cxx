#include <iostream>
#include <vector>
#include <TSystem.h>

#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDFHelpers.hxx"
#include "ROOT/RVec.hxx"
#include "Math/LorentzVector.h"
#include "Math/Vector4D.h"

using namespace ROOT::VecOps;
using ROOT::RDF::RSampleInfo;
using namespace ROOT::RDF::Experimental;
using PtEtaPhiMVectorD = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

template <typename T>
RVec<T> dimuonKinematic(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi)
{
  
   T muonRestMass = 0.1056583715;

   PtEtaPhiMVectorD P(0.,0.,0.,0.);
  
   PtEtaPhiMVectorD p1(pt[0], eta[0], phi[0], muonRestMass);
   PtEtaPhiMVectorD p2(pt[1], eta[1], phi[1], muonRestMass);

   P = p1 + p2;
   T Pt = P.Pt();
   T M = P.M();
   T Eta = P.Eta();
   T Phi = P.Phi();
      
  RVec<T> dimuon {Pt, M, Eta, Phi};
   
   return dimuon;
}

std::vector<std::string> Split(std::string mystring, std::string delimiter)
{
    std::vector<std::string> subStringList;
    std::string token;
    while (true)
    {
        size_t findfirst = mystring.find(delimiter);
        if (findfirst == std::string::npos) //find returns npos if it couldn't find the delimiter anymore
        {
            subStringList.push_back(mystring); //push back the final piece of mystring
            return subStringList;
        }
        token = mystring.substr(0, mystring.find(delimiter));
        mystring = mystring.substr(mystring.find(delimiter) + delimiter.size());
        subStringList.push_back(token);
    }
    return subStringList;
}

void Cut(ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager, void> d, std::string output)
{
   ROOT::RDF::Experimental::AddProgressBar(d);
   auto d1 = 
      d
      // Skimming
      // Should not be asked for trigger efficiency, biasing the computation.
      .Filter([](Int_t n){ return n == 2;}, {"nScoutingMuon"}, "Exactly two muons")
      .Filter([](Int_t n){return n == 0;}, {"nScoutingDisplacedVertex"}, "No displaced vertices")
      .Filter([](RVec<float_t> eta, RVec<float_t> pt){return All(abs(eta) < 2.4) && All(pt > 5.0) ;}, {"ScoutingMuon_eta", "ScoutingMuon_pt"}, "In Eta and Pt Range")
      //
      .Define("dimass", dimuonKinematic<float_t>, {"ScoutingMuon_pt", "ScoutingMuon_eta", "ScoutingMuon_phi"} )
      // .Filter([](float_t M){ return M > 10 ; }, {"dimass"}, "Dimuon Mass > 10 Gev")
      ;

    std::cout << "hello !" << std::endl;  
    
    d1.Snapshot("Events", "output.root",   
        "^run$|^event$|^luminosityBlock$|^(.|)L1Mu.*$|^(.|)ScoutingMuon.*$|^L1_DoubleMu.*$");
    d1.Report()->Print();

  //  std::string out = "rsync -aP output.root " + output;
  //  std::cout << out << std::endl;
  //  gSystem->Exec(out.c_str());
}

void SortSamples(const std::vector<std::string>& sample_names, const std::string& input_path, const std::string& output_path)
{
    for (const auto& sample_name : sample_names) {
        if (input_path.find(sample_name) != std::string::npos) {
            const std::string output_dir = output_path.substr(0, output_path.find("/o")) + "/" + sample_name + "/";
            const std::string output_file = output_dir + output_path.substr(output_path.find("/o") + 1);

            const std::string mkdir_cmd = "mkdir -p " + output_dir;
            gSystem->Exec(mkdir_cmd.c_str());

            ROOT::RDataFrame d("Events", input_path);
            auto d1 = d.Define("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", [](){return bool(0) ; });
            Cut(d1, output_file);

            break;
        }
    }
}

void HTC_sub(std::string type, std::string input, std::string output)
{
   ROOT::EnableImplicitMT();
   std::vector<std::string> samples;

   // Separate with respect to type of data

   std::cout << "Type is " << type << std::endl;
   if ( std::strcmp(type.c_str(), "DATA") == 0 )
   {
      ROOT::RDataFrame d("DYTree/Events", "input.root");
      auto d1 = d.Define("genWeight", [](){return float(1.) ; })
                  // .Redefine("nSCMuon", [](int n){return std::make_unsigned_t<int>(n) ;}, {"nSCMuon"})
                  ;
      Cut(d1, output);
   }

   // Separate with respect to type of sample
   else
   {
      if ( std::strcmp(type.c_str(), "QCD") == 0) samples = {"Pt-15To20", "Pt-20To30", "Pt-30To50", "Pt-50To80", "Pt-80To120", "Pt-120To170", "Pt-170To300", "Pt-300To470", "Pt-470To600", "Pt-600To800", "Pt-800To1000", "Pt-1000"};
      else if ( std::strcmp(type.c_str(), "DY") == 0) samples = {"M-10to50", "M-50"};
      else std::cout << "Type is ill-defined" << std::endl;

      for ( int i = 0; i < samples.size(); i++)
      SortSamples(samples, input, output); //Used to put different samples in different folders.
   }

}

int main(int argc, char *argv[])
{
  ROOT::RDataFrame df("Events", argv[1]);
  Cut(df, argv[2]);
}
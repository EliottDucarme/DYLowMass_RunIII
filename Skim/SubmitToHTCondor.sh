#!/bin/bash                                                           

# Set the paths below according to your needs:
jobpath=JobSub                                         # New directory to be created for the submission files
subpath=${PWD}/${jobpath}                              # Path to be used for the submission files of jobs to HTCondor

# Color variables for message and error printing
RED='\033[0;31m'
PURPLE='\033[1;35m'
NC='\033[0m' # No Color 
             
# Help message                                                       
Help(){
    echo                                                                
    printf "=%.0s" {1..114}; printf "\n"                                 
    echo -e "${RED}1)                Usage:   $0  <Dataset>  <Year>  <Era>  <Output>${NC}"
    printf "=%.0s" {1..114}; printf "\n"                                 
    echo
    echo "Dataset            ---> Data / DY / QCD / TT"
    echo "Year               ---> 2022"
    echo "Era or MC Binning  ---> BCDEFG || XXtoYY  MC (Depending on the Year and Dataset: check Datasets.md)"
    echo "Output             ---> Output directory to be created in /pnfs/iihe/cms/store/user/${USER}/ScoutingSkim/<Year>/<Dataset>_<Era>/"
    echo
    # echo -e "                                                 \033[1m OR \033[0m                                                               "
    # echo
    # printf "=%.0s" {1..114}; printf "\n"
    # echo -e "${RED}2)                Usage:   $0 -f input.txt${NC}"
    # printf "=%.0s" {1..114}; printf "\n"
    # echo
    # echo "input.txt  ---> Inputs folder"
    # echo                                                                
    exit 1                                                              
}

dataset=$1
year=$2
era=$3
folder=$5
part=$4

# Check if dataset name is correct 
if ! [[ "$dataset" =~ ^(Data|DY|QCD|TT) ]]
then                                                                                     
    echo
    echo -e "${RED}Error : Invalid Dataset name!${NC}"                                                       
    Help
    exit 1   
fi                                                                           
    
# Check if year is correct
if ! [[ "$year" =~ ^(2022) ]]; then
    echo
    echo -e "${RED}Error : Invalid Year!${NC}"                                                       
    Help
    exit 1
fi

# Check if era (depending on the year) or HT bin is correct
if [[ $year == 2022 && $dataset == "Data" ]]; then
   if ! [[ "$era" =~ ^(B|C|D|E|F|G) ]]; then
      echo -e "${RED}Error : Invalid era for year 2022!${NC}"
      echo -e "${RED}2022 eras : B C D E F G${NC}"
      Help
      exit 1
   fi
elif [[ $year == 2022 && $dataset == "DY" ]]; then
   if ! [[ "$era" == "10to50" || "$era" == "50" ]]; then
      echo -e "${RED}Error : Invalid Binning for DY ! ${NC}"
      echo -e "${RED} 10to50, 50 ${NC}"
      Help
      exit 1
   fi
elif [[ $year == 2022 && $dataset == "TT" ]]; then
   if ! [[ "$era" == "4to50" || "$era" == "50" ]]; then
      echo -e "${RED}Error : Invalid Binning for DY ! ${NC}"
      echo -e "${RED} 4to50, 50 ${NC}"
      Help
      exit 1
   fi
elif [[ $year == 2022 && $dataset == "QCD" ]]; then
   if ! [[ "$era" == "15to20" || "$era" == "20to30" || "$era" == "30to50" || "$era" == "50to80" || 
   "$era" == "80to120" || "$era" == "120to170" || "$era" == "170to300" || 
   "$era" == "300to470" || "$era" == "470to600" || "$era" == "600to800" || 
   "$era" == "800to1000" || "$era" == "1000" ]]; then
      echo -e "${RED}Error : Invalid binning for QCD!${NC}"
      echo -e "${RED}2022 eras : C D${NC}"
      Help
      exit 1
   fi
fi

# The output directory in personal pnfs store area
if [[ $dataset == "QCD" ]]; then
   output=/pnfs/iihe/cms/store/user/${USER}/ScoutingSkim/${year}/${dataset}/PT-${era}/${folder} 
elif [[ $dataset == "DY" || $dataset == "TT" ]]; then
   output=/pnfs/iihe/cms/store/user/${USER}/ScoutingSkim/${year}/${dataset}/M-${era}/${folder}
elif [[ $dataset == "Data" ]]; then
  output=/pnfs/iihe/cms/store/user/${USER}/ScoutingSkim/${year}/${dataset}_${era}_${part}/${folder}
else
  echo
  echo -e "${RED}Dataset is invalid !${NC}"
  echo -e "${RED}Use Data, QCD or DY${NC}"
  echo
  Help
  exit 1
fi

if [ ! -d $output ] 
then
    mkdir -p $output
else
    echo
    echo -e "${RED}The directory $output already exists, please give another Output name!${NC}"
    echo
    exit 1
fi

# Running on NANOAOD or JME custom NANOAOD based on the last argument
if [[ "$dataset" == "Data" ]]; then
  # files="/pnfs/iihe/cms/store/user/educarme/NanoScouting_Run3_v01/ScoutingPFRun3/crab_Scouting_${year}${era}v1_GoldenJSON_${part}/*/0000/*71.root"    # Small subset of files
  files="/pnfs/iihe/cms/store/user/educarme/NanoScouting_Run3_v01/ScoutingPFRun3/crab_Scouting_${year}${era}v1_GoldenJSON_${part}/*/*/*.root"       # All files
# MC
elif [[ $dataset == "QCD" ]]; then
  files="/pnfs/iihe/cms/store/user/educarme/ScoutingNANO_MC${year}_v02/QCD_PT-${era}_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/*/*/*/*.root"     
elif [[ $dataset == "TT" ]]; then
  files="/pnfs/iihe/cms/store/user/educarme/ScoutingNANO_MC${year}_v02/TTLL_MLL-${era}_TuneCP5_13p6TeV_amcatnlo-pythia8//*/*/*/*.root"              # All files
elif [[ $dataset == "DY" ]]; then
  # files="/pnfs/iihe/cms/store/user/educarme/ScoutingNANO_MC${year}_v02/DYto2L-2Jets_MLL-${era}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/*/*/0000/*71.root"  # Small subset of files
  files="/pnfs/iihe/cms/store/user/educarme/ScoutingNANO_MC${year}_v02/DYto2L-2Jets_MLL-${era}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/*/*/*/*.root"         # All files
fi

# Modify the template scripts and store the submitted files in the submission directory
# Template scripts
tmpexe="Template.sh"
tmpsub="Template.sub"

# New scripts where the parameters are set
newexe="$dataset"_"$year"_Run"$era".sh
newsub="$dataset"_"$year"_Run"$era".sub

# New executable script
sed 's@DATASET@'$dataset'@g' $tmpexe > $newexe     # dataset as set above
chmod 744 $newexe

# New submission script
sed 's@exe.sh@'$newexe'@g' $tmpsub > $newsub       # executable name in the submit file
sed -i 's@PATH_TO_OUTPUT@'$output'@g' $newsub      # path for the output root files in the submit file
sed -i 's@LIST_OF_FILES@'$files'@g' $newsub        # list of input files in the submit file

# Check whether the directory as set above exists. 
# Otherwise create it and move inside it to proceed with job submission.
if [ ! -d $jobpath ]; then
    mkdir $jobpath
fi

# New scripts will be moved inside the submission directory
mv $newexe ./${jobpath}
mv $newsub ./${jobpath}
cd ./${jobpath}

# Create directories error - log - output
if [ ! -d error ]; then
    mkdir error
fi
if [ ! -d log ]; then
    mkdir log
fi
if [ ! -d output ]; then
    mkdir output
fi

# Submit the jobs
condor_submit $newsub -batch-name "${dataset}_${year}_${era}_${part}"

# Print sumbission information
echo
printf "=%.0s" {1..120}; printf "\n"
echo -e "                                           ${PURPLE}Jobs submitted!${NC}"
printf "=%.0s" {1..120}; printf "\n"
echo
echo "The submission files can be found in: ${PWD}"
echo "The error/output/log files will be stored in: ${PWD}"
echo "The output root files will be stored in: $output"
printf "=%.0s" {1..120}; printf "\n"
echo
echo "load LCG environment"
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_106a x86_64-el9-gcc14-opt
echo "Done !"

echo "start of the process"
# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/DY/M-10to50/genInfo/DY_M-10to50.root /user/educarme/pnfs/ScoutingSkim/2022/DY/M-10to50/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/DY/M-10to50/genInfo/DY_M-10to50.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/DY/M-50/genInfo/DY_M-50.root /user/educarme/pnfs/ScoutingSkim/2022/DY/M-50/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/DY/M-50/genInfo/DY_M-50.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-15to20/genInfo/QCD_PT-15to20.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-15to20/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-15to20/genInfo/QCD_PT-15to20.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-20to30/genInfo/QCD_PT-20to30.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-20to30/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-20to30/genInfo/QCD_PT-20to30.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-30to50/genInfo/QCD_PT-30to50.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-30to50/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-30to50/genInfo/QCD_PT-30to50.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-50to80/genInfo/QCD_PT-50to80.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-50to80/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-50to80/genInfo/QCD_PT-50to80.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-80to120/genInfo/QCD_PT-80to120.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-80to120/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-80to120/genInfo/QCD_PT-80to120.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-120to170/genInfo/QCD_PT-120to170.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-120to170/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-120to170/genInfo/QCD_PT-120to170.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-170to300/genInfo/QCD_PT-170to300.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-170to300/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-170to300/genInfo/QCD_PT-170to300.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-300to470/genInfo/QCD_PT-300to470.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-300to470/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-300to470/genInfo/QCD_PT-300to470.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-470to600/genInfo/QCD_PT-470to600.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-470to600/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-470to600/genInfo/QCD_PT-470to600.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-600to800/genInfo/QCD_PT-600to800.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-600to800/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-600to800/genInfo/QCD_PT-600to800.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-800to1000/genInfo/QCD_PT-800to1000.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-800to1000/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-800to1000/genInfo/QCD_PT-800to1000.root

# hadd -ff /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-1000/genInfo/QCD_PT-1000.root /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-1000/genInfo/*.root
python weights.py /user/educarme/pnfs/ScoutingSkim/2022/QCD/PT-1000/genInfo/QCD_PT-1000.root



export DCACHE_RAHEAD=true
export DCACHE_RA_BUFFER=50000000
echo "Transfer file to ${TMPDIR} and go to the dir"
cd $TMPDIR
gfal-copy  davs://maite.iihe.ac.be:2880$1 ./input.root
echo "Done !"
echo 
echo "Transfer skim.cxx"
gfal-copy /user/educarme/DYLowMass_RunIII/Skim/skim.cxx .
echo "Done !"
echo
echo "load LCG env and compile the skim procedure"
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_108 x86_64-el9-gcc15-opt
g++ -o skim skim.cxx  $(root-config --cflags --libs)
echo "Done !"
echo
echo "Run the skimming procedure"
./skim input.root "DATASET"
echo "Done !"
echo
echo "unset PYTHONHOME to use gfal commands"
unset PYTHONHOME
echo "Transfering to /pnfs"
gfal-copy  output.root davs://maite.iihe.ac.be:2880$2
echo "Finished !"
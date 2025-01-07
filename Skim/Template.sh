echo "Transfer file to $TMPDIR and go to the dir"
rsync -aP $1 $TMPDIR/input.root
cd $TMPDIR
echo "Done !"
echo 
echo "load LCG env"
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_106a x86_64-el9-gcc14-opt
echo "Done !"
echo
echo "Transfer and compile skim.cxx"
rsync -aP ~/Run3/Skim/skim.cxx .
g++ -o skim skim.cxx  $(root-config --cflags --libs)
echo "Done !"
echo
echo "Run the skimming procedure"
./skim $TMPDIR/input.root "DATASET"
echo "Done !"
echo
echo "Transfering to /pnfs"
rsync -aP output.root $2
echo "Finished !"
#!/bin/bash

echo "Hello World, I run on the cluster !"
echo
echo "Transfer file to $TMPDIR and go to the dir"
rsync -aP $1 $TMPDIR/input.root
cd $TMPDIR
echo "Done !"
echo
echo "load LCG env"
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_106a x86_64-el9-gcc14-opt
echo "Done !"
echo
echo "Compile skim.cxx"
g++ -o skim ~/Run3/Skim/skim.cxx  $(root-config --cflags --libs)
echo "Done !"
echo
echo "Run the skimming procedure"
./skim $TMPDIR/input.root
echo "Done !"
echo
echo "Transfering to /pnfs"
rsync -aP output.root $2
echo "Finished !"
import os, os.path
import sys
import subprocess

# use this command to reduce the huge number of files provided by crab
def main(path) :
  # convert the div arg to int
  div = len(next(os.walk(path))[1])
  # div = int(div) 
  print(div, "sub-directories")
  div = 4*div # give more files to each process to improve efficiency
  inPath = path + "*/"
  # get the list of files to hadd
  os.system("find {} -name '*.root' > inputFiles.txt".format(inPath))
  fileList = open("inputFiles.txt", "r")

  # get the nu;ber of files in the dir of interest
  n_inf: int = len(fileList.readlines())
  print(n_inf, "input files")
  reminder = n_inf % div
  n_inf = n_inf - reminder
  n_outf: int = n_inf // div + 1
  print(n_outf, "number of output files")
  fileList.seek(0)                # go back to first line
  for i in range(n_outf) :
    outf = path + "output_{}.root".format(i)
    inFiles = ""
    start = i*div
    end = (1+i)*div
    for j in range(start, end) :
      inFile=fileList.readline().strip()
      inFiles = inFiles + inFile + " "
    os.system("hadd -fk -j 4 {} {}".format(outf, inFiles))




if __name__ == "__main__" :
  main(sys.argv[1])
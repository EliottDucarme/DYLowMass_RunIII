import logging
import ROOT
import socket
from distributed import LocalCluster, Client
from dask_jobqueue import HTCondorCluster

def create_connection():
  cluster = HTCondorCluster(
        cores=1,
        memory='2000MB',
        disk='2000MB',     
        local_directory='$TMPDIR',
        death_timeout = '60',
        nanny = False,
        log_directory = "/user/educarme/DYLowMass_RunIII/Analysis/dask_jobLog",
        scheduler_options={'dashboard_address': ':7249'},
        job_script_prologue=[
          'source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_108 x86_64-el9-gcc15-opt'
        ],
        name="worker",
        job_extra_directives={'batch_name' : "RDF_DaskJob"}
  )
  cluster
  cluster.scale(jobs=20)
  client = Client(cluster)
  client
  # print(cluster.job_script())
  # logger = logging.getLogger(__name__)
  # logger.setLevel(logging.DEBUG)
  return client

def simpleCompute():
    #print( "Create the connection to the mock Dask cluster on the local machine" )
    connection = create_connection()
    connection 
    #print( "Create an RDataFrame that will use Dask as a backend for computation" )
    df = ROOT.RDataFrame(pow(10,3), executor=connection, npartitions=60)

    ROOT.gInterpreter.Declare('''
        #include "ROOT/RVec.hxx"
        using namespace ROOT::VecOps;

        RVec<float> simple_vector(){
          RVec<float> vec {1, 2, 3, 4};
          return vec;
        }
    ''')
    
    df = df.Define("ASimpleVector", 'simple_vector()')
    print(df.Sum("ASimpleVector").GetValue())
 
if __name__ == "__main__" :
  simpleCompute()
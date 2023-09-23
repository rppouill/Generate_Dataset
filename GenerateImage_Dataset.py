from ImageGenerator.Blender.Blender import Blender_Render
import numpy as np
from utils import *

import importlib


def main(args):
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    input_environment = args.input_blender
    frame = args.frame

    generate_json(args,rank)
    
    print(args.scenario)
    scenario_module = importlib.import_module(f"Scenario")
    scenario = getattr(scenario_module,args.scenario)
    
    _,params = json_load(f'camera_{rank+1:02d}.json', scenario)
    params["exclude"] = ['lefttube', 'lefttube2', 'metalpiece', 'support', 'thintubes', 'tube1', 'walls']
    blender = (Blender_Render(input_environment,params,scenario = scenario,camera_Name = params["camera"]))

    print(f"Camera Name: {params['camera']}")
    for j in range(1,frame+1):
        blender.render_image(j,filename = f"{params['camera']}_{j}", occultation=True)

    pass


if __name__ == '__main__':

    args = parser()
    main(args)

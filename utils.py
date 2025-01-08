import re
import os

def generate_json(args):
    with open(args.json,'r') as f:
        template_json = f.read()


    values = {
        'camera_folder'  : os.path.join(args.output_blender),
        'camera_folder'  : os.path.join(args.output_blender),
        'input_blender'  : args.input_blender,

        'output_blender' : os.path.join(args.output_blender)

    }

    after_replace = re.sub('<(.+?) placeholder>', lambda match: values.get(match.group(1)), template_json)

    with open(f'Camera.json','w') as f:
        f.write(after_replace)


def json_load(filename,scenario):
    import json
    f = open(filename,'r')
    data = json.load(f)

    for config in data['Camera']:
        camera_environment = {}
        for key,value in config.items():
            camera_environment[key] = value
    camera_environment["size"] = tuple(map(int,camera_environment["size"].split(',')))

    for config in data['Blender']:
        blender_environment = {}
        for key,value in config.items():
            blender_environment[key] = value
        blender_environment["positions"] = scenario["positions"]
        blender_environment["rotations"] = scenario["rotations"]
        blender_environment["keypoints_graph"] = scenario["keypoints_graph"]
        blender_environment["scale"] = scenario["scale"]

    
    for config in data['FPGA']:
        fpga_config = {}
        fpga_config["type"] = config["type"]
        if config["type"] == "GHDL":
            for ghdl in config['GHDL']:
                for key,value in ghdl.items():
                    fpga_config[key] = value
        elif config["type"] == "ModelSim":
            for modelsim in config['ModelSim']:
                for key,value in modelsim.items():
                    fpga_config[key] = value
        else:
            raise ValueError(f"Type {config['type']} not found")

    return camera_environment,blender_environment, fpga_config
def redirect_print():
    import sys
    logfile = os.path.join('logfile.log')
    open(logfile, 'a').close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)

    return logfile,old,fd
def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Simulateur')
    parser.add_argument('--generate'      , '-g', action='store_true', help='generate json file (default: False)')
    parser.add_argument('--json'          , '-j', type=str, default='camera_XX.json', help='json file')

    parser.add_argument('--input_blender'       , type=str, default=None, help='input blender file (default: None')
    parser.add_argument('--output_blender'      , type=str, default='./test', help='input folder (default: None)')    
    parser.add_argument('--scenario'      , '-s', type=str, default=None, help='scenario (default: None)')
    
    parser.add_argument('--frame'       , '-f', type=int, default=0, help='Frame')
    parser.add_argument('--numberCamera', '-n', type=int, default=0, help='Number of Camera')

    parser.add_argument('--occultation', '-o', action='store_true', help='Occultation (default: False)')

    parser.add_argument('--verbose', '-v', default='INFO', help="NOTSET     : 0 \n"
                                                            "DEBUG      : 10 \n"
                                                            "INFO       : 20 \n"
                                                            "WARNING    : 30 \n"
                                                            "ERROR      : 40 \n"
                                                            "CRITICAL   : 50\n ")
    
    parser.add_argument('--gpu',  action='store_true', help='GPU (default: False)')

    parser.add_argument('--dataset_path', '-d', type=str, default=None, help='dataset path (default: None)')

    
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('--mpi_core', '-m', type=int, default=None, help='number of mpi core (default: None)')
    #group.add_argument('--n_core', '-n', type=int, default=1, help='number of core (default: 1) if mpi_core is None')

    return(parser.parse_args())
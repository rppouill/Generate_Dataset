import re
import os

def generate_json(args,rank):
    with open(args.json,'r') as f:
        template_json = f.read()


    values = {
        'camera_folder'  : os.path.join(args.output_blender,f'Camera_{rank+1:02d}'),
        'name'           : f'Camera.{rank+1:02d}',
        'input_blender'  : args.input_blender,

        'output_blender' : os.path.join(args.output_blender,f'Camera_{rank+1:02d}','images')

    }

    after_replace = re.sub('<(.+?) placeholder>', lambda match: values.get(match.group(1)), template_json)

    with open(f'camera_{rank+1:02d}.json','w') as f:
        f.write(after_replace)


def json_load(filename,scenario):
    import json
    f = open(filename,'r')
    data = json.load(f)

    for config in data['Camera']:
        camera_environment = {}
        for key,value in config.items():
            camera_environment[key] = value

    for config in data['Blender']:
        blender_environment = {}
        for key,value in config.items():
            blender_environment[key] = value
        blender_environment["scenario"] = scenario



    return camera_environment,blender_environment

def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Simulateur')
    parser.add_argument('--generate'      , '-g', action='store_true', help='generate json file (default: False)')
    parser.add_argument('--json'          , '-j', type=str, default='camera_XX.json', help='json file')

    parser.add_argument('--input_blender' , '-b', type=str, default=None, help='input blender file (default: None')
    parser.add_argument('--output_blender', '-i', type=str, default=None, help='input folder (default: None)')    
    parser.add_argument('--scenario'      , '-s', type=str, default=None, help='scenario (default: None)')
    
    parser.add_argument('--frame', type=int, default=0, help='Frame')
    parser.add_argument('--numberCamera', '-n', type=int, default=0, help='Number of Camera')
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('--mpi_core', '-m', type=int, default=None, help='number of mpi core (default: None)')
    #group.add_argument('--n_core', '-n', type=int, default=1, help='number of core (default: 1) if mpi_core is None')

    return(parser.parse_args())
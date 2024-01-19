from ImageGenerator.Blender.Environment import Environment
from Scenario import Scenario
import numpy as np
from utils import *
import logging as log
import coloredlogs
import importlib



def redirect_print():
    import sys
    logfile = os.path.join('logfile.log')
    open(logfile, 'a').close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)

    return logfile,old,fd

def main(args):    
    input_environment = args.input_blender

    generate_json(args)

    log.debug(args.scenario)
    log.debug(args.scenario.upper())
    scenario = Scenario[args.scenario.upper()].value

    log.debug(scenario['rotations'])
    log.debug(scenario['positions'])
    log.debug(scenario['exclude'])
    
    _,params = json_load('Camera.json', scenario)
    params["exclude"] = scenario["exclude"]
    params["GPU"] = args.gpu

    log.debug(f"params: {params}")

    blender_render = Environment(input_environment,params, log_level=log.INFO)
    
    #blender_render.generate_all(ocultation=args.occultation)
    distance_Cam005 = np.ones(blender_render.scene.frame_end) * 5
    distance_Cam007 = np.ones(blender_render.scene.frame_end) * 5

    blender_render.generate_all(distance = distance_Cam005, ocultation=args.occultation)

    #blender_render.__call__(camera = 'Caméra.005', frame = 47, distance = distance_Cam005, ocultation=args.occultation)
    #blender_render.generate_all_frames(camera = 'Caméra.005', output_folder = args.output_blender, ocultation=args.occultation, distance = distance_Cam005)
    #blender_render.generate_all_frames(camera = 'Caméra.007', output_folder = args.output_blender, ocultation=args.occultation, distance = distance_Cam007)
#
    #np.savetxt(os.path.join(args.output_blender,'Caméra.005.txt'),distance_Cam005)
    #np.savetxt(os.path.join(args.output_blender,'Caméra.007.txt'),distance_Cam007)

    

    


def viewer_Camera(path,folder):
    import cv2
    import matplotlib.pyplot as plt

    distance = np.loadtxt(os.path.join(path,f'{folder}.txt'))
    log.info(f"Distance shape: {distance.shape}")
    plt.plot(distance)
    plt.show()

    for i,file in enumerate(sorted(os.listdir(os.path.join(path,folder)))):
        log.info(os.path.join(path,folder,file))
        img = cv2.imread(os.path.join(path,folder,file))
        cv2.putText(img, f"{distance[i]:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('image',img)
        key = cv2.waitKey(100)
        if key == ord('q'):
            break
        if key == ord('p'):
            cv2.waitKey(-1)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    logfile,old,fd = redirect_print()

    args = parser()

    log.basicConfig(level=args.verbose)
    logger = log.getLogger(__name__)

    coloredlogs.install(level=args.verbose, logger=logger)

    main(args)
    viewer_Camera(args.output_blender,'Caméra.005')

    os.close(fd)
    os.dup(old)
    os.close(old)

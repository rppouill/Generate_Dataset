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
    import networkx as nx

    G = nx.Graph(params["keypoints_graph"])
    params["keypoints_path"] = {}
    for key, value in params['positions'].items():
        params["keypoints_path"][key] = []
        for position in value:
            # Concat list
            params["keypoints_path"][key] += nx.shortest_path(G,source=position[0],target=position[1])
 

    log.debug(f"params: {params}")
    log.info(params["keypoints_path"])  

    blender_render = Environment(input_environment,params, log_level=log.INFO)

    #blender_render.generate_all(distance = np.zeros(blender_render.scene.frame_end), ocultation = args.occultation)
    blender_render.generate_all_frames('Caméra.005', output_folder = args.output_blender, ocultation = args.occultation)
    blender_render.generate_all_frames('Caméra.007', output_folder = args.output_blender, ocultation = args.occultation)

    np.savetxt(os.path.join(args.output_blender,'Caméra.005.txt'),blender_render.distance['Caméra.005'])
    np.savetxt(os.path.join(args.output_blender,'Caméra.007.txt'),blender_render.distance['Caméra.007'])

    viewer_Camera(args.output_blender, 'Caméra.007')
    #import matplotlib.pyplot as plt
    #G = nx.Graph(params["keypoints_graph"])
    #pos = nx.spring_layout(G)
    #nx.draw(G,pos,with_labels=True)
#
    #shortest_path = nx.shortest_path(G,source=1,target=6)
    #log.info(f"Shortest path: {shortest_path}")
#
    #nx.draw_networkx_nodes(G,pos,nodelist=shortest_path,node_color='r')
    #plt.show()
    


def viewer_Camera(path,folder):
    import cv2
    import matplotlib.pyplot as plt

    #distance = np.loadtxt(os.path.join(path,f'{folder}.txt'))
    #log.info(f"Distance shape: {distance.shape}")
    #plt.plot(distance)
    #plt.show()

    for i,file in enumerate(sorted(os.listdir(os.path.join(path,folder)))):
        log.info(os.path.join(path,folder,file))
        img = cv2.imread(os.path.join(path,folder,file))
        #cv2.putText(img, f"{distance[i]:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
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


    fmt =  fmt='%(asctime)s [%(process)d] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
    coloredlogs.install(level=args.verbose, logger=logger)

    main(args)

    os.close(fd)
    os.dup(old)
    os.close(old)

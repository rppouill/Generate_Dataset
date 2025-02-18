import bpy
import logging as log
import os
import sys
from tqdm import tqdm
import numpy as np

from TqdmToLogger import TqdmHandler

#from Generate_Dataset.ImageGenerator.Blender.Blender_Camera import  Blender_Camera
from ImageGenerator.Blender.Blender_Camera import  Blender_Camera
class Environment():
    def __init__(self, input_environment, params, log_level = log.INFO):
        log.basicConfig(level=log_level)

        log.info("Environment.__init__")
        log.info(f"input_environment: {input_environment}")

        #import the blender file
        self.imported_object = bpy.ops.wm.open_mainfile(filepath=input_environment)
        
        #Set the parameters
        self.context = bpy.context
        self.scene = self.context.scene
        self.scene.frame_end = params["frame"]
        self.scene.render.fps = params["fps"]
        self.scene.render.resolution_x = params["resolution_x"]
        self.scene.render.resolution_y = params["resolution_y"]
        self.scene.render.image_settings.color_mode = params["color_mode"]


        self.scene.render.image_settings.color_depth = '8'

        if params["GPU"]:
            self._using_GPU()

        log.info(f'Scene: {self.scene}')

        log.info(f"frame_end: {self.scene.frame_end}")
        log.info(f"fps: {self.scene.render.fps}")
        log.info(f"resolution_x: {self.scene.render.resolution_x}")
        log.info(f"resolution_y: {self.scene.render.resolution_y}")
        log.info(f"color_mode: {self.scene.render.image_settings.color_mode}")

        log.debug(bpy.data.collections.keys())


        # Get the exclude list
        exclude = params["exclude"]
        for ob in bpy.data.collections['Environment'].objects:
            if ob.name not in exclude:
                exclude.append(ob.name)
                log.debug(f"Exclude: {ob.name}")
        log.debug(f"Exclude: {exclude}")

        # Get the Actors
        self.actors = {}
        for ob in bpy.data.collections['Actors'].objects:
            self.actors[ob.name] = ob
            log.debug(f"Actor: {ob.name}")

        self.camera_list = {}
        self.distance = {}
        # Get the camera
        for ob in bpy.data.collections['Cameras'].objects:
            self.camera_list[ob.name] = Blender_Camera(self.context,ob,
                                                       params["exclude"],
                                                       output_folder = params['output_blender'],                                                       
                                                       res_ratio = 1, 
                                                       log_level = log_level)
            self.distance[ob.name] = np.zeros(self.scene.frame_end)

            log.debug(f"Camera: {ob.name}")
        
        self._getKp()
        self._path2kp(params["keypoints_path"])
        log.debug(f"Type params: {type(params)}")
        log.debug(f"params rotation: {params}")
        self._compute_Rotation(params["keypoints_path"], params["rotations"])
        log.debug(f"Path: {self.path_kp}")
        for key in self.path_kp.keys():
            log.debug(f"Scale {key}: {params['scale'][key]}")
            log.debug(f"Path {key}: {self.path_kp[key]}")
            for i in range(len(self.path_kp[key])):
                log.debug(f"{self.path_kp[key][i][2]} + {params['scale'][key]}")
                self.path_kp[key][i][2] = self.path_kp[key][i][2] + params["scale"][key]
                log.debug(f"Path: {self.path_kp[key][i]}")
        self.scenario(self.path_kp, self.path_rotation)

    # _getKp
    # @param None
    # @return None
    # @description: Retrieves collection of keypoints from the environment
    def _getKp(self):
        self.kp_position = {}
        self.kp_rotation = {}
        for ob in bpy.data.collections['keypoints'].objects:
            self.kp_position[ob.name] = list(ob.location)
            self.kp_rotation[ob.name] = list(ob.rotation_euler)

    # _path2kp
    # @param path: path to follow
    # @return None
    # @description: Converts the path to a list of keypoints
    def _path2kp(self,path):
        self.path_kp = {}
        for key, value in path.items():
            log.debug(f"Key: {key}")
            self.path_kp[key] = []
            for position in value:
                self.path_kp[key].append(self.kp_position[f"kp.{position:03d}"].copy())
                log.debug(f"Position {key}: {self.path_kp[key]}")

    # _compute_Rotation
    # @param path: path to follow
    # @return None
    # @description: Computes the rotation between keypoints
    def _compute_Rotation(self,path, params_rotations):
        self.path_rotation = {}
        for key, value in path.items():
            self.path_rotation[key] = []
            for position in value:
                self.path_rotation[key].append([params_rotations[key][0], params_rotations[key][1], self.kp_rotation[f"kp.{position:03d}"][2]])

        


    def _using_GPU(self):
        log.info("Using GPU")
        self.scene.render.engine = 'CYCLES'
        self.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        self.scene.cycles.device = 'GPU'

        self.context.preferences.addons['cycles'].preferences.get_devices()
        log.info(f"Devices: {self.context.preferences.addons['cycles'].preferences.compute_device_type}")
        for d in self.context.preferences.addons['cycles'].preferences.devices:
            d.use = True
            log.info(f"Device: {d.name}")




        #self.context.scene.render.engine = 'CYCLES'
        #cprefs = self.context.preferences.addons['cycles'].preferences 
        #cprefs.compute_device_type = 'CUDA'
        #for device in cprefs.devices:
        #    if device.type == 'CUDA':
        #        device.use = True
    def _delete_animation(self,objets):
        for obj in objets.values():
            log.debug(f"Delete animation: {obj}")
            obj.animation_data_clear()
    def _update(self,obj,frame):
        obj.keyframe_insert("location", frame = frame)
        obj.keyframe_insert("rotation_euler", frame = frame)
    
    def scenario(self,positions, rotations):
        from numpy import floor

        self._delete_animation(self.actors)
        
        
        log.debug(positions)
        for (key_position,values_position),(key_rotation,values_rotation) in zip(positions.items(),rotations.items()):
            frame_partition = floor(self.scene.frame_end/len(values_position))
            log.debug(f"Key: {key_position}")
            log.debug(f"Actor: {self.actors[key_position]}")
            for i,(position,rotation) in enumerate(zip(values_position, values_rotation)):
                log.debug(f"Position: {position}")
                log.debug(f"Rotation: {rotation}")
                self.actors[key_position].location = position
                self.actors[key_position].rotation_euler = rotation
                self._update(self.actors[key_position],frame = i*frame_partition)


        #for key,values in positions.items():
        #    frame_partition = floor(self.scene.frame_end/len(values))
        #    log.debug(f"Key: {key}")
        #    log.debug(f"Actor: {self.actors[key]}")
        #    for i,position in enumerate(values):
        #        log.debug(f"Position: {position}")
        #        self.actors[key].location = position
        #        self.actors[key].rotation_euler = (0.0,0.0,0.0)
        #        self._update(self.actors[key],frame = i*frame_partition)

    def generate_all_camera(self,frame,distance = None, ocultation = False):
        for camera in self.camera_list.keys():
            self.__call__(camera,frame,distance,ocultation)         
    def generate_all_frames(self, camera, output_folder = None, ocultation = False):
        pbar = log.getLogger()
        pbar.info(f"Camera: {camera}")
        handler = TqdmHandler()
        #output = os.path.join(output_folder) if output_folder is not None else os.path.join('output',camera)
        for frame in tqdm(range(self.scene.frame_end)):
            self.__call__(camera = camera,
                            frame = frame,
                            distance = self.distance[camera],
                            ocultation = ocultation)
            pbar.addHandler(handler)

        #np.savetxt(f'{camera}', self.distance[camera])
        np.savetxt(f'{output_folder}/{camera}/{camera}.txt', self.distance[camera])
    def generate_all(self,  distance = None, ocultation = False):
        pbar = log.getLogger()
        for camera in self.camera_list.keys():
            pbar.info(f"Camera: {camera}")
            handler = TqdmHandler()
            for frame in tqdm(range(self.scene.frame_end)):
                #log.info(f"\tFrame: {frame}")
                self.__call__(camera = camera,
                              frame = frame,
                              distance = distance,
                              ocultation = ocultation)
                pbar.addHandler(handler)

    def __call__(self,camera = 'Camera.01', frame = 1,  distance = None, ocultation = False):
        self.camera_list[camera].render_image(frame, 
                                distance = distance, 
                                occultation = ocultation)


def redirect_print():
    logfile = os.path.join('logfile.log')
    open(logfile, 'a').close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)

    return logfile,old,fd

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate images from blender')
    parser.add_argument('--input_blender', type=str, default='blender/scene.blend', help='Input blender file')
    parser.add_argument('--output', type=str, default='output', help='Output folder')
    parser.add_argument('--frame', type=int, default=1, help='Number of frames to generate')

    args = parser.parse_args()

    logfile,old,fd = redirect_print()

    input_environment = args.input_blender
    params = {
        "frame": args.frame,
        "fps": 24,
        "resolution_x": 640,
        "resolution_y": 480,
        "color_mode": 'RGB',
        "exclude": ['lefttube', 'lefttube2', 'metalpiece', 'support', 'thintubes', 'tube1', 'walls'],
        "output_blender": args.output
    }

    environment = Environment(input_environment, params, None, log_level=log.DEBUG)
    environment('Camera.01',5)
    #environment.generate_all_camera(5)


    os.close(fd)
    os.dup(old)
    os.close(old)

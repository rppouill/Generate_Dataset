# give Python access to Blender's functionality
import bpy
import os 
import numpy as np
from mathutils import Vector

import logging as log
import sys


class Blender_Render():
    def __init__(self, input_environment,params, scenario = None, camera_Name = None) -> None:
        

        print("Blender_Render.__init__")
        print(f"input_environment: {input_environment}")
        
        # Import the blender file
        self.imported_object = bpy.ops.wm.open_mainfile(filepath=input_environment)
        
        # Set the parameters
        self.context = bpy.context
        self.scene = self.context.scene
        self.scene.frame_end = params["frame"]
        self.scene.render.fps = params["fps"]
        self.scene.render.resolution_x = params["resolution_x"]
        self.scene.render.resolution_y = params["resolution_y"]
        self.scene.render.image_settings.color_mode = params["color_mode"]

        self.exclude = params["exclude"]

        print(f'Scene: {self.scene}')

        print(f"camera_Name: {camera_Name}")
        print(f"frame_end: {self.scene.frame_end}")
        print(f"fps: {self.scene.render.fps}")
        print(f"resolution_x: {self.scene.render.resolution_x}")
        print(f"resolution_y: {self.scene.render.resolution_y}")
        print(f"color_mode: {self.scene.render.image_settings.color_mode}")


        
        self.camera = bpy.data.objects.get(camera_Name)
        self.other_object = [ob.name for ob in self.scene.objects if ob.type != 'CAMERA']
        self.scenario = scenario if scenario is not None else self.scenario
        print(f"Camera Name: {camera_Name}")
        print(f"Camera: {self.camera}")
        self.camera_position = (bpy.data.objects[self.camera.name].location.x, bpy.data.objects[self.camera.name].location.y, bpy.data.objects[self.camera.name].location.z)
        self.scenario(self.scene.frame_end)
        # Set the occulusion test parameters
        res_ratio = 1
        self.res_x = int(self.context.scene.render.resolution_x * res_ratio)
        self.res_y = int(self.context.scene.render.resolution_y * res_ratio)

        print(f'Scene: {self.scene}')

    def scenario(self):
        pass
    def occlusion_test(self,depsgraph, camera, resolution_x, resolution_y, exclude=[]):
        # get vectors which define view frustum of camera
        top_right, _, bottom_left, top_left = camera.data.view_frame(scene=self.scene)

        camera_quaternion = camera.matrix_world.to_quaternion()
        camera_translation = camera.matrix_world.translation

        # get iteration range for both the x and y axes, sampled based on the resolution
        x_range = np.linspace(top_left[0], top_right[0], resolution_x)
        y_range = np.linspace(top_left[1], bottom_left[1], resolution_y)

        z_dir = top_left[2]

        hit_data = set()

        # iterate over all X/Y coordinates
        for x in x_range:
            for y in y_range:
                # get current pixel vector from camera center to pixel
                pixel_vector = Vector((x, y, z_dir))
                # rotate that vector according to camera rotation
                pixel_vector.rotate(camera_quaternion)
                pixel_vector.normalized()

                is_hit, _, _, _, hit_obj, _ = self.scene.ray_cast(depsgraph, camera_translation, pixel_vector)

                if is_hit:
                    if hit_obj.name not in exclude:
                        hit_data.add(hit_obj.name)

        return hit_data
    
    # Get Distance
    # @param p0: point 0
    # @param p1: point 1
    # @return distance: distance between p0 and p1
    def _getDistance(self,p0, p1):
        return np.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2  + (p0[2] - p1[2])**2)
    
    # Compute distance
    # @param frame: frame to render
    # @param distance: distance between the camera and the nearest object
    # @param visible_objects: list of visible objects
    # @description: Compute the distance between the camera and the nearest object
    def _compute_distance(self,frame, distance, visible_objects):
        buff_distance = np.Infinity
        print(f"{self.camera.name} visible_objects: {visible_objects}")
        for visible_object in visible_objects:
            start = (bpy.data.objects[visible_object].location.x, bpy.data.objects[visible_object].location.y, bpy.data.objects[visible_object].location.z)
            buff_distance = self._getDistance(start, self.camera_position) if buff_distance > self._getDistance(start, self.camera_position) else buff_distance
            print(f"{self.camera.name} start: {start}")
        
        distance[frame-1] = buff_distance

    # Render Image
    # @param frame: frame to render
    # @param distance: distance between the camera and the nearest object
    # @param filepath: path to save the image
    # @return render_filepath: path to the image
    # @return distance: distance between the camera and the nearest object
    # @description: Render the image and compute the distance between the camera and the nearest object

    def render_image(self, frame, distance = None, filepath = './output', filename = None, occultation = True):
        print(frame)
        print(self.scene)
        self.scene.frame_set(frame)
        self.scene.render.filepath = f'./{filepath}/{frame}.png' if filename is None else f'./{filepath}/{filename}.png'
        render_filepath = self.scene.render.filepath
        print(f"Render frame {frame}")
        if occultation:
            visible_objects = self.occlusion_test(self.context.evaluated_depsgraph_get(), 
                                                self.camera, self.res_x, self.res_y,
                                                exclude= self.exclude)
            print(f"visible_objects: {visible_objects}")
            print(f"Len visible_objects: {len(visible_objects)}")
        else:
            visible_objects = [1]

        if len(visible_objects) > 0:
            bpy.context.scene.camera = self.camera
            bpy.ops.render.render(write_still=True) 
            if distance is not None:
                self._compute_distance(frame, distance,visible_objects)
        else:
            render_filepath = None
            print("No visible object")
            if distance is not None:
                distance[frame-1] = 0 

        #print(f"{self.camera.name} distance: {distance[frame-1]}")
        return render_filepath
    
    def render_animation(self, filepath = './output'):
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.ffmpeg.format = 'MPEG4'
        self.scene.render.ffmpeg.codec = 'H264'
        self.scene.render.ffmpeg.audio_codec = 'NONE'

        for camera in self.cameras:
            scene = bpy.context.scene
            self.scene.render.filepath = f'./{filepath}/{camera.name}.mp4'
            bpy.ops.render.render(animation=True)


#def getFormat():
#    return 'blend'
#def getNumberCameraFromBlenderFile(pathfile):
#    f = bpy.ops.wm.open_mainfile(filepath=pathfile)
#    cameras = [ob.name for ob in bpy.context.scene.objects if ob.type == 'CAMERA']
#    return len(cameras)


def scenario(end_frame):
    from numpy import floor

    def update(obj,frame):
        for value in obj.values():
            for item in value:
                item.keyframe_insert("rotation_euler", frame = frame)
                item.keyframe_insert("location", frame = frame)

    cube = bpy.data.objects['Cube']
    cone = bpy.data.objects['Cône']

    obj = {'cube': [cube], 'cone': [cone]}

    obj['cube'][0].location = (0,0,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,0.0)

    obj['cone'][0].location = (9,8,0.3)
    obj['cone'][0].rotation_euler = (1.5708,0.0,0.0)

    start_frame = 1
    update(obj,frame = start_frame)

    obj['cube'][0].location = (9,0,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,1.5708)

    obj['cone'][0].location = (9,0,1.3)
    obj['cone'][0].rotation_euler = (1.5708,0.0,-1.5708)
    
    middle_frame = floor(end_frame/2)
    update(obj,frame = middle_frame)


    obj['cube'][0].location = (9,7,0.3)
    obj['cone'][0].location = (0.3,0,0.3)
    cube.location = (9,8,0.3)
    update(obj,frame = end_frame)

def getDistance(p0, p1):
    return np.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2  + (p0[2] - p1[2])**2)

def test_Blender_Render(input_environment,frame,output):

    blender_render = [Blender_Render(input_environment, frame, camera_Name='Caméra_01'),
                      Blender_Render(input_environment, frame, camera_Name='Caméra_02') ]

    blender_render[0].scenario = scenario
    blender_render[1].scenario = scenario

    distance = [0]*frame
    
    blender_render[0].render_image(5,distance,output, processing = getDistance)
    blender_render[1].render_image(5,distance,output, processing = getDistance)

    blender_render.render_animation(output)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input_environment', type=str, default='./Blender/Environment/elbow_corridor.blend',
                        help='Path to the blender file')
    parser.add_argument('--output', type=str, default='./output',)
    parser.add_argument('--frame', '-f', type=int, default=300)
    args = parser.parse_args()


    test_Blender_Render(args.input_environment, args.frame,args.output)  
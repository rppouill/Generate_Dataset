import bpy
import logging as log
from mathutils import Vector
import numpy as np
import os

class Blender_Camera():
    def __init__(self, context, camera, exclude, output_folder = './output', res_ratio = 1, log_level = log.INFO):
        log.basicConfig(level=log_level)

        self.context = context
        self.scene = self.context.scene
        self.camera = camera
        
        self.camera_position = (self.camera.location.x, self.camera.location.y, self.camera.location.z)

        self.exclude = exclude
        self.res_x = int(self.context.scene.render.resolution_x * res_ratio)
        self.res_y = int(self.context.scene.render.resolution_y * res_ratio)

        self.filepath = os.path.join(output_folder,self.camera.name,f'{self.camera.name}_in' )


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
        log.debug(f"{self.camera.name} visible_objects: {visible_objects}")
        for visible_object in visible_objects:
            log.debug(f"Visible object: {visible_object}")
            start = (bpy.data.objects[visible_object].location.x, bpy.data.objects[visible_object].location.y, bpy.data.objects[visible_object].location.z)
            buff_distance = self._getDistance(start, self.camera_position) if buff_distance > self._getDistance(start, self.camera_position) else buff_distance
            log.debug(f"{self.camera.name} start: {start}")
        
        distance[frame-1] = buff_distance

    # Render Image
    # @param frame: frame to render
    # @param distance: distance between the camera and the nearest object
    # @param filepath: path to save the image
    # @return render_filepath: path to the image
    # @return distance: distance between the camera and the nearest object
    # @description: Render the image and compute the distance between the camera and the nearest object

    def render_image(self, frame, distance = None,  occultation = True):
        log.debug(frame)
        log.debug(self.scene)
        self.scene.frame_set(frame)
        #self.scene.render.filepath = f'./{self.filepath}/{frame:0{len(str(self.scene.frame_end))}}.png'
        self.scene.render.filepath = os.path.join(self.filepath, f'{frame:0{len(str(self.scene.frame_end))}}.png')
        render_filepath = self.scene.render.filepath
        log.debug(f"Render frame {frame}")
        visible_objects = []
        if occultation:
            visible_objects = self.occlusion_test(self.context.evaluated_depsgraph_get(), 
                                                self.camera, self.res_x, self.res_y,
                                                exclude= self.exclude)
            log.debug(f"visible_objects: {visible_objects}")
            log.debug(f"Len visible_objects: {len(visible_objects)}")
        else:
            visible_objects = [1]

        if len(visible_objects) > 0:
            bpy.context.scene.camera = self.camera
            bpy.ops.render.render(write_still=True)

            if distance is not None:
                self._compute_distance(frame, distance,visible_objects)

        #if occultation or distance is not None:
        #    visible_objects = self.occlusion_test(self.context.evaluated_depsgraph_get(), 
        #                                        self.camera, self.res_x, self.res_y,
        #                                        exclude= self.exclude)
        #    log.debug(f"visible_objects: {visible_objects}")
        #    log.debug(f"Len visible_objects: {len(visible_objects)}")
        #else:
        #    visible_objects = [1]
        #
        #if len(visible_objects) > 0:
        #    bpy.context.scene.camera = self.camera
        #    bpy.ops.render.render(write_still=True) 
        #    if distance is not None:
        #        self._compute_distance(frame, distance,visible_objects)
        #else:
        #    render_filepath = None
        #    log.debug("No visible object")
        #    if distance is not None:
        #        distance[frame-1] = 0 
        return render_filepath

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
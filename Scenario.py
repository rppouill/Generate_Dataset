def update(obj,frame):
    for value in obj.values():
        for item in value:
            item.keyframe_insert("rotation_euler", frame = frame)
            item.keyframe_insert("location", frame = frame)

def Delete_Animation(obj):
    for item in obj.values():
        for value in item:
            value.animation_data_clear()

def Elbow_Corridor(end_frame):
    import bpy
    from numpy import floor


    cube = bpy.data.objects['Cube']
    cone = bpy.data.objects['Cône']

    obj = {'cube': [cube], 'cone': [cone]}

    Delete_Animation(obj)

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
def Square(end_frame):
    import bpy
    from numpy import floor

    cube = bpy.data.objects['Cube']
    cone = bpy.data.objects['Cône']
    torus = bpy.data.objects['Torus']

    obj = {'cube': [cube], 'cone': [cone], 'torus': [torus]}
    obj_slow = {'cube': [cube], 'cone': [cone]}
    obj_speed = {'torus': [torus]}
    Delete_Animation(obj)
    Square_Torus(obj_speed,end_frame)
    obj_slow['cube'][0].location = (1,4,0.3)
    obj_slow['cube'][0].rotation_euler = (0.0,0.0,0.0)

    obj_slow['cone'][0].location = (-9,-14,0.3)
    obj_slow['cone'][0].rotation_euler = (0.0,1.5708,0.0)

    
    start_frame = 1        # Set the output folder for the bpy verbosity

    update(obj_slow,frame = start_frame)

    obj_slow['cube'][0].location = (1,-6,0.3)
    obj_slow['cube'][0].rotation_euler = (0.0,0.0,-1.5708)

    obj_slow['cone'][0].location = (1,-14,0.3)
    obj_slow['cone'][0].rotation_euler = (-1.5708,0.0,0.0)


    middle_frame = floor(end_frame/2)
    update(obj_slow,frame = middle_frame)

    obj_slow['cube'][0].location = (-9,-6,0.3)

    obj_slow['cone'][0].location = (1,4,0.3)

    update(obj_slow,frame = end_frame)
def S_Corridor(end_frame):
    import bpy
    from numpy import floor


    cube = bpy.data.objects['Cube']
    torus = bpy.data.objects['Torus']

    obj = {'cube': [cube], 'torus': [torus]}
    Delete_Animation(obj)
    positions_torus = [[   0  ,- 8  ,-1.5],
                        [  0  , 13.5,-1.5],
                        [- 6.5, 20  ,-1.5],
                        [-21  , 24.5,-1.5],
                        [-23  , 32  ,-1.5],
                        [-20.5, 40.5,-1.5],
                        [-14  , 44.5,-1.5],
                        [  5  , 44.5,-1.5],
                       ]
    frame_partition = floor(end_frame / len(positions_torus))
    for i,position in enumerate(positions_torus):
        obj['torus'][0].location = position
        obj['torus'][0].rotation_euler = (0.0,0.0,0.0)
        update(obj,frame = i*frame_partition)

def Square_Torus(obj,end_frame):
    print(end_frame)
    obj['torus'][0].location = (-9, -6, 0.5)
    obj['torus'][0].rotation_euler = (0.0,0.0,0.0)
    start_frame = 1
    update(obj,frame = start_frame)

    frame_partition = end_frame / 5

    obj['torus'][0].location = (-9, -14, 0.5)
    update(obj,frame = frame_partition)

    obj['torus'][0].location = (1, -14, 0.5)
    update(obj,frame = 2*frame_partition)

    obj['torus'][0].location = (1, 4, 1)
    update(obj,frame = 3*frame_partition)

    obj['torus'][0].location = (1, -6, 0.5)
    update(obj,frame = 4*frame_partition)

    obj['torus'][0].location = (-9, -6, 1)
    update(obj,frame = end_frame)






from enum import Enum
from functools import partial

class Scenario(Enum):        
    ELBOW_CORRIDOR = partial(Elbow_Corridor)
    SQUARE = partial(Square)

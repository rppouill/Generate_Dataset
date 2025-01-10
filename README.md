# Generate_Dataset

Parameters
```
    --generate  -g          Generate JSON file              [False]
    --json      -j          Pathfile of patern JSON file    [Camera_XX.json]

    --input_blender         Input Blender Model
    --output_blender        Folder of output generated
    --scenario              Scenario associated of Model

    --frame         -f  
    --numberCamera  -n

    --occultation   -o      Generated only if actor in see by a camera

    --verbose       -v      NOTSET / DEBUG /INFO / WARNING / ERROR / CRITICAL [INFO]

    --gpu                   using GPU for generated image
```


Command using to generate the dataset.
```
 python3 GenerateImage_Dataset.py --input_blender ./ImageGenerator/Blender/Environment/Square4Camera9Person.blend --output_blender ./Dataset49/ --scenario SQUARE --occultation
```
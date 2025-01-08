import logging as log
import os 
import sys
import glob

from tqdm import tqdm
from TqdmToLogger import TqdmHandler

class RealDataset():
    def __init__(self, path_dataset, path_dataset_simulator, video = True, func = None, output_size = None):
        self.path_dataset   = path_dataset
        self.output_path    = path_dataset_simulator
        self.output_size    = output_size

        log.info("Real Dataset  : Generating dataset from real images")
        log.info(f"Path dataset : {self.path_dataset}")
        log.info(f"Output path  : {self.output_path}")

        if os.path.exists(self.output_path) is False:
            log.warning(f"Output path {self.output_path} does'nt exists")
            os.makedirs(self.output_path)
        
            
        

        if func is not None:
            func[0](self.path_dataset, func[1])
            self.path_dataset = func[1]



    def __call__(self, video = True):
        if video:
            self._video_process(self.path_dataset, self.output_path)
        
        else:
            pass

    def _video_process(self, directory, output_path):
        lenght = len(glob.glob(os.path.join(directory, "*.avi")))
        cnt = 0
        for filename in sorted(os.listdir(directory)):
            if os.path.isfile(os.path.join(directory, filename)):
                if filename.endswith(".avi"):
                    camera_path = os.path.join(output_path, f"Caméra.{cnt:0{len(str(lenght))}}",f"Caméra.{cnt:0{len(str(lenght))}}_in")
                    if os.path.exists(camera_path) is False:
                        os.makedirs(camera_path)
                    #Test if output path exists
                    self._video2frame(os.path.join(directory, filename), 
                                     camera_path)
                    cnt += 1



    def _video2frame(self, video_path, output_path):
        import cv2

        resize = self.output_size
        cap = cv2.VideoCapture(video_path)

        ret, frame = cap.read()
        cnt = 0
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = log.getLogger()
        pbar.info(f"Folder Input: {video_path.split('/')[-1]}")
        handler = TqdmHandler()
        for _ in tqdm(range(length)):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if resize is not None:
                while(frame.shape[0] > resize[0] and frame.shape[1] > resize[1]):
                    frame = cv2.pyrDown(frame)
                if frame.shape != resize:
                    frame = cv2.resize(frame, resize)
            
            #log.info(os.path.join(output_path, f"{cnt:0{len(str(length))}}.png"))
            cv2.imwrite(os.path.join(output_path, f"{cnt:0{len(str(length))}}.png"), frame)
            cnt += 1
            pbar.addHandler(handler)
            ret, frame = cap.read()
            


        


def main(args):
    dataset = RealDataset(args.dataset, args.output, output_size=args.resize)
    dataset(args.video)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = "Real Dataset")
    parser.add_argument("--dataset" , type = str    , help = "Path to dataset")
    parser.add_argument("--output"  , type = str    , help = "Output path")
    parser.add_argument("--video"   , type = bool   , help = "Process video")
    parser.add_argument("--resize"  , type = str  , default = None, help = "Resize image")

    args = parser.parse_args()

    print(args.resize)
    print(type(args.resize))
    args.resize = tuple(map(int, args.resize.split(',')))

    log.basicConfig(level = log.INFO)

    main(args)
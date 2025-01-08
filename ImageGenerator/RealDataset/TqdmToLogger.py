import logging
import time
import colorlog
from tqdm import tqdm

class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = TqdmHandler()
    for x in tqdm(range(100)):

        
        logger.addHandler(handler)
        #logger.debug("Inside subtask: "+str(x))
        time.sleep(.5)
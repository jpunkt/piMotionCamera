import queue
import subprocess
import logging
import threading
from time import sleep

import cv2

from .constants import *
from .producers import CamProducer, ImgProducer


logger = logging.getLogger(__name__)


def main(printer_ip,
         printer_id,
         job_time,
         camera_score_threshold,
         camera_long_interval,
         camera_short_interval,
         image_folder,
         image_wait_interval):

    q = queue.Queue(maxsize=1)
    cmd = ['lp', '-h', printer_ip, '-d', printer_id]

    cam_thread = CamProducer(q,
                             wait_long=camera_long_interval,
                             wait_short=camera_short_interval,
                             score_threshold=camera_score_threshold)
    img_thread = ImgProducer(q,
                             img_folder=image_folder,
                             wait=image_wait_interval)

    cam_thread.start()
    img_thread.start()

    while True:
        img = q.get()
        logger.debug('Printing Job')
        sp = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        sp.communicate(cv2.imencode('.png', img)[1].tobytes())
        sleep(job_time)

    cam_thread.running = False
    img_thread.running = False

    cam_thread.join()
    img_thread.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main(printer_ip=PRINT_SERVER_IP,
         printer_id=PRINTER_ID,
         job_time=PRINT_JOB_WAIT,
         camera_score_threshold=SCORE_THRESH,
         camera_long_interval=CAM_WAIT_LONG,
         camera_short_interval=CAM_WAIT_SHORT,
         image_folder=IMAGE_FOLDER,
         image_wait_interval=IMAGE_WAIT_INTERVAL)

import logging
import queue
import subprocess
import cv2

from time import sleep

from .constants import *
from .producers import CamProducer, ImgProducer

__version__ = '0.0.1'

logger = logging.getLogger(__name__)


def main(printer_ip=PRINT_SERVER_IP,
         printer_id=PRINTER_ID,
         job_time=PRINT_JOB_WAIT):
    q = queue.Queue(maxsize=1)

    cam_thread = CamProducer(q)
    img_thread = ImgProducer(q)

    cam_thread.start()
    img_thread.start()

    while True:
        img = q.get()
        logger.debug('Printing Job')
        cmd = ['lp', '-h', printer_ip, '-d', printer_id]
        sp = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        sp.communicate(cv2.imencode('.png', img)[1].tobytes())
        sleep(job_time)

    cam_thread.running = False
    img_thread.running = False
    cam_thread.join()
    img_thread.join()

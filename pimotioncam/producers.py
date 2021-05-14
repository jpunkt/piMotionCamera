import logging
import threading
from time import sleep
import queue
import picamera
import numpy as np
import cv2

from datetime import datetime
from .constants import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def capture(cam):
    img = np.empty((ROWS * COLS * 3,), dtype=np.uint8)
    cam.capture(img, 'bgr')
    img = img.reshape((ROWS, COLS, 3))[:, :, 0]
    return img


def calc_score(img, prev):
    prev = cv2.blur(prev, KERNELSIZE_GAUSS)
    img = cv2.blur(img, KERNELSIZE_GAUSS)

    diff = np.abs(np.int8(prev) - np.int8(img))
    nz = np.count_nonzero(diff)
    nz_perc = nz / (ROWS * COLS)
    mx = np.max(diff)
    s = nz_perc * mx
    logger.info(f'nonzero: {nz}/ {(100 * nz_perc):2.2f}% | max: {mx} | score: {s:2.2f} | movement: {s > 50}')
    return s


def make_diff_image(img1, img2):
    img = np.uint8(np.abs(np.int8(img1) - np.int8(img2)))
    # img = cv2.fastNlMeansDenoising(img, None)
    c = 255 / np.log(1 + np.max(img))
    return 255 - np.uint8(c * np.log(1 + img))


def get_files(path):
    pass
    return []


class CamProducer(threading.Thread):
    def __init__(self,
                 q: queue.Queue,
                 wait_long=CAM_WAIT_LONG,
                 wait_short=CAM_WAIT_SHORT):
        threading.Thread.__init__(self)
        self.queue = q
        self.long_wait = wait_long
        self.short_wait = wait_short
        self.running = True

    def run(self):
        with picamera.PiCamera() as camera:
            camera.color_effects = (128, 128)
            camera.resolution = RESOLUTION
            camera.framerate = 24
            sleep(2)

            camera.start_preview()
            base_img = capture(camera)

            while self.running:
                sleep(self.long_wait)
                image = capture(camera)
                score = calc_score(image, base_img)

                max_img = inv = max_score = None

                while score > SCORE_THRESH:
                    if (max_score is None) or (score > max_score):
                        max_img = image
                        max_score = score
                    sleep(self.short_wait)
                    new_img = capture(camera)
                    score = calc_score(new_img, image)
                    image = new_img

                if max_score is not None:
                    now = datetime.now().strftime('%y%m%d_%H%M%S')
                    logger.info(f'new highscore {max_score} at {now}')
                    inv = make_diff_image(max_img, base_img)
                    self.queue.put(inv)

                base_img = image


class ImgProducer(threading.Thread):
    def __init__(self, q: queue.Queue,
                 img_folder,
                 wait=IMAGE_WAIT_INTERVAL):
        threading.Thread.__init__(self)
        self.queue = q
        self.img_folder = img_folder
        self.wait_time = wait
        self.running = True

    def run(self):
        img_list = []

        while self.running:
            if len(img_list) == 0:
                img_list = get_files(self.img_folder)

            img = cv2.imread(img_list.pop())
            self.queue.put(img)
            sleep(self.wait_time)




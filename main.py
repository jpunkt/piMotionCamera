from datetime import datetime
import time
import picamera
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

COLS = 1312
ROWS = 976
RESOLUTION = (COLS, ROWS)

SCORE_THRESH = 50

KERNELSIZE_GAUSS = (21, 21)


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


if __name__ == '__main__':
    logging.basicConfig()

    with picamera.PiCamera() as camera:
        camera.color_effects = (128, 128)
        camera.resolution = RESOLUTION
        camera.framerate = 24
        time.sleep(2)

        camera.start_preview()
        base_img = capture(camera)

        while True:
            time.sleep(1)
            image = capture(camera)
            score = calc_score(image, base_img)

            max_img = inv = max_score = None

            while score > SCORE_THRESH:
                if (max_score is None) or (score > max_score):
                    max_img = image
                    max_score = score
                time.sleep(0.2)
                new_img = capture(camera)
                score = calc_score(new_img, image)
                image = new_img

            if max_score is not None:
                logger.info(f'new highscore: {max_score}')
                inv = make_diff_image(max_img, base_img)
                now = datetime.now().strftime('%y%m%d_%H%M%S')
                cv2.imwrite(f'test-img_{now}.png', max_img)
                cv2.imwrite(f'test-diff_{now}.png', inv)

            base_img = image


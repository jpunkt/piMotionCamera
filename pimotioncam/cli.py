import click
import logging

from pimotioncam.constants import *
from pimotioncam import main


@click.command()
@click.option('-i', '--printer_ip',
              help='IP of CUPS server',
              default=PRINT_SERVER_IP,
              show_default=True)
@click.option('-p', '--printer_id',
              help='Printer ID with CUPS',
              default=PRINTER_ID,
              show_default=True)
@click.option('-t', '--job_time',
              help='Seconds to wait after sending file to printer before printing another image',
              default=PRINT_JOB_WAIT,
              show_default=True)
@click.option('-f', '--img_folder',
              help='Folder to retrieve random images from',
              default=IMAGE_FOLDER,
              show_default=True)
@click.option('--img_interval',
              help='Interval between images printed from disk',
              default=IMAGE_WAIT_INTERVAL,
              show_default=True)
@click.option('--camera_interval',
              help='Interval in seconds between camera images when no motion is detected',
              default=CAM_WAIT_LONG,
              show_default=True)
@click.option('--motion_interval',
              help='Interval in seconds between camera images if motion was detected',
              default=CAM_WAIT_SHORT,
              show_default=True)
@click.option('--motion_threshold',
              help='Score threshold for motion detection',
              default=SCORE_THRESH,
              show_default=True)
def pimotion(printer_ip,
             printer_id,
             job_time,
             img_folder,
             img_interval,
             camera_interval,
             motion_interval,
             motion_threshold):
    logging.basicConfig(level=logging.INFO)
    main(printer_ip=printer_ip,
         printer_id=printer_id,
         job_time=job_time,
         image_folder=img_folder,
         image_wait_interval=img_interval,
         camera_long_interval=camera_interval,
         camera_short_interval=motion_interval,
         camera_score_threshold=motion_threshold
         )

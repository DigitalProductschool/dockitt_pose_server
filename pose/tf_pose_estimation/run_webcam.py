import argparse
import logging
import time

import cv2
import numpy as np

from pose.tf_pose_estimation.tf_pose.estimator import TfPoseEstimator
from pose.tf_pose_estimation.tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0


def webcam():
    # parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    # parser.add_argument('--camera', type=int, default=0)

    # parser.add_argument('--resize', type=str, default='432x368',
    #                     help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    # parser.add_argument('--resize-out-ratio', type=float, default=4.0,
    #                     help='if provided, resize heatmaps before they are post-processed. default=1.0')

    # parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    # parser.add_argument('--show-process', type=bool, default=False,
    #                     help='for debug purpose, if enabled, speed for inference is dropped.')
    # args = parser.parse_args()

    logger.debug('initialization %s : %s' % ('mobilenet_thin', get_graph_path('mobilenet_thin')))
    w, h = model_wh('432x368')
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(432, 368))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(0)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    while True:
        ret_val, image = cam.read()

        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=4.0)

        logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        logger.debug('show+')
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()


import argparse
import os
import sys

import cv2
import numpy as np
from tqdm import tqdm
#
# __dir__ = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.abspath(os.path.join(__dir__, '../../../')))
from paddleseg.utils import get_sys_env, logger, get_image_list

from infer import Predictor


def get_bg_img(bg_img_path, img_shape):
    if bg_img_path is None:
        bg = 255 * np.ones(img_shape)
    elif not os.path.exists(bg_img_path):
        raise Exception('The --bg_img_path is not existed: {}'.format(
            bg_img_path))
    else:
        bg = cv2.imread(bg_img_path)
    return bg


def makedirs(save_dir):
    dirname = save_dir if os.path.isdir(save_dir) else \
        os.path.dirname(save_dir)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def seg_image(args,predictor):
    assert os.path.exists(args.img_path), \
        "The --img_path is not existed: {}.".format(args.img_path)

    logger.info("Input: image")
    logger.info("Create predictor...")

    logger.info("Start predicting...")
    img = cv2.imread(args.img_path)
    bg_img = get_bg_img(args.bg_img_path, img.shape)
    out_img = predictor.run(img, bg_img)
    cv2.imwrite(args.save_dir, out_img)


def seg_video(args,predictor):
    assert os.path.exists(args.video_path), \
        'The --video_path is not existed: {}'.format(args.video_path)
    assert args.save_dir.endswith(".avi"), 'The --save_dir should be xxx.avi'

    cap_img = cv2.VideoCapture(args.video_path)
    assert cap_img.isOpened(), "Fail to open video:{}".format(args.video_path)
    fps = cap_img.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap_img.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap_img.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap_img.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_out = cv2.VideoWriter(args.save_dir,
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
                              (width, height))

    if args.bg_video_path is not None:
        assert os.path.exists(args.bg_video_path), \
            'The --bg_video_path is not existed: {}'.format(args.bg_video_path)
        is_video_bg = True
        cap_bg = cv2.VideoCapture(args.bg_video_path)
        assert cap_bg.isOpened(), "Fail to open video:{}".format(
            args.bg_video_path)
        bg_frame_nums = cap_bg.get(cv2.CAP_PROP_FRAME_COUNT)
        bg_frame_idx = 1
    else:
        is_video_bg = False
        bg = get_bg_img(args.bg_img_path, [height, width, 3])

    logger.info("Input: video")
    logger.info("Create predictor...")

    logger.info("Start predicting...")
    with tqdm(total=total_frames) as pbar:
        img_frame_idx = 0
        while cap_img.isOpened():
            ret_img, img = cap_img.read()
            if not ret_img:
                break

            if is_video_bg:
                ret_bg, bg = cap_bg.read()
                if not ret_bg:
                    break
                bg_frame_idx += 1
                if bg_frame_idx == bg_frame_nums:
                    bg_frame_idx = 1
                    cap_bg.set(cv2.CAP_PROP_POS_FRAMES, 0)

            out = predictor.run(img, bg)
            cap_out.write(out)
            img_frame_idx += 1
            pbar.update(1)

    cap_img.release()
    cap_out.release()
    if is_video_bg:
        cap_bg.release()


def seg_camera(args,predictor):
    cap_camera = cv2.VideoCapture(0)
    assert cap_camera.isOpened(), "Fail to open camera"
    width = int(cap_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if args.bg_video_path is not None:
        assert os.path.exists(args.bg_video_path), \
            'The --bg_video_path is not existed: {}'.format(args.bg_video_path)
        is_video_bg = True
        cap_bg = cv2.VideoCapture(args.bg_video_path)
        bg_frame_nums = cap_bg.get(cv2.CAP_PROP_FRAME_COUNT)
        bg_frame_idx = 1
    else:
        is_video_bg = False
        bg = get_bg_img(args.bg_img_path, [height, width, 3])

    logger.info("Input: camera")
    logger.info("Create predictor...")

    logger.info("Start predicting...")
    while cap_camera.isOpened():
        ret_img, img = cap_camera.read()
        if not ret_img:
            break

        if is_video_bg:
            ret_bg, bg = cap_bg.read()
            if not ret_bg:
                break
            if bg_frame_idx == bg_frame_nums:
                bg_frame_idx = 1
                cap_bg.set(cv2.CAP_PROP_POS_FRAMES, 0)
            bg_frame_idx += 1

        out = predictor.run(img, bg)
        cv2.imshow('PP-HumanSeg', out)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if is_video_bg:
        cap_bg.release()
    cap_camera.release()






def parse_args():
    parser = argparse.ArgumentParser(
        description='PP-HumanSeg inference for video')
    parser.add_argument(
        "--config",
        help="The config file of the inference model.",
        type=str,
        required=False)
    parser.add_argument(
        '--img_path', help='The image that to be predicted.', type=str)
    parser.add_argument(
        '--video_path', help='Video path for inference', type=str)
    parser.add_argument(
        '--bg_img_path',
        help='Background image path for replacing. If not specified, a white background is used',
        type=str)
    parser.add_argument(
        '--bg_video_path', help='Background video path for replacing', type=str)
    parser.add_argument(
        '--save_dir',
        help='The directory for saving the inference results',
        type=str,
        default='./output')

    parser.add_argument(
        '--vertical_screen',
        help='The input image is generated by vertical screen, i.e. height is bigger than width.'
        'For the input image, we assume the width is bigger than the height by default.',
        action='store_true')
    parser.add_argument(
        '--use_post_process', help='Use post process.', action='store_true')
    parser.add_argument(
        '--use_optic_flow', help='Use optical flow.', action='store_true')
    parser.add_argument(
        '--test_speed',
        help='Whether to test inference speed',
        action='store_true')

    return parser.parse_args()



if __name__ == "__main__":
    args = parse_args()
    env_info = get_sys_env()
    args.use_gpu = True if env_info['Paddle compiled with cuda'] \
        and env_info['GPUs used'] else False

    makedirs(args.save_dir)

    if args.img_path is not None:
        seg_image(args)
    elif args.video_path is not None:
        seg_video(args)
    else:
        seg_camera(args)

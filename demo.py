import os
import os.path as op

import cv2
import numpy as np
import skimage.io

from pipeline import Pipeline
from utils.yacs import Config


OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def demo_intermediate_results():
    cfg = Config('configs/my_test.yaml')
    pipeline = Pipeline(cfg)

    raw_path = 'raw/1_1.RAW'
    bayer = np.fromfile(raw_path, dtype='uint16', sep='')
    bayer = bayer.reshape((cfg.hardware.raw_height, cfg.hardware.raw_width))

    _, intermediates = pipeline.execute(bayer, save_intermediates=True)
    for module_name, result in intermediates.items():
        output = pipeline.get_output(result)
        output_path = op.join(OUTPUT_DIR, '{}.jpg'.format(module_name))
        output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, output)


if __name__ == '__main__':
    demo_intermediate_results()

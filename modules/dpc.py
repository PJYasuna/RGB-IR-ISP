# File: dpc.py
# Description: Dead Pixel Correction
# Created: 2021/10/22 20:50
# Author: Qiu Jueqin (qiujueqin@gmail.com)


import numpy as np
import cv2
from .basic_module import BasicModule
from .helpers import pad, split_bayer, reconstruct_bayer, shift_array


class DPC(BasicModule):
    def convert_IR_to_R(self, bayer):
        pad_bayer = pad(bayer, pads=(0, 1, 0, 1))
        bayer = pad_bayer
        for h in range(1, bayer.shape[0], 2):
            if h == bayer.shape[0]-1:
                bayer[h, 1::2] = bayer[h-2, 1::2]
                break
            if h % 4 == 1:
                for w in range(3, bayer.shape[1], 4):
                    bayer[h,w] = (bayer[h-1,w-1] + bayer[h+1,w+1])//2
                for w in range(1, bayer.shape[1], 4):
                    bayer[h,w] = (bayer[h-1,w+1] + bayer[h+1,w-1])//2
            elif h % 4 == 3:
                for w in range(1, bayer.shape[1], 4):
                    bayer[h,w] = (bayer[h-1,w-1] + bayer[h+1,w+1])//2
                for w in range(3, bayer.shape[1], 4):
                    bayer[h,w] = (bayer[h-1,w+1] + bayer[h+1,w-1])//2 
        return bayer[:-1, :-1]
    
    def convert_R_to_B(self, bayer):
        pad_bayer = pad(bayer, pads=2)
        for h in range(2, pad_bayer.shape[0]-2,2):
            if h%4 == 2: 
                for w in range(4,pad_bayer.shape[1]-2,4):
                    pad_bayer[h, w] = (pad_bayer[h,w-2] + pad_bayer[h,w+2]+ pad_bayer[h-2,w] + pad_bayer[h+2,w])//4
            elif h%4 == 0:
                for w in range(2,pad_bayer.shape[1]-2,4):
                    pad_bayer[h, w] = (pad_bayer[h,w-2] + pad_bayer[h,w+2] + pad_bayer[h-2,w] +  pad_bayer[h+2,w])//4
        return pad_bayer[2:-2, 2:-2]
        
        
    def execute_IR(self, data):
        bayer = data['bayer'].astype(np.int32)
        IR_channal = bayer[1::2, 1::2]

        height, width = IR_channal.shape
        padded_ir = pad(IR_channal, pads=(1, 0, 1, 0))
        ir_top = padded_ir[:height, 1:1 + width]
        ir_left = padded_ir[1:1 + height, :width]
        ir_tl = padded_ir[:height, :width]

        ir_on_r = np.right_shift(ir_tl + ir_top + ir_left + IR_channal, 2)
        ir_on_gr = np.right_shift(ir_top + IR_channal, 1)
        ir_on_gb = np.right_shift(ir_left + IR_channal, 1)

        ir_image = reconstruct_bayer((ir_on_r, ir_on_gr, ir_on_gb, IR_channal), bayer_pattern='rggb')
        cv2.imwrite('./output/ir_image_2_no.png', ir_image)

    def execute(self, data):
        bayer = data['bayer'].astype(np.int32)
        if self.cfg.hardware.bayer_pattern == 'rgb-ir':
            self.execute_IR(data)
            bayer = self.convert_IR_to_R(bayer)
            bayer = self.convert_R_to_B(bayer)
        padded_bayer = pad(bayer, pads=2)
        padded_sub_arrays = split_bayer(padded_bayer, self.cfg.hardware.bayer_pattern)

        dpc_sub_arrays = []
        for padded_array in padded_sub_arrays:
            shifted_arrays = tuple(shift_array(padded_array, window_size=3))   # generator --> tuple

            mask = (np.abs(shifted_arrays[4] - shifted_arrays[1]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[7]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[3]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[5]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[0]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[2]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[6]) > self.params.diff_threshold) * \
                   (np.abs(shifted_arrays[4] - shifted_arrays[8]) > self.params.diff_threshold)

            dv = np.abs(2 * shifted_arrays[4] - shifted_arrays[1] - shifted_arrays[7])
            dh = np.abs(2 * shifted_arrays[4] - shifted_arrays[3] - shifted_arrays[5])
            ddl = np.abs(2 * shifted_arrays[4] - shifted_arrays[0] - shifted_arrays[8])
            ddr = np.abs(2 * shifted_arrays[4] - shifted_arrays[6] - shifted_arrays[2])
            indices = np.argmin(np.dstack([dv, dh, ddl, ddr]), axis=2)[..., None]

            neighbor_stack = np.right_shift(np.dstack([
                shifted_arrays[1] + shifted_arrays[7],
                shifted_arrays[3] + shifted_arrays[5],
                shifted_arrays[0] + shifted_arrays[8],
                shifted_arrays[6] + shifted_arrays[2]
            ]), 1)
            dpc_array = np.take_along_axis(neighbor_stack, indices, axis=2).squeeze(2)
            dpc_sub_arrays.append(
                mask * dpc_array + ~mask * shifted_arrays[4]
            )

        dpc_bayer = reconstruct_bayer(dpc_sub_arrays, self.cfg.hardware.bayer_pattern)

        data['bayer'] = dpc_bayer.astype(np.uint16)
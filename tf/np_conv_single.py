#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# good example from:
# numpy conv: https://blog.csdn.net/xiongwei111/article/details/100610364
# tf conv:    https://blog.csdn.net/xiongwei111/article/details/100839022

import numpy as np
import tensorflow as tf
import time

class Timer:
    def __init__(self):
        self.last = time.time()
    def elapsed(self):
        t = time.time()
        e = t - self.last
        self.last = t
        return e

def np_conv(inputs, cc ,_result): #padding="VALID"):
    H, W = inputs.shape
    filter_size = cc.shape[0]

    result = np.zeros((_result.shape))

    #更新下新输入,SAME模式下，会改变HW
    H, W = inputs.shape

    #卷积核通过输入的每块区域，stride=1，注意输出坐标起始位置
    for r in range(0, H - filter_size + 1):
        for c in range(0, W - filter_size + 1):
            cur_input = inputs[r:r + filter_size, c:c + filter_size]
            cur_output = cur_input * cc
            conv_sum = np.sum(cur_output)
            result[r, c] = conv_sum
    return result

def _conv(inputs, cc, strides=[1,1], padding="SAME"):
    C_in, H, W = inputs.shape
    filter_size = cc.shape[2]

    # C_out指核对个数，也是最后结果对通道个数
    C_out = cc.shape[0]

    # 同样我们任务核对宽高相等
    if padding == "VALID":
        result = np.zeros(
            [C_out, int(np.ceil(H - filter_size + 1) / strides[0]), int(np.ceil(W - filter_size + 1) / strides[1])],
            np.float32)
    else:
        result = np.zeros([C_out, int(H / strides[0]), int(W / strides[1])], np.float32)
        C, H_new, W_new = inputs.shape
        pad_h = (H_new - 1) * strides[0] + filter_size - H
        pad_top = int(pad_h / 2)
        pad_down = pad_h - pad_top

        pad_w = (W_new - 1) * strides[1] + filter_size - W
        pad_left = int(pad_w / 2)
        pad_right = pad_w - pad_left
        inputs = np.pad(inputs, ((0, 0), (pad_top, pad_down), (pad_left, pad_right)), 'constant',
                        constant_values=(0, 0))
    # 核个数对循环
    for channel_out in range(C_out):
        # 输入通道数对循环
        for channel_in in range(C_in):
            # 当前通道对数据
            channel_data = inputs[channel_in]
            # 采用上面对逻辑，单核单通道卷积,然后累计
            result[channel_out, :, :] += np_conv(channel_data, cc[channel_out][channel_in], result[0])

    # print(result)
    return result

if __name__ == '__main__':
    timer = Timer()

    '''
    feature = 18            # C_in, it will be 18
    in_H = 19; in_W = 19    # it will be 19 x 19
    channel = 32            # C_out, it will be 32
    '''

    feature = 3         # C_in, it will be 18
    in_H = 9; in_W = 9  # it will be 19 x 19
    channel = 2         # C_out, it will be 32
    cc_H = 3; cc_W = 3

    #out_H = 9; out_W = 9

    #输入[C_in,H,W]
    inputs = np.zeros([feature, in_H, in_W])
    print("input:     ", inputs.shape)
    for i in range(feature):
        for j in range(in_H):
            for z in range(in_W):
                inputs[i][j][z] = i+j+z
                print("%3d" % inputs[i][j][z], end=' ')
            print("")
        print("")
        print("")
    #print("input[0]:\n",inputs[0],"\n")

    #卷积核[C_out,C_in,K,K]
    cc = np.zeros([channel, feature, cc_H, cc_W])
    print("conv_core:     ", cc.shape)
    for i in range(channel):
        for j in range(feature):
            for x in range(cc_H):
                for y in range(cc_W):
                    cc[i][j][x][y] = i + j + x + y
                    print("%3d" % cc[i][j][x][y], end=' ')
                print("")
            print("")
        print("")
    #print("conv_core[0][0]\n", conv_core[0][0], "\n")

    print("demo for single np_conv, no pad, the output will shrink")
    final_result = np.zeros([channel, in_H-2, in_W-2], np.float32)
    timer.elapsed()
    final_result = np_conv(inputs[0], cc[0][0], final_result[0])
    print("input:      ", inputs[0].shape)
    print("cc:         ", cc[0][0].shape)
    print("output:     ", final_result.shape)
    print("result, cost %.3f" % (1000.0*timer.elapsed()),"ms\n",final_result)
    print("")

    print("demo for single np_conv, pad 0")
    inputs_pad = np.pad(inputs[0], ((1, 1), (1, 1)), 'constant')
    final_result = np.zeros([channel, in_H, in_W], np.float32)
    timer.elapsed()
    final_result = np_conv(inputs_pad, cc[0][0], final_result[0])
    print("input:      ", inputs_pad.shape)
    print("cc:         ", cc[0][0].shape)
    print("output:     ", final_result.shape)
    print("result, cost %.3f" % (1000.0*timer.elapsed()),"ms\n",final_result)
    print("")

    print("demo for conv")
    timer.elapsed()
    final_result = _conv(inputs, cc, strides=[1,1], padding="SAME")
    print("input:      ", inputs.shape)
    print("cc:         ", cc.shape)
    print("output:     ", final_result.shape)
    print("result, cost %.3f" % (1000.0*timer.elapsed()),"ms\n",final_result)

    # 'NCHW', input=[9,9,1,1] and output=[9,9,1,1]
    # 'NHWC', input=[1,9,9,1] and output=[1,9,9,1]
    # tf default is NHWC, but leelazero use NCHW

    # original inputs [feature, in_H, in_W]
    # expand_dims     [N, feature, in_H, in_W]
    # transpose       [N, in_H, in_W, feature]
    inputs = np.expand_dims(inputs, axis=0).transpose(0,2,3,1)
    inputs_tf = tf.Variable(tf.constant(inputs, shape=[1, in_H, in_W, feature]))

    # original cc     [channel, feature, cc_H, cc_W]
    # transpose       [cc_H, cc_W, feature, channel]
    cc_tf = tf.Variable(tf.constant(cc.transpose(2,3,1,0), shape=[cc_H, cc_W, feature, channel]))
    op = tf.nn.conv2d(inputs_tf, cc_tf, strides=[1,1,1,1], padding='SAME', data_format='NHWC')

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        inputs_tf_prn = sess.run(inputs_tf)
        print("inputs_tf     ", inputs_tf_prn.shape, type(inputs_tf_prn))
        for j in range(feature):
            for x in range(0, in_H):
                for y in range(0, in_W):
                    print("%3d" % inputs_tf_prn[0][x][y][j], end=' ')
                print('')
            print('')

        cc_tf_prn = sess.run(cc_tf)
        print("conv_core_tf     ", cc_tf_prn.shape, type(cc_tf_prn))
        for i in range(channel):
            for j in range(feature):
                for x in range(cc_H):
                    for y in range(cc_W):
                        print("%3d" % cc_tf_prn[x][y][j][i], end=' ')
                    print("")
                print("")
            print("")

        timer.elapsed()
        op_prn = sess.run(op)
        print("cost %.3f" % (timer.elapsed()*1000.0), "ms")
        print("op_prn     ", op_prn.shape, type(op_prn))
        for i in range(channel):
            for x in range(in_H):
                for y in range(in_W):
                    print("%4d" % op_prn[0][x][y][i], end=' ')
                print('')
            print('')

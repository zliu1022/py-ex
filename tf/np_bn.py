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

def float32_variable_storage_getter(getter, name, shape=None, dtype=None,
                                    initializer=None, regularizer=None,
                                    trainable=True,
                                    *args, **kwargs):
    print('float32_variable_storage_getter')
    print(name)
    print(trainable)
    """Custom variable getter that forces trainable variables to be stored in
    float32 precision and then casts them to the training precision."""
    storage_dtype = tf.float32 if trainable else dtype
    variable = getter(name, shape, dtype=storage_dtype,
                      initializer=initializer,
                      regularizer=regularizer,
                      trainable=trainable,
                      *args, **kwargs)
    print(variable)
    if trainable and dtype != tf.float32:
        cast_name = name + '/fp16_cast'
        print(cast_name)
        try:
            cast_variable = tf.get_default_graph().get_tensor_by_name(cast_name + ':0')
        except KeyError:
            cast_variable = tf.cast(variable, dtype, name=cast_name)
        print(cast_variable)
        cast_variable._ref = variable._ref
        variable = cast_variable
    print(variable)
    print('')
    return variable

if __name__ == '__main__':
    timer = Timer()

    '''
    feature = 18            # C_in, it will be 18
    in_H = 19; in_W = 19    # it will be 19 x 19
    channel = 32            # C_out, it will be 32
    '''

    feature = 1         # C_in, it will be 18
    in_H = 2; in_W = 2  # it will be 19 x 19
    #channel = 2         # C_out, it will be 32
    #cc_H = 3; cc_W = 3

    beta = 1.0 #0.677432060
    #输入[C_in,H,W]
    inputs = np.zeros([feature, in_H, in_W])
    print("input:     ", inputs.shape)
    for i in range(feature):
        for j in range(in_H):
            for z in range(in_W):
                #inputs[i][j][z] = i+j+z+1.0
                inputs[i][j][z] = i+j+z+beta
                print("%3d" % inputs[i][j][z], end=' ')
            print("")
        print("")
        print("")
    #print("input[0]:\n",inputs[0],"\n")

    print("demo for np_bn")
    timer.elapsed()
    print("input:      ", inputs[0].shape)
    arr = inputs[0]
    mean = np.mean(arr)
    var = np.var(arr)
    #mean = -0.648249100
    #var = 1.959622000
    print('beta:    %f' % beta)
    print('np.mean: %f' % mean)
    print('np.var:  %f' % var)

    new_arr = arr - mean
    print('arr-mean:\n', new_arr, '\n')
    if (var==0):
        new_arr = new_arr/1e-5
    else:
        new_arr = new_arr/np.sqrt(var+1e-5)

    print('arr/var:\n')
    for x in range(in_H):
        for y in range(in_W):
            print("%3.9f" % new_arr[x][y], end=' ')
        print('')
    print('')
    print("result, cost %.3f" % (1000.0*timer.elapsed()),"ms\n")
    print("")

    # 'NCHW', input=[9,9,1,1] and output=[9,9,1,1]
    # 'NHWC', input=[1,9,9,1] and output=[1,9,9,1]
    # tf default is NHWC, but leelazero use NCHW

    # original inputs [feature, in_H, in_W]
    # expand_dims     [N, feature, in_H, in_W]
    # transpose       [N, in_H, in_W, feature]
    inputs_tf = tf.Variable(tf.constant(inputs, shape=[in_H, in_W, feature]))

    with tf.variable_scope("bn", custom_getter=float32_variable_storage_getter):
        op = tf.layers.batch_normalization(
            inputs_tf,
            epsilon=1e-5, axis=2, fused=True,
            center=True, beta_initializer=tf.constant_initializer(beta),
            scale=False, gamma_initializer=tf.constant_initializer(1.0),
            training=False, #inference mode: use input mean and var
            moving_mean_initializer=tf.constant_initializer(mean),
            moving_variance_initializer=tf.constant_initializer(var),
            #trainable=False) # beta & gamma can't be trained, they will be variable
            trainable=True)  # beta & gamma can be trained, they will be Tensor
        '''
        op = tf.layers.batch_normalization(
            inputs_tf)
        '''

    #beta = tf.get_default_graph().get_tensor_by_name('bn/batch_normalization/beta/fp16_cast:0') # trainable=True
    beta = tf.get_default_graph().get_tensor_by_name('bn/batch_normalization/beta:0')           # trainable=False
    mean = tf.get_default_graph().get_tensor_by_name('bn/batch_normalization/moving_mean:0')
    var  = tf.get_default_graph().get_tensor_by_name('bn/batch_normalization/moving_variance:0')

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        inputs_tf_prn = sess.run(inputs_tf)
        print("inputs_tf     ", inputs_tf_prn.shape, type(inputs_tf_prn))
        for j in range(feature):
            for x in range(0, in_H):
                for y in range(0, in_W):
                    print("%3.9f" % inputs_tf_prn[x][y][j], end=' ')
                print('')
            print('')

        print('sess.run(beta) %.9f' % sess.run(beta))
        print(beta)
        print('sess.run(mean) %.9f' % sess.run(mean))
        print(mean)
        print('sess.run(var)  %.9f' % sess.run(var))
        print(var)
        print('')

        timer.elapsed()
        op_prn = sess.run(op)
        print("cost %.3f" % (timer.elapsed()*1000.0), "ms")
        print("op_prn     ", op_prn.shape, type(op_prn))
        for i in range(feature):
            for x in range(in_H):
                for y in range(in_W):
                    print("%3.9f" % op_prn[x][y][i], end=' ')
                print('')
            print('')


#!/usr/bin/env python3
#
#    This file is part of Leela Zero.
#    Copyright (C) 2017-2018 Gian-Carlo Pascutto
#
#    Leela Zero is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Leela Zero is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Leela Zero.  If not, see <http://www.gnu.org/licenses/>.

import math
import numpy as np
import os
import tensorflow as tf
import time
import unittest

from mixprec import float32_variable_storage_getter, LossScalingOptimizer


def weight_variable(name, shape, dtype, trainable):
    """Xavier initialization"""
    stddev = np.sqrt(2.0 / (sum(shape)))
    # Do not use a constant as the initializer, that will cause the
    # variable to be stored in wrong dtype.
    weights = tf.get_variable(
        name, shape, dtype=dtype,
        initializer=tf.truncated_normal_initializer(stddev=stddev, dtype=dtype), trainable=trainable)
    tf.add_to_collection(tf.GraphKeys.WEIGHTS, weights)
    return weights

# Bias weights for layers not followed by BatchNorm
# We do not regularlize biases, so they are not
# added to the regularlizer collection
def bias_variable(name, shape, dtype, trainable):
    bias = tf.get_variable(name, shape, dtype=dtype,
                           initializer=tf.zeros_initializer(), trainable=trainable)
    return bias


def conv2d(x, W, cpuonly=False):
    if cpuonly:
        print("        conv2d x", x.shape)
        print("        conv2d W", W.shape)
        return tf.nn.conv2d(x, W, data_format='NHWC',
                        strides=[1, 1, 1, 1], padding='SAME')
    else:
        return tf.nn.conv2d(x, W, data_format='NCHW',
                        strides=[1, 1, 1, 1], padding='SAME')

# Restore session from checkpoint. It silently ignore mis-matches
# between the checkpoint and the graph. Specifically
# 1. values in the checkpoint for which there is no corresponding variable.
# 2. variables in the graph for which there is no specified value in the
#    checkpoint.
# 3. values where the checkpoint shape differs from the variable shape.
# (variables without a value in the checkpoint are left at their default
# initialized value)
def optimistic_restore(session, save_file, graph=tf.get_default_graph()):
    reader = tf.train.NewCheckpointReader(save_file)
    saved_shapes = reader.get_variable_to_shape_map()
    var_names = sorted(
        [(var.name, var.name.split(':')[0]) for var in tf.global_variables()
         if var.name.split(':')[0] in saved_shapes])
    restore_vars = []
    for var_name, saved_var_name in var_names:
        curr_var = graph.get_tensor_by_name(var_name)
        var_shape = curr_var.get_shape().as_list()
        if var_shape == saved_shapes[saved_var_name]:
            restore_vars.append(curr_var)
    opt_saver = tf.train.Saver(restore_vars)
    opt_saver.restore(session, save_file)

# Class holding statistics
class Stats:
    def __init__(self):
        self.s = {}
    def add(self, stat_dict):
        for (k,v) in stat_dict.items():
            if k not in self.s:
                self.s[k] = []
            self.s[k].append(v)
    def n(self, name):
        return len(self.s[name] or [])
    def mean(self, name):
        return np.mean(self.s[name] or [0])
    def stddev_mean(self, name):
        # standard deviation in the sample mean.
        return math.sqrt(
            np.var(self.s[name] or [0]) / max(0.0001, (len(self.s[name]) - 1)))
    def str(self):
        return ', '.join(
            ["{}={:g}".format(k, np.mean(v or [0])) for k,v in self.s.items()])
    def clear(self):
        self.s = {}
    def summaries(self, tags):
        return [tf.Summary.Value(
            tag=k, simple_value=self.mean(v)) for k,v in tags.items()]

# Simple timer
class Timer:
    def __init__(self):
        self.last = time.time()
    def elapsed(self):
        # Return time since last call to 'elapsed()'
        t = time.time()
        e = t - self.last
        self.last = t
        return e

class TFProcess:
    def __init__(self, cpuonly=False):
        # Network structure
        self.RESIDUAL_FILTERS = 32
        self.RESIDUAL_BLOCKS = 4

        # model type: full precision (fp32) or mixed precision (fp16)
        self.model_dtype = tf.float32

        # Scale the loss to prevent gradient underflow
        self.loss_scale = 1 if self.model_dtype == tf.float32 else 128

        # L2 regularization parameter applied to weights.
        self.l2_scale = 1e-4

        # Set number of GPUs for training
        self.gpus_num = 1

        # For exporting
        self.weights = []

        # Output weight file with averaged weights
        self.swa_enabled = False

        # Net sampling rate (e.g 2 == every 2nd network).
        self.swa_c = 1

        # Take an exponentially weighted moving average over this
        # many networks. Under the SWA assumptions, this will reduce
        # the distance to the optimal value by a factor of 1/sqrt(n)
        self.swa_max_n = 16

        # Recalculate SWA weight batchnorm means and variances
        self.swa_recalc_bn = True

        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.8)
        config = tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True)
        self.session = tf.Session(config=config)

        self.training = tf.placeholder(tf.bool)
        self.global_step = tf.Variable(0, name='global_step', trainable=False)

        self.cpuonly = cpuonly

    def init(self, batch_size, macrobatch=1, gpus_num=None, logbase='leelalogs'):
        self.batch_size = batch_size
        self.macrobatch = macrobatch
        self.logbase = logbase
        # Input batch placeholders
        self.planes = tf.placeholder(tf.string, name='in_planes')
        self.probs = tf.placeholder(tf.string, name='in_probs')
        self.winner = tf.placeholder(tf.string, name='in_winner')

        # Mini-batches come as raw packed strings. Decode
        # into tensors to feed into network.
        planes = tf.decode_raw(self.planes, tf.uint8)
        probs = tf.decode_raw(self.probs, tf.float32)
        winner = tf.decode_raw(self.winner, tf.float32)

        planes = tf.cast(planes, self.model_dtype)

        planes = tf.reshape(planes, (batch_size, 18, 19*19))
        probs = tf.reshape(probs, (batch_size, 19*19 + 1))
        winner = tf.reshape(winner, (batch_size, 1))

        if gpus_num is None:
            gpus_num = self.gpus_num
        self.init_net(planes, probs, winner, gpus_num)

    def init_net(self, planes, probs, winner, gpus_num):
        self.y_ = probs   # (tf.float32, [None, 362])
        self.sx = tf.split(planes, gpus_num)
        self.sy_ = tf.split(probs, gpus_num)
        self.sz_ = tf.split(winner, gpus_num)
        self.batch_norm_count = 0
        self.reuse_var = None

        self.learning_rate = 0.01
        # You need to change the learning rate here if you are training
        # from a self-play training set, for example start with 0.005 instead.
        opt = tf.train.MomentumOptimizer(
            learning_rate=self.learning_rate, momentum=0.9, use_nesterov=True)

        opt = LossScalingOptimizer(opt, scale=self.loss_scale)

        # Construct net here.
        tower_grads = []
        tower_loss = []
        tower_policy_loss = []
        tower_mse_loss = []
        tower_reg_term = []
        tower_y_conv = []
        tower_z_conv = []
        tower_bn0_in = []
        tower_bn0_out = []
        tower_bn0_relu = []
        with tf.variable_scope("fp32_storage",
                               # this forces trainable variables to be stored as fp32
                               custom_getter=float32_variable_storage_getter):
            for i in range(gpus_num):
                print("gpus_num ", i)
                with tf.device("/gpu:%d" % i):
                    with tf.name_scope("tower_%d" % i):
                        loss, policy_loss, mse_loss, reg_term, y_conv, z_conv, bn0_in, bn0_out, bn0_relu = self.tower_loss(
                            self.sx[i], self.sy_[i], self.sz_[i])

                        # Reset batchnorm key to 0.
                        self.reset_batchnorm_key()

                        tf.get_variable_scope().reuse_variables()
                        with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
                            grads = opt.compute_gradients(loss)

                        tower_grads.append(grads)
                        tower_loss.append(loss)
                        tower_policy_loss.append(policy_loss)
                        tower_mse_loss.append(mse_loss)
                        tower_reg_term.append(reg_term)
                        tower_y_conv.append(y_conv)
                        tower_z_conv.append(z_conv)
                        tower_bn0_in.append(bn0_in)
                        tower_bn0_out.append(bn0_out)
                        tower_bn0_relu.append(bn0_relu)

        # Average gradients from different GPUs
        self.loss = tf.reduce_mean(tower_loss)
        self.policy_loss = tf.reduce_mean(tower_policy_loss)
        self.mse_loss = tf.reduce_mean(tower_mse_loss)
        self.reg_term = tf.reduce_mean(tower_reg_term)
        self.y_conv = tf.concat(tower_y_conv, axis=0)
        self.z_conv = tf.concat(tower_z_conv, axis=0)
        self.bn0_in = tf.concat(tower_bn0_in, axis=0)
        self.bn0_out = tf.concat(tower_bn0_out, axis=0)
        self.bn0_relu = tf.concat(tower_bn0_relu, axis=0)
        self.mean_grads = self.average_gradients(tower_grads)

        # Do swa after we contruct the net
        if self.swa_enabled is True:
            # Count of networks accumulated into SWA
            self.swa_count = tf.Variable(0., name='swa_count', trainable=False)
            # Count of networks to skip
            self.swa_skip = tf.Variable(self.swa_c, name='swa_skip',
                trainable=False)
            # Build the SWA variables and accumulators
            accum=[]
            load=[]
            n = self.swa_count
            for w in self.weights:
                name = w.name.split(':')[0]
                var = tf.Variable(
                    tf.zeros(shape=w.shape), name='swa/'+name, trainable=False)
                accum.append(
                    tf.assign(var, var * (n / (n + 1.)) + w * (1. / (n + 1.))))
                load.append(tf.assign(w, var))
            with tf.control_dependencies(accum):
                self.swa_accum_op = tf.assign_add(n, 1.)
            self.swa_load_op = tf.group(*load)

        # Accumulate gradients
        self.update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        total_grad=[]
        grad_ops=[]
        clear_var=[]
        self.grad_op_real = self.mean_grads
        for (g, v) in self.grad_op_real:
            if g is None:
                total_grad.append((g,v))
            name = v.name.split(':')[0]
            gsum = tf.get_variable(name='gsum/'+name,
                                   shape=g.shape,
                                   trainable=False,
                                   initializer=tf.zeros_initializer)
            total_grad.append((gsum, v))
            grad_ops.append(tf.assign_add(gsum, g))
            clear_var.append(gsum)
        # Op to compute gradients and add to running total in 'gsum/'
        self.grad_op = tf.group(*grad_ops)

        # Op to apply accmulated gradients
        self.train_op = opt.apply_gradients(total_grad)

        zero_ops = []
        for g in clear_var:
            zero_ops.append(
                tf.assign(g, tf.zeros(shape=g.shape, dtype=g.dtype)))
        # Op to clear accumulated gradients
        self.clear_op = tf.group(*zero_ops)

        # Op to increment global step counter
        self.step_op = tf.assign_add(self.global_step, 1)

        correct_prediction = \
            tf.equal(tf.argmax(self.y_conv, 1), tf.argmax(self.y_, 1))
        correct_prediction = tf.cast(correct_prediction, tf.float32)
        self.accuracy = tf.reduce_mean(correct_prediction)

        # Summary part
        self.test_writer = tf.summary.FileWriter(
            os.path.join(os.getcwd(),
                         self.logbase + "/test"), self.session.graph)
        self.train_writer = tf.summary.FileWriter(
            os.path.join(os.getcwd(),
                         self.logbase + "/train"), self.session.graph)

        # Build checkpoint saver
        self.saver = tf.train.Saver()

        # Initialize all variables
        self.session.run(tf.global_variables_initializer())

    def average_gradients(self, tower_grads):
        # Average gradients from different GPUs
        average_grads = []
        for grad_and_vars in zip(*tower_grads):
            grads = []
            for g, _ in grad_and_vars:
                expanded_g = tf.expand_dims(g, dim=0)
                grads.append(expanded_g)

            grad = tf.concat(grads, axis=0)
            grad = tf.reduce_mean(grad, reduction_indices=0)

            v = grad_and_vars[0][1]
            grad_and_var = (grad, v)
            average_grads.append(grad_and_var)
        return average_grads

    def tower_loss(self, x, y_, z_):
        y_conv, z_conv, bn0_in, bn0_out, bn0_relu = self.construct_net(x)

        # Cast the nn result back to fp32 to avoid loss overflow/underflow
        if self.model_dtype != tf.float32:
            y_conv = tf.cast(y_conv, tf.float32)
            z_conv = tf.cast(z_conv, tf.float32)

        # Calculate loss on policy head
        cross_entropy = \
            tf.nn.softmax_cross_entropy_with_logits(labels=y_,
                                                    logits=y_conv)
        policy_loss = tf.reduce_mean(cross_entropy)

        # Loss on value head
        mse_loss = \
            tf.reduce_mean(tf.squared_difference(z_, z_conv))

        # Regularizer
        reg_variables = tf.get_collection(tf.GraphKeys.WEIGHTS)
        reg_term = self.l2_scale * tf.add_n(
            [tf.cast(tf.nn.l2_loss(v), tf.float32) for v in reg_variables])

        # For training from a (smaller) dataset of strong players, you will
        # want to reduce the factor in front of self.mse_loss here.
        #loss = 1.0 * policy_loss + 1.0 * mse_loss + reg_term
        loss = 1.0 * mse_loss + reg_term

        print("")
        print("tower_loss")
        print("loss:        ", loss)
        print("policy_loss: ", policy_loss)
        print("mse_loss:    ", mse_loss)
        print("reg_term:    ", reg_term)
        print("y_conv:      ", y_conv)
        print("z_conv:      ", z_conv)
        print("")
        return loss, policy_loss, mse_loss, reg_term, y_conv, z_conv, bn0_in, bn0_out, bn0_relu

    def assign(self, var, values):
        try:
            self.session.run(tf.assign(var, values))
        except:
            print("Failed to assign {}: var shape {}, values shape {}".format(
                var.name, var.shape, values.shape))
            raise

    def replace_weights(self, new_weights):
        for e, weights in enumerate(self.weights):
            if isinstance(weights, str):
                weights = tf.get_default_graph().get_tensor_by_name(weights)
            if weights.name.endswith('/batch_normalization/beta:0'):
                # Batch norm beta is written as bias before the batch
                # normalization in the weight file for backwards
                # compatibility reasons.
                bias = tf.constant(new_weights[e], shape=weights.shape)
                # Weight file order: bias, means, variances
                var = tf.constant(new_weights[e + 2], shape=weights.shape)
                new_beta = tf.divide(bias, tf.sqrt(var + tf.constant(1e-5)))
                self.assign(weights, new_beta)
            elif weights.shape.ndims == 4:
                # Convolution weights need a transpose
                #
                # TF (kYXInputOutput)
                # [filter_height, filter_width, in_channels, out_channels]
                #
                # Leela/cuDNN/Caffe (kOutputInputYX)
                # [output, input, filter_size, filter_size]
                s = weights.shape.as_list()
                shape = [s[i] for i in [3, 2, 0, 1]]
                new_weight = tf.constant(new_weights[e], shape=shape)
                self.assign(weights, tf.transpose(new_weight, [2, 3, 1, 0]))
            elif weights.shape.ndims == 2:
                # Fully connected layers are [in, out] in TF
                #
                # [out, in] in Leela
                #
                s = weights.shape.as_list()
                shape = [s[i] for i in [1, 0]]
                new_weight = tf.constant(new_weights[e], shape=shape)
                self.assign(weights, tf.transpose(new_weight, [1, 0]))
            else:
                # Biases, batchnorm etc
                new_weight = tf.constant(new_weights[e], shape=weights.shape)
                self.assign(weights, new_weight)
        #This should result in identical file to the starting one
        #self.save_leelaz_weights('restored.txt')

    def restore(self, file):
        print("Restoring from {0}".format(file))
        optimistic_restore(self.session, file)

    def measure_loss(self, batch, training=False):
        print("weight value check, len", len(self.weights), 'training', training)

        for e, weights in enumerate(self.weights):
            if isinstance(weights, str):
                weights = tf.get_default_graph().get_tensor_by_name(weights)
                print('isinstance')
                print(e, weights.name, weights.shape)
            else:
                print(e, weights.name, weights.shape, weights.shape.ndims)
        print('')

        print("line 2 ", self.weights[0].shape)
        cc = self.session.run(self.weights[0])
        for i in range(3):
            for j in range(3):
                print(cc[i][j][0][0], end=' ')
            print('')
        print('')

        print("line 3 bias", self.weights[1].shape)
        cc = self.session.run(self.weights[1])
        for j in range(len(cc)):
            print(cc[j], end=' ')
        print('')

        print("line 4 mean", self.weights[2].shape)
        cc = self.session.run(self.weights[2])
        for j in range(len(cc)):
            print(cc[j], end=' ')
        print('')

        print("line 5 variance", self.weights[3].shape)
        cc = self.session.run(self.weights[3])
        for j in range(len(cc)):
            print(cc[j], end=' ')
        print('')

        #print("line 51 random %.9f" % self.session.run(self.weights[49]))

        # Measure loss over one batch. If training is true, also
        # accumulate the gradient and increment the global step.
        ops = [self.policy_loss, self.mse_loss, self.reg_term, self.accuracy, self.y_conv, self.z_conv, self.bn0_in, self.bn0_out, self.bn0_relu]
        if training:
            ops += [self.grad_op, self.step_op],
        print("input")
        print("planes_len:  ", len(batch[0]))
        '''
        # should be -1,18,19,19
        for num in range(0, 18):
            print("line ", num+1)
            for i in range(0,361):
                print(batch[0][num*361+i], end=' ')
            print("")
            print("")
        print("")
        '''
        print("probs_len:   ", len(batch[1]))
        '''
        # why there are 4 policy?
        for num in range(0, 4):
            print("line ", num+1)
            for i in range(0,19):
                for j in range(0,19):
                    print(batch[1][num*362+i*19+j], end=' ')
                print("")
            print("")
        print("")
        '''
        print("winner:      ", batch[2])
        print("")
        r = self.session.run(ops, feed_dict={self.training: training,
                           self.planes: batch[0],
                           self.probs: batch[1],
                           self.winner: batch[2]})
        print("output", len(r))
        for i in range(0, len(r)):
            print("r[",i,"] type: ", type(r[i]), "size: ", r[i].size, "shape: ", r[i].shape, "ndim: ", r[i].ndim, "dtype: ", r[i].dtype)
            if i==8: break
        print("")

        print("policy_loss: ", r[0])
        print("mse_loss:    ", r[1])
        print("reg_term:    ", r[2])
        print("accuracy:    ", r[3])

        print("y_conv:      ", r[4].shape)
        y = r[4][0]
        for i in range(0,19):
            for j in range(0,19):
                print('%+2.3f' % (y[i*19+j]), end=' ')
            print("")
        print('pass: %+2.3f' % (y[18*19+18+1]), end=' ')
        print("")

        for i in range(0,19):
            for j in range(0,19):
                print('%+2.3f' % np.exp(y[i*19+j]), end=' ')
            print("")
        print('pass: %+2.3f' % np.exp(y[18*19+18+1]), end=' ')
        print("")
        print('sum(np.exp(y): %+2.3f' % sum(np.exp(y)), end=' ')
        print("")

        y1 = (np.exp(y)/sum(np.exp(y)))
        print("")
        for i in range(0,19):
            for j in range(0,19):
                print('%3.0f' % (1000*y1[i*19+j]), end=' ')
            print("")
        print('pass: %3.0f' % (1000*y1[18*19+18+1]), end=' ')

        z_tmp = r[5][0]
        print("z_conv:      %.9f %.9f %.9f" % (z_tmp, math.tan(z_tmp), (1+math.tan(math.tan(z_tmp)))/2))
        print('')

        '''
        1 fp32_storage/bn0/batch_normalization/beta:0 (32,) 1
        2 fp32_storage/bn0/batch_normalization/moving_mean:0 (32,) 1
        3 fp32_storage/bn0/batch_normalization/moving_variance:0 (32,) 1
        '''
        bn0_beta = tf.get_default_graph().get_tensor_by_name('fp32_storage/bn0/batch_normalization/beta:0')
        bn0_mean = tf.get_default_graph().get_tensor_by_name('fp32_storage/bn0/batch_normalization/moving_mean:0')
        bn0_var = tf.get_default_graph().get_tensor_by_name('fp32_storage/bn0/batch_normalization/moving_variance:0')

        print('check bn...')

        bn0_beta = self.session.run(bn0_beta)
        print('bn0_beta', bn0_beta[0], bn0_beta.shape)
        bn0_mean = self.session.run(bn0_mean)
        print('bn0_mean', bn0_mean[0], bn0_mean.shape)
        bn0_var = self.session.run(bn0_var)
        print('bn0_var', bn0_var[0], bn0_var.shape)
        print('')

        prn_sz = 19
        # bn0_in (1, 19, 19, 32)
        print('input before bn0')
        print('r[6]', r[6].shape)
        arr = r[6][0,:,:,0]
        print('arr ', arr.shape)
        for i in range(0,prn_sz):
            for j in range(0,prn_sz):
                print('%.3f' % arr[i][j], end=' ')
            print("")
        print("")

        print('expect output after bn0, recalculate mean and var, but use input beta, training = True')
        arr_mean = np.mean(arr)
        print('new_mean', arr_mean)
        arr_var = np.var(arr)
        print('new_var ', arr_var)
        new_arr = (arr - arr_mean)/np.sqrt(arr_var) + bn0_beta[0]
        for i in range(0,prn_sz):
            for j in range(0,prn_sz):
                print('%.3f' % new_arr[i][j], end=' ')
            print("")
        print("")

        print('expect output after bn0, use input mean and var and beta')
        new_arr = (arr - bn0_mean[0])/np.sqrt(bn0_var[0]+1e-5) + bn0_beta[0]
        for i in range(0,prn_sz):
            for j in range(0,prn_sz):
                print('%.3f' % new_arr[i][j], end=' ')
            print("")
        print("")

        # bn0_out (1, 19, 19, 32)
        print('output after bn0')
        arr = r[7][0][:,:,0]
        for i in range(0,prn_sz):
            for j in range(0,prn_sz):
                print('%.3f' % arr[i][j], end=' ')
            print("")
        print("")

        # bn0_relu (1, 19, 19, 32)
        '''
        print('bn0_relu')
        arr = r[8][0]
        for i in range(0,19):
            for j in range(0,19):
                print('%3.3f' % arr[i][j][0], end=' ')
            print("")
        print("")
        '''

        # Google's paper scales mse by 1/4 to a [0,1] range, so we do the same here
        return {'policy': r[0], 'mse': r[1]/4., 'reg': r[2],
                'accuracy': r[3], 'total': r[0]+r[1]+r[2] }

    def process(self, train_data, test_data):
        info_steps=1
        stats = Stats()
        timer = Timer()
        while True:
            batch = next(train_data)
            # Measure losses and compute gradients for this batch.
            losses = self.measure_loss(batch, training=False)
            print("losses: ", losses)
            print("break mandatory")
            break
            stats.add(losses)
            # fetch the current global step.
            steps = tf.train.global_step(self.session, self.global_step)
            if steps % self.macrobatch == (self.macrobatch-1):
                # Apply the accumulated gradients to the weights.
                self.session.run([self.train_op])
                # Clear the accumulated gradient.
                self.session.run([self.clear_op])

            if steps % info_steps == 0:
                speed = info_steps * self.batch_size / timer.elapsed()
                print("lr {}, step {}, policy={:g} mse={:g} reg={:g} total={:g} ({:g} pos/s)".format(
                    self.learning_rate, steps, stats.mean('policy'), stats.mean('mse'), stats.mean('reg'),
                    stats.mean('total'), speed))
                summaries = stats.summaries({'Policy Loss': 'policy',
                                             'MSE Loss': 'mse'})
                self.train_writer.add_summary(
                    tf.Summary(value=summaries), steps)
                stats.clear()
                break

            if steps % 1 == 0:
                test_stats = Stats()
                test_batches = 200 # reduce sample mean variance by ~28x
                for _ in range(0, test_batches):
                    test_batch = next(test_data)
                    losses = self.measure_loss(test_batch, training=False)
                    test_stats.add(losses)
                summaries = test_stats.summaries({'Policy Loss': 'policy',
                                                  'MSE Loss': 'mse',
                                                  'Accuracy': 'accuracy'})
                self.test_writer.add_summary(tf.Summary(value=summaries), steps)
                print("step {}, policy={:g} training accuracy={:g}%, mse={:g}".\
                    format(steps, test_stats.mean('policy'),
                        test_stats.mean('accuracy')*100.0,
                        test_stats.mean('mse')))

                # Write out current model and checkpoint
                '''
                path = os.path.join(os.getcwd(), "leelaz-model")
                save_path = self.saver.save(self.session, path, global_step=steps)
                print("Model saved in file: {}".format(save_path))
                leela_path = path + "-" + str(steps) + ".txt"
                self.save_leelaz_weights(leela_path)
                print("Leela weights saved to {}".format(leela_path))
                # Things have likely changed enough
                # that stats are no longer valid.

                if self.swa_enabled:
                    self.save_swa_network(steps, path, leela_path, train_data)

                #save_path = self.saver.save(self.session, path, global_step=steps)
                #print("Model saved in file: {}".format(save_path))
                '''

            if steps == 1:
                while True:
                    batch = next(train_data)
                break

    def save_leelaz_weights(self, filename):
        with open(filename, "w") as file:
            # Version tag
            file.write("1")
            for e,weights in enumerate(self.weights):
                # Newline unless last line (single bias)
                file.write("\n")
                work_weights = None
                if weights.name.endswith('/batch_normalization/beta:0'):
                    # Batch norm beta needs to be converted to biases before
                    # the batch norm for backwards compatibility reasons
                    var_key = weights.name.replace('beta', 'moving_variance')
                    var = tf.get_default_graph().get_tensor_by_name(var_key)
                    work_weights = tf.multiply(weights,
                                               tf.sqrt(var + tf.constant(1e-5)))
                elif weights.shape.ndims == 4:
                    # Convolution weights need a transpose
                    #
                    # TF (kYXInputOutput)
                    # [filter_height, filter_width, in_channels, out_channels]
                    #
                    # Leela/cuDNN/Caffe (kOutputInputYX)
                    # [output, input, filter_size, filter_size]
                    work_weights = tf.transpose(weights, [3, 2, 0, 1])
                elif weights.shape.ndims == 2:
                    # Fully connected layers are [in, out] in TF
                    #
                    # [out, in] in Leela
                    #
                    work_weights = tf.transpose(weights, [1, 0])
                else:
                    # Biases, batchnorm etc
                    work_weights = weights
                nparray = work_weights.eval(session=self.session)
                wt_str = [str(wt) for wt in np.ravel(nparray)]
                if e==21:
                    print('22')
                    print(nparray.shape, nparray.size)
                    print('%.15f' % nparray[1])
                    #print(wt_str)
                file.write(" ".join(wt_str))

    def get_batchnorm_key(self):
        result = "bn" + str(self.batch_norm_count)
        self.batch_norm_count += 1
        return result

    def reset_batchnorm_key(self):
        self.batch_norm_count = 0
        self.reuse_var = True

    def add_weights(self, var):
        if self.reuse_var is None:
            if var.name[-11:] == "fp16_cast:0":
                name = var.name[:-12] + ":0"
                var = tf.get_default_graph().get_tensor_by_name(name)
            # All trainable variables should be stored as fp32
            assert var.dtype.base_dtype == tf.float32
            self.weights.append(var)

    def batch_norm(self, net, trainable):
        # The weights are internal to the batchnorm layer, so apply
        # a unique scope that we can store, and use to look them back up
        # later on.
        scope = self.get_batchnorm_key()
        with tf.variable_scope(scope,
                               custom_getter=float32_variable_storage_getter):
            if self.cpuonly:
                net = tf.layers.batch_normalization(
                        net,
                        epsilon=1e-5, 
                        axis=3, fused=True,
                        center=True, 
                        scale=False,
                        beta_initializer=tf.constant_initializer(0.0),
                        #moving_mean_initializer=tf.constant_initializer(mean),
                        #moving_variance_initializer=tf.constant_initializer(var),
                        training=self.training,
                        trainable=trainable,
                        reuse=self.reuse_var)
            else:
                net = tf.layers.batch_normalization(
                        net,
                        epsilon=1e-5, axis=1, fused=True,
                        center=True, scale=False,
                        training=self.training,
                        trainable=trainable,
                        reuse=self.reuse_var)


        for v in ['beta', 'moving_mean', 'moving_variance' ]:
            name = "fp32_storage/" + scope + '/batch_normalization/' + v + ':0'
            var = tf.get_default_graph().get_tensor_by_name(name)
            self.add_weights(var)

        return net

    def conv_block(self, inputs, filter_size, input_channels, output_channels, name, trainable):
        W_conv = weight_variable(
            name,
            [filter_size, filter_size, input_channels, output_channels],
            self.model_dtype, trainable)

        self.add_weights(W_conv)

        net = inputs
        print("    conv_block input ", net)
        net = conv2d(net, W_conv, self.cpuonly)
        print("    conv_block conv2d ", net)
        net = self.batch_norm(net, trainable)
        print("    conv_block batch_norm ", net)
        net = tf.nn.relu(net)
        print("    conv_block relu ", net)
        return net

    def conv_first_block(self, inputs, filter_size, input_channels, output_channels, name, trainable):
        W_conv = weight_variable(
            name,
            [filter_size, filter_size, input_channels, output_channels],
            self.model_dtype, trainable)

        self.add_weights(W_conv)

        net = inputs
        net = conv2d(net, W_conv, self.cpuonly)
        bn0_in = net
        net = self.batch_norm(net, trainable)
        bn0_out = net
        net = tf.nn.relu(net)
        bn0_relu = net
        return net, bn0_in, bn0_out, bn0_relu

    def conv_block_value(self, inputs, filter_size, input_channels, output_channels, name, trainable):
        W_conv = weight_variable(
            name,
            [filter_size, filter_size, input_channels, output_channels],
            self.model_dtype, trainable)

        self.add_weights(W_conv)

        net = inputs
        net = conv2d(net, W_conv, self.cpuonly)
        bn0_in = net
        net = self.batch_norm(net, trainable)
        bn0_out = net
        net = tf.nn.relu(net)
        #return net
        return net, bn0_in, bn0_out

    def residual_block(self, inputs, channels, name, trainable):
        net = inputs
        orig = tf.identity(net)

        # First convnet weights
        W_conv_1 = weight_variable(name + "_conv_1", [3, 3, channels, channels],
                                   self.model_dtype, trainable)
        self.add_weights(W_conv_1)

        net = conv2d(net, W_conv_1, self.cpuonly)
        net = self.batch_norm(net, trainable)
        net = tf.nn.relu(net)

        # Second convnet weights
        W_conv_2 = weight_variable(name + "_conv_2", [3, 3, channels, channels],
                                   self.model_dtype, trainable)
        self.add_weights(W_conv_2)

        net = conv2d(net, W_conv_2, self.cpuonly)
        net = self.batch_norm(net, trainable)
        net = tf.add(net, orig)
        net = tf.nn.relu(net)

        return net

    def construct_net(self, planes):
        # NCHW format
        # batch, 18 channels, 19 x 19
        x_planes = tf.reshape(planes, [-1, 18, 19, 19])
        print("x_planes", x_planes.shape)
        if self.cpuonly:
            x_planes = tf.transpose(x_planes, perm=[0, 2, 3, 1]) #x_planes = tf.reshape(planes, [-1, 19, 19, 18])
            print("x_planes", x_planes)
            print("x_planes", x_planes.shape)

        print("construct_net input:", x_planes)
        # Input convolution
        flow, bn0_in, bn0_out, bn0_relu = self.conv_first_block(x_planes, filter_size=3,
                               input_channels=18,
                               output_channels=self.RESIDUAL_FILTERS,
                               name="first_conv", trainable=False)
        print("construct_net input->conv:", flow)
        # Residual tower
        for i in range(0, self.RESIDUAL_BLOCKS):
            block_name = "res_" + str(i)
            flow = self.residual_block(flow, self.RESIDUAL_FILTERS,
                                       name=block_name, trainable=False)
        print("construct_net 4*resudial:", flow)

        # Policy head
        conv_pol = self.conv_block(flow, filter_size=1,
                                   input_channels=self.RESIDUAL_FILTERS,
                                   output_channels=2,
                                   name="policy_head", trainable=False)
        print("construct_net policy head:", conv_pol.shape)
        conv_pol = tf.transpose(conv_pol, perm=[0, 3, 1, 2])
        print("construct_net policy head:", conv_pol.shape)
        h_conv_pol_flat = tf.reshape(conv_pol, [-1, 2 * 19 * 19])
        print("construct_net policy head:", h_conv_pol_flat.shape)
        W_fc1 = weight_variable("w_fc_1", [2 * 19 * 19, (19 * 19) + 1], self.model_dtype, trainable=False)
        b_fc1 = bias_variable("b_fc_1", [(19 * 19) + 1], self.model_dtype, trainable=False)
        self.add_weights(W_fc1)
        self.add_weights(b_fc1)
        h_fc1 = tf.add(tf.matmul(h_conv_pol_flat, W_fc1), b_fc1)
        print("construct_net h_fc1:", h_fc1.shape)

        # Value head
        conv_val, v_in, v_out = self.conv_block_value(flow, filter_size=1,
                                   input_channels=self.RESIDUAL_FILTERS,
                                   output_channels=1,
                                   name="value_head", trainable=True)
        print("construct_net value head:", conv_val.shape)
        print("construct_net value head:", v_in.shape)
        print("construct_net value head:", v_out.shape)
        h_conv_val_flat = tf.reshape(conv_val, [-1, 19 * 19])
        W_fc2 = weight_variable("w_fc_2", [19 * 19, 256], self.model_dtype, trainable=True)
        b_fc2 = bias_variable("b_fc_2", [256], self.model_dtype, trainable=True)
        self.add_weights(W_fc2)
        self.add_weights(b_fc2)
        h_fc2 = tf.nn.relu(tf.add(tf.matmul(h_conv_val_flat, W_fc2), b_fc2))
        print("construct_net h_fc2:", h_fc2.shape)
        W_fc3 = weight_variable("w_fc_3", [256, 1], self.model_dtype, trainable=True)
        b_fc3 = bias_variable("b_fc_3", [1], self.model_dtype, trainable=True)
        self.add_weights(W_fc3)
        self.add_weights(b_fc3)
        h_fc3 = tf.nn.tanh(tf.add(tf.matmul(h_fc2, W_fc3), b_fc3))
        print("construct_net h_fc3:", h_fc3.shape)

        return h_fc1, h_fc3, bn0_in, bn0_out, bn0_relu
        #return h_fc1, h_fc3, v_in, v_out, bn0_relu

    def snap_save(self):
        # Save a snapshot of all the variables in the current graph.
        if not hasattr(self, 'save_op'):
            save_ops = []
            rest_ops = []
            for var in self.weights:
                if isinstance(var, str):
                    var = tf.get_default_graph().get_tensor_by_name(var)
                name = var.name.split(':')[0]
                v = tf.Variable(var, name='save/'+name, trainable=False)
                save_ops.append(tf.assign(v, var))
                rest_ops.append(tf.assign(var, v))
            self.save_op = tf.group(*save_ops)
            self.restore_op = tf.group(*rest_ops)
        self.session.run(self.save_op)

    def snap_restore(self):
        # Restore variables in the current graph from the snapshot.
        self.session.run(self.restore_op)

    def save_swa_network(self, steps, path, leela_path, data):
        # Sample 1 in self.swa_c of the networks. Compute in this way so
        # that it's safe to change the value of self.swa_c
        rem = self.session.run(tf.assign_add(self.swa_skip, -1))
        if rem > 0:
            return
        self.swa_skip.load(self.swa_c, self.session)

        # Add the current weight vars to the running average.
        num = self.session.run(self.swa_accum_op)

        if self.swa_max_n != None:
            num = min(num, self.swa_max_n)
            self.swa_count.load(float(num), self.session)

        swa_path = path + "-swa-" + str(int(num)) + "-" + str(steps) + ".txt"

        # save the current network.
        self.snap_save()
        # Copy the swa weights into the current network.
        self.session.run(self.swa_load_op)
        if self.swa_recalc_bn:
            print("Refining SWA batch normalization")
            for _ in range(200):
                batch = next(data)
                self.session.run(
                    [self.loss, self.update_ops],
                    feed_dict={self.training: True,
                               self.planes: batch[0], self.probs: batch[1],
                               self.winner: batch[2]})

        self.save_leelaz_weights(swa_path)
        # restore the saved network.
        self.snap_restore()

        print("Wrote averaged network to {}".format(swa_path))

# Unit tests for TFProcess.
def gen_block(size, f_in, f_out):
    return [ [1.1] * size * size * f_in * f_out, # conv
             [-.1] * f_out,  # bias weights
             [-.2] * f_out,  # batch norm mean
             [-.3] * f_out ] # batch norm var

class TFProcessTest(unittest.TestCase):
    def test_can_replace_weights(self):
        tfprocess = TFProcess()
        tfprocess.init(batch_size=1)
        # use known data to test replace_weights() works.
        data = gen_block(3, 18, tfprocess.RESIDUAL_FILTERS) # input conv
        for _ in range(tfprocess.RESIDUAL_BLOCKS):
            data.extend(gen_block(3,
                tfprocess.RESIDUAL_FILTERS, tfprocess.RESIDUAL_FILTERS))
            data.extend(gen_block(3,
                tfprocess.RESIDUAL_FILTERS, tfprocess.RESIDUAL_FILTERS))
        # policy
        data.extend(gen_block(1, tfprocess.RESIDUAL_FILTERS, 2))
        data.append([0.4] * 2*19*19 * (19*19+1))
        data.append([0.5] * (19*19+1))
        # value
        data.extend(gen_block(1, tfprocess.RESIDUAL_FILTERS, 1))
        data.append([0.6] * 19*19 * 256)
        data.append([0.7] * 256)
        data.append([0.8] * 256)
        data.append([0.9] * 1)
        tfprocess.replace_weights(data)

if __name__ == '__main__':
    unittest.main()

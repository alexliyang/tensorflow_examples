#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import tensorflow as tf
from arch.layers import conv2d_bn, separable_conv2d, max_pool, Kumar_initializer

#https://arxiv.org/pdf/1610.02357.pdf

def entry_block(
        inputs,
        n_filters,
        n_repeat = 2,
        conv_size = 3,
        pool_size = 3,
        init_activation = tf.nn.relu,
        kernel_init = Kumar_initializer(),
        is_training = False,
        name = "entry_block"):
    
    with tf.variable_scope(name):
        shortcut = conv2d_bn(
                inputs, size=1, n_filters=n_filters,
                stride=2, activation=None,
                is_training=is_training,
                kernel_init=kernel_init,
                name="shortcut")
        x = inputs
        for r in range(n_repeat):
            if r == 0:
                activation = init_activation
            else:
                activation = tf.nn.relu
            if activation is not None:
                x = activation(x)
            x = separable_conv2d(
                    x, size=conv_size, n_filters=n_filters,
                    stride=1, activation=None,
                    depth_kernel_init=kernel_init,
                    pointwise_kernel_init=kernel_init,
                    name="separable_conv_"+str(r))
            x = tf.layers.batch_normalization(x, training=is_training, name="bn_"+str(r))
        x = max_pool(x, size=pool_size, stride=2, name="max_pool")
        outputs = tf.add(x, shortcut, name="add")
    return outputs
        

def entry_module(
        inputs,
        conv_size = 3,
        pool_size = 3,
        n_filters = [128, 256, 728],
        is_training = False,        
        kernel_init = Kumar_initializer(),
        name = "entry_module"
        ):
    with tf.variable_scope(name):
        x = inputs
        for s in range(len(n_filters)):
            init_act = None if s == 0 else tf.nn.relu
            x = entry_block(
                    x,
                    n_filters=n_filters[s],
                    conv_size=conv_size,
                    pool_size=pool_size,
                    init_activation=init_act,
                    kernel_init=kernel_init,
                    is_training=is_training,
                    name="entry_block_"+str(s))
    return x


def middle_module(
        inputs,
        size = 3,
        n_filters = 728,
        n_repeat = 8,
        block_size = 3,
        is_training = False,        
        kernel_init = Kumar_initializer(),
        name = "middle_module"
        ):
    x = inputs
    with tf.variable_scope(name):
        for r in range(n_repeat):
            shortcut = tf.identity(x, name="shortcut_"+str(r))
            for s in range(block_size):
                x = tf.nn.relu(x, name="relu_"+str(r)+"_"+str(s))
                x = separable_conv2d(
                        x, size=size, n_filters=n_filters,
                        stride=1, activation=None,
                        depth_kernel_init=kernel_init,
                        pointwise_kernel_init=kernel_init,
                        name="separable_conv_"+str(r)+"_"+str(s))
                x = tf.layers.batch_normalization(x, training=is_training, name="bn_"+str(r)+"_"+str(s))
            x = tf.add(x, shortcut, name="add_"+str(r))
    return x


def exit_module(
        inputs,
        size = 3,
        n_filters_1 = [728, 1024],
        n_filters_2 = [1536, 2048],
        pool_size = 3,
        is_training = False,        
        kernel_init = Kumar_initializer(),
        name = "exit_module"):
    with tf.variable_scope(name):    
        shortcut = conv2d_bn(
                inputs, size=1, n_filters=n_filters_1[-1],
                stride=2, activation=None,
                is_training=is_training,
                kernel_init=kernel_init,
                name="shortcut")

        x = inputs
        for r in range(len(n_filters_1)):
            x = tf.nn.relu(x, name="relu_1_"+str(r))
            x = separable_conv2d(
                    x, size=size, n_filters=n_filters_1[r],
                    stride=1, activation=None,
                    depth_kernel_init=kernel_init,
                    pointwise_kernel_init=kernel_init,
                    name="separable_conv_1_"+str(r))
            x = tf.layers.batch_normalization(x, training=is_training, name="bn_1_"+str(r))
        x = max_pool(x, size=pool_size, stride=2, name="max_pool")
        x = tf.add(x, shortcut, name="add_1")
            
        for r in range(len(n_filters_2)):
            x = separable_conv2d(
                    x, size=size, n_filters=n_filters_2[r],
                    stride=1, activation=None,
                    depth_kernel_init=kernel_init,
                    pointwise_kernel_init=kernel_init,
                    name="separable_conv_2_"+str(r))
            x = tf.layers.batch_normalization(x, training=is_training, name="bn_2_"+str(r))
            x = tf.nn.relu(x, name="relu_2_"+str(r))
    return x
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import tensorflow as tf
from functools import partial
from arch.initializers import variance_scaling_initializer_multi



truncated_n_seeded = partial(tf.truncated_normal_initializer, seed=42)
"""The seeded version of the truncated normal initializer.
"""    


#variance_s_seeded = partial(tf.variance_scaling_initializer, seed=42)

glorot_u_seeded = partial(tf.glorot_uniform_initializer, seed=42)

def He_initializer(seed=42):
    return tf.contrib.layers.variance_scaling_initializer(factor=2.0, mode='FAN_IN', uniform=False, seed=seed)
    #return tf.variance_scaling_initializer(scale=2.0, mode='fan_in', distribution='normal', seed=seed)

def Kumar_initializer(activation="relu", mode="FAN_AVG", seed=42):
    """Kumar's weight initializer, i.e. a truncated normal without scale
       variance initialized with activation specific standard deviation. 
       See https://arxiv.org/pdf/1704.08863.pdf
    Args:
        activation: A string representing the output activation of the layer 
            the weights are used for.
        seed: Random seed number.
    Returns:
        A weight initializer.
    """    
    
    if activation is None:
        factor = 1.0
    elif activation == "relu":
        # stdev = sqrt(2.0/N) for normal, or sqrt(1.3*2.0/N) for truncated
        factor = 2.0
    elif activation == "sigmoid":
        # stdev = 3.6/sqrt(N) = sqrt(12.96/N) for normal, or sqrt(1.3*12.96/N) for truncated
        factor = 12.96
    elif activation == "tanh":
        # stdev = sqrt(1/N) for normal, or sqrt(1.3/N) for truncated
        factor = 1.0
    else:
        factor = 1.0
        
#    mode = "FAN_AVG" # should be "FAN_IN" but it fails for the first conv2d on the single-channel input, sqrt(2/(3*3)) is too large
    uniform = False
    return tf.contrib.layers.variance_scaling_initializer(factor=factor,
                                                          mode=mode,
                                                          uniform=uniform,
                                                          seed=seed)


def Kumar_initializer_multi(activation="relu", mode="FAN_AVG", C=[1,1], seed=42):
    """Kumar's weight initializer, i.e. a truncated normal without scale
       variance initialized with activation specific standard deviation. 
       See https://arxiv.org/pdf/1704.08863.pdf
    Args:
        activation: A string representing the output activation of the layer 
            the weights are used for.
        seed: Random seed number.
    Returns:
        A weight initializer.
    """    
    
    if activation is None:
        factor = 1.0
    elif activation == "relu":
        # stdev = sqrt(2.0/N) for normal, or sqrt(1.3*2.0/N) for truncated
        factor = 2.0
    elif activation == "sigmoid":
        # stdev = 3.6/sqrt(N) = sqrt(12.96/N) for normal, or sqrt(1.3*12.96/N) for truncated
        factor = 12.96
    elif activation == "tanh":
        # stdev = sqrt(1/N) for normal, or sqrt(1.3/N) for truncated
        factor = 1.0
    else:
        factor = 1.0
        
#    mode = "FAN_AVG" # should be "FAN_IN" but it fails for the first conv2d on the single-channel input, sqrt(2/(3*3)) is too large
    uniform = False
    return variance_scaling_initializer_multi(
            factor=factor,
            mode=mode,
            C=C,
            uniform=uniform,
            seed=seed)


def conv2d(inputs, size, n_filters,
           stride = 1,
           activation = tf.nn.relu,
           kernel_init = Kumar_initializer(),
           bias_init = tf.zeros_initializer(),
           name = "conv2d"):
    """Creates a 2d convolutional layer.
    Args:
        inputs: A tensor representing the inputs.
        size: An integer representing the kernel size.
        n_filters: An integer representing the number of filters.
        stride: An integer representing the stride size.
        activation: An activation function to be applied.
        kernel_init: A function used for initializing the kernel.
        bias_init: A function used for initializing the bias.
        name: A string representing the name of the layer.
    Returns:
        A tensor representing the layer.
    """    
    in_filt = inputs.shape[3].value    
    with tf.variable_scope(name):
        weights = tf.get_variable(shape=[size,size,in_filt,n_filters], initializer=kernel_init, name="weight")
        biases = tf.get_variable(shape=[n_filters], initializer=bias_init, name="bias")
        conv = tf.nn.conv2d(inputs, weights, strides=[1,stride,stride,1], padding="SAME", name="conv")
        bias_add = tf.nn.bias_add(conv, biases, name="bias_add")
        if activation is None:
            outputs = bias_add
        else:
            outputs = activation(bias_add, name="activation")
    return outputs


def conv2d_bn(inputs, size, n_filters,
              stride = 1,
              activation = tf.nn.relu,
              kernel_init = Kumar_initializer(),
              bias_init = tf.zeros_initializer(),
              bn_order = "after",
              is_training = False,
              name = "conv2d"):
    """Creates a 2d convolutional layer with batch normalization.
    Args:
        inputs: A tensor representing the inputs.
        size: An integer representing the kernel size.
        n_filters: An integer representing the number of filters.
        stride: An integer representing the stride size.
        activation: An activation function to be applied.
        kernel_init: A function used for initializing the kernel.
        bias_init: A function used for initializing the bias.
        bn_order: A string indicating when to apply batch normalization. Two
            options are available: "before", or "after" the activation.
        is_training: A boolean or a TensorFlow boolean scalar tensor for
            indicating training or testing mode.
        name: A string representing the name of the layer.
    Returns:
        A tensor representing the layer.
    """    
    in_filt = inputs.shape[3].value    
    with tf.variable_scope(name):
        weights = tf.get_variable(shape=[size,size,in_filt,n_filters], initializer=kernel_init, name="weight")
        biases = tf.get_variable(shape=[n_filters], initializer=bias_init, name="bias")
        conv = tf.nn.conv2d(inputs, weights, strides=[1,stride,stride,1], padding="SAME", name="conv")
        outputs = tf.nn.bias_add(conv, biases, name="bias_add")
        if bn_order == "before":
            outputs = tf.layers.batch_normalization(outputs, training=is_training, name="bn")
        if activation is not None:
            outputs = activation(outputs, name="activation")
        if bn_order == "after":
            outputs = tf.layers.batch_normalization(outputs, training=is_training, name="bn")
    return outputs


def max_pool(inputs, size=2, stride=2, padding="SAME", name="max_pool"):
    return tf.nn.max_pool(inputs, ksize=[1,size,size,1], strides=[1,stride,stride,1], padding=padding, name=name)


def avg_pool(inputs, size=2, stride=2, padding="SAME", name="avg_pool"):
    return tf.nn.avg_pool(inputs, ksize=[1,size,size,1], strides=[1,stride,stride,1], padding=padding, name=name)


def flatten(inputs, name="flatten"):
    """Creates a flattening layer.
    Args:
        inputs: A tensor representing the inputs.
        name: A string representing the name of the layer.
    Returns:
        A tensor representing the layer.
    """    
    return tf.reshape(inputs, [-1, np.prod(inputs.get_shape()[1:].as_list())], name=name)


def dense(inputs, n_units,
          activation = tf.nn.relu,
          kernel_init = Kumar_initializer(),
          bias_init = tf.zeros_initializer(),
          name = "dense"):
    """Creates a fully-connected dense layer.
    Args:
        inputs: A tensor representing the inputs.
        n_units: An integer representing the number of units.
        activation: An activation function to be applied.
        kernel_init: A function used for initializing the kernel.
        bias_init: A function used for initializing the bias.
        name: A string representing the name of the layer.
    Returns:
        A tensor representing the layer.
    """    
    with tf.variable_scope(name):
        weights = tf.get_variable(shape=[inputs.shape[1].value, n_units], initializer=kernel_init, name="weight")
        biases = tf.get_variable(shape=[n_units], initializer=bias_init, name="bias")
        fc = tf.matmul(inputs, weights, name="matmul")
        bias_add = tf.nn.bias_add(fc, biases, name="bias_add")
        if activation is None:
            outputs = bias_add
        else:
            outputs = activation(bias_add, name="activation")
    return outputs
    

def dense_bn(inputs, n_units,
             activation = tf.nn.relu,
             kernel_init = Kumar_initializer(),
             bias_init = tf.zeros_initializer(),
             bn_order = "after",
             is_training = False,
             name = "dense"):
    """Creates a fully-connected dense layer with batch normalization.
    Args:
        inputs: A tensor representing the inputs.
        n_units: An integer representing the number of units.
        activation: An activation function to be applied.
        kernel_init: A function used for initializing the kernel.
        bias_init: A function used for initializing the bias.
        bn_order: A string indicating when to apply batch normalization. Two
            options are available: "before", or "after" the activation.
        is_training: A boolean or a TensorFlow boolean scalar tensor for
            indicating training or testing mode.
        name: A string representing the name of the layer.
    Returns:
        A tensor representing the layer.
    """    
    with tf.variable_scope(name):
        weights = tf.get_variable(shape=[inputs.shape[1].value, n_units], initializer=kernel_init, name="weight")
        biases = tf.get_variable(shape=[n_units], initializer=bias_init, name="bias")
        fc = tf.matmul(inputs, weights, name="matmul")
        outputs = tf.nn.bias_add(fc, biases, name="bias_add")
        if bn_order == "before":
            outputs = tf.layers.batch_normalization(outputs, training=is_training, name="bn")
        if activation is not None:
            outputs = activation(outputs, name="activation")
        if bn_order == "after":
            outputs = tf.layers.batch_normalization(outputs, training=is_training, name="bn")
    return outputs


## initialization
## https://arxiv.org/pdf/1709.02956.pdf
## batch norm: http://torch.ch/blog/2016/02/04/resnets.html
def residual_block(inputs, n_filters,
                   stride = 1,
                   activation = tf.nn.relu,
                   kernel_init = Kumar_initializer(mode="FAN_IN"),
                   is_training = False,
                   name = "residual_block"):   
    with tf.variable_scope(name):        
        if (inputs.shape[3] != n_filters) or (stride != 1):
            shortcut = conv2d(
                        inputs, size=1, n_filters=n_filters,
                        stride = stride, activation = None,
                        kernel_init = kernel_init,
                        name = "shortcut_projection")
        else:
            shortcut = tf.identity(inputs, name="shortcut")
        
        x = conv2d(
                inputs, size=3, n_filters = n_filters,
                stride = stride,
                activation = None,
                kernel_init = kernel_init,
                name = "conv2d_1")
        x = tf.layers.batch_normalization(x, training=is_training, name="bn_1")
        x = activation(x, name="activation_1")
        
        x = conv2d(
                x, size=3, n_filters = n_filters,
                stride = 1,
                activation = None,
                kernel_init = kernel_init,
                name = "conv2d_2")
        x = tf.layers.batch_normalization(x, training=is_training, name="bn_2")

        x = tf.add(x, shortcut, name="add")
        x = activation(x, name="activation_2")
    return x


def residual_layer(inputs, n_filters, n_blocks, 
                   stride = 1,
                   is_training = False,
                   kernel_init = Kumar_initializer(mode="FAN_IN"),
                   name = "residual_layer"
                   ):
    with tf.variable_scope(name):
        x = residual_block(inputs, n_filters = n_filters,
                           stride = stride,
                           is_training = is_training,
                           kernel_init = kernel_init,
                           name = "residual_block_0")
        
        for n in range(1, n_blocks):
            x = residual_block(x, n_filters = n_filters,
                               stride = 1,
                               is_training = is_training,
                               kernel_init = kernel_init,
                               name = "residual_block_" + str(n+1))
    return x


def inception_layer(inputs,
                    n_filters_1x1 = 32,
                    n_filters_3x3 = 32,
                    n_reduce_3x3 = 16,
                    n_filters_5x5 = 32,
                    n_reduce_5x5 = 16,
                    n_filters_pool = 32,
                    is_training = False,
#                    kernel_init = Kumar_initializer(mode="FAN_IN"),
                    mode = "FAN_IN",
                    mode_reduce = "FAN_AVG",
                    name = "inception_layer"
                    ):
    with tf.variable_scope(name):
        x_1x1_1 = conv2d(
                    inputs, size=1, n_filters = n_filters_1x1,
                    stride = 1,
                    activation = None,
                    kernel_init = Kumar_initializer(mode=mode),
                    name = "conv2d_1x1_1")
        
        x_1x1_2 = conv2d(
                    inputs, size=1, n_filters = n_reduce_3x3,
                    stride = 1,
                    activation = tf.nn.relu,
                    kernel_init = Kumar_initializer(mode=mode),
                    name = "conv2d_1x1_2")
        
        x_1x1_3 = conv2d(
                    inputs, size=1, n_filters = n_reduce_5x5,
                    stride = 1,
                    activation = tf.nn.relu,
                    kernel_init = Kumar_initializer(mode=mode),
                    name = "conv2d_1x1_3")
        
        x_3x3 = conv2d(
                    x_1x1_2, size=3, n_filters = n_filters_3x3,
                    stride = 1,
                    activation = None,
                    kernel_init = Kumar_initializer(mode=mode_reduce),
                    name = "conv2d_3x3")
        
        x_5x5 = conv2d(
                    x_1x1_3, size=5, n_filters = n_filters_5x5,
                    stride = 1,
                    activation = None,
                    kernel_init = Kumar_initializer(mode=mode_reduce),
                    name = "conv2d_5x5")
        
        maxpool1 = max_pool(inputs, size=3, stride=1, name="max_pool")
        x_1x1_4 = conv2d(
                    maxpool1, size=1, n_filters = n_filters_pool,
                    stride = 1,
                    activation = None,
                    kernel_init = Kumar_initializer(mode=mode),
                    name = "conv2d_1x1_4")
        
        inception = tf.nn.relu(tf.concat([x_1x1_1,x_3x3,x_5x5,x_1x1_4], axis=3))
        
    return inception
                    
        
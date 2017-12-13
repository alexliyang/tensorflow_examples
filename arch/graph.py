#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tensorflow as tf
from arch.layers import conv2d, conv2d_bn, max_pool, flatten, dense, dense_bn
from arch.layers import variance_s_seeded, truncated_n_seeded, residual_layer
from arch.layers import batch_norm_activation


def mnist_sequential_dbn2d1(x, drop_rate=0.5):
    """Creates sequential neural network for MNIST. The network contains 2 
        batch-normalized fully-connected dense layers. Dropout layers are used 
        for regularization. The output  probabilities are generated by one 
        dense layer followed by a softmax function.
    Args:
        x: A tensor representing the input.
    Returns:
        A tuple containing the layers of the network graph and additional
        placeholders if any. Layers are represented as list of named tuples.
    """    
    layers = []
    variables = []

    training = tf.placeholder(tf.bool, name="training")
    variables.append(("training", training))

    # flatten
    flat = flatten(x, name="flatten")
    layers.append(("flatten", flat))

    # fc1
    fc1 = dense_bn(flat, n_units=256, is_training=training, name="fc1")
    layers.append(("fc1", fc1))
    
    # dropout1
    dropout1 = tf.layers.dropout(fc1, rate=drop_rate, training=training, seed=42, name="dropout1")
    layers.append(("dropout1", dropout1))

    # fc2
    fc2 = dense_bn(dropout1, n_units=64, is_training=training, name="fc2")
    layers.append(("fc2", fc2))
    
    # dropout2
    dropout2 = tf.layers.dropout(fc2, rate=drop_rate, training=training, seed=42, name="dropout2")
    layers.append(("dropout2", dropout2))
    
    # dense2
    fc3 = dense(dropout2, n_units=10, activation=None, name="fc3")
    layers.append(("fc3", fc3))
    
    prob = tf.nn.softmax(fc2, name="prob")
    layers.append(("prob", prob))
    
    return layers, variables


def mnist_sequential_c2d2(x):
    """Creates sequential convolutional neural network for MNIST. The network
        uses 2 convolutional+pooling layers to create the representation part
        of the network, and 1 fully-connected dense layer to create the
        classifier part. Dropout layer is used for regularization. The output 
        probabilities are generated by one dense layer followed by a softmax 
        function.
    Args:
        x: A tensor representing the input.
    Returns:
        A tuple containing the layers of the network graph and additional
        placeholders if any. Layers are represented as list of named tuples.
    """    
    
    layers = []
    variables = []

    # conv1
    conv1 = conv2d(x, size=5, n_filters=32, name="conv1")
    layers.append(("conv1", conv1))
            
    pool1 = max_pool(conv1, name="pool1")
    layers.append(("pool1", pool1))

    # conv2
    conv2 = conv2d(pool1, size=5, n_filters=64, name="conv2")
    layers.append(("conv2", conv2))
        
    pool2 = max_pool(conv2, name="pool2")
    layers.append(("pool2", pool2))

    # flatten
    flat = flatten(pool2, name="flatten")
    layers.append(("flatten", flat))

    # fc1
    fc1 = dense(flat, n_units=1024, name="fc1")
    layers.append(("fc1", fc1))
    
    # dropout
    training = tf.placeholder(tf.bool, name="training")
    dropout1 = tf.layers.dropout(fc1, rate=0.5, training=training, seed=42, name="dropout")
    layers.append(("dropout1", dropout1))
    variables.append(("training", training))
    
    # dense2
    fc2 = dense(dropout1, n_units=10, activation=None, name="fc2")
    layers.append(("fc2", fc2))
    
    prob = tf.nn.softmax(fc2, name="prob")
    layers.append(("prob", prob))
    
    return layers, variables


def mnist_sequential_c2dbn1d1(x):
    """Creates sequential convolutional neural network for MNIST. The network
        uses 2 convolutional+pooling layers to create the representation part
        of the network, and 1 fully-connected dense layer to create the
        classifier part. Batch normalization is applied in the dense layer.
        Dropout layer is used for regularization. The output probabilities are 
        generated by one dense layer followed by a softmax function.
    Args:
        x: A tensor representing the input.
    Returns:
        A tuple containing the layers of the network graph and additional
        placeholders if any. Layers are represented as list of named tuples.
    """    
    
    layers = []
    variables = []

    # training or testing
    training = tf.placeholder(tf.bool, name="training")
    variables.append(("training", training))

    # conv1
    conv1 = conv2d(x, size=5, n_filters=32, name="conv1")
    layers.append(("conv1", conv1))
            
    pool1 = max_pool(conv1, name="pool1")
    layers.append(("pool1", pool1))

    # conv2
    conv2 = conv2d(pool1, size=5, n_filters=64, name="conv2")
    layers.append(("conv2", conv2))
        
    pool2 = max_pool(conv2, name="pool2")
    layers.append(("pool2", pool2))

    # flatten
    flat = flatten(pool2, name="flatten")
    layers.append(("flatten", flat))

    # fc1
    fc1 = dense_bn(flat, n_units=1024, is_training=training, name="fc1")
    layers.append(("fc1", fc1))
    
    # dropout
    dropout1 = tf.layers.dropout(fc1, rate=0.5, training=training, seed=42, name="dropout")
    layers.append(("dropout1", dropout1))
    
    # dense2
    fc2 = dense(dropout1, n_units=10, activation=None, name="fc2")
    layers.append(("fc2", fc2))
    
    prob = tf.nn.softmax(fc2, name="prob")
    layers.append(("prob", prob))
    
    return layers, variables
    

def mnist_resnet_c1r2d2(x):
    """Creates residual neural network for MNIST. The network
        uses 2 convolutional+pooling layers to create the representation part
        of the network, and 1 fully-connected dense layer to create the
        classifier part. Dropout layer is used for regularization. The output 
        probabilities are generated by one dense layer followed by a softmax 
        function.
    Args:
        x: A tensor representing the input.
    Returns:
        A tuple containing the layers of the network graph and additional
        placeholders if any. Layers are represented as list of named tuples.
    """    
    
    layers = []
    variables = []

    training = tf.placeholder(tf.bool, name="training")
    variables.append(("training", training))

    # conv1
    conv1 = conv2d_bn(
                x, size=3, n_filters=16,                
                activation = tf.nn.relu,
                kernel_init=variance_s_seeded(),
                name="initial_conv")
    layers.append(("initial_conv", conv1))
            
    # residual 1
    res1 = residual_layer(conv1, n_filters=16, n_blocks=2, strides=[1,1,1,1],
                          is_training=training, name="residual1")
    layers.append(("residual1", res1))

    # residual 2
    res2 = residual_layer(res1, n_filters=32, n_blocks=2, strides=[1,2,2,1],
                          is_training=training, name="residual2")
    layers.append(("residual2", res2))
    
    pool1 = tf.nn.avg_pool(res2, ksize=[1,8,8,1], strides=[1,1,1,1],
                           padding="VALID", name="pool1")    
    layers.append(("pool", pool1))

    # flatten
    flat = flatten(pool1, name="flatten")
    layers.append(("flatten", flat))

    # fc1
    fc1 = dense(flat, n_units=128, name="fc1")
    layers.append(("fc1", fc1))
    
    # dropout
    dropout1 = tf.layers.dropout(fc1, rate=0.5, training=training, seed=42, name="dropout")
    layers.append(("dropout1", dropout1))
    
    # dense2
    fc2 = dense(dropout1, n_units=10, activation=None, name="fc2")
    layers.append(("fc2", fc2))
    
    prob = tf.nn.softmax(fc2, name="prob")
    layers.append(("prob", prob))
    
    return layers, variables


def cifar10_sequential_c2d2(x):
    """Creates sequential convolutional neural network for CIFAR10. The network
        uses 2 convolutional+pooling layers to create the representation part
        of the network, and 1 fully-connected dense layer to create the
        classifier part. Dropout layer is used for regularization. The output 
        probabilities are generated by one dense layer followed by a softmax 
        function.
    Args:
        x: A tensor representing the input.
    Returns:
        A tuple containing the layers of the network graph and additional
        placeholders if any. Layers are represented as list of named tuples.
    """    
    
    layers = []
    variables = []

    training = tf.placeholder(tf.bool, name="training")
    variables.append(("training", training))

    # conv1
    conv1 = conv2d(x, size=5, n_filters=64, kernel_init=truncated_n_seeded(stddev=5e-2), name="conv1")
    layers.append(("conv1", conv1))
    
    norm1 = tf.nn.lrn(conv1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm1')
    layers.append(("norm1", norm1))
            
    pool1 = tf.nn.max_pool(norm1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool1')
    layers.append(("pool1", pool1))

    # conv2
    conv2 = conv2d(pool1, size=5, n_filters=64, kernel_init=truncated_n_seeded(stddev=5e-2), name="conv2")
    layers.append(("conv2", conv2))
            
    norm2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm2')
    layers.append(("norm2", norm2))

    pool2 = tf.nn.max_pool(norm2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool2')    
    layers.append(("pool2", pool2))

    # conv3
    conv3 = conv2d(pool2, size=3, n_filters=128, kernel_init=truncated_n_seeded(stddev=5e-2), name="conv3")
    layers.append(("conv3", conv3))

    # conv4
    conv4 = conv2d(conv3, size=3, n_filters=128, kernel_init=truncated_n_seeded(stddev=5e-2), name="conv4")
    layers.append(("conv4", conv4))
            
    # conv5
    conv5 = conv2d(conv3, size=3, n_filters=128, kernel_init=truncated_n_seeded(stddev=5e-2), name="conv5")
    layers.append(("conv5", conv5))

    norm5 = tf.nn.lrn(conv5, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm5')
    layers.append(("norm5", norm5))

    pool5 = tf.nn.max_pool(norm5, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool5')
    layers.append(("pool5", pool5))


    # flatten
    flat = flatten(pool2, name="flatten")
    layers.append(("flatten", flat))

    # fc1
    fc1 = dense(flat, n_units=384,
                kernel_init=truncated_n_seeded(stddev=0.04),
                bias_init=tf.constant_initializer(0.1),
                name="fc1")
    layers.append(("fc1", fc1))
    
    # dropout
    dropout1 = tf.layers.dropout(fc1, rate=0.25, training=training, seed=42, name="dropout")
    layers.append(("dropout1", dropout1))

    # fc2
    fc2 = dense(dropout1, n_units=192,
                kernel_init=truncated_n_seeded(stddev=0.04),
                bias_init=tf.constant_initializer(0.1),
                name="fc2")
    layers.append(("fc2", fc2))

    
    # fc3
    fc3 = dense(fc2, n_units=10, activation=None,
                kernel_init=truncated_n_seeded(stddev=1 / 192.0),
                name="fc3")
    layers.append(("fc3", fc3))
    
    prob = tf.nn.softmax(fc3, name="prob")
    layers.append(("prob", prob))
    
    return layers, variables
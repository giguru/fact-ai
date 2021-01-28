import tensorflow as tf
import numpy as np

EPS = 1e-20


def log_likelihood_gaussian(x, mu, sigma_square):
    return tf.reduce_sum(input_tensor=-0.5 * tf.math.log(2.0 * np.pi) - 0.5 * tf.math.log(sigma_square) -
                         (x - mu) ** 2 / (2.0 * sigma_square), axis=1)


def log_likelihood_student(x, mu, sigma_square, df=2.0):
    sigma = tf.sqrt(sigma_square)

    dist = tf.contrib.distributions.StudentT(df=df,
                                             loc=mu,
                                             scale=sigma)
    return tf.reduce_sum(input_tensor=dist.log_prob(x), axis=1)

import numpy as np


def gini(array):
    array = np.array(array, dtype=float)

    if np.amin(array) < 0:
        array -= np.amin(array)

    array += 1e-9
    array = np.sort(array)

    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]

    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))
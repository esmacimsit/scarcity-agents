import numpy as np

def gini(array):
    array = np.array(array, dtype=float)

    if array.size == 0:
        return 0.0

    if np.amin(array) < 0:
        array -= np.amin(array)

    array += 1e-9
    array = np.sort(array)

    n = array.shape[0]
    index = np.arange(1, n + 1)

    return np.sum((2 * index - n - 1) * array) / (n * np.sum(array))
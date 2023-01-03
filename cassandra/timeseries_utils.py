import numpy as np
from .utils import windowed


def sliding_window(data, window_size: int):
    """Makes snippets of data for sequence prediction by sliding a window with size `look_back`
    Args:
        data (np.array): data with x and y values, shape = (T, F)
        window_size (int): window size
    """
    # shape = (N, W, F)
    assert len(data) >= window_size
    return np.array(list(windowed(data, window_size)))

def make_ts_samples(data, look_back):
    snippets = sliding_window(data, look_back) # (N, W, F+1)
    x = np.swapaxes(snippets[:, :-1, :-1], 1, 2) # (N, F, W-1)
    y = snippets[:, -1, -1] # (N, )
    return x, y
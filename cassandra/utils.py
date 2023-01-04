from collections import deque
from itertools import chain, repeat
from pathlib import Path

import requests


# https://github.com/more-itertools/more-itertools/blob/master/more_itertools/more.py
def windowed(seq, n, fillvalue=None, step=1):
    """Return a sliding window of width *n* over the given iterable.
        >>> all_windows = windowed([1, 2, 3, 4, 5], 3)
        >>> list(all_windows)
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    When the window is larger than the iterable, *fillvalue* is used in place
    of missing values:
        >>> list(windowed([1, 2, 3], 4))
        [(1, 2, 3, None)]
    Each window will advance in increments of *step*:
        >>> list(windowed([1, 2, 3, 4, 5, 6], 3, fillvalue='!', step=2))
        [(1, 2, 3), (3, 4, 5), (5, 6, '!')]
    To slide into the iterable's items, use :func:`chain` to add filler items
    to the left:
        >>> iterable = [1, 2, 3, 4]
        >>> n = 3
        >>> padding = [None] * (n - 1)
        >>> list(windowed(chain(padding, iterable), 3))
        [(None, None, 1), (None, 1, 2), (1, 2, 3), (2, 3, 4)]
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        yield tuple()
        return
    if step < 1:
        raise ValueError("step must be >= 1")

    window = deque(maxlen=n)
    i = n
    for _ in map(window.append, seq):
        i -= 1
        if not i:
            i = step
            yield tuple(window)

    size = len(window)
    if size == 0:
        return
    elif size < n:
        yield tuple(chain(window, repeat(fillvalue, n - size)))
    elif 0 < i < min(step, n):
        window += (fillvalue,) * i
        yield tuple(window)


def make_artifact_filepath(uri):
    return Path(__file__).parent.parent / "artifacts" / uri


def download_artifact(uri):
    print(f"Downloading asset {uri}")
    artifact_filepath = make_artifact_filepath(uri)
    artifact_filepath.parent.mkdir(exist_ok=True, parents=True)
    url = f"https://raw.github.com/bdsaglam/cassandra-api/master/artifacts/{uri}"
    print(f"Fetching from {url}")
    response = requests.get(url)
    with open(artifact_filepath, "wb") as f:
        f.write(response.content)


def get_artifact_filepath(uri):
    artifact_filepath = make_artifact_filepath(uri)
    if not artifact_filepath.exists():
        download_artifact(uri)
    return artifact_filepath

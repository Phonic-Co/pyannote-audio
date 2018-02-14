#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2016 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


import numpy as np
import scipy.spatial.distance


def l2_normalize(fX):

    norm = np.sqrt(np.sum(fX ** 2, axis=1))
    norm[norm == 0] = 1.
    return (fX.T / norm).T


def get_range(metric='euclidean'):
    return {
        'angular': (0, np.pi),
        'euclidean': (0, 2),
        'sqeuclidean': (0, 4),
        'cosine': (-1.0, 1.0)
    }.get(metric, None)


def _pdist_func_1D(X, func):
    """Helper function for pdist"""

    X = X.squeeze()
    n_items, = X.shape

    distances = []

    for i in range(n_items - 1):
        distance = func(X[i], X[i+1:])
        distances.append(distance)

    return np.hstack(distances)


def pdist(fX, metric='euclidean', **kwargs):
    """Same as scipy.spatial.distance with support for additional metrics

    * 'angular': pairwise angular distance
    * 'equal':   pairwise equality check (only for 1-dimensional fX)
    * 'minimum': pairwise minimum (only for 1-dimensional fX)
    * 'maximum': pairwise maximum (only for 1-dimensional fX)
    * 'average': pairwise average (only for 1-dimensional fX)
    """

    if metric == 'angular':
        cosine = scipy.spatial.distance.pdist(
            fX, metric='cosine', **kwargs)
        return np.arccos(np.clip(1.0 - cosine, -1.0, 1.0))

    elif metric == 'equal':
        return _pdist_func_1D(fX, lambda x, X: x == X)

    elif metric == 'minimum':
        return _pdist_func_1D(fX, np.minimum)

    elif metric == 'maximum':
        return _pdist_func_1D(fX, np.maximum)

    elif metric == 'average':
        return _pdist_func_1D(fX, lambda x, X: .5 * (x + X))

    else:
        return scipy.spatial.distance.pdist(fX, metric=metric, **kwargs)


def _cdist_func_1D(X_trn, X_tst, func):
    """Helper function for cdist"""

    X_trn = X_trn.squeeze()
    n_items, = X_tst.shape
    X_tst = X_tst.squeeze()

    return np.vstack(func(x_trn, X_tst) for x_trn in iter(X_trn))


def cdist(fX_trn, fX_tst, metric='euclidean', **kwargs):
    """Same as scipy.spatial.distance.cdist with support for additional metrics

    * 'angular': pairwise angular distance
    * 'equal':   pairwise equality check (only for 1-dimensional fX)
    * 'minimum': pairwise minimum (only for 1-dimensional fX)
    * 'maximum': pairwise maximum (only for 1-dimensional fX)
    * 'average': pairwise average (only for 1-dimensional fX)
    """

    if metric == 'angular':
        cosine = scipy.spatial.distance.cdist(
            fX_trn, fX_tst, metric='cosine', **kwargs)
        return np.arccos(np.clip(1.0 - cosine, -1.0, 1.0))

    elif metric == 'equal':
        return _cdist_func_1D(fX_trn, fX_tst,
                              lambda x_trn, X_tst: x_trn == X_tst)

    elif metric == 'minimum':
        return _cdist_func_1D(fX_trn, fX_tst, np.minimum)

    elif metric == 'maximum':
        return _cdist_func_1D(fX_trn, fX_tst, np.maximum)

    elif metric == 'average':
        return _cdist_func_1D(fX_trn, fX_tst,
                              lambda x_trn, X_tst: .5 * (x_trn + X_tst))

    return scipy.spatial.distance.cdist(
        fX_trn, fX_tst, metric=metric, **kwargs)


def to_condensed(n, i, j):
    """Compute index in condensed pdist matrix

                V
        0 | . 0 1 2 3
     -> 1 | . . 4 5 6 <-   ==>   0 1 2 3 4 5 6 7 8 9
        2 | . . . 7 8                    ^
        3 | . . . . 9
        4 | . . . . .
           ----------
            0 1 2 3 4

    Parameters
    ----------
    n : int
        Number of inputs in squared pdist matrix
    i, j : int
        Indices in squared pdist matrix

    Returns
    -------
    k : int
        Index in condensed pdist matrix
    """
    if i == j:
        raise ValueError('i and j should be different.')
    i, j = min(i, j), max(i, j)
    return int(i * n - i * i / 2 - 3 * i / 2 + j - 1)


def to_squared(n, k):
    """Compute indices in squared matrix

    Parameters
    ----------
    n : int
        Number of inputs in squared pdist matrix
    k : int
        Index in condensed pdist matrix

    Returns
    -------
    i, j : int
        Indices in squared pdist matrix

    """
    i = int(n - np.sqrt(-8*k + 4*n**2 - 4*n + 1)/2 - 1/2)
    j = int(i**2/2 - i*n + 3*i/2 + k + 1)
    return i, j


# for n in range(2, 10):
#     for k in range(int(n*(n-1)/2)):
#         assert to_condensed(n, *to_squared(n, k)) == k

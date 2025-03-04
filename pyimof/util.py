# coding: utf-8
"""Common tools to optical flow algorithms.

"""

import numpy as np
import skimage
from skimage.transform import pyramid_reduce, resize


def tv_regularize(x, tau=0.3, dt=0.2, max_iter=100, p=None, g=None):
    """Total variation regularization using Chambolle algorithm [1]_.

    Parameters
    ----------
    x : ~numpy.ndarray
        The target array.
    tau : float
        Tightness parameter. It should have a small value in order to
        maintain attachement and regularization parts in
        correspondence.
    dt : float
        Time step of the numerical scheme. Convergence is proved for
        values dt < 0.125, but it can be larger for faster
        convergence.
    max_iter : int
        Maximum number of iteration.
    p : ~numpy.ndarray
        Optional buffer array of shape (x.ndim, ) + x.shape.
    g : ~numpy.ndarray
        Optional buffer array of shape (x.ndim, ) + x.shape.

    References
    ----------
    .. [1] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    """
    if p is None:
        p = np.zeros((x.ndim, ) + x.shape)
    if g is None:
        g = np.zeros_like(p)
    f = dt / tau
    out = x

    s_g = [slice(None), ] * (x.ndim + 1)
    s_d = [slice(None), ] * x.ndim
    s_p = [slice(None), ] * (x.ndim + 1)

    for _ in range(max_iter):
        for ax in range(x.ndim):
            s_g[0] = ax
            s_g[ax+1] = slice(0, -1)
            g[tuple(s_g)] = np.diff(out, axis=ax)
            s_g[ax+1] = slice(None)

        norm = np.sqrt((g ** 2).sum(axis=0))[np.newaxis, ...]
        norm *= f
        norm += 1.
        p -= dt * g
        p /= norm

        # d will be the (negative) divergence of p
        d = -p.sum(0)
        for ax in range(x.ndim):
            s_d[ax] = slice(1, None)
            s_p[ax+1] = slice(0, -1)
            s_p[0] = ax
            d[tuple(s_d)] += p[tuple(s_p)]
            s_d[ax] = slice(None)
            s_p[ax+1] = slice(None)

        out = x + d
    return out


def resize_flow(u, v, shape):
    """Rescale the values of the vector field (u, v) to the desired shape.

    The values of the output vector field are scaled to the new
    resolution.

    Parameters
    ----------
    u : ~numpy.ndarray
        The horizontal component of the motion field.
    v : ~numpy.ndarray
        The vertical component of the motion field.
    shape : iterable
        Couple of integers representing the output shape.

    Returns
    -------
    ru, rv : tuple[~numpy.ndarray]
        The resized and rescaled horizontal and vertical components of
        the motion field.

    """

    nl, nc = u.shape
    sy, sx = shape[0]/nl, shape[1]/nc

    u = resize(u, shape, order=0, preserve_range=True,
               anti_aliasing=False)
    v = resize(v, shape, order=0, preserve_range=True,
               anti_aliasing=False)

    ru, rv = sx*u, sy*v

    return ru, rv


def get_pyramid(I, downscale=2.0, nlevel=10, min_size=16):
    """Construct image pyramid.

    Parameters
    ----------
    I : ~numpy.ndarray
        The image to be preprocessed (Gray scale or RGB).
    downscale : float
        The pyramid downscale factor.
    nlevel : int
        The maximum number of pyramid levels.
    min_size : int
        The minimum size for any dimension of the pyramid levels.

    Returns
    -------
    pyramid : list[~numpy.ndarray]
        The coarse to fine images pyramid.

    """

    pyramid = [I]
    size = min(I.shape)
    count = 1

    while (count < nlevel) and (size > min_size):
        J = pyramid_reduce(pyramid[-1], downscale)
        pyramid.append(J)
        size = min(J.shape)
        count += 1

    return pyramid[::-1]


def coarse_to_fine(I0, I1, solver, downscale=2, nlevel=10, min_size=16):
    """Generic coarse to fine solver.

    Parameters
    ----------
    I0 : ~numpy.ndarray
        The first gray scale image of the sequence.
    I1 : ~numpy.ndarray
        The second gray scale image of the sequence.
    solver : callable
        The solver applyed at each pyramid level.
    downscale : float
        The pyramid downscale factor.
    nlevel : int
        The maximum number of pyramid levels.
    min_size : int
        The minimum size for any dimension of the pyramid levels.

    Returns
    -------
    u, v : tuple[~numpy.ndarray]
        The horizontal and vertical components of the estimated
        optical flow.

    """

    if (I0.ndim != 2) or (I1.ndim != 2):
        raise ValueError("Only grayscale images are supported.")

    if I0.shape != I1.shape:
        raise ValueError("Input images should have the same shape")

    pyramid = list(zip(get_pyramid(skimage.img_as_float32(I0),
                                   downscale, nlevel, min_size),
                       get_pyramid(skimage.img_as_float32(I1),
                                   downscale, nlevel, min_size)))

    u = np.zeros_like(pyramid[0][0])
    v = np.zeros_like(u)

    u, v = solver(pyramid[0][0], pyramid[0][1], u, v)

    for J0, J1 in pyramid[1:]:
        u, v = resize_flow(u, v, J0.shape)
        u, v = solver(J0, J1, u, v)

    return u, v

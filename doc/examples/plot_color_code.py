# coding: utf-8
"""Vector field color coding
=========================

Demonstration of colormap application to a vector field.

Pyimof provides the :func:`pyimof.display.plot` that displays a color
mapping applyed to a dense vector field according to its orientation
and magnitude. Any circular colormap can be applyed. Matplotlib
provides some of them by default: ``hsv``, ``twilight``,
``twilight_shifted``, ``hsv_r``, ``twilight_r``,
``twilight_shifted_r``.

If no colormap is provided to the :func:`pyimof.display.plot`
function, the fector field color coding is made by constructing a HSV
image in which the hue is the orientation of the vector flow and the
value is its magnitude. The saturation is set to 1.

Pyimof defines the ``middlebury`` matplotlib colormap that is inspired
by the color coding introduced by the Middlebury optical flow
evaluation website__ for displaying algorithms results. Its reverse
version ``middlebury_r`` is also provided.

.. __: http://vision.middlebury.edu/flow/

"""


import matplotlib.pyplot as plt
import pyimof

# --- Load the Hydrangea sequence

I0, I1 = pyimof.data.hydrangea()

# --- Estimate the optical flow

u, v = pyimof.solvers.ilk(I0, I1)

# --- Display it with different colormaps

fig = plt.figure(figsize=((9, 10)))
ax0, ax1, ax2, ax3, ax4, ax5 = fig.subplots(3, 2, True, True).ravel()
fig.tight_layout()

ax0.imshow(I0, cmap='gray')
ax0.set_axis_off()
ax0.set_title("Reference image")

pyimof.display.plot(u, v, ax=ax1, cmap=None)
ax1.set_title("Vector field to HSV image")

pyimof.display.plot(u, v, ax=ax2, cmap='middlebury')
ax2.set_title("'middlebury' colormap")

pyimof.display.plot(u, v, ax=ax3, cmap='hsv')
ax3.set_title("'hsv' colormap")

pyimof.display.plot(u, v, ax=ax4, cmap='twilight')
ax4.set_title("'twilight' colormap")

pyimof.display.plot(u, v, ax=ax5, cmap='twilight_shifted')
ax5.set_title("'twilight_shifted' colormap")

plt.show()

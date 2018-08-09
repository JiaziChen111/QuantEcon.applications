"""
Plots reservation wage against unemployment compensation

"""

import numpy as np
import matplotlib.pyplot as plt
from mccall_bellman_iteration import McCallModel, solve_mccall_model
from compute_reservation_wage import compute_reservation_wage


grid_size = 25  
c_vals = np.linspace(2, 12, grid_size)  # values of unemployment compensation
w_bar_vals = np.empty_like(c_vals)

mcm = McCallModel()

fig, ax = plt.subplots()

for i, c in enumerate(c_vals):
    mcm.c = c
    w_bar = compute_reservation_wage(mcm)
    w_bar_vals[i] = w_bar

ax.set_xlabel('unemployment compensation')
ax.set_ylabel('reservation wage')
txt = r'$\bar w$ as a function of $c$'
ax.plot(c_vals, w_bar_vals, 'b-', lw=2, alpha=0.7, label=txt)
ax.legend(loc='upper left')
ax.grid()

plt.show()

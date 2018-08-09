import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from smoothing_actions import *

N_simul = 150

def complete_ss(beta, b0, x0, A, C, S_y, T=12):
    """
    Computes the path of consumption and debt for the previously described
    complete markets model where exogenous income follows a linear
    state space
    """
    # Create a linear state space for simulation purposes
    # This adds "b" as a state to the linear state space system
    # so that setting the seed places shocks in same place for
    # both the complete and incomplete markets economy
    # Atilde = np.vstack([np.hstack([A, np.zeros((A.shape[0], 1))]),
    #                   np.zeros((1, A.shape[1] + 1))])
    # Ctilde = np.vstack([C, np.zeros((1, 1))])
    # S_ytilde = np.hstack([S_y, np.zeros((1, 1))])

    lss = qe.LinearStateSpace(A, C, S_y, mu_0=x0)

    # Add extra state to initial condition
    # x0 = np.hstack([x0, np.zeros(1)])

    # Compute the (I - beta*A)^{-1}
    rm = la.inv(np.eye(A.shape[0]) - beta*A)

    # Constant level of consumption
    cbar = (1-beta) * (S_y @ rm @ x0 - b0)
    c_hist = np.ones(T)*cbar

    # Debt
    x_hist, y_hist = lss.simulate(T)
    b_hist = np.squeeze(S_y @ rm @ x_hist - cbar/(1-beta))
    

    return c_hist, b_hist, np.squeeze(y_hist), x_hist


if __name__ == '__main__':

    # Define parameters
    alpha, rho1, rho2 = 10.0, 0.9, 0.0
    sigma = 1.0
    # N_simul = 1
    # T = N_simul
    A = np.array([[1., 0., 0.],
                  [alpha, rho1, rho2],
                  [0., 1., 0.]])
    C = np.array([[0.], [sigma], [0.]])
    S_y = np.array([[1,  1.0, 0.]])
    beta, b0 = 0.95, -10.0
    x0 = np.array([1.0, alpha/(1-rho1), alpha/(1-rho1)])

    # Do simulation for complete markets
    s = np.random.randint(0, 10000)
    np.random.seed(s)  # Seeds get set the same for both economies
    out = complete_ss(beta, b0, x0, A, C, S_y, 150)
    c_hist_com, b_hist_com, y_hist_com, x_hist_com = out


    fig, ax = plt.subplots(1, 2, figsize = (15, 5))

    # Consumption plots
    ax[0].set_title('Cons and income', fontsize = 17)
    ax[0].plot(np.arange(N_simul), c_hist_com, label = 'consumption', lw = 3)
    ax[0].plot(np.arange(N_simul), y_hist_com, label = 'income',
               lw = 2, color = sb.color_palette()[3], alpha = .6, linestyle = '--')
    ax[0].legend(loc = 'best', fontsize = 15)
    ax[0].set_xlabel('Periods', fontsize = 13)
    ax[0].set_ylim([-5.0, 110])

    # Debt plots
    ax[1].set_title('Debt and income', fontsize = 17)
    ax[1].plot(np.arange(N_simul), b_hist_com, label = 'debt', lw = 2)
    ax[1].plot(np.arange(N_simul), y_hist_com, label = 'Income',
               lw = 2, color = sb.color_palette()[3], alpha = .6, linestyle = '--')
    ax[1].legend(loc = 'best', fontsize = 15)
    ax[1].axhline(0, color = 'k', lw = 1)
    ax[1].set_xlabel('Periods', fontsize = 13)

    plt.show()

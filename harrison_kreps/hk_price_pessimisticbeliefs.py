"""
Provides a function to solve for asset prices under pessimistic beliefs in the
Harrison -- Kreps model.

Authors: Chase Coleman, Tom Sargent
"""
import numpy as np

def price_pessimisticbeliefs(transitions, dividend_payoff, beta=.75,
                             max_iter=50000, tol=1e-16):
    """
    Function to Solve Pessimistic Beliefs
    """
    # We will guess an initial price vector of [0, 0]
    p_new = np.array([[0], [0]])
    p_old = np.array([[10.], [10.]])

    # We know this is a contraction mapping, so we can iterate to conv
    for i in range(max_iter):
        p_old = p_new
        p_new = beta * np.min([np.dot(q, p_old) + np.dot(q, dividend_payoff)
                               for q in transitions], 1)

        # If we succed in converging, break out of for loop
        if np.max(np.sqrt((p_new - p_old)**2)) < 1e-12:
            break

    return p_new


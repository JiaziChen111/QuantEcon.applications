"""

Code to simulate the model in Globalization and Synchronization of Innovation
Cycles by Kiminori Matsuyama, Laura Gardini and Iryna Sushko 

See <http://www.centreformacroeconomics.ac.uk/Discussion-Papers/2015/CFMDP2015-27-Paper.pdf>

"""


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from numba import jit, vectorize


@jit(nopython=True)
def _hj(j, nk, s1, s2, theta, delta, rho):
    """
    If we expand the implicit function for h_j(n_k) then we find that
    it is a quadratic. We know that h_j(n_k) > 0 so we can get its
    value by using the quadratic form
    """
    # Find out who's h we are evaluating
    if j == 1:
        sj = s1
        sk = s2
    else:
        sj = s2
        sk = s1

    # Coefficients on the quadratic a x^2 + b x + c = 0
    a = 1.0
    b = ((rho + 1/rho)*nk - sj - sk)
    c = (nk*nk - (sj*nk)/rho - sk*rho*nk)

    # Positive solution of quadratic form
    root = (-b + np.sqrt(b*b - 4*a*c))/(2*a)

    return root

@jit(nopython=True)
def DLL(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    "Determine whether (n1, n2) is in the set DLL"
    return (n1 <= s1_rho) and (n2 <= s2_rho)

@jit(nopython=True)
def DHH(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    "Determine whether (n1, n2) is in the set DHH"
    return (n1 >= _hj(1, n2, s1, s2, theta, delta, rho)) and (n2 >= _hj(2, n1, s1, s2, theta, delta, rho))

@jit(nopython=True)
def DHL(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    "Determine whether (n1, n2) is in the set DHL"
    return (n1 >= s1_rho) and (n2 <= _hj(2, n1, s1, s2, theta, delta, rho))

@jit(nopython=True)
def DLH(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    "Determine whether (n1, n2) is in the set DLH"
    return (n1 <= _hj(1, n2, s1, s2, theta, delta, rho)) and (n2 >= s2_rho)

@jit(nopython=True)
def one_step(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    """
    Takes a current value for (n_{1, t}, n_{2, t}) and returns the
    values (n_{1, t+1}, n_{2, t+1}) according to the law of motion.
    """
    # Depending on where we are, evaluate the right branch
    if DLL(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
        n1_tp1 = delta*(theta*s1_rho + (1-theta)*n1)
        n2_tp1 = delta*(theta*s2_rho + (1-theta)*n2)
    elif DHH(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
        n1_tp1 = delta*n1
        n2_tp1 = delta*n2
    elif DHL(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
        n1_tp1 = delta*n1
        n2_tp1 = delta*(theta*_hj(2, n1, s1, s2, theta, delta, rho) + (1-theta)*n2)
    elif DLH(n1, n2, s1_rho, s2_rho, s1, s2, theta, delta, rho):
        n1_tp1 = delta*(theta*_hj(1, n2, s1, s2, theta, delta, rho) + (1-theta)*n1)
        n2_tp1 = delta*n2

    return n1_tp1, n2_tp1

@jit(nopython=True)
def n_generator(n1_0, n2_0, s1_rho, s2_rho, s1, s2, theta, delta, rho):
    """
    Given an initial condition, continues to yield new values of
    n1 and n2
    """
    n1_t, n2_t = n1_0, n2_0
    while True:
        n1_tp1, n2_tp1 = one_step(n1_t, n2_t, s1_rho, s2_rho, s1, s2, theta, delta, rho)
        yield (n1_tp1, n2_tp1)
        n1_t, n2_t = n1_tp1, n2_tp1

@jit(nopython=True)
def _pers_till_sync(n1_0, n2_0, s1_rho, s2_rho, s1, s2, theta, delta, rho, maxiter, npers):
    """
    Takes initial values and iterates forward to see whether
    the histories eventually end up in sync.

    If countries are symmetric then as soon as the two countries have the
    same measure of firms then they will by synchronized -- However, if
    they are not symmetric then it is possible they have the same measure
    of firms but are not yet synchronized. To address this, we check whether
    firms stay synchronized for `npers` periods with Euclidean norm

    Parameters
    ----------
    n1_0 : scalar(Float)
        Initial normalized measure of firms in country one
    n2_0 : scalar(Float)
        Initial normalized measure of firms in country two
    maxiter : scalar(Int)
        Maximum number of periods to simulate
    npers : scalar(Int)
        Number of periods we would like the countries to have the
        same measure for

    Returns
    -------
    synchronized : scalar(Bool)
        Did they two economies end up synchronized
    pers_2_sync : scalar(Int)
        The number of periods required until they synchronized
    """
    # Initialize the status of synchronization
    synchronized = False
    pers_2_sync = maxiter
    iters = 0

    # Initialize generator
    n_gen = n_generator(n1_0, n2_0, s1_rho, s2_rho, s1, s2, theta, delta, rho)

    # Will use a counter to determine how many times in a row
    # the firm measures are the same
    nsync = 0

    while (not synchronized) and (iters < maxiter):
        # Increment the number of iterations and get next values
        iters += 1
        n1_t, n2_t = next(n_gen)

        # Check whether same in this period
        if abs(n1_t - n2_t) < 1e-8:
            nsync += 1
        # If not, then reset the nsync counter
        else:
            nsync = 0

        # If we have been in sync for npers then stop and countries
        # became synchronized nsync periods ago
        if nsync > npers:
            synchronized = True
            pers_2_sync = iters - nsync

    return synchronized, pers_2_sync

@jit(nopython=True)
def _create_attraction_basis(s1_rho, s2_rho, s1, s2, theta, delta, rho, maxiter, npers, npts):
    # Create unit range with npts
    synchronized, pers_2_sync = False, 0
    unit_range = np.linspace(0.0, 1.0, npts)

    # Allocate space to store time to sync
    time_2_sync = np.empty((npts, npts))
    # Iterate over initial conditions
    for (i, n1_0) in enumerate(unit_range):
        for (j, n2_0) in enumerate(unit_range):
            synchronized, pers_2_sync = _pers_till_sync(n1_0, n2_0, s1_rho, s2_rho,
                                                        s1, s2, theta, delta, rho,
                                                        maxiter, npers)
            time_2_sync[i, j] = pers_2_sync

    return time_2_sync


# == Now we define a class for the model == #

class MSGSync:
    """
    The paper "Globalization and Synchronization of Innovation Cycles" presents
    a two country model with endogenous innovation cycles. Combines elements
    from Deneckere Judd (1985) and Helpman Krugman (1985) to allow for a
    model with trade that has firms who can introduce new varieties into
    the economy.

    We focus on being able to determine whether two countries eventually
    synchronize their innovation cycles. To do this, we only need a few
    of the many parameters. In particular, we need the parameters listed
    below

    Parameters
    ----------
    s1 : scalar(Float)
        Amount of total labor in country 1 relative to total worldwide labor
    theta : scalar(Float)
        A measure of how mcuh more of the competitive variety is used in
        production of final goods
    delta : scalar(Float)
        Percentage of firms that are not exogenously destroyed every period
    rho : scalar(Float)
        Measure of how expensive it is to trade between countries
    """
    def __init__(self, s1=0.5, theta=2.5, delta=0.7, rho=0.2):
        # Store model parameters
        self.s1, self.theta, self.delta, self.rho = s1, theta, delta, rho

        # Store other cutoffs and parameters we use
        self.s2 = 1 - s1
        self.s1_rho = self._calc_s1_rho()
        self.s2_rho = 1 - self.s1_rho

    def _unpack_params(self):
        return self.s1, self.s2, self.theta, self.delta, self.rho

    def _calc_s1_rho(self):
        # Unpack params
        s1, s2, theta, delta, rho = self._unpack_params()

        # s_1(rho) = min(val, 1)
        val = (s1 - rho*s2) / (1 - rho)
        return min(val, 1)

    def simulate_n(self, n1_0, n2_0, T):
        """
        Simulates the values of (n1, n2) for T periods

        Parameters
        ----------
        n1_0 : scalar(Float)
            Initial normalized measure of firms in country one
        n2_0 : scalar(Float)
            Initial normalized measure of firms in country two
        T : scalar(Int)
            Number of periods to simulate

        Returns
        -------
        n1 : Array(Float64, ndim=1)
            A history of normalized measures of firms in country one
        n2 : Array(Float64, ndim=1)
            A history of normalized measures of firms in country two
        """
        # Unpack parameters
        s1, s2, theta, delta, rho = self._unpack_params()
        s1_rho, s2_rho = self.s1_rho, self.s2_rho

        # Allocate space
        n1 = np.empty(T)
        n2 = np.empty(T)

        # Create the generator
        n1[0], n2[0] = n1_0, n2_0
        n_gen = n_generator(n1_0, n2_0, s1_rho, s2_rho, s1, s2, theta, delta, rho)

        # Simulate for T periods
        for t in range(1, T):
            # Get next values
            n1_tp1, n2_tp1 = next(n_gen)

            # Store in arrays
            n1[t] = n1_tp1
            n2[t] = n2_tp1

        return n1, n2

    def pers_till_sync(self, n1_0, n2_0, maxiter=500, npers=3):
        """
        Takes initial values and iterates forward to see whether
        the histories eventually end up in sync.

        If countries are symmetric then as soon as the two countries have the
        same measure of firms then they will by synchronized -- However, if
        they are not symmetric then it is possible they have the same measure
        of firms but are not yet synchronized. To address this, we check whether
        firms stay synchronized for `npers` periods with Euclidean norm
        
        Parameters
        ----------
        n1_0 : scalar(Float)
            Initial normalized measure of firms in country one
        n2_0 : scalar(Float)
            Initial normalized measure of firms in country two
        maxiter : scalar(Int)
            Maximum number of periods to simulate
        npers : scalar(Int)
            Number of periods we would like the countries to have the
            same measure for

        Returns
        -------
        synchronized : scalar(Bool)
            Did they two economies end up synchronized
        pers_2_sync : scalar(Int)
            The number of periods required until they synchronized
        """
        # Unpack parameters
        s1, s2, theta, delta, rho = self._unpack_params()
        s1_rho, s2_rho = self.s1_rho, self.s2_rho
    
        return _pers_till_sync(n1_0, n2_0, s1_rho, s2_rho, s1, s2, theta, delta, rho, maxiter, npers)

    def create_attraction_basis(self, maxiter=250, npers=3, npts=50):
        """
        Creates an attraction basis for values of n on [0, 1] X [0, 1] with npts in each dimension
        """
        # Unpack parameters
        s1, s2, theta, delta, rho = self._unpack_params()
        s1_rho, s2_rho = self.s1_rho, self.s2_rho

        ab = _create_attraction_basis(s1_rho, s2_rho, s1, s2, theta, delta,
                                      rho, maxiter, npers, npts)

        return ab

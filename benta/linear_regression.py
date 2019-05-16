"""
Libary of linear regressions.
"""
import numpy as np
from scipy.stats import linregress
from astroML.linear_model import TLS_logL
from scipy.odr import Model, Data, RealData, ODR
import scipy.optimize as op
import emcee

def mcmc_linear_model(x, y, xerr, yerr, nwalkers=100, nruns=2000,
                      cut=100):
    """
    This was built using the following references:

    * http://dan.iel.fm/emcee/current/user/line/
    * http://www.astroml.org/book_figures/chapter8/fig_total_least_squares.html
    * https://github.com/astroML/astroML/blob/master/astroML/linear_model/TLS.py

    The linear models is $y=a*x+b$

    Returns (a,b), ((a_lower, a_upper), (b_lower, b_upper))
    """

    # translate between typical slope-intercept representation,
    # and the normal vector representation

    def get_a_b(theta):
        b = np.dot(theta, theta) / theta[1]
        a = -theta[0] / theta[1]

        return a, b

    def get_beta(a, b):
        denom = (1 + a * a)
        return np.array([-b * a / denom, b / denom])


    # Define the log-maximum likelihood
    def lnlike(theta, x, y, xerr, yerr):
        arr = np.column_stack((x, y))
        arr_err = np.column_stack((xerr, yerr))

        return TLS_logL(theta, arr, arr_err**2)

    # Get a first extimative of the parameters
    # based on the maximum likelihood
    nll = lambda *args: -lnlike(*args)
    x0 = get_beta(*linregress(x, y)[:2]) # Initial guesses from
                                         # Ordinary Least Squares
    result = op.minimize(nll, x0=x0, args=(x, y, xerr, yerr),
                         method='Nelder-Mead')
    theta = result["x"]

    # Define the log-prior
    def lnprior(theta):
        a, b = get_a_b(theta)
        if -5.0 < a < 0.5 and 0.0 < b < 10.0:
            return 0.0
        return -np.inf

    # Define the full log-probability function
    def lnprob(theta, x, y, xerr, yerr):
        lp = lnprior(theta)
        if not np.isfinite(lp):
            return -np.inf
        return lp + lnlike(theta, x, y, xerr, yerr)

    # Set the MCMC walkers
    ndim = 2
    pos = [theta + 1e-4*np.random.randn(ndim) for i in range(nwalkers)]

    # Set and Run
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(x, y, xerr, yerr))
    sampler.run_mcmc(pos, nruns)

    # Get the samples. Do not get the first `cut` ones.
    samples = sampler.chain[:, cut:, :].reshape((-1, ndim))
    coeffs = np.array([get_a_b(bt) for bt in samples])

    # Get the a, b and their errors
    # The value of a and are the median of the
    # sampling distribution, while the lower and
    # upper values are the 16% and 84% percentiles.

    a_mcmc, b_mcmc = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
                         zip(*np.percentile(coeffs, [16, 50, 84], axis=0)))

    return (a_mcmc[0], b_mcmc[0]), ((a_mcmc[1], a_mcmc[2]),
                                    (b_mcmc[1], b_mcmc[2]))


def odr_linear_fit(x, y, xerr, yerr):
    """
    Obtained from Scipy ODR webpage with small modifications

    https://docs.scipy.org/doc/scipy/reference/odr.html
    """
    def f(B, x):
        '''Linear function y = m*x + b'''
        # B is a vector of the parameters.
        # x is an array of the current x values.
        # x is in the same format as the x passed to Data or RealData.
        #
        # Return an array in the same format as y passed to Data or RealData.
        return B[0]*x + B[1]

    # Create a model
    linear = Model(f)

    # Create a Data instance

    mydata = Data(x, y, wd=1./np.power(xerr,2), we=1./np.power(yerr,2))

    #Instantiate ODR with your data, model and initial parameter estimate.:
    beta0 = linregress(x, y)[:2]
    myodr = ODR(mydata, linear, beta0=beta0)

    #Run the fit.:
    myoutput = myodr.run()

    a, b = myoutput.beta
    a_error, b_error = myoutput.sd_beta

    return a, b, a_error, b_error

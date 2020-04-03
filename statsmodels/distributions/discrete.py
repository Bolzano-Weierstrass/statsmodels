import numpy as np
from scipy.stats import rv_discrete, nbinom, poisson
from scipy.special import gammaln, pdtr, pdtrik
from statsmodels.compat.scipy import _lazywhere


class genpoisson_p_gen(rv_discrete):
    '''Generalized Poisson distribution
    '''
    def _argcheck(self, mu, alpha, p):
        return (mu >= 0) & (alpha==alpha) & (p > 0)

    def _logpmf(self, x, mu, alpha, p):
        mu_p = mu ** (p - 1.)
        a1 = np.maximum(np.nextafter(0, 1), 1 + alpha * mu_p)
        a2 = np.maximum(np.nextafter(0, 1), mu + (a1 - 1.) * x)
        logpmf_ = np.log(mu) + (x - 1.) * np.log(a2)
        logpmf_ -=  x * np.log(a1) + gammaln(x + 1.) + a2 / a1
        return logpmf_

    def _pmf(self, x, mu, alpha, p):
        return np.exp(self._logpmf(x, mu, alpha, p))

genpoisson_p = genpoisson_p_gen(name='genpoisson_p',
                                longname='Generalized Poisson')

class zipoisson_gen(rv_discrete):
    '''Zero Inflated Poisson distribution
    '''
    def _argcheck(self, mu, w):
        return (mu > 0) & (w >= 0) & (w<=1)

    def _logpmf(self, x, mu, w):
        return _lazywhere(x != 0, (x, mu, w),
                          (lambda x, mu, w: np.log(1. - w) + x * np.log(mu) -
                          gammaln(x + 1.) - mu),
                          np.log(w + (1. - w) * np.exp(-mu)))

    def _pmf(self, x, mu, w):
        return np.exp(self._logpmf(x, mu, w))

    def _rvs(self, mu, w):
        # mixing a Bernouilli(1-w) and a Poisson(mu)
        zero_inflated_sampling = np.random.binomial(1, 1 - w, size=self._size)
        distibution_sampling = np.random.poisson(mu, size=self._size)
        return zero_inflated_sampling * distibution_sampling

    def _cdf(self, x, mu, w):
        # construct cdf from standard poisson's cdf and the w inflation of zero
        return w + poisson(mu=mu).cdf(x) * (1 - w)

    def _pff(self, q, mu, w):
        # we just translated and stretched q to remove zi
        q_mod = (q - w) / (1 - w)
        x = poisson(mu=mu).ppf(q_mod)
        # set to zero if in the zi range
        x[q < w] = 0
        return x

zipoisson = zipoisson_gen(name='zipoisson',
                          longname='Zero Inflated Poisson')

class zigeneralizedpoisson_gen(rv_discrete):
    '''Zero Inflated Generalized Poisson distribution
    '''
    def _argcheck(self, mu, alpha, p, w):
        return (mu > 0) & (w >= 0) & (w<=1)

    def _logpmf(self, x, mu, alpha, p, w):
        return _lazywhere(x != 0, (x, mu, alpha, p, w),
                          (lambda x, mu, alpha, p, w: np.log(1. - w) +
                          genpoisson_p.logpmf(x, mu, alpha, p)),
                          np.log(w + (1. - w) *
                          genpoisson_p.pmf(x, mu, alpha, p)))

    def _pmf(self, x, mu, alpha, p, w):
        return np.exp(self._logpmf(x, mu, alpha, p, w))

zigenpoisson = zigeneralizedpoisson_gen(name='zigenpoisson',
    longname='Zero Inflated Generalized Poisson')

class zinegativebinomial_gen(rv_discrete):
    '''Zero Inflated Generalized Negative Binomial distribution
    '''
    def _argcheck(self, mu, alpha, p, w):
        return (mu > 0) & (w >= 0) & (w<=1)

    def _logpmf(self, x, mu, alpha, p, w):
        s, p = self.convert_params(mu, alpha, p)
        return _lazywhere(x != 0, (x, s, p, w),
                          (lambda x, s, p, w: np.log(1. - w) +
                          nbinom.logpmf(x, s, p)),
                          np.log(w + (1. - w) *
                          nbinom.pmf(x, s, p)))

    def _pmf(self, x, mu, alpha, p, w):
        return np.exp(self._logpmf(x, mu, alpha, p, w))

    def convert_params(self, mu, alpha, p):
        size = 1. / alpha * mu**(2-p)
        prob = size / (size + mu)
        return (size, prob)

zinegbin = zinegativebinomial_gen(name='zinegbin',
    longname='Zero Inflated Generalized Negative Binomial')

from __future__ import absolute_import

import numpy as np
from pandas import DataFrame
from .base_sampler import NestedSampler


class Nestle(NestedSampler):
    """tupak wrapper `nestle.Sampler` (http://kylebarbary.com/nestle/)

    All positional and keyword arguments (i.e., the args and kwargs) passed to
    `run_sampler` will be propagated to `nestle.sample`, see documentation for
    that function for further help. Under Keyword Arguments, we list commonly
    used kwargs and the tupak defaults

    Keyword Arguments
   ------------------
    npoints: int
        The number of live points, note this can also equivalently be given as
        one of [nlive, nlives, n_live_points]
    method: {'classic', 'single', 'multi'} ('multi')
        Method used to select new points
    verbose: Bool
        If true, print information information about the convergence during
        sampling

    """
    default_kwargs = dict(verbose=True, method='multi', npoints=500,
                          update_interval=None, npdim=None, maxiter=None,
                          maxcall=None, dlogz=None, decline_factor=None,
                          rstate=None, callback=None)

    def _translate_kwargs(self, kwargs):
        if 'npoints' not in kwargs:
            for equiv in self.npoints_equiv_kwargs:
                if equiv in kwargs:
                    kwargs['npoints'] = kwargs.pop(equiv)

    def _verify_kwargs_against_default_kwargs(self):
        if self.kwargs['verbose']:
            import nestle
            self.kwargs['callback'] = nestle.print_progress
            self.kwargs.pop('verbose')
        NestedSampler._verify_kwargs_against_default_kwargs(self)

    def run_sampler(self):
        """ Runs Nestle sampler with given kwargs and returns the result

        Returns
        -------
        tupak.core.result.Result: Packaged information about the result

        """
        import nestle
        out = nestle.sample(
            loglikelihood=self.log_likelihood,
            prior_transform=self.prior_transform,
            ndim=self.ndim, **self.kwargs)
        print("")

        self.result.sampler_output = out
        self.result.samples = nestle.resample_equal(out.samples, out.weights)
        self.result.nested_samples = DataFrame(
            out.samples, columns=self.search_parameter_keys)
        self.result.nested_samples['weights'] = out.weights
        self.result.nested_samples['log_likelihood'] = out.logl
        idxs = [np.unique(np.where(self.result.samples[ii] == out.samples)[0])
                for ii in range(len(out.logl))]
        self.result.log_likelihood_evaluations = out.logl[idxs]
        self.result.log_evidence = out.logz
        self.result.log_evidence_err = out.logzerr
        return self.result

    def _run_test(self):
        """
        Runs to test whether the sampler is properly running with the given
        kwargs without actually running to the end

        Returns
        -------
        tupak.core.result.Result: Dummy container for sampling results.

        """
        import nestle
        kwargs = self.kwargs.copy()
        kwargs['maxiter'] = 2
        nestle.sample(
            loglikelihood=self.log_likelihood,
            prior_transform=self.prior_transform,
            ndim=self.ndim, **kwargs)
        self.result.samples = np.random.uniform(0, 1, (100, self.ndim))
        self.result.log_evidence = np.nan
        self.result.log_evidence_err = np.nan
        return self.result

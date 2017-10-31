# -*- coding: utf-8 -*-
# Copyright (C) Scott Coughlin (2017)
#
# This file is part of aCOSMIC.
#
# aCOSMIC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aCOSMIC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with aCOSMIC.  If not, see <http://www.gnu.org/licenses/>.

"""`sample`
"""

import numpy as np
from gwpy.utils import mp as mp_utils
from aCOSMIC import _evolvebin

__author__ = 'Katelyn Breivik <katie.breivik@gmail.com>'
__credits__ = 'Scott Coughlin <scott.coughlin@ligo.org>'
__all__ = 'Evolve'

class Evolve:
    def __init__(self, sample):
        '''
        initialize Evolve
        '''
        self.initial_conditions = sample


    def evolve(self, **kwargs):
        """After setting a number of initial conditions
        we evolve the system.

        Parameters
        ----------
        nproc : `int`, optional, default: 1
            number of CPUs to use for parallel file reading

        kwargs: 

        Returns
        -------
        An evolved binary
        """
        # Populate BSEDict
        BSEDict = kwargs.pop('BSEDict')
        import pdb
        pdb.set_trace()

        initial_conditions = np.vstack([self.initial_conditions.kstar1, self.initial_conditions.kstar2, self.initial_conditions.mass1_binary, self.initial_conditions.mass2_binary, self.initial_conditions.porb, self.initial_conditions.ecc, self.initial_conditions.metallicity[0:self.initial_conditions.mass1_binary.size], self.initial_conditions.tphysf]).T

        # calculate maximum number of processes
        nproc = min(kwargs.pop('nproc', 1), len(initial_conditions))
        # define multiprocessing method
        def _evolve_single_system(f):
            try:
                # kstar, mass, orbital period (days), eccentricity, metaliccity, evolution time (millions of years)
                tmp = _evolvebin.evolv2(f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7])
                return f, tmp[np.argwhere(tmp[:,0]>0),:]
            except Exception as e:
                if nproc == 1:
                    raise
                else:
                    return f, e

        # evolve sysyems
        output = mp_utils.multiprocess_with_queues(
            nproc, _evolve_single_system, initial_conditions, raise_exceptions=False)

        # raise exceptions (from multiprocessing, single process raises inline)
        for f, x in output:
            if isinstance(x, Exception):
                x.args = ('Failed to evolve %s: %s' % (f, str(x)),)
                raise x

        return output

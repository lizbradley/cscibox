"""
Experiment.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os

class Experiment(object):

    def __init__(self, name):
        self.atts         = {}
        self.atts["name"] = name

    def __len__(self):
        return len(self.atts)
        
    def __contains__(self, key):
        return key in self.atts

    def __getitem__(self, key):
        return self.atts[key]

    def __setitem__(self, key, item):
        self.atts[key] = item

    def __delitem__(self, key):
        del self.atts[key]

    def keys(self):
        return self.atts.keys()

    def report(self):
        names = self.atts.keys()
        names.sort()

        longest = 0
        for name in names:
            if len(name) > longest:
                longest = len(name)

        names.remove('name')

        buf = ""
        buf += "name"
        buf += " " * (longest - 4)
        buf += " : %s\n" % (self.atts['name'])
        for name in names:
            buf += "%s" % (name)
            buf += " " * (longest - len(name))
            val = self.atts[name]
            if int == type(val):
                buf += " : %d\n" % (val)
            elif float == type(val):
                buf += " : %g\n" % (val)
            elif str == type(val):
                buf += " : %s\n" % (val)
            else:
                pass
        return buf

    def calibration_report(self):
        buf = ""
        if self.atts["nuclide"] == '36Cl':
            buf += "psi_ca_0          : %g\n" % (self.atts["psi_ca_0"])
            buf += "psi_k_0           : %g\n" % (self.atts["psi_k_0"])
            buf += "Pf_0              : %g\n" % (self.atts["Pf_0"])
            buf += "psi_ca_uncertainty: %g\n" % (self.atts["psi_ca_uncertainty"])
            buf += "psi_k_uncertainty : %g\n" % (self.atts["psi_k_uncertainty"])
            buf += "Pf_uncertainty    : %g\n" % (self.atts["Pf_uncertainty"])
        else:
            buf += "psi_spallation_nuclide    : %g\n" % (self.atts["psi_spallation_nuclide"])
            buf += "psi_spallation_uncertainty: %g\n" % (self.atts["psi_spallation_uncertainty"])
            buf += "post_calibrated_slowMuon  : %g\n" % (self.atts["post_calibrated_slowMuon"])
            buf += "post_calibrated_fastMuon  : %g\n" % (self.atts["post_calibrated_fastMuon"])
        buf += "chi_square        : %g\n" % (self.atts["chi_square"])
        buf += "sample_size       : %d\n" % (self.atts["sample_size"])
        buf += "probability       : %g\n" % (self.atts["probability"])
        return buf

    def is_calibrated(self):
        keys = self.atts.keys()
        return "psi_ca_0" in keys or "psi_spallation_nuclide" in keys

    def remove_calibration(self):
        if not self.is_calibrated():
            return

        if self.atts["nuclide"] == '36Cl':
            del self.atts['psi_ca_0']
            del self.atts['psi_k_0']
            del self.atts['Pf_0']
            del self.atts['psi_ca_uncertainty']
            del self.atts['psi_k_uncertainty']
            del self.atts['Pf_uncertainty']
        else:
            del self.atts['psi_spallation_nuclide']
            del self.atts['psi_spallation_uncertainty']
            del self.atts['post_calibrated_slowMuon']
            del self.atts['post_calibrated_fastMuon']

        del self.atts['chi_square']
        del self.atts['sample_size']
        del self.atts['probability']

    def save(self, path):
        exp_path = os.path.join(path, self["name"] + ".txt")
        f = open(exp_path, "w")
        f.write(repr(self.atts))
        f.write(os.linesep)
        f.flush()
        f.close()

    def load(self, file):
        f = open(file, "U")
        self.atts = eval(f.readline().strip())
        f.close()

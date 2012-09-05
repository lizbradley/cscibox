import os

class Experiment(object):

    def __init__(self, name):
        self.atts         = {}
        self.atts["name"] = name

    def __getitem__(self, key):
        return self.atts[key]

    def __setitem__(self, key, item):
        self.atts[key] = item

    def __delitem__(self, key):
        del self.atts[key]

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

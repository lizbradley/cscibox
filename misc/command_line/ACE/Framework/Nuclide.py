import os

class Nuclide(object):

    #Why give HLSL production rates here when they should be calibrated?
    #For non-36Cl nuclides, muon contributions are given as a percentage
    #of total production, which we don't know ahead of time.  For the values
    #below, 'absolute' muon contributions are calculated as specified percent
    #values times total production rates given below.  These contributions
    #are then removed from the observed inventory and a linear regression
    #for spallation is computed.  This is why pre and post calibrated 
    #muon percentages differ
    psi_spallation_total         = {}
    psi_spallation_total["3He"]  = 116.0 # Licciardi et al 19999
    psi_spallation_total["10Be"] = 4.98  # Balco and Stone 2007
    psi_spallation_total["14C"]  = 17.5  # Lifton pers comm
    psi_spallation_total["21Ne"] = 19.0  # Niedermann 2000
    psi_spallation_total["26Al"] = 30.6  # Balco and Stone 2007

    decay         = {}
    decay["3He"]  = 0.0
    decay["10Be"] = 4.5903788079470E-7
    decay["14C"]  = 0.000120968
    decay["21Ne"] = 0.0
    decay["26Al"] = 9.68082654E-7

    @staticmethod
    def stable(element):
        if element == "3He" or element == "21Ne":
            return True
        return False
    
    @staticmethod
    def output_atts():
        return ["P_sp_ca", "P_sp_k", "P_mu", "Pn", "P_total", "cosmogenic inventory", "cosmogenic inventory uncertainty", "measured inventory", "measured inventory uncertainty", "nucleogenic inventory", "S_sp", "S_th", "S_mu", "age", "age uncertainty"]
         
    def __init__(self, name="DEFAULT"):
        self.element       = name
        self.required = []
        self.optional = []
        
    def add_optional(self, att):
        self.add_sorted(att, self.optional)

    def add_required(self, att):
        self.add_sorted(att, self.required)

    def add_sorted(self, att, atts):
        index = 0
        while index < len(atts):
            name = atts[index]
            if att == name:
                return
            if att < name:
                atts.insert(index, att)
                return
            index += 1
        atts.append(att)
        
    def contains(self, att):
        return (att in self.required) or (att in self.optional)
        
    def name(self):
        return self.element

    def remove_optional(self, att):
        self.optional.remove(att)

    def remove_required(self, att):
        self.required.remove(att)
        
    def required_atts(self):
        return self.required[:]

    def optional_atts(self):
        return self.optional[:]

    def save(self, f):
        f.write(self.element)
        f.write(os.linesep)
        f.write('BEGIN REQUIRED')
        f.write(os.linesep)
        for att in self.required:
            f.write(att)
            f.write(os.linesep)
        f.write('END REQUIRED')
        f.write(os.linesep)
        f.write('BEGIN OPTIONAL')
        f.write(os.linesep)
        for att in self.optional:
            f.write(att)
            f.write(os.linesep)
        f.write('END OPTIONAL')
        f.write(os.linesep)

    def load(self, f):
        # read name of nuclide
        self.element = f.readline().strip()
        # skip 'BEGIN REQUIRED' line
        f.readline()
        
        # read required atts
        att = f.readline().strip()
        while att != 'END REQUIRED':
            self.add_required(att)
            att = f.readline().strip()
            
        # skip 'BEGIN OPTIONAL' line
        f.readline()
        # read optional atts
        att = f.readline().strip()
        while att != 'END OPTIONAL':
            self.add_optional(att)
            att = f.readline().strip()

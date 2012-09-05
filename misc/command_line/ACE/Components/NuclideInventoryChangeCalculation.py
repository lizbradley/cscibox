from ACE.Framework.Component  import Component
from ACE.Framework.Nuclide    import Nuclide
import math

class NuclideInventoryChangeCalculation(Component):
    
    def __init__(self, collections, workflow):
        super(NuclideInventoryChangeCalculation, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.LAMBDA_36 = self.constants["lambda_36"]
        
        
    def __call__(self, samples):
        self.timestep  = self.experiment['timestep']

        for s in samples:
            if s["age"] == self.timestep:
                # first time step. Set the 'modelled' inventory Inv_c_mod
                s["Inv_c_mod"] = s["cosmogenic inventory"]
                s["Inv_c_uncertainty"] = 0.0
            else:
                self.calculate_age(s)

        return (([self.get_connection()], samples),)
        
    def calculate_age(self, s):

        #print
        #print "Entering calculate_age"
        #print "    age      : " + str(s["age"])
        #print "    Inv_c_mod: " + str(s["Inv_c_mod"])
        #print
        
        # calculate how much the inventory has changed over the timestep
        # also wind the age back timestep years (10)
        
        # Set the decay time for the current nuclide
        self.LAMBDA_36 = Nuclide.decay[self.experiment['nuclide']]
       
        prod0 = -1.0 * self.LAMBDA_36 * self.timestep
        minu0 = 1.0 - math.exp(prod0)
        #Stable isotopes have no exponential decreasing effect
        if Nuclide.stable(self.experiment['nuclide']):
            divi1 = self.timestep
        else:
            divi1 = minu0 / self.LAMBDA_36
        prod1 = s["P_total"] * divi1 
        #prod1 = s["P_total"] * self.timestep
        prod2 = -1.0 * self.LAMBDA_36 * s["age"]
        prod3 = math.exp(prod2)
        prod4 = prod3 * prod1

        #Stable isotopes have no exponential decreasing effect
        if Nuclide.stable(self.experiment['nuclide']):
            prod4 = prod1

        s["Inv_c_mod"] -= prod4
        
        prod5 = s["P_total_uncertainty"] * self.timestep
        prod6 = prod3 * prod5

        #Stable isotopes have no exponential decreasing effect
        if Nuclide.stable(self.experiment['nuclide']):
            prod6 = prod5

        s["Inv_c_uncertainty"] += prod6

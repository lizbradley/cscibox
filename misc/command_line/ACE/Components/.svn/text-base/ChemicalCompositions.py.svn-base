"""
ChemicalCompositions.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class ChemicalCompositions(Component):
    def __init__(self, collections, workflow):
        super(ChemicalCompositions,self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.elements = collections.get("elements")

    def __call__(self, samples):
        for s in samples:
            self.setDefaultsIfNeeded(s)
            self.calculateWaterContent(s)
            self.calculateNormalization(s)

            self.calculateFirstTwelve("H", s["H2OwtPercentage"], s);

            elements = ["H", "C", "Na", "Mg", "Al", "Si", "P", "K", "Ca", "Ti", "Mn", "Fe"]
            amounts  = ["H2OwtPercentage", "CO2", "Na2O", "MgO", "Al2O3", "SiO2", "P2O5", "K2O", "CaO", "TiO2", "MnO", "Fe2O3"]

            for i in range(len(elements)):
                self.calculateFirstTwelve(elements[i], s[amounts[i]], s)

            elements = ["Cl", "B", "Sm", "Gd", "U", "Th"]

            for i in range(len(elements)):
                self.calculateLastSix(elements[i], s[elements[i]], s)

            self.calculateOxygen(s)

        return (([self.get_connection()], samples),)

    def setDefaultsIfNeeded(self, s):
        if s["clRatio uncertainty"] == None:
            s["clRatio uncertainty"] = 0.05 * s["clRatio"]

        if s["Cl uncertainty"] == None:
            s["Cl uncertainty"] = 0.05 * s["Cl"]

        if s["volumetric water"] == None:
            s["volumetric water"] = 0.0

    def calculateWaterContent(self, s):
        if not s.has_key("H2OwtPercentage"):
            s["H2OwtPercentage"] = (s["volumetric water"] / s["density"]) * 100.0

    def calculateFirstTwelve(self, name, element, s):

        Oweight = self.elements["O"]["alpha"]

        entry = self.elements[name]

        weight     = entry["alpha"]
        numElement = entry["numElement"]
        numOxygen  = entry["numOxygen"]

        normalization = s["normalization"]

        # calculate ((inputElement/normalization)/100)

        div1 = (element / normalization)/100.0

        # calculate div1*weight*numElement

        prodWtNumElem = weight * numElement

        prod1 = div1 * prodWtNumElem

        # calculate (prodWtNumElem+oWeight*numOxygen)

        prodOWtNumOx = Oweight * numOxygen

        sum1 = prodWtNumElem + prodOWtNumOx

        # calculate prod1/sum1
        div2 = prod1 / sum1

        # calculate div2/weight
        div3 = div2 / weight

        s[name + "Calc"] = div3 * self.constants["AV"]

    def calculateLastSix(self, name, element, s):
        entry  = self.elements[name]

        weight = entry["alpha"]

        normalization = s["normalization"]

        div1 = element / normalization

        prod1 = div1 * 0.000001

        div2 = prod1 / weight

        s[name + "Calc"] = div2 * self.constants["AV"]

    def calculateNormalization(self, s):
        water = s["H2OwtPercentage"]

        total1 = s["CO2"]   + s["Na2O"] + s["MgO"] + s["Al2O3"] + s["SiO2"] + \
                 s["P2O5"]  + s["K2O"]  + s["CaO"] + s["TiO2"]  + s["MnO"]  + \
                 s["Fe2O3"] + water

        total2 = s["Cl"] + s["Cl uncertainty"] + s["B"] + \
                 s["Sm"] + s["Gd"] + s["U"] + s["Th"];

        div1 = total1 / 100.0
        div2 = total2 / 1000000.0

        s["normalization"] = div1 + div2

    def calculateOxygen(self, s):

        elements = ["H", "C", "Na", "Mg", "Al", "Si", "P", "K", "Ca", "Ti", "Mn", "Fe"]

        total = 0.0
        for element in elements:
            entry = self.elements[element]
            stoichiom = entry["Stoichiom"]
            value     = s[element + "Calc"]
            product   = value * stoichiom

            total += product

        s["OCalc"] = total

# vim: ts=4:sw=4:et

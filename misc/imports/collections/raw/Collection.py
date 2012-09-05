import csv

from xml.dom import minidom
#from pprint import pprint

class Collection(object):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Collection, cls).__new__(
                               cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if (not hasattr(self, "collections")):
            self.collections    = {}
            self.collections["constants"] = self.loadConstants()
            self.collections["paleomag"] = self.loadPaleomag()
            self.collections["polepositions"] = self.loadPolepositions()
            self.collections["fairbanks"] = self.loadSeaLevel("fairbanks")
            self.collections["elements"] = self.loadElements()
            self.collections["sunspots"] = self.loadSunspots()
    
    def get_collection(self, name):
        return self.collections[name]

    def loadConstants(self):
        #print "loading Constants"
        xmldoc = minidom.parse('constants.xml')
        if xmldoc != None:
            constants = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]
                
                nameNode  =  children[0]
                kids      = [e for e in nameNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                nameVal   =  kids[1]
                name      =  str(nameVal.firstChild.data)
                
                valueNode =  children[1]
                kids      = [e for e in valueNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                valueVal  =  kids[1]
                value     =  float(valueVal.firstChild.data)
                
                # print "<" + name + ", " + value + ">"
                constants[name] = value
                
            #pprint(constants)
            return constants
        return None

    def loadElements(self):
        #print "loading Elements"
        xmldoc = minidom.parse('elements.xml')
        if xmldoc != None:
            elements = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]

                entry = {}
                
                entryName = None
                
                for kid in children:
                    name  = str(kid.tagName)
                    kids  = [e for e in kid.childNodes if e.nodeType == e.ELEMENT_NODE]
                    value = None
                    if name == "name":
                        value     = str(kids[1].firstChild.data)
                        entryName = value
                    else:
                        value = float(kids[1].firstChild.data)
                    entry[name] = value
                
                # no need to store the name of the element in entry since the name of the
                # element is used as the index in the elements collection to access the entry
                del entry["name"]
                
                elements[entryName] = entry

            #pprint(elements)
            return elements
        return None

    def loadPaleomag(self):
        #print "loading Paleomag"
        xmldoc = minidom.parse('paleomag.xml')
        if xmldoc != None:
            paleomag = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]
                
                ageNode  =  children[0]
                kids     = [e for e in ageNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                ageVal   =  kids[1]
                age      =  int(ageVal.firstChild.data)
                
                intensityNode =  children[1]
                kids          = [e for e in intensityNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                intensityVal  =  kids[1]
                intensity     =  float(intensityVal.firstChild.data)
                
                #print "<" + age + ", " + intensity + ">"
                paleomag[age] = intensity
            
            #pprint(paleomag)
            return paleomag
        return None
        
    def loadPolepositions(self):
        #print "loading Polepositions"
        xmldoc = minidom.parse('polepositions.xml')
        if xmldoc != None:
            polepositions = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]
                
                ageNode  =  children[0]
                kids     = [e for e in ageNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                ageVal   =  kids[1]
                age      =  int(ageVal.firstChild.data)
                
                latitudeNode =  children[1]
                kids         = [e for e in latitudeNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                latitudeVal  =  kids[1]
                latitude     =  float(latitudeVal.firstChild.data)

                longitudeNode =  children[2]
                kids          = [e for e in longitudeNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                longitudeVal  =  kids[1]
                longitude     =  float(longitudeVal.firstChild.data)
                
                #print "<" + age + ", " + latitude + ", " + longitude + ">"
                
                entry = {}
                
                entry["latitude"] = latitude
                entry["longitude"] = longitude
                
                polepositions[age] = entry
                
            #pprint(polepositions)
            return polepositions
        return None
        
    def loadSeaLevel(self, name):
        #print "loading Sea Level"
        xmldoc = minidom.parse(name + '.xml')
        if xmldoc != None:
            sealevel = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]
                
                ageNode  =  children[0]
                kids     = [e for e in ageNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                ageVal   =  kids[1]
                age      =  int(ageVal.firstChild.data)

                seaLevelNode =  children[1]
                kids = [e for e in seaLevelNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                seaLevelVal  =  kids[1]
                seaLevel     =  float(seaLevelVal.firstChild.data)

                #print "<" + age + ", " + seaLevel + ">"
                sealevel[age] = seaLevel

            #pprint(sealevel)
            return sealevel
        return None

    def loadSunspots(self):
        #print "loading Sunspotnumber"
        xmldoc = minidom.parse('sunspots.xml')
        if xmldoc != None:
            sunspot = {}
            sunspotError = {}
            root      = xmldoc.childNodes[0]
            items     = [e for e in root.childNodes if e.nodeType == e.ELEMENT_NODE]
            for item in items:
                children = [e for e in item.childNodes if e.nodeType == e.ELEMENT_NODE]

                ageNode  =  children[0]
                kids     = [e for e in ageNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                ageVal   =  kids[1]
                age      =  int(ageVal.firstChild.data)

                sunspotsNode =  children[1]
                kids          = [e for e in sunspotsNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                sunspotsVal  =  kids[1]
                sunspots     =  float(sunspotsVal.firstChild.data)

                sunspotsErrorNode =  children[2]
                kids          = [e for e in sunspotsErrorNode.childNodes if e.nodeType == e.ELEMENT_NODE]
                sunspotsErrorVal  =  kids[1]
                sunspotsError     =  float(sunspotsErrorVal.firstChild.data)

                # print "<" + age + ", " + sunspots + ">"
                # print age, sunspots, sunspotsError

                entry = {}

                entry["sunspots"] = sunspots
                entry["error"] = sunspotsError

                sunspot[age] = entry

            #print(sunspot)
            return sunspot
        return None

def gen_constants_csv(collection):
    output_file = file("constants.csv", "w")
    output_file.write("name,value\n")
    keys = collection.keys()
    keys.sort()
    for name in keys:
        output_file.write("%s,%g\n" % (name,collection[name]))
    output_file.close()

def gen_paleomag_csv(collection):
    output_file = file("paleomag.csv", "w")
    output_file.write("age,intensity\n")
    keys = collection.keys()
    keys.sort()
    for age in keys:
        output_file.write("%d,%g\n" % (age,collection[age]))
    output_file.close()

def gen_polepositions_csv(collection):
    output_file = file("polepositions.csv", "w")
    output_file.write("age,latitude,longitude\n")
    keys = collection.keys()
    keys.sort()
    for age in keys:
        output_file.write("%d,%g,%g\n" % (age,collection[age]["latitude"],collection[age]["longitude"]))
    output_file.close()

def gen_fairbanks_csv(collection):
    output_file = file("fairbanks.csv", "w")
    output_file.write("age,sealevel\n")
    keys = collection.keys()
    keys.sort()
    for age in keys:
        output_file.write("%d,%g\n" % (age,collection[age]))
    output_file.close()

def gen_elements_csv(collection):
    output_file = file("elements.csv", "w")
    element = collection["Al"]
    keys    = element.keys()
    keys.sort()
    output_file.write("name,")
    output_file.write(keys[0])
    for index in range(1,len(keys)):
        output_file.write("," + keys[index])
    output_file.write("\n")
    elements = collection.keys()
    elements.sort()
    for name in elements:
        element = collection[name]
        output_file.write(name + ",")
        output_file.write("%g" % (element[keys[0]]))
        for index in range(1,len(keys)):
            output_file.write(",%g" % (element[keys[index]]))
        output_file.write("\n")
    output_file.close()

def gen_sunspots_csv(collection):
    output_file = file("sunspots.csv", "w")
    output_file.write("age,sunspots,error\n")
    keys = collection.keys()
    keys.sort()
    for age in keys:
        output_file.write("%d,%g,%g\n" % (age,collection[age]["sunspots"],collection[age]["error"]))
    output_file.close()

if __name__ == '__main__':
    data = Collection()

    constants = data.get_collection("constants")
    gen_constants_csv(constants)

    paleomag = data.get_collection("paleomag")
    gen_paleomag_csv(paleomag)

    polepositions = data.get_collection("polepositions")
    gen_polepositions_csv(polepositions)

    fairbanks = data.get_collection("fairbanks")
    gen_fairbanks_csv(fairbanks)

    elements = data.get_collection("elements")
    gen_elements_csv(elements)

    sunspots = data.get_collection("sunspots")
    gen_sunspots_csv(sunspots)

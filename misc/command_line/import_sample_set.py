import csv
import sys
import os.path

from ACE.Framework import Nuclide
from ACE.Framework import Nuclides
from ACE.Framework import Sample
from ACE.Framework import SampleSet
from ACE.Framework import SampleSets

nuclides     = None
samples      = None

def loadModels():
    global nuclides, samples

    nuclides     = Nuclides()
    samples      = SampleSets()

    nuclides.load('data')
    samples.load('data')
    
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "Usage: python import_sample_set.py name_of_csv_file.csv"
        sys.exit()

    csv_file = sys.argv[1]

    if not os.path.exists(csv_file):
        print "<%s> does not exist." % (csv_file)
        sys.exit()

    loadModels()

    sample_set = SampleSet("tmp")

    r = csv.DictReader(open(csv_file, "rb"))
    keysAnalyzed = False
    
    for row in r:
        if not keysAnalyzed:
            keys = row.keys()
            if not 'nuclide' in keys:
                print "Required attribute ('nuclide') are missing from CSV file. Aborting."
                sys.exit()
            nuclide_key = row['nuclide']
            if not nuclides.contains(nuclide_key):
                print "Unknown nuclide (%s) specified in CSV file. Aborting." % (nuclide_key)
            nuclide       = nuclides.get(nuclide_key)
            nuclideALL    = nuclides.get('ALL')
            required_atts = nuclide.required_atts()
            required_atts.extend(nuclideALL.required_atts())
            for att in keys:
                try:
                    required_atts.remove(att)
                except Exception:
                    pass
            if len(required_atts) > 0:
                print "Aborting: Samples in CSV file are missing required attributes: %s" % (required_atts)
                sys.exit()
            for att in keys:
                result = nuclide.contains(att)
                if not result:
                    result = nuclideALL.contains(att)
                if not result:
                    print "Abortin: Samples in CSV file contain an unknown attribute: %s" % (att)
                    sys.exit()
            keysAnalyzed = True
        keys = row.keys()
        s = Sample()
        for key in keys:
            if key == 'id' or key == 'nuclide':
                s[key] = row[key]
            else:
                s[key] = float(row[key])
        sample_set.add(s)
        
    print "%d samples loaded." % sample_set.size()
        
    name = None
    while name == None:
        name = raw_input("Enter name for New Sample Set: ")
        if name == '':
            name = None
            
    sample_set.name = name
    samples.add(sample_set)
    samples.save('data')

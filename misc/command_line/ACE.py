import csv
import os 

from ACE.Framework import CalibrationSets
from ACE.Framework import Collections
from ACE.Framework import Experiment
from ACE.Framework import Experiments
from ACE.Framework import Factors
from ACE.Framework import Nuclide
from ACE.Framework import Nuclides
from ACE.Framework import Sample
from ACE.Framework import SampleSets
from ACE.Framework import Workflow
from ACE.Framework import Workflows

calibrations = None
collections  = None
experiments  = None
factors      = None
nuclides     = None
samples      = None
workflows    = None

def clearscreen(numlines=100): 
    """Clear the console. 
    numlines is an optional argument used only as a fall-back. 
    """ 
    if os.name == "posix": 
        # Unix/Linux/MacOS/BSD/etc 
        os.system('clear') 
    elif os.name in ("nt", "dos", "ce"): 
        # DOS/Windows 
        os.system('cls') 
    else: 
        # Fallback for other operating systems. 
        print '\n' * numlines 

def loadModels():
    global calibrations, collections, experiments
    global factors, nuclides, samples, workflows

    calibrations = CalibrationSets()
    collections  = Collections()
    experiments  = Experiments()
    factors      = Factors()
    nuclides     = Nuclides()
    samples      = SampleSets()
    workflows    = Workflows()

    calibrations.load('data')
    collections.load('data')
    experiments.load('data')
    factors.load('data')
    nuclides.load('data')
    samples.load('data')
    workflows.load('data')

def displayMainCommands():
    print
    print "========================"
    print " 1. List Experiments"
    print " 2. List Calibration Sets"
    print " 3. List Sample Sets"
    print " 4. List Workflows"
    print "------------------------"
    print " 5. Browse Experiment"
    print " 6. Strip Calibration from Experiment"
    print " 7. Delete Experiment"
    print "------------------------"
    print " 8. Create Experiment"
    print " 9. Calibrate Experiment"
    print "10. Apply Experiment"
    print "------------------------"
    print "11. Quit"
    print "========================"
    print

def getMainCommandsSelection():
    selection = raw_input("Enter your selection: ")
    if selection == '':
        raise ValueError
    command = int(selection)
    if command < 1 or command > 11:
        raise ValueError
    if command == 11:
        return -1
    return command

def print_choices(choices):
    index = 1
    for item in choices:
        print "    %d. %s" % (index, item)
        index += 1

def select_item(choices):
    selection = raw_input("Enter your selection: ")
    if selection == '':
        raise ValueError
    command = int(selection)
    if command < 1 or command > len(choices):
        raise ValueError
    command -= 1
    return choices[command]

def listExperiments():
    names = experiments.names()
    print "============================================"
    print "The following experiments are available:"
    print
    print "Uncalibrated:"
    print
    for name in names:
        exp = experiments.get(name)
        if not exp.is_calibrated():
            print "    " + name 
    print
    print "Calibrated:"
    print
    for name in names:
        exp = experiments.get(name)
        if exp.is_calibrated():
            print "    " + name 
    print
    print "============================================"

def listCalibrationSets():
    names = calibrations.names()
    print "============================================"
    print "The following calibration sets are available:"
    print
    for name in names:
        print "    " + name 

def listSampleSets():
    names = samples.names()
    print "============================================"
    print "The following sample sets are available:"
    print
    for name in names:
        print "    " + name 

def listWorkflows():
    names = workflows.names()
    print "======================================"
    print "The following workflows are available:"
    print
    for name in names:
        print "    " + name 

def createExperiment():

    exp = Experiment("tmp")

    nucs = nuclides.names()
    nucs.remove('ALL')

    print "============================================"
    print "Select a nuclide for this experiment:       "
    print
    print_choices(nucs)
    print

    nuclide = None
    while nuclide == None:
        try:
            nuclide = select_item(nucs)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    exp["nuclide"] = nuclide

    wfs = []
    names = workflows.names()
    for name in names:
        w = workflows.get(name)
        if w.get_type() == "calibration":
            if w.supports_nuclide(nuclide):
                wfs.append(w)

    print
    print "Select a calibration workflow for this experiment"
    print
    print_choices([w.get_name() for w in wfs])
    print

    w = None
    while w == None:
        try:
            w = select_item(wfs)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    exp['calibration'] = w.get_name()

    wfs = []
    names = workflows.names()
    for name in names:
        w = workflows.get(name)
        if w.get_type() == "dating":
            if w.supports_nuclide(nuclide):
                wfs.append(w)

    print
    print "Select a dating workflow for this experiment"
    print
    print_choices([w.get_name() for w in wfs])
    print

    w = None
    while w == None:
        try:
            w = select_item(wfs)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    exp['dating'] = w.get_name()

    sets = []
    names = calibrations.names()
    for name in names:
        calib_set = calibrations.get(name)
        if calib_set.get_nuclide() == nuclide:
            sets.append(calib_set)
        
    print
    print "Select a calibration data set for this experiment"
    print
    print_choices([set.get_name() for set in sets])

    data = None
    while data == None:
        try:
            data = select_item(sets)
        except Exception:
            print "ACE: Invalid Selection. Try Again."
    exp['calibration_set'] = data.get_name()

    facts = w.get_factors()
    for name in facts:
        factor = factors.get(name)
        modes  = factor.get_mode_names()

        print
        print "Select a mode for %s" % (factor.get_name())
        print
        print_choices(modes)
        print

        mode = None
        while mode == None:
            try:
                mode = select_item(modes)
            except Exception:
                print "ACE: Invalid Selection. Try Again."

        exp[factor.get_name()] = mode

    timestep = 0
    while timestep <= 0:
        try:
            print
            val = raw_input("Enter a timestep for the experiment (>0): ")
            timestep = int(val) 
        except Exception:
            print "ACE: Invalid Selection. Try Again."
            timestep = 0

    exp["timestep"] = timestep

    #Slow muons (original) here, fast muons (new) below.
    if nuclide == "36Cl":
        muonLabel = "psi_mu_0"
    else:
        muonLabel = "slowMuonPerc"

    muon = None
    while muon == None:
        try:
            print
            val = raw_input("Enter a value for %s: " % (muonLabel))
            muon = float(val) 
        except Exception:
            print "ACE: Invalid Selection. Try Again."
            muon = None

    exp[muonLabel] = muon

    #Fast muons here
    if nuclide == "36Cl":
        fmuonLabel = "phi_mu_f0"
    else:
        fmuonLabel = "fastMuonPerc"

    fmuon = None
    while fmuon == None:
        try:
            print
            val = raw_input("Enter a value for %s: " % (fmuonLabel))
            fmuon = float(val)
        except Exception:
            print "ACE: Invalid Selection. Try Again."
            fmuon = None

    exp[fmuonLabel] = fmuon 

    name = None
    while name == None:
        print
        name = raw_input("Enter a name for this experiment: ")
        if name == "":
            print "Name cannot be empty."
            name = None
        if name in experiments.names():
            print "'%s' is already in use. Pick another name." % (name)
            name = None

    exp['name'] = name

    print
    print "-" * 40
    print "Experiment Report"
    print "-" * 40
    print
    print exp.report()
    print

    selection = raw_input("Save Experiment (y/n): ")
    if selection != "n":
        experiments.add(exp)
        experiments.save('data')
        print
        print "Experiment Saved."
    else:
        print "Experiment Not Saved."

def calibrateExperiment():
    names = experiments.names()
    uncalibrated = []
    for name in names:
        exp = experiments.get(name)
        if not exp.is_calibrated():
            uncalibrated.append(exp)
    if len(uncalibrated) == 0:
        print "There are no uncalibrated experiments."
        print
        return
    uncalibrated_names = [item["name"] for item in uncalibrated]

    print "============================================"
    print "Select an experiment to calibrate:          "
    print
    print_choices(uncalibrated_names)
    print
    exp = None
    while exp == None:
        try:
            exp = select_item(uncalibrated)
        except Exception:
            print "ACE: Invalid Selection. Try Again."
    print
    print "This experiment will be calibrated with this workflow:"
    print
    print "    " + exp["calibration"]
    print
    print "using this calibration data set:"
    print
    print "    " + exp["calibration_set"]
    print
    print
    selection = raw_input("Perform Calibration (y/n): ")
    if selection != "n":
        print
        print "Performing Calibration"
        print

        w = workflows.get(exp["calibration"])
        print "Retrieved Workflow"
        print

        w.set_factors(factors)
        w.set_collections(collections)
        w.set_nuclides(nuclides)

        print "Configured Workflow"
        print

        print "Preparing Calibration Data...",
        data = calibrations.get(exp["calibration_set"])
        ids = data.ids()
        current_samples = []
        for id in ids:
            sample = data.get(id)
            sample.set_experiment(exp["name"])
            current_samples.append(sample)
        print "Done."
        print

        print "Calibrating..."
        print

        w.execute(exp, current_samples)

        print
        print "Cleaning Calibration Samples...",
        for s in current_samples:
            s.remove_experiment(exp["name"])
        print "Done."
        print

        print "-" * 40
        print "Calibration Report"
        print "-" * 40
        print exp.calibration_report()
        print

        selection = raw_input("Save Calibration (y/n): ")
        if selection != "n":
            experiments.save('data')
            print
            print "Calibration Results Saved."
        else:
            print "Calibration Results Not Saved."
         
    else:
        print
        print "Calibration Cancelled."
   

def applyExperiment():
    names = experiments.names()
    calibrated = []

    for name in names:
        exp = experiments.get(name)
        if exp.is_calibrated():
            calibrated.append(exp)

    if len(calibrated) == 0:
        print "There are no calibrated experiments."
        print
        return

    calibrated_names = [item["name"] for item in calibrated]

    print "============================================"
    print "Select an experiment to apply:              "
    print
    print_choices(calibrated_names)
    print

    exp = None
    while exp == None:
        try:
            exp = select_item(calibrated)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    sets = []
    names = samples.names()
    for name in names:
        sample_set = samples.get(name)
        if sample_set.get_nuclide() == exp["nuclide"]:
            sets.append(sample_set)

    print
    print "Select a sample set to process:"
    print
    print_choices([set.get_name() for set in sets])

    sample_set = None
    while sample_set == None:
        try:
            sample_set = select_item(sets)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    w = workflows.get(exp["dating"])
    print "Retrieved Workflow"
    print

    w.set_factors(factors)
    w.set_collections(collections)
    w.set_nuclides(nuclides)

    print "Configured Workflow"
    print

    print "Preparing Sample Data...",
    ids = sample_set.ids()
    current_samples = []
    for id in ids:
        sample = sample_set.get(id)
        sample.set_experiment(exp["name"])
        current_samples.append(sample)
    print "Done."
    print

    print "Dating Samples"
    print

    w.execute(exp, current_samples)

    print "Cleaning Samples"
    print
    nuclide_ALL      = nuclides.get("ALL")
    nuclide_specific = nuclides.get(exp["nuclide"])

    atts_current = []
    atts_current.extend(nuclide_ALL.required_atts())
    atts_current.extend(nuclide_ALL.optional_atts())
    atts_current.extend(nuclide_specific.required_atts())
    atts_current.extend(nuclide_specific.optional_atts())
    atts_current.extend(Nuclide.output_atts())

    for s in current_samples:
        atts = s.properties()
        for att in atts:
            if not att in atts_current:
                del s[att]

    output_name = "results/%s_%s.csv" % (sample_set.get_name(), exp["name"])
    output_name = output_name.replace(" ", "_")
    print "Saving Results to %s" % (output_name),

    output = []
    output.append(atts_current)

    for s in current_samples:
        values = []
        for key in atts_current:
            values.append(s[key])
        output.append(values)
    

    f = open(output_name, "w")
    w = csv.writer(f)
    w.writerows(output)
    f.close()

    print "Done."

def ignoreCommand():
    pass

def browseExperiment():
    exps = []
    names = experiments.names()
    for name in names:
        exps.append(experiments.get(name))

    if len(exps) == 0:
        print "There are no experiments to browse."
        print
        return

    print "============================================"
    print "The following experiments are available to browse:"
    print
    print_choices([exp['name'] for exp in exps])
    print

    exp = None
    while exp == None:
        try:
            exp = select_item(exps)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    print
    print "-" * 40
    print "Experiment Report"
    print "-" * 40
    print
    print exp.report()
    print

def stripCalibration():
    names = experiments.names()

    calibrated = []

    for name in names:
        exp = experiments.get(name)
        if exp.is_calibrated():
            calibrated.append(exp)

    if len(calibrated) == 0:
        print "There are no calibrated experiments."
        print
        return

    print "============================================"
    print "The following calibrated experiments are available:"
    print
    print_choices([exp['name'] for exp in calibrated])
    print

    exp = None
    while exp == None:
        try:
            exp = select_item(calibrated)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    exp.remove_calibration()
    experiments.save('data')

def deleteExperiment():
    exps = []
    names = experiments.names()
    for name in names:
        exps.append(experiments.get(name))

    if len(exps) == 0:
        print "There are no experiments to delete."
        print
        return

    print "============================================"
    print "The following experiments are available to delete:"
    print
    print_choices([exp['name'] for exp in exps])
    print

    exp = None
    while exp == None:
        try:
            exp = select_item(exps)
        except Exception:
            print "ACE: Invalid Selection. Try Again."

    experiments.remove(exp['name'])
    experiments.save('data')

def performMainCommand(command):
    { 
      -1  : ignoreCommand,
       1  : listExperiments,
       2  : listCalibrationSets,
       3  : listSampleSets,
       4  : listWorkflows,
       5  : browseExperiment,
       6  : stripCalibration,
       7  : deleteExperiment,
       8  : createExperiment,
       9  : calibrateExperiment,
       10 : applyExperiment}[command]()

if __name__ == '__main__':

    command = 0

    loadModels()

    clearscreen()
    print "ACE Command-Line Prototype, version 2.1"
    print "---------------------------------------"

    while command != -1:
        displayMainCommands()
        try:
            command = getMainCommandsSelection()
            clearscreen()
            performMainCommand(command)
        except Exception, detail:
            print "ACE: Did Not Understand Selection"
            print "detail: ", detail
            #raise
            command = 0

    print "ACE: Good Bye!"

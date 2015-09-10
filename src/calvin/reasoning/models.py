#where the objects for making decisions about models go, at least for now



#currently just a typed-up version of the obj struct I set up with kathleen

class Assumption(object):
    """
    holds information about an assumption required for using a given type of
    model
    """
    def __init__(self, content, precheck=True, corrections=[], cost=cost.LOW):
        self.content = content
        self.precheck = precheck
        self.corrections = corrections
        self.cost = cost
        
    def check(self, core):
        result = engine.check(self.content, core)
        if result:
            return (True, [])
        else:
            if corrections:
                return (True, ['how to correct'])
                "express corrections for someone"
            else:
                return False
            
class Parameter(object):
    """
    a parameter is basically any knob we can twiddle on a model builder
    """
    def __init__(self, name, space_info, model_effects, param_interactions=[],
                 cost_map=[cost.FREE]):
        self.name = name
        self.space_info = space_info
        self.model_effects = model_effects
        self.param_interactions = param_interactions
        self.cost_map = cost_map
        
    def generate_actions(self, core):
        """
        Generate the set of changes that make sense on this paramter for this core
        """
        return []


class ModelType(object):
    """
    holds what we know about a type of model/model building tool/paradigm/thing 
    """
    
    def __init__(self, name, assumptions=[], parameters=[], 
                 goodness=validity.PLAUS, cost=cost.HIGH):
        self.name = name
        self.assumptions = assumptions
        self.expected_goodness = model_goodness
        self.cost = cost
        self.parameters = parameters
        
    def precheck_assumptions(self, core):
        optionset = []
        #sort assumption list by cost?
        for assumption in self.assumptions:
            if not assumption.precheck:
                continue
            check = self.check_assumption(assumption, core, optionset)
            if check is not False:
                optionset = check
            else:
                return False
        return optionset
            
    def check_assumption(self, assumption, core, optionset):
        result = assumption.check(core)
        if not result:
            return False
        else:
            return optionset + result[1]

class Action(object):
    """
    An action we can take, yo. Something we can put in the queue of stuff-to-do
    """

    def __init__(self, desc_of_action, cost, expected_benefit):
        self.action = desc_of_action
        self.cost = cost
        self.expected_benefit = expected_benefit
        
        
    #hm. so this should have, like, sorting.
        
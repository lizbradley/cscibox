#where the objects for making decisions about models go, at least for now

cost = (NONE, LOW, MEDIUM, HIGH)



#currently just a typed-up version of the obj struct I set up with kathleen

class Assumption(object):
    """
    holds information about an assumption required for using a given type of
    model
    """
    def __init__(self, content, precheck=True, corrections=[], cost=cost.LOW):
        """
        content -- the actual thing assumed, as a rule structure
        precheck -- can this assumption be checked before actually constructing the model
        corrections -- set of Actions that can be taken to try and meet the Assumption
          if it is not met initially
        cost -- cost of checking this assumption
        """
        self.content = content
        self.precheck = precheck
        self.corrections = corrections
        self.cost = cost
        
    def check(self, parameterset):
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
        """
        name -- whatever it's called in the model
        space_info -- mathematical description of the parameter space
          min/max, discrete or continuous, how to set initial value
          whether we should want to fiddle with it, probability dist of values
        model_effects -- how we expect changing this parameter to affec the model output
        param_interactions -- params that interact with this one, possibly with
          descriptions of how those behave
        cost_map -> change param in x direction changes cost of model x way
        
        
        parameter to any alg includes list of actual samples being passed; can
        use a boolean list or whatever makes sense to exclude some
        """
        self.name = name
        self.space_info = space_info
        self.model_effects = model_effects
        self.param_interactions = param_interactions
        self.cost_map = cost_map
        
    def generate_actions(self, core):
        """
        Generate the set of changes that make sense on this parameter for this core
        
        may morph to take a goal for changes to accomplish
        
        we actually generate "protoactions" here, which indicate just a change
        in a single parameter value which are then conglomerated appropriately
        to create full action plans
        """
        #incremental action -- increase/decrease parameter
        return []


class Algorithm(object):
    """
    holds what we know about a type of model/model building tool/paradigm/thing 
    """
    
    def __init__(self, name, assumptions=[], parameters=[], 
                 goodness=validity.PLAUS, cost=cost.HIGH):
        """
        name -- name of algorithm/model generation strategy
        assumptions -- set of Assumption objects
        parameters -- set of Parameter objects
        goodness -- upper limit of quality/goodness of models generated using this
          specific algorithm type
        cost -- average/typical cost of generating a model using this Algorithm
        """
        self.name = name
        self.assumptions = assumptions
        self.quality_limit = goodness
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
    
    def postcheck_assumptions(self, core, model):
        pass
            
    def check_assumption(self, assumption, core, optionset):
        result = assumption.check(core)
        if not result:
            return False
        else:
            return optionset + result[1]

class Action(object):
    """
    An action we can take, yo. Something we can put in the queue of stuff-to-do
    
    plan
    
    initial list - action can be
    - run an algorithm with <x> set of parameter values
      - generates an age/depth model (or fails)
      - always has an attached goal
        can be "generate a good model" in which case we analyze the model next;
          possibly generate more actions to make a better model
        can be some change to a previous model, in which case we check if that
          change has been accomplished
        can be to better assess the value/goodness of some other model or
          potentially action; in which case we should then run that assessment
          (eg explore space of possible models potentially for sensitivity or
          other things)
        
    - check an expensive assumption -- running a set of rules
      - assess value of model or algorithm using that assumption
      - returns a value assessment -- do what we do with value assessments;
        that be engine job
      - might generate a set of parameter changes
      
    - compare/contrast 2 models & generate a report of differences
      - not done with a plan, just done because it's cheap/there
      
    - analyze an individual model for quality; potentially accounting for reports
      of differences
      - final result
      
    results
    - some age/depth model -- stick it in the list of candidate models tagged w/
     how we got it
    - 
    """

    def __init__(self, desc_of_action, cost, expected_benefit):
        """
        """
        self.action = desc_of_action
        self.cost = cost
        self.expected_benefit = expected_benefit
        
    def take(self):
        pass
        
    #hm. so this should have, like, sorting.
        
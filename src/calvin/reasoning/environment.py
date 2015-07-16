

class Environment(object):
    
    def __init__(self, core):
        self.core = core
        self.variables = [{}]
        self.memoized_results = {}
        self.quick_results = {}
        
    def new_scope(self):
        self.variables.append(self.variables[-1].copy())
        return self.variables[-1]
    
    def leave_scope(self):
        self.variables.pop()
        
    def setvar(self, name, value):
        self.variables[-1][name] = value
    
    #TODO: do we need to do something with the env here?!
    #TODO: this should be a conf, but the mem results should be full args.
    def quick_cached(self, conclusion):
        return self.memoized_results.get(conclusion, 
                    self.quick_results.get(conclusion, None))
        
    def cached(self, conclusion):
        return self.memoized_results.get(conclusion, None)
    
    def fill_params(self, param_list):
        """
        Takes a set of parameter designations (may be simple names OR tuples
        of <function object; (parameters)>) and returns their values according
        to the current environment.
        If a variable is not found in the current environment (eg 5), it is used
        directly rather than causing some error.
        """
        #TODO: we can use this to semi-trivially get out sample values, yay.
        fill = []
        for param in param_list:
            if hasattr(param, '__iter__') and not isinstance(param, basestring):
                funcfill = []
                if len(param) > 1:
                    funcfill = self.fill_params(param[1])
                fill.append(param[0](*funcfill))
            else:
                fill.append(self.variables[-1].get(param, param))
        return fill
    
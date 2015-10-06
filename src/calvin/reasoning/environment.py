import calculations

definitions = {}

class Environment(object):
    
    def __init__(self, core):
        self.core = core
        self.variables = [{}]
        self.conclusions = []
        
    def new_scope(self):
        self.variables.append(self.variables[-1].copy())
        return self.variables[-1]
    
    def leave_scope(self):
        self.variables.pop()
        
    def new_rule(self, conclusion, filler):
        self.conclusions.append(conclusion)
        for param, fill in zip(conclusion.params, filler.params):
            self.setvar(param, fill)
        #TODO: do we unset this param when we leave the rule?
            
    def leave_rule(self):
        self.conclusions.pop()
        
    def setvar(self, name, value):
        self.variables[-1][name] = value
    
    def fill_params(self, param_list):
        """
        Takes a set of parameter designations and returns their values according
        to the current environment.
        If a variable is not found in the current environment, we attempt to
        find a rule defining it
        """
        #TODO: we can use this to semi-trivially get out sample values, yay.
        fill = []
        for param in param_list:
            if isinstance(param, basestring):
                if param in self.variables[-1]:
                    fill.append(self.variables[-1][param])
                elif param in definitions:
                    value = definitions[param](self)
                    self.setvar(param, value)
                    fill.append(value)
                else:
                    fill.append(param)
            else:
                fill.append(param)
        return fill
    
def define(varname, definer):
    definitions[varname] = definer
    
def calc(fname, *params):
    try:
        fn = getattr(calculations, fname)
    except KeyError:
        return None
    def do_calc(env):
        paramset = env.fill_params(params)
        try:
            return fn(env.core, *paramset)
        except:
            return None
    return do_calc

def lookup(*locations):
    def do_lookup(env):
        for loc in locations:
            try:
                value = loc(env)
            except Exception as exc:
                continue
            else:
                if value is not None:
                    return value
        return None
    return do_lookup

def metadata(varname, *args):
    def do_lookup(env):
        return env.core['all'][varname]
    return do_lookup

def db(dbname, *key):
    def do_lookup(env):
        #TODO: this needs to actually work, ofc
        return env[db][key]
    return do_lookup
    
    
    
    
    
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
        #TODO: cleanup on aisle copypasta
        for param in param_list:
            pname = VariableName(param).dkey()
            if isinstance(param, basestring):
                if param in self.variables[-1]:
                    #self.variables[-1]
                    fill.append(self.variables[-1][param])
                elif pname in definitions:
                    value = definitions[pname][1](self)
                    self.setvar(param, value)
                    fill.append(value)
                else:
                    fill.append(param)
            elif isinstance(param, tuple):
                new_key = tuple(self.fill_params(param))
                if new_key in self.variables[-1]:
                    fill.append(self.variables[-1][new_key])
                elif pname in definitions:
                    self.new_scope()
                    vname, defin = definitions[pname]
                    vname.ready_env(self, new_key)
                    value = defin(self)
                    self.leave_scope()

                    self.setvar(new_key, value)
                    fill.append(value)
                else:
                    fill.append(new_key)
            else:
                fill.append(param)
        return fill

class VariableName(object):
    def __init__(self, name):
        if isinstance(name, tuple):
            self.name = name[0]
            self.params = name[1:]
        else:
            self.name = name
            self.params = []

    def dkey(self):
        #this is a bleg hack, but it's easier than figuring out what's actually borked here.
        return (self.name, len(self.params))

    def __eq__(self, other):
        if isinstance(other, VariableName):
            return self.name == other.name and len(self.params) == len(other.params)
        elif isinstance(other, tuple):
            return self.name == other[0] and len(self.params) == (len(other) - 1)
        else:
            return self.name == other and len(self.params) == 0

    def ready_env(self, env, ready):
        if not self.params:
            return
        assert self == ready
        if isinstance(ready, VariableName):
            fills = zip(self.params, ready.params)
        else:
            fills = zip(self.params, ready[1:])
        for name, val in fills:
            env.setvar(name, val)

def define(varname, definer):
    if definer:
        vname = VariableName(varname)
        definitions[vname.dkey()] = (vname, definer)

def calc(fname, *params):
    try:
        fn = getattr(calculations, fname)
    except AttributeError:
        #if it's not a "basic" calculation function, it should be a function
        #of our first parameter...
        def do_calc(env):
            paramset = env.fill_params(params)
            try:
                func = getattr(paramset[0], fname)
            except AttributeError:
                print 'Function %s does not exist! Parameters: %s' % (fname, str(paramset))
                return None
            try:
                return func(*paramset[1:])
            except Exception:
                import traceback
                print repr(exc)
                print traceback.format_exc()
                return None
    else:
        def do_calc(env):
            paramset = env.fill_params(params)
            try:
                return fn(env.core, *paramset)
            except Exception as exc:
                import traceback
                print repr(exc)
                print traceback.format_exc()
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
        return env.core.properties[varname]
    return do_lookup

def db(dbname, *key):
    def do_lookup(env):
        #TODO: this needs to actually work, ofc
        return env[db][key]
    return do_lookup

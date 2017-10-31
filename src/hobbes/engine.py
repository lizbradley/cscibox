"""
engine.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from pprint import pprint
from copy import deepcopy
import quantities as pq
import logging
import rule_list
import rules
import arguments
import confidence
from environment import Environment
from conclusions import Conclusion

def build_argument(conclusion, env):
    """
    Builds an argument for the conclusion given. The conclusion should contain
    "filled" parameters, if it has any parameters.
    Arguments
    conclusion - A conclusion object to build the argument around
    Returns : An argument object
    """
    env.new_scope()
    ruleset = rules.get_rules(conclusion)
    runset = []

    for rule in ruleset:
        runset.append(rule.run(conclusion, env))
    env.leave_scope()

    return arguments.Argument(conclusion, env, runset)

def execute_flow_with_core(dstore, ai_params, core, flow_name, plan_name):
    flow = dstore.workflows[flow_name]
    comp_plan = dstore.computation_plans[plan_name]
    virt_core = core.new_computation(comp_plan)
    flow.execute(comp_plan, virt_core, None, ai_params)
    return virt_core

def execute_flow(dstore, ai_params, core_name, flow_name, plan_name):
    flow = dstore.workflows[flow_name]
    comp_plan = dstore.computation_plans[plan_name]
    virt_core = dstore.cores[core_name].new_computation(comp_plan)
    flow.execute(comp_plan, virt_core, None, ai_params)
    return virt_core

def build_hobbes_observations(dstore, core):
    output = ""
    output += "\nHobbes is looking at the core...\n"
    for cur_run in core.core.runs:
        output += "Run " + cur_run + "\n"
        data = core.core._data
        tot = 0
        out = 0
        for depth in data:
            tot += 1
            print depth/10.0 
            try:
                model_age = data[depth][cur_run]['Age from Model']
                c14_age = data[depth][cur_run]['Calibrated 14C Age']
                print "model age:" + str(model_age)
                print "c14 age:" + str(c14_age)
                low = c14_age.magnitude - c14_age.uncertainty.magnitude[0].magnitude
                high = c14_age.magnitude + c14_age.uncertainty.magnitude[1].magnitude #WWTF
                print "low error bound:" + str(low)
                print "high error bound:" + str(high)
                if model_age.magnitude > high or model_age.magnitude < low:
                    output += "depth " + str(depth/10.0) + ": "
                    output += "Model prediction for point outside C14 bounds.\n"
                    out += 1
            except KeyError:
                continue
    output += str(out) + "/" + str(tot) + " points not in model."
    return output


def search_bacon(dstore, core):
    def double_section_thickness(m):
        m2 = deepcopy(m)
        m2['Bacon Section Thickness'] *= 2
        return m2

    def halve_section_thickness(m):
        m2 = deepcopy(m)
        m2['Bacon Section Thickness'] /= 2
        return m2

    def double_iterations(m):
        m2 = deepcopy(m)
        m2['Bacon Number of Iterations'] *= 2
        return m2

    def halve_iterations(m):
        m2 = deepcopy(m)
        m2['Bacon Number of Iterations'] /= 2
        return m2

    def double_memory_mean(m):
        m2 = deepcopy(m)
        m2['Bacon Memory: Mean'] *= 2
        return m2

    def halve_memory_mean(m):
        m2 = deepcopy(m)
        m2['Bacon Memory: Mean'] /= 2
        return m2

    def double_memory_strength(m):
        m2 = deepcopy(m)
        m2['Bacon Memory: Strength'] *= 2
        return m2

    def halve_memory_strength(m):
        m2 = deepcopy(m)
        m2['Bacon Memory: Strength'] /= 2
        return m2

    improvers = [double_section_thickness, halve_section_thickness, double_iterations,
            halve_iterations, double_memory_mean, halve_memory_mean, double_memory_strength,
            halve_memory_strength]

    def run_bacon(model):
        logging.debug('running Bacon for Hobbes')
        logging.debug(str(model))
        return execute_flow_with_core(dstore, model, core, 'BACON Style',
            'Bacon Marine')

    seed_model = {'Bacon Memory: Mean': 0.7,
                 'Bacon Memory: Strength': 4.0,
                 'Bacon Number of Iterations': 200,
                 'Bacon Section Thickness': 50.0 * pq.cm,
                 'Bacon Accumulation Rate: Mean': 30.0 * pq.year / pq.cm,
                 'Bacon Accumulation Rate: Shape': 1.5,
                 'Bacon t_a': 3}

    unchecked_models = [seed_model]
    argument = ""
    K = 0
    while unchecked_models and K < 4:
        argument += "testing model" + str(K) + '\n'
        K += 1
        model = unchecked_models.pop(0)
        argument += "model params:" + str(model) + '\n'
        vcore = run_bacon(model)
        is_good_model = build_argument(Conclusion('valid model'), Environment(vcore))
        argument += str(is_good_model) + '\n'
        if is_good_model.confidence.is_true():
            return (is_good_model, vcore) # stop on good model
        else:
            # given model has low error only has three rules
            # we can first limit improvers to 2 of them
            improvers = [halve_section_thickness, double_iterations]
        for i in improvers:
            unchecked_models.append(i(model))
        # Note this can loop forever...
    finished_model = {'Bacon Memory: Mean': 0.1,
                 'Bacon Number of Iterations': 500,
                 'Bacon Section Thickness': 50.0 * pq.cm,
                 'Bacon t_a': 2}
    argument += "Recomended model params to change:\n"
    argument += str(finished_model)
    return (argument, vcore)

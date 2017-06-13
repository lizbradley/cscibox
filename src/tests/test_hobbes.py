from cscience import datastore
import hobbes.argue
from hobbes.reasoning import engine, environment, conclusions, rules

if __name__ == '__main__':
    datastore = datastore.Datastore()
    try:
        datastore.load_from_config()
    except Exception as exc:
        import traceback
        print repr(exc)
        print traceback.format_exc()

        raise datastore.RepositoryException()
    
    core = datastore.cores['Harding Lake']
    for sample in core:
        pass
    for c in core.virtualize():
        if c.properties['Age/Depth Model']:
            core = c
            break
        
    
    env = environment.Environment(core)
    result = engine.build_argument(conclusions.Conclusion('invalid model'), env)
    print result
    """
    core = datastore.cores['smaller_dataset2']
    core = core.virtualize()[0]
    #hack to force load; so gross like whoa.
    for sample in core:
        pass
    env = environment.Environment(core)
    
    print 'Calvin, should we stop layer counting in core "smaller_dataset2" between depths 3525.34 and 3534.48?\n'
    result = engine.build_argument(conclusions.Conclusion('stop layer counting', (3525.34,3534.48)),env)
    print 'Answer:', result
    print '---------'

    core = datastore.cores['NGRIP - Ice Core']
    core = core.virtualize()[0]
    for sample in core:
        pass
    core['all']['average temperature'] = -3.34
    core['all']['temperature variability'] = 482.9
    core['all']['latitude'] = 75.1
    core['all']['longitude'] = -42.32
    env = environment.Environment(core)
    
    print 'Should we be concerned about snow melt (for firn modeling) at the NGRIP core?'
    print '(using average annual temperature of -3.34, standard deviation 22.97, pulled manually from online)\n'
    result = engine.build_argument(conclusions.Conclusion('no snow melt'), env)
    print result
    print '---------'
    
    print 'Is the NGRIP core in the ocean? (based on lat/lng)\n'
    result = engine.build_argument(conclusions.Conclusion('need marine curve'), env)
    print result
    print '---------'
    
    core = datastore.cores['OMZ01-PC14']
    core = core.virtualize()[0]
    for sample in core:
        pass
    core['all']['latitude'] = 37.5
    core['all']['longitude'] = -143.5
    env = environment.Environment(core)
   
    print 'Does the accumulation rate for core "OMZ01-PC14" change smoothly?'
    print '(Useful for determining how appropriate it is to use Bacon, find hiatuses, etc.)\n'
    result = engine.build_argument(conclusions.Conclusion('smooth accumulation rate'), env)
    print result
    print '---------'
    
    print 'Is "OMZ01-PC14 in the ocean (needing a marine calibration)?'
    print '(did not have lat/lng handy, using (+37.5, -143.5)\n'
    result = engine.build_argument(conclusions.Conclusion('need marine curve'), env)
    print result
    print '---------'
    """

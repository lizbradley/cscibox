from cscience import datastore
from calvin.reasoning import environment, engine, conclusions

if __name__ == '__main__':
    datastore = datastore.Datastore()
    try:
        datastore.load_from_config()
    except Exception as exc:
        import traceback
        print repr(exc)
        print traceback.format_exc()

        raise datastore.RepositoryException()
    
    core = datastore.cores['NGRIP - Ice Core']
    core = core.virtualize()[0]
    #hack to force load; so gross like whoa.
    for sample in core:
        pass
    core['all']['average temperature'] = -3.34
    core['all']['temperature variability'] = 482.9
    core['all']['latitude'] = 75.1
    core['all']['longitude'] = -42.32
    core['all']['depth interval'] = (0,10)
    env = environment.Environment(core)
    
    result = engine.build_argument(conclusions.Conclusion('keep layer counting', (0, 10)),env)
    print result

    # a bunch of rules that Kathleen tried!

    #result = engine.build_argument(conclusions.Conclusion('past temperature rarely above freezing'),env)
    #print result
    #result = engine.build_argument(conclusions.Conclusion('no snow melt'), env)
    
    #result = engine.build_argument(conclusions.Conclusion('number of peaks is normal'), env)
    #print result

    #engine.build_argument(conclusions.Conclusion('number of peaks is normal'), env)

    #result = engine.build_argument(conclusions.Conclusion('keep layer counting'),env)
    #print result

    #newResult = engine.build_argument(calculations.number_of_peaks_is_normal(core,(0,10)))
    #print newResult
    """
    result = engine.build_argument(conclusions.Conclusion('no snow melt'), env)
    print result
    
    print '---------'
    
    result = engine.build_argument(conclusions.Conclusion('no annual signal', (1, 10)), env)
    print result
    
    print '---------'
    
    result = engine.build_argument(conclusions.Conclusion('need marine curve'), env)
    print result
    
    print '---------'
    
    core = datastore.cores['OMZ01-PC14']
    core = core.virtualize()[0]
    #hack to force load; so gross like whoa.
    for sample in core:
        pass
    core['all']['latitude'] = 37.476205
    core['all']['longitude'] = -143.491622
    env = environment.Environment(core)
   
    result = engine.build_argument(conclusions.Conclusion('smooth accumulation rate'), env)
    print result
    
    print '---------'
    
    result = engine.build_argument(conclusions.Conclusion('need marine curve'), env)
    print result
    
    """
    

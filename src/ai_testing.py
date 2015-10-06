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
    core['all']['average temperature'] = -3.34
    core['all']['temperature variability'] = 482.9
    core['all']['latitude'] = 75.1
    core['all']['longitude'] = -42.32
    env = environment.Environment(core)
    result = engine.build_argument(conclusions.Conclusion('no snow melt'), env)
    print result
    
    print '---------'
    
    result = engine.build_argument(conclusions.Conclusion('no annual signal', (1, 10)), env)
    print result
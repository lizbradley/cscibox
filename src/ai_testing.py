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
    
    env = environment.Environment(datastore.cores['NGRIP - Ice Core'])
    result = engine.build_argument(conclusions.Conclusion('no snow melt'), env)
    print result
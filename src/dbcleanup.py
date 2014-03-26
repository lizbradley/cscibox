#some notes on how to clean up dev-related db cruft


def setup_batch():
    sc = cores.scan()
    for row in sc:
        if row[0][:3] == 'dev':
            bt.delete(row[0])
        else:
            for colfam in row[1].keys():
                if colfam != 'm:input':
                    bt.delete(row[0], columns=[colfam])
                    
cm.put('OMZ01-PC14', {'m:cplans':'\x80\x02c__builtin__\nset\nq\x01]q\x02U\x05inputq\x03a\x85Rq\x04.')
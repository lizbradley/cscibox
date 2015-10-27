#!/usr/bin/env python

import json
import pymongo
import gridfs


def convert_data(repo):
    corefs = gridfs.GridFS(repo, collection='core_files')
    corefs._GridFS__files.ensure_index('name', unique=True)
    cores = repo['cores']
    for core in cores.find():
        if not core.get('entries', None):
            continue
        newfile = corefs.new_file(name=core['name'])
        json.dump(core['entries'], newfile)
        newfile.close()
        del core['entries']
        cores.save(core)
        
    milfs = gridfs.GridFS(repo, collection='milieu_files')
    milfs._GridFS__files.ensure_index('name', unique=True)
    milieus = repo['milieus']
    for mil in milieus.find():
        if not mil.get('entries', None):
            continue
        newfile = milfs.new_file(name=mil['name'])
        json.dump(mil['entries'], newfile)
        newfile.close()
        del mil['entries']
        milieus.save(mil)
        

if __name__ == '__main__':
    conn = pymongo.MongoClient()
    repo = conn['repository']
    convert_data(repo)
    print 'database successfully converted!'




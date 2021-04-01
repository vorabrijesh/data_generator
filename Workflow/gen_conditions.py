from pymongo import MongoClient

def conditionHandler(curr):
    currNode = curr['nodeid']['content']
    currMsg = {}
    if(currNode == 'nx'):
        currMsg['hide'] = ['nstatus', 'jobid']
        currMsg['read_only'] = ['nodeid', 'role']
        return ['nz'], currMsg

    elif(currNode == 'nz'):
        currMsg['hide'] = ['nstatus', 'job_name']
        currMsg['read_only'] = ['nodeid', 'jobid', 'test2']
        return ['ny'], currMsg

    elif(currNode == 'ny'):
        currMsg['hide'] = ['nstatus', 'job_name']
        currMsg['read_only'] = ['nodeid', 'jobid', 'test3']
        return ['nx'], currMsg
    return None, currMsg
    
"""
The codes are copyrighted to Dr. Kalidas Yeturu of IIT Tirupati. 2019/Nov/28. Please contact him at ykalidas@iittp.ac.in for permission to use these codes.
The codes are not to be distributed or used without prior permission.
The author is not liable for any damage incurred by the user of these codes.
"""

import pandas as pd

class WFLog(object) :

    def __init__(self) :
        self.wfdf = pd.DataFrame()

    def submit(self,mydata) :
        self.wfdf = self.wfdf.append(mydata,ignore_index=True)

    def process(self) :

        print ('wf processing...')

        print ('before',self.wfdf)

        for i in self.wfdf[self.wfdf['status']=='pending'].index :
            
            row = self.wfdf.iloc[i]

            print ('processing row',row)
            
            target = self.cond_handler.gettarget(row)

            print ('obtained target',target)


            if target != '0000' :
                
                row_copy = row.copy()
                row_copy['status'] = 'pending'
                row_copy['node'] = target
                self.nodelog.submit(row_copy)

                self.wfdf.iloc[i]['status'] = 'processed'

        print ('after',self.wfdf)

        return 'process WFLog'   

    def setnodelog(self,nodelog) :
        self.nodelog = nodelog

    def sethandler(self,cond_handler) :
        self.cond_handler = cond_handler

    def debug_getdf(self) :
        return self.wfdf

"""
The codes are copyrighted to Dr. Kalidas Yeturu of IIT Tirupati. 2019/Nov/28. Please contact him at ykalidas@iittp.ac.in for permission to use these codes.
The codes are not to be distributed or used without prior permission.
The author is not liable for any damage incurred by the user of these codes.
"""

class NodeLog(object) :

    def __init__(self) :
        self.nodedf = pd.DataFrame()

    def submit(self,mydata) :
        #mydata['msgid'] = 'msg' + str(self.nodedf.shape[0] + 1)
        self.nodedf = self.nodedf.append(mydata,ignore_index=True)

    def process(self,msgid) :
        self.nodedf.loc[self.nodedf['msgid']==msgid,'status']='processed'

    def setwflog(self,wflog) :
        self.setwflog = wflog

    def debug_getdf(self) :
        return self.nodedf

"""
The codes are copyrighted to Dr. Kalidas Yeturu of IIT Tirupati. 2019/Nov/28. Please contact him at ykalidas@iittp.ac.in for permission to use these codes.
The codes are not to be distributed or used without prior permission.
The author is not liable for any damage incurred by the user of these codes.
"""
class ConditionHandler(object):

    def __load__(self) :

        f_con = open(self.condn_path,'r')

        self.map_cond = {}

        for line in f_con :
            if len(line.split())>0 :
                dict_obj = eval(line)
                print ('loading line',line)
                self.map_cond.update(dict_obj)

        f_con.close()

        print('loaded conditions',self.map_cond)

    def __init__(self,condn_path) :
        self.condn_path = condn_path
        self.__load__()


    #determine the target node (0000 is invalid node)
    def gettarget(self,x) :
        if x['wfid'] in self.map_cond :
            for my_f in self.map_cond[x['wfid']] :
                retval = my_f(x)
                if retval != '0000' :
                    return retval
        return '0000'

    def refresh(self) :
        self.__load__()






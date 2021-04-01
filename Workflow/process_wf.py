# -*- coding: utf-8 -*-
"""
Created on 16-Mar-2020

@author: KALIDAS Y
"""

from pymongo import MongoClient
from time import sleep
import numpy as np

def GetNextJobId(self):
  if len(list(self.find())) != 0:
    last_user = list(self.find({}).sort("jobid.content", -1).limit(1))
    return (int(last_user[0]["jobid"]['content'])+1)
  else:
    return 0

def course_registration(job,message,curr_node,dest_node):
    client = MongoClient('localhost',27017)
    student_collection = client['kali_db']['students']
    if curr_node == 'academics':
        job['rollno'] = {'type':'text', 'content': dest_node}
        job['student_name'] = {'type':'text', 'content':message['student_names'][dest_node]}
        job['faculty_advisor'] = {'type':'text','content':message['faculty_advisors'][dest_node]}
        job['unsigned_form'] = {'type':'file', 'content':message['file']}                            
    elif curr_node in student_collection.distinct('rollno'):
        job['signed_form'] = {'type':'file', 'content':message['file']}
    elif curr_node in student_collection.distinct('faculty_advisor'):
        job['role']['content'] = message['role']
    return job

def course_add_drop(job, message, curr_node, dest_node):
    client = MongoClient('localhost', 27017)
    student_collection = client['kali_db']['students']
    course_collection = client['kali_db']['courses']
    file_collection = client['kali_db']['kali_files']
    if curr_node == 'academics':
        job['rollno'] = {'type': 'text', 'content':dest_node}
        job['student_name'] = {'type':'text', 'content':message['student_names'][dest_node]}
        job['faculty_advisor'] = {'type':'text','content':message['faculty_advisors'][dest_node]}
        job['unsigned_add_drop'] = {'type':'file', 'content':message['file']}                          
    elif curr_node in student_collection.distinct('rollno'):
        job['signed_add_drop'] = {'type':'file', 'content':''}
        if len(message['file']) != 0:
            file_1 = file_collection.delete_one({'key':'unsigned_add_drop', 'file_name':message['file']})
            file_2 = file_collection.update_one({'key':'signed_add_drop', 'file_name' : message['file']},{"$set":{'key':'unsigned_add_drop'}})
            job['unsigned_add_drop']['content'] = message['file']
        if message['faculty_advisor'] == 'yes':
            job['signed_faculty_advisor'] = {'type':'file', 'content': ''}
    elif curr_node in course_collection.distinct('course_instructor'):
        job['signed_add_drop']['content'] = message['file']   
    elif curr_node in student_collection.distinct('faculty_advisor'):
        job['role']['content'] = message['role']
    return job

#engine infinite loop
while True :

    client= MongoClient('localhost',27017)
    node_collection = client['kali_db']['kali_node']
    wf_collection = client['kali_db']['kali_wf']
    file_collection = client['kali_db']['kali_files']
 
    sleep(3) #sleep for one sec

    print ('Processing workflow')

    #just process one pending job at a time
    for row in wf_collection.find():
        
       
        id = row['_id']
        con = __import__('conditions')
        dest_nodes, msg = con.conditionHandler(row)		# Conditional routing is done here 
       
        if dest_nodes == None or len(dest_nodes) == 0:
            continue
        if(dest_nodes[0] == 'controller' and msg['msg']['content']!='synthetic_data' and msg['msg']['content']!='gmm_predictions' and msg['msg']['content']!='gan_predictions'):
            continue
        
        elif(dest_nodes[0] == 'controller' and msg['msg']['content']=='synthetic_data'):
            print('synthetic data before inserted')
            wf_collection.delete_one({'_id':id})
            temp1 = GetNextJobId(node_collection)
            temp2 = GetNextJobId(wf_collection)
            row['msg']['content'] = 'retrain'
            row['jobid']={'type':'text','content':max(temp1,temp2)}
            row['role'] = {'type':'text','content':'ga'}
            row['nstatus']={'type':'text','content':'pending'}
            row['synthetic_data'] = msg['synthetic_data']
            row['fitness_of_population'] = msg['fitness_of_population']
            row['hide'] = ['synthetic_data']
            row['read_only'] = ['fitness_of_population','nstatus','role','jobid','synthetic_data']
            node_collection.insert_one(row)
            print('synthetic data after inserted')
        elif(dest_nodes[0] == 'controller' and msg['msg']['content']=='gmm_predictions'):
            print('synthetic data before inserted')
            wf_collection.delete_one({'_id':id})
            temp1 = GetNextJobId(node_collection)
            temp2 = GetNextJobId(wf_collection)
            row['msg']['content'] = 'retrain'
            row['jobid']={'type':'text','content':max(temp1,temp2)}
            row['role'] = {'type':'text','content':'gmm'}
            row['nstatus']={'type':'text','content':'pending'}
            # extracted_data = data[np.where(labels==target_class)]
            row['extracted_data'] = msg['extracted_data']
            # row['predictions'] = msg['predictions']
            # row['fitness_of_population'] = msg['fitness_of_population']
            row['hide'] = ['images']
            row['read_only'] = ['nstatus','role','jobid','extracted_data']
            node_collection.insert_one(row)
            print('synthetic data after inserted')
        elif(dest_nodes[0] == 'controller' and msg['msg']['content']=='gan_predictions'):
            print('synthetic data before inserted')
            wf_collection.delete_one({'_id':id})
            temp1 = GetNextJobId(node_collection)
            temp2 = GetNextJobId(wf_collection)
            row['msg']['content'] = 'retrain'
            row['jobid']={'type':'text','content':max(temp1,temp2)}
            row['role'] = {'type':'text','content':'gan'}
            row['nstatus']={'type':'text','content':'pending'}
            # row['predictions'] = msg['predictions']
            row['extracted_data'] = msg['extracted_data']
            # row['fitness_of_population'] = msg['fitness_of_population']
            row['hide'] = ['images']
            row['read_only'] = ['nstatus','role','jobid','extracted_data']
            node_collection.insert_one(row)
            print('synthetic data after inserted')
        else:
            currnode = row['nodeid']['content']
            role = row['role']['content']
            flag=0
            # print('rowid', row)
            q1 = wf_collection.find_one({'_id':id})
            if q1!={}:
                q1 = wf_collection.delete_one({'_id':id})
            print(q1)
            curr_jobid = row['jobid']['content']
            print('deleting job: ',row['jobid']['content'])
            if '_id' in row:
                del row['_id']		
            for x in dest_nodes:
                if flag!=0:
                        temp1 = GetNextJobId(node_collection)
                        temp2 = GetNextJobId(wf_collection)
                        row['jobid']['content']=max(temp1,temp2)

                # course registration
                if role == 'course_registration':
                    row = course_registration(row,msg,currnode,x)  # function to perform course_registration service
                
                # add/drop course
                if role == 'course_add_drop':
                    row = course_add_drop(row,msg,currnode,x)  # function to perform add/drop course service

                row['nodeid']['content']=x	
                if len(msg)!=0:
                    row['hide'] = msg['hide']
                    row['read_only'] = msg['read_only']	
                q2 = node_collection.insert_one(row)
                print('inserting job: ',row['jobid']['content'])
                del row['_id']
                flag=flag+1

        break
    # end for loop
# end while loop

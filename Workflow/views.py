"""
The codes are copyrighted to Dr. Kalidas Yeturu of IIT Tirupati. 2019/Nov/28. Please contact him at ykalidas@iittp.ac.in for permission to use these codes.
The codes are not to be distributed or used without prior permission.
The author is not liable for any damage incurred by the user of these codes.
"""

from datetime import datetime
from flask import Flask, redirect, url_for, request, render_template, make_response
from werkzeug.utils import secure_filename
import pandas as pd

from ast import literal_eval
from pymongo import MongoClient
from flask import Flask
from flask.wrappers import Response

from flask_cors import CORS
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

@app.route('/insertjob',  methods = ['GET', 'POST'])
def insert_job():
    return render_template('insert_job.html')

@app.route('/ga',  methods = ['GET', 'POST'])
def ga():
    return render_template('ga.html')

@app.route('/gan',  methods = ['GET', 'POST'])
def gan():
    return render_template('gan.html')

@app.route('/gmm',  methods = ['GET', 'POST'])
def gmm():
    return render_template('gmm.html')

@app.route('/invigilation',  methods = ['GET', 'POST'])
def invigilation():
    return render_template('invigilation.html')

'''@app.route('/dynamic_wf_template', methods = ['GET', 'POST'])
def dynamic_wf_template():
     
    form_data = request.form.to_dict()
    template_name = form_data['template_name']
    template_data = {} # get from data base for that template name
    return render_template('wf_renderer.html',template_data = template_data)'''


@app.route('/add_drop_course' ,methods = ['GET', 'POST'])
def add_drop_course():
    return render_template('add_drop_course.html')

@app.route('/course_registration' ,methods = ['GET', 'POST'])
def course_registration():
    client = MongoClient('localhost',27017)
    student_collection = client['kali_db']['students']
    batches = student_collection.distinct('batch')
    branches = student_collection.distinct('branch')
    return render_template('course_registration.html', batches = batches, branches = branches)

#function for generating next jobid
def GetNextJobId(self):
  if len(list(self.find())) != 0:
    last_user = list(self.find({}).sort("jobid.content", -1).limit(1))
    return (int(last_user[0]["jobid"]['content'])+1)
  else:
    return 0

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return render_template('dashboard.html')
    else:
        return render_template('dashboard.html')


@app.route('/file', methods=['GET'])
def fileupload():
    try:
        client= MongoClient('localhost',27017)
        db = client.kali_db
        key = request.args.get('key')
        filename = request.args.get('filename')
        file_ = db.kali_files.find_one({'key': key, 'file_name': filename})
        file_content = file_['content']
        contentType = file_['content_type']
        response =  Response(file_content,content_type=contentType)
        #response.headers['Content-Disposition'] = 'attachment; filename='+filename
        return response
    except:
        return 'File not found'


@app.route('/wfe/wf/strsubmit', methods=['GET','POST'])
def wf_strsubmit() : 
    try:
        client= MongoClient('localhost',27017)
        form_data = request.form.to_dict()
        input_no = 0
        form = {}
        form['jobid'] = {'type' : 'text', 'content' : 0}
        files = []
        int_data = 0
        for key_name in form_data:
            if key_name.startswith('key_'):
                id = key_name.split('.')[0]
                input_no = int(id[4:])                 # format: eg. key_1.dropdown/ value_3.text
                key = form_data[key_name]
                data_obj = ''
                if key_name.endswith('.file'):
                    cf = key_name[4:-5]
                    file = request.files['value_'+cf+'.file']
                    if file.filename == '':
                        data_obj = {'type' : 'file', 'content' : ''}
                    else:
                        files.append({'key': key, 'file_name': file.filename, 'content' : file.read(), 'content_type': file.content_type})
                        data_obj = {'type': 'file', 'content' : file.filename } 
                elif key_name.endswith('.file_pre'):
                    node_collection = client['kali_db']['kali_node']
                    val = key + '.type'
                    file_node = node_collection.find_one({val: 'file'})
                    data_obj = file_node[key]
                else:
                    value_name = next( p for p, q in form_data.items() if p.startswith('value_'+str(input_no)))
                    if value_name.endswith('.text'):
                        if key == 'jobid':
                            int_data = int(form_data[value_name])
                            print('jobid: ', int_data)
                            data_obj = {'type' : 'text', 'content': int_data}
                        else:
                            text_data = form_data[value_name]
                            data_obj = {'type': 'text', 'content' : text_data}
                    elif value_name.endswith('.dropdown'):
                        drop_data = form_data[value_name]
                        arr_d = literal_eval(form_data['selection'])[key_name]
                        data_obj = {'type': 'dropdown', 'content': drop_data, 'values' : arr_d}
                    elif value_name.endswith('.checkbox'):
                        cl = request.form.getlist(value_name)
                        check_data = []
                        arr_c = literal_eval(form_data['checkbox'])[key_name]
                        for ch in cl:
                            i = int(ch[6:])
                            check_data.append(arr_c[i])
                        data_obj = {'type': 'checkbox', 'content': check_data, 'values' : arr_c}
                    else:
                        cr = request.form.get(value_name)
                        arr_r = literal_eval(form_data['radio'])[key_name]
                        radio_data = arr_r[int(cr[6:])]
                        data_obj = {'type' : 'radio', 'content' : radio_data, 'values' : arr_r}
                form[key] = data_obj

        node_collection = client['kali_db']['kali_node']
        wf_collection = client['kali_db']['kali_wf']
        file_collection = client['kali_db']['kali_files']
        
        # store data in data_collection db and circulate the urls instead of the full file content
        # insert the job in workflow
        print ('insertion is being fired')
        if form['jobid']['content'] == 0:
            temp1 = GetNextJobId(node_collection)
            temp2 = GetNextJobId(wf_collection)
            jobid = max(temp1, temp2)
            form['jobid']['content'] = jobid
            form['nstatus'] = {'type': 'text', 'content': 'pending'}
            for file in files:
                file['jobid'] = jobid
            q1 = node_collection.insert_one(form)
        else:
            jobid = form['jobid']['content']
            q2 = wf_collection.insert_one(form)
            #now to delete the job from node table
            q3 = node_collection.delete_one({'jobid.content': jobid})
            
        if len(files)!=0:
            q1 = file_collection.insert_many(files)      

    except:
        pass
    return 'processed POST request via form'   

@app.route('/wfe/wf/strsubmit1', methods=['GET','POST'])
def wf_strsubmit1() :
    data = request.form.to_dict()
    mydata = {}
    for key in data:
        value = {'type' : 'text', 'content' : data[key] }
        # general
        if key == 'job_name':
            mydata['job_name'] = value
        if key == 'role':
            mydata['role'] = value
        if key == 'node':
            mydata['nodeid'] = value
        # add drop course
        if key =='add_course_1':
            mydata['add_course_1'] = value
        if key == 'drop_course_1':
            mydata['drop_course_1'] = value
        if key =='add_course_2':
            mydata['add_course_2'] = value
        if key == 'drop_course_2':
            mydata['drop_course_2'] = value
        # for course registration 
        if key =='course_register_1':
            mydata['course_register_1'] = value
        if key =='course_register_2':
            mydata['course_register_2'] = value
        if key =='course_register_3':
            mydata['course_register_3'] = value
        if key =='course_register_4':
            mydata['course_register_4'] = value
        if key =='course_register_5':
            mydata['course_register_5'] = value
        if key =='course_register_6':
            mydata['course_register_6'] = value
        if key =='faculty_advisor':
            mydata['faculty_advisor'] = value

        # For invigilation
        if key =='exam':
            mydata['exam'] = value
        if key =='date':
            mydata['date'] = value
        if key =='time':
            mydata['time'] = value
        if key =='invigilator':
            mydata['invigilator'] = value
        if key =='paper_given_to_profs':
            mydata['paper_given_to_profs'] = value
        if key =='accepted':
            mydata['accepted'] = value
        if key =='ans_sheets_returned':
            mydata['ans_sheets_returned'] = value
    mydata['nstatus']={'type' : 'text', 'content' : 'pending'}

    #this data to fly to database as well
    # make connection with mongodb
    try:
        client= MongoClient('localhost',27017)
        node_collection = client['kali_db']['kali_node']
        wf_collection = client['kali_db']['kali_wf']

        temp1 = GetNextJobId(node_collection)
        temp2 = GetNextJobId(wf_collection)
        mydata['jobid'] = {'type': 'text', 'content' : max(temp1,temp2) }
        #print(mydata)
        # insert the job in workflow
        print ('insertion is being fired')
        q1 = node_collection.insert_one(mydata)
        print ('query1',q1)
    except:
        pass
            #end try-except
    return 'processed GET request via dict'

@app.route('/wfe/wf/invigilation', methods=['GET','POST'])
def wf_invigilation() :
    data = request.form.to_dict()
    mydata = {}
    mydata['nstatus']={'type' : 'text', 'content' : 'pending'}
    for key in data:
        value = {'type' : 'text', 'content' : data[key] }
        # general
        if key == 'job_name':
            mydata['job_name'] = value
        if key == 'role':
            mydata['role'] = value
        if key == 'node':
            mydata['nodeid'] = value
        if key =='exam':
            mydata['exam'] = value
        if key =='date':
            mydata['date'] = value
        if key =='time':
            mydata['time'] = value
        if key =='invigilator':
            mydata['invigilator'] = value
    mydata['accepted'] = {'type' : 'radio', 'content' : 'no', 'values':['yes','no'] }
    mydata['papers_given_to_invigilator'] = {'type' : 'radio', 'content' : 'no', 'values':['yes','no'] }
    mydata['ans_sheets_returned'] = {'type' : 'radio', 'content' : 'no', 'values':['yes','no'] }
    #this data to fly to database as well
    # make connection with mongodb
    try:
        client= MongoClient('localhost',27017)
        node_collection = client['kali_db']['kali_node']
        wf_collection = client['kali_db']['kali_wf']

        temp1 = GetNextJobId(node_collection)
        temp2 = GetNextJobId(wf_collection)
        mydata['jobid'] = {'type': 'text', 'content' : max(temp1,temp2) }
        #print(mydata)
        # insert the job in workflow
        print ('insertion is being fired')
        q1 = node_collection.insert_one(mydata)
        print ('query1',q1)
    except:
        pass
            #end try-except
    return 'processed GET request via dict'



@app.route('/getjobs', methods=['GET'])
def getjobs() :

    nid = request.args.get('nodeid')
    print(nid)
    joblist = {}

    try :

        client= MongoClient('localhost',27017)
        node_collection = client['kali_db']['kali_node']
        wf_collection = client['kali_db']['kali_wf']
        
        for x in node_collection.find({"nodeid":{'type':'text','content':nid},'nstatus':{'type':'text' ,'content':'pending'}}):
            #print(x)
            joblist[x['role']['content']]=[]

        for row in node_collection.find({"nodeid":{'type':'text','content':nid},'nstatus':{'type':'text' ,'content':'pending'}}):
            #print(row)
            joblist[row['role']['content']].append(row['jobid']['content'])
            #joblist.append(row['jobid']['content'])
       

        print ('after execution')
        print ('joblist',joblist)

    except :
        pass
    #end try-except

    # return ','.join([str(x) for x in joblist]) #this works, but we show in a better way
    return render_template('node_jobs.html',joblist=joblist)
    
@app.route('/renderjob',methods=['GET'])
def renderjob() :
    
    #job id type
    jid = int(request.args.get('jobid'))
    #print(type(jid))
    retdict = {}
    readonly = []
    hidden = []
    #to actually get data from database table and load the template
  
    client= MongoClient('localhost',27017)
    node_collection = client['kali_db']['kali_node']
    wf_collection = client['kali_db']['kali_wf']

    for row in node_collection.find({'jobid.content': jid}):
        del row['_id']
        readonly = []
        hidden = []
        try:
            readonly = row['read_only']
            hidden = row['hide']
            del row['read_only']
            del row['hide']    
        except:
            pass
        retdict = row
        print('Displayed job: ',row['jobid']['content'])
        #print(retdict)
        break
   
    return render_template('wf_renderer.html',data = retdict, readonly=readonly, hidden = hidden)

if __name__ == '__main__':
    app.run(port='5000',debug=True)

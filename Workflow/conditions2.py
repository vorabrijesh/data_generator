from pymongo import MongoClient

def conditionHandler(curr):
    currNode = curr['nodeid']['content']
    currMsg = {}
    client = MongoClient('localhost',27017)
    student_collection = client['kali_db']['students']
    if curr['role']['content'] == 'course_registration':
        if(currNode == 'academics'):
            batch = curr['batch']['content']
            branch = curr['branch']['content']
            student_nodes = []
            student_names = {}
            faculty_advisors = {}
            for student in student_collection.find({'batch':batch,'branch':branch}):
                rollno = student['rollno']
                student_nodes.append(rollno)
                faculty_advisors[rollno] = student['faculty_advisor']
                student_names[rollno] = student['student_name']
            currMsg['hide'] = ['nstatus','nodeid']
            currMsg['read_only'] = ['role', 'faculty_advisor', 'batch', 'branch', 'student_name', 'rollno']
            currMsg['student_names'] = student_names
            currMsg['faculty_advisors'] = faculty_advisors
            currMsg['file'] = ''
            return student_nodes, currMsg
        elif currNode in student_collection.distinct('rollno'):
            faculty_node = curr['faculty_advisor']['content']
            currMsg['hide'] = ['nstatus', 'registration_form','nodeid']
            currMsg['read_only'] = ['nodeid', 'role', 'faculty_advisor','batch', 'branch', 'student_name', 'rollno']
            currMsg['file'] = ''
            currMsg['rollno'] = currNode
            return [faculty_node], currMsg
        elif currNode in student_collection.distinct('faculty_advisor'):
            currMsg['hide'] = ['nstatus', 'unsigned_form', 'registration_form', 'nodeid']
            currMsg['read_only'] = ['nodeid', 'role', 'faculty_advisor','batch', 'branch', 'student_name', 'rollno']
            currMsg['role'] = 'course_registration_forms'
            return ['academics'], currMsg
        else:
            return None, currMsg
    elif curr['role']['content'] == 'course_registration_forms':
        if(currNode == 'academics'):
            currMsg['hide'] = ['nstatus']
            currMsg['read_only'] = ['nodeid', 'role', 'faculty_advisor', 'batch', 'branch', 'student_name', 'rollno']
            return ['logs'], currMsg
        else:
            return None, currMsg
    elif curr['role']['content'] == 'course_add_drop':
        course_collection = client['kali_db']['courses']
        if(currNode == 'academics'):
            student_nodes = []
            student_names = {}
            faculty_advisors = {}
            for student in student_collection.find():
                rollno = student['rollno']
                student_nodes.append(rollno)
                faculty_advisors[rollno] = student['faculty_advisor']
                student_names[rollno] = student['student_name']
            currMsg['hide'] = ['nstatus','nodeid']
            currMsg['read_only'] = ['role', 'faculty_advisor', 'student_name', 'rollno']
            currMsg['student_names'] = student_names
            currMsg['faculty_advisors'] = faculty_advisors
            currMsg['file'] = ''
            return student_nodes, currMsg
        elif currNode in student_collection.distinct('rollno'):
            advisor_node = curr['faculty_advisor']['content']
            currMsg['rollno'] = currNode
            currMsg['hide'] = ['nstatus','nodeid', 'add_drop_form']
            currMsg['read_only'] = ['role', 'faculty_advisor','student_name', 'rollno', 'send_to_faculty_advisor', 'course_name', 'course_instructor']
            currMsg['file'] = ''
            if curr['send_to_faculty_advisor']['content'] == 'No':
                instructor_node = curr['course_instructor']['content']
                if 'signed_add_drop' in curr:
                    print('checking...')
                    currMsg['file'] = curr['signed_add_drop']['content']
                currMsg['faculty_advisor'] = 'no'
                return [instructor_node], currMsg
            else:
                currMsg['hide'].append('signed_add_drop')
                currMsg['file'] = curr['signed_add_drop']['content']
                currMsg['faculty_advisor'] = 'yes'
                return [advisor_node], currMsg
        elif currNode in course_collection.distinct('course_instructor') and curr['send_to_faculty_advisor']['content'] == 'No':
            student_node = curr['rollno']['content']
            currMsg['hide'] = ['nstatus','nodeid', 'unsigned_add_drop']
            currMsg['read_only'] = ['role', 'faculty_advisor','student_name', 'rollno']
            currMsg['file'] = curr['signed_add_drop']['content']
            return [student_node], currMsg
        elif currNode in student_collection.distinct('faculty_advisor') and curr['send_to_faculty_advisor']['content'] == 'Yes':
            currMsg['role'] = 'add_drop_forms'
            currMsg['hide'] = ['nstatus','nodeid','unsigned_add_drop', 'signed_add_drop', 'course_name', 'course_instructor']
            currMsg['read_only'] = ['role', 'faculty_advisor','student_name', 'rollno', 'send_to_faculty_advisor']
            return ['academics'], currMsg
        else:
            return None, currMsg
    elif curr['role']['content'] == 'add_drop_forms':
        if(currNode == 'academics'):
            currMsg['hide'] = ['nstatus']
            currMsg['read_only'] = ['nodeid', 'role', 'faculty_advisor', 'student_name', 'rollno', 'unsigned_add_drop', 'signed_add_drop','course_name', 'course_instructor']
            return ['logs'], currMsg
        else:
            return None, currMsg
    else:
        return None, currMsg
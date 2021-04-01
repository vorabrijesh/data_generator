# run this file first for inserting sample docs into the collection
from pymongo import MongoClient

client = MongoClient('localhost',27017)
student_collection = client['kali_db']['students']
course_collection = client['kali_db']['courses']
files = client['kali_db']['kali_files']

docs = [
    {'rollno': 'B123', 'student_name': 'Abc', 'batch': 'B.tech-2017', 'semester': 'VIII', 'branch': 'Computer_Science_and_Engineering','faculty_advisor': 'advisor1'},
    {'rollno': 'M456', 'student_name': 'Def', 'batch': 'M.tech-2019', 'semester': 'II', 'branch': 'Civil_Engineering','faculty_advisor': 'advisor2'},
    {'rollno': 'B789', 'student_name': 'Ghi', 'batch': 'B.tech-2018', 'semester': 'VI', 'branch': 'Electrical_Engineering','faculty_advisor': 'advisor3'},
    {'rollno': 'B321', 'student_name': 'Jkl', 'batch': 'B.tech-2019', 'semester': 'IV', 'branch': 'Chemical_Engineering','faculty_advisor': 'advisor1'},
    {'rollno': 'B543', 'student_name': 'Mno', 'batch': 'B.tech-2017', 'semester': 'VIII', 'branch': 'Computer_Science_and_Engineering','faculty_advisor': 'advisor2'},
    {'rollno': 'B765', 'student_name': 'Pqr', 'batch': 'B.tech-2017', 'semester': 'VIII', 'branch': 'Mechanical_Engineering','faculty_advisor': 'advisor3'},
    {'rollno': 'M123', 'student_name': 'Stu', 'batch': 'M.tech-2018', 'semester': 'IV', 'branch': 'Civil_Engineering','faculty_advisor': 'advisor1'},
    {'rollno': 'M987', 'student_name': 'Vwx', 'batch': 'M.tech-2019', 'semester': 'II', 'branch': 'Computer_Science_and_Engineering','faculty_advisor': 'advisor2'},
]
x = student_collection.insert_many(docs)
print("8 rows inserted")

docs2 = [
    {'course_id':'123', 'course_name':'course_1', 'course_instructor':'instructor_1'},
    {'course_id':'456', 'course_name':'course_2', 'course_instructor':'instructor_2'},
    {'course_id':'789', 'course_name':'course_3', 'course_instructor':'instructor_3'},
    {'course_id':'987', 'course_name':'course_4', 'course_instructor':'instructor_4'},
    {'course_id':'654', 'course_name':'course_5', 'course_instructor':'instructor_1'},
    {'course_id':'321', 'course_name':'course_6', 'course_instructor':'instructor_2'}
]
y = course_collection.insert_many(docs2)


print("6 rows inserted")
# files.delete_many({})


from fastapi import FastAPI,HTTPException,Path,Query
import json
import math

app=FastAPI()

# helper function
def load_data():
    with open("students.json","r") as file:
        return json.load(file)

@app.get('/student')
def student():
    return load_data()

# student_id-> This is our Path Parameter.
@app.get("/student/{student_id}")
def get_id(student_id:str = Path(...,description="The Id of the student", examples=["S001"])):
    data=load_data()
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Student with Id '{student_id}' not found"
        )
    return data[student_id]


@app.get('/filter')
def filter_student(course:str=Query(None, description="show only students in this course",examples=["Python"])):
    data=load_data()
    if course is None:
        return data

    # Because we need a separate dictionary to store only students who belong to the requested course
    #data.items() gives us both the key and value of every dictionary entry
    filtered={}
    for student_id, info in data.items():
        if info["course"]==course:
            filtered[student_id]=info
    return filtered


SORT_FIELDS = ["marks", "age", "name"]
SORT_ORDERS =["asc","desc"]

@app.get('/sort')
def sort_students(
    sort_by:str = Query(None, description="Sort by marks, name, age", examples=["marks"]),
    order:str = Query(None, description="asc or desc", examples=["asc","desc"])
):
    # if the given sort_by input doesn't belongs to any(marks, age, name) we will raise an error
    if sort_by not in SORT_FIELDS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid sort_by  '{sort_by}, choose from {SORT_FIELDS}"
        )

        # if the given order input doesn't belongs to any(asc,desc) we will raise an error
    if order not in SORT_ORDERS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid order '{order}.Choose from {SORT_ORDERS}"
        )

    data=load_data()

    # step-1 Turn the dictionary into a list, putting the ID inside each student
    student=[]
    for student_id, info in data.items():
        info["id"]=student_id
        student.append(info)

    # step-2 sort the list by the choosen field
    reverse=(order=="desc") 
    sorted_students=sorted(student,key=lambda s: s[sort_by], reverse=reverse)

    return sorted_students


'''
PAGINATION
http://127.0.0.1:8000/pagination?page=1&limit=2

page->which page you want
limit->how many students(records) on one page

Formula
start=(page-1)*limit
end=start+limit

'''

@app.get("/paginate")
def paginate_student(page:int=Query(1, ge=1), description="Which page you want (start from 1)" , limit:int=Query(2, ge=1, le=100, description="How many students on one page(1 to 100)")):
    data=load_data()

    # Turn the dictionary into a list, putting the ID inside each student
    student=[]
    for student_id, info in data.items():
        info['id']=student_id
        student.append(info)

    start=(page-1)*limit
    end=start+limit

    page_student=student[start:end]
    total_students=len(student)
    return {
        "page":page,
        "limit":limit,
        "total_students":total_students,
        "students":page_student
    }
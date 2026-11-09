from fastapi import FastAPI,HTTPException,Path,Query
from pydantic import BaseModel,Field,EmailStr,field_validator,computed_field
import json

app=FastAPI()


# helper function 1
def load_data():
    with open("students.json","r") as file:
        return json.load(file)
# json mei jana aur jo bhi uska content hai usko read kar ana aur usko store karna

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

# Helper function 2
def save_data(data):
    with open("students.json","w") as file:
        json.dump(data, file, indent=4)  #indent=4 keeps the file readable


'''
REQUEST BODY

POST-> data comes in the BODY( a JSON sent with the request )

when a function argument is a pydantic model, FastAPI reads it from the body and validates autoimatically , Bad data->422

'''


class Student(BaseModel):
    id:str = Field(..., examples=["S001"])
    name:str = Field(...,min_length=2, max_length=50)
    age:int = Field(...,gt=0, le=100)
    course:str = Field(...,max_length=50)
    marks:int = Field(...,ge=0, le=100)
    email:EmailStr

    # Custom rule: nam emust contain only letters and spaces
    @field_validator("name")
    @classmethod
    def check_name(cls, value):  #value="name"
        if not value.replace(" ", "").isalpha():
            raise ValueError("letters and spaces")
        return value.title()

# 2.computed field-> a value Pydantic calculates for us

    @computed_field
    @property
    def grade(self) ->str:
        if self.marks>=90:
            return "A+"
        elif self.marks>=80:
            return "A"
        elif self.marks>=70:
            return "B"
        elif self.marks>=60:
            return "C"
        else:
            return "Fail"

s=Student(id="S001",
        name="aarav sharma",
        age=8,
        course="Python",
        marks=88,
        email="aarav@gmail.com" )

@app.post('/create', status_code=201)
def create_student(student:Student):
    data=load_data()

    if student.id in data:
        raise HTTPException(
            status_code=400,
            detail=f"Student with Id '{student.id}' already exist"
        )
    
    data[student.id]=student.model_dump(exclude={"id", "grade"})
    save_data(data)
    return {"message":"Student created Successfully", "student":student}




class StudentUpdate(BaseModel):
    name:str | None = Field(None, min_length=2, max_length=50)
    age:int | None = Field(None, gt=0, lt=100)
    course:str | None = Field(None, max_length=50)
    marks:int | None = Field(None, ge=0, le=100)
    email:EmailStr | None = None

# PUT-updating the existing data
@app.put("/update/{student_id}")
def update_student(
    student_update: StudentUpdate,
    student_id:str = Path(..., description="The Id of the student", examples=["S001"])
):
    data=load_data()
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Student with Id '{student_id}' not found"
        )

    # step 1: The student as it is right now.
    # we are extracting the information of the particular student we want to update
    existing=data[student_id]  #S001

    # step 2: Only the fields the client actually sent
    update=student_update.model_dump(exclude_unset=True)
    # jo cheez user bheej raha hai woh object form mei hai hum usey dictionary mei convert kar rahe hai

    # step 3: COPY the new value on the top of old value
    for key, value in update.items():
        existing[key]=value



    # step final: check the student again
    student=Student(id=student_id, **existing) #Student hamare class hai aur yeh object form mei data expect karti hai
    data[student_id]=student.model_dump(exclude=["id", "grade"])
    save_data(data)
    return {"Message":"Student updated successfully","student":student}



# delete
@app.delete('/delete/{student_id}')
def delete_student(
    student_id:str = Path(..., description="The Id of the student", examples=["S001"])
):
    data=load_data()
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Student with id '{student_id}' not found"
        )
    del data[student_id] #data[S007]
    save_data(data)
    return{"message": f"Student '{student_id}' deleted successfully"}
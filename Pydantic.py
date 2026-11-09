from fastapi import FastAPI
from pydantic import BaseModel,Field,EmailStr,field_validator,computed_field
import json

app=FastAPI()

'''
STEP-1-THE PROBLEM
a normsl dictionary accepts anything. Nobody checks the data.
'''

# class SimpleStudent(BaseModel):
#     name:str
#     age:int
#     marks:int

'''
STEP 2- BASEMODEL + TYPE HINTS checks every student against it.
'''

# s=SimpleStudent(name="Arav Sharma", age="21", marks=80)
# print(s.name, s.age, s.marks)

'''
STEP 3 - FIELD() RULES

gt=greater than          lt=less than
ge=greater or equal      le=less or equal
'''

# class RuleStudent(BaseModel):
#     name:str = Field(...,min_length=2, max_length=50) #...=required
#     age:int = Field(..., gt=0, lt=100)                #1to 99
#     marks:int = Field(..., gt=0, le=100)
#     course:str ="Python"                               #default value=python
#     phone:str |None=None

# s=RuleStudent(name="Rohan Verma", age=21, marks=77)
# print(s.name, s.age, s.marks)
# print(s.course)
# print(s.phone)




'''
STEP 4-EMAILSTR
checks the text really looks like an email.
'''
# class EmailStudent(BaseModel):
#     name:str
#     email:EmailStr

# s=EmailStudent(name="Kabir Singh", email="kabirsingh30@gmail.com")
# print(s.name)
# print(s.email)


'''
STEP 5-FINAL STUDENT MODEL
1.field_validator ->our own custom rule
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

# print(s.id)
# print(s.name)
# print(s.age)
# print(s.course)
# print(s.marks)
# print(s.email)
# print(s.grade)

'''
STEP 6 MODEL_DUMP()
tura a model back into python dictionary(so that we can save it later)
model_dump kisi bhi object ko dictionary mei convert kar deta hai so it can easily be stored in our database
'''

data=s.model_dump()
print(data)


'''
STEP 7-check our deal data(students.json)
Every student in our file will go through the student model
'''

with open("students.json","r") as file:
    raw=json.load(file)
# print(raw)

for student_id, info in raw.items():
    s=Student(id=student_id, **info)
    print(s.id, s.name, s.grade)

# unpacking = kabhi bhi dictionary ko khol ke object ko bheeja jata hai verify karne ko tab usey unpacking khetey hai
# ** - it is used for unpacking
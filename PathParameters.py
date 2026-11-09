from fastapi import FastAPI,HTTPException,Path
import json

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
from fastapi import FastAPI
import json


app=FastAPI()

''''
HTTP Method:
1. GET-> to just show or display any message on the website or the page or on the application
'''

@app.get('/') 
def greet():
    return {"Hello and Welcome to Sheryians AI School"}

@app.get('/hello')
def hello():
    return {"This is hello page"}

# helper function 
def load_data():
    with open("students.json","r") as file:
        return json.load(file)
# json mei jana aur jo bhi uska content hai usko read kar ana aur usko store karna

@app.get('/student')
def student():
    return load_data()
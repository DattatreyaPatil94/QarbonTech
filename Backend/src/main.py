from schema import req_body,resp_body,cust_req,cust_resp,patch_resp,book_req,status_choose
from typing import Annotated, Union,Optional
import json
import string
import secrets
from fastapi import FastAPI, Query,Path,Body,HTTPException,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from datetime import datetime,date,timedelta
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel,Field
from enum import Enum
from datetime import datetime,date,timedelta

app=FastAPI()

# class patch_req:
#     def __init__(self,seat_no:str
#     name:Optional[str]=Query(default=None), email:str=Query(min_length=3,max_length=30,regex=r"^[a-zA-Z0-9\.+_]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
#     payment_method:pay or None=None,
#     price:int or None=None):
#         self.seat_no:seat_no
#         name:str or None=None
#         email:str=Query(min_length=3,max_length=30,regex=r"^[a-zA-Z0-9\.+_]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
#         payment_method:pay or None
#         price:int or None=None

def create_response_json(unique_id, data_dict, file_location):
    
    try:
        with open(file_location, 'r') as file:
            existing_data = json.load(file)
    except Exception:
        existing_data = {}
    
    existing_data[unique_id] = data_dict
    
    try:
        with open(file_location, 'w') as file:
            json.dump(existing_data, file, indent=4)

    except Exception as e:
        print(f"An error occurred while writing to {file_location}: {e}")
    return existing_data

#function to autogenerate id
def generate_id():
    char=string.ascii_letters+string.digits
    length=secrets.randbelow(4)+2
    random_id="".join(secrets.choice(char) for _ in range(length))
    return random_id

path="C:/Users/DPatil/Backend/response/response.json"

path1="C:/Users/DPatil/Backend/response/cust_billing.json"
path2="C:/Users/DPatil/Backend/response/books.json"

@app.post("/movie_details/",response_model=resp_body,tags=['movie_details'])
async def add_details(mv:req_body):
    k=jsonable_encoder(mv)
    id=generate_id()
    k["id"]=id
    release=datetime.now()+timedelta(days=10)
    k["release_date"]=jsonable_encoder(release)
    delta=int(k["release_date"][8:10])-int(k["current_date"][8:10])
    days_after_r=delta
    k["Days_after_release"]=days_after_r
    a=create_response_json(id,k,path)
   
    return k

@app.post("/customer_booking/",response_model=cust_resp,tags=['cust_booking'])
async def cust_details(cust:cust_req):
    data=jsonable_encoder(cust)
    cust_id=generate_id()
    data["id"]=cust_id
    data["payment_status"]="confirmed"
    create_response_json(cust_id,data,path1)
    return data

@app.get("/get_by_cust/{id}",tags=['cust_booking'])
async def get_cust_details(id:str):
    
        try:
            with open(path1,"r") as file:
                
                cust_data=json.load(file)
                
                if id in cust_data:
                    return cust_data[id]
                else:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="id not found")
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="file not found")
        
@app.get("/get_by_list/",tags=['movie_details'])
async def get_l(title:Optional[str]=Query(default=None),
                seat_no:Optional[str]=Query(default=None),
                status:Optional[status_choose]=Query(default=None),
                offset:Optional[int]=Query(default=None),limit:Optional[int]=Query(default=10)):
    if offset is not None and offset<0:
        raise HTTPException(status_code=400,detail="offset cannot be negative")
    if limit is not None and limit<0:
        raise HTTPException(status_code=400,detail="limit cannot be negative")
    if offset is None:
        offset=0
    if limit is None:
        limit=0
    try:
        with open(path,"r") as file:
            data1=json.load(file)
    except Exception:
        raise HTTPException(status_code=404,detail="file not found")
    exc_data=[]
    for _,movie_details in data1.items():
        json_title=movie_details.get("title")
        for i in range(len(movie_details.get("seats"))):
            json_seat=movie_details.get("seats")[i]["seat_no"]
            json_status=movie_details.get("seats")[i]["status"]
        
        if (title==json_title or title==None) and (seat_no==json_seat or seat_no==None) and (status==json_status or status==None):
            extracted={
                "title":movie_details.get("title"),
                "genre":movie_details.get("genre"),
                "current_date":movie_details.get("current_date"),
                "seats":movie_details.get("seats"),
                "duration":movie_details.get("duration"),
                "id":movie_details.get("id"),
                "Days_after_release":movie_details.get("Days_after_release"),
                "release_date":movie_details.get("release_date")
            }
            exc_data.append(extracted)
    response=exc_data[offset:offset+limit]
    if not response or not exc_data:
        raise HTTPException(status_code=404,detail="no matching record found")
    return response


@app.delete("/remove/{seat_no}",tags=['cust_booking'])
async def del_ele(seat_no:str):
    try:
        with open(path1,"r") as file1:
            k=json.load(file1)
            for i,cust_details in k.items():
                if seat_no in cust_details["seat_no"]:
                    k.pop(i)
                    
                    with open(path1,"w") as file2:
                        json.dump(k,file2,indent=4)
                        
                    try:
                        with open(path,"r") as f3:
                            d=json.load(f3)
                            for j,details in d.items():
                                seat_d=details.get("seats")
                                for k in range(len(seat_d)):
                                    if d[j]["seats"][k]["seat_no"]==seat_no:
                                        d[j]["seats"][k]["status"]="available"
                            with open(path,"w") as f4:
                                json.dump(d,f4,indent=4)
                    except Exception:
                        raise HTTPException(status_code=404,detail="file not found")
                    return {"data":"removed successfully"}
            else:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"seat_no":"not found"})
    except Exception:
        raise HTTPException(status_code=404,detail='file not found')
    
@app.patch("/update/{item_id}",tags=["cust_booking"],response_model=patch_resp)
async def updating(item_id:str,details:patch_resp):
    try:
        with open(path1,"r") as f1:
            json_detail=json.load(f1)

            if item_id in json_detail:
                
                a=json_detail[item_id]["name"]
                b=json_detail[item_id]["payment_method"]
                c=json_detail[item_id]["price"]

                con=jsonable_encoder(details)
                json_detail[item_id]=con
                if json_detail[item_id]["name"]==None:
                    json_detail[item_id]["name"]=a
                if json_detail[item_id]["payment_method"]==None:
                    json_detail[item_id]["payment_method"]=b

                if json_detail[item_id]["price"]==None:
                    json_detail[item_id]["price"]=c
                
                with open(path1,"w") as f2:
                    
                    json.dump(json_detail,f2,indent=4)
                    return json_detail[item_id]
            else:
                
              return  JSONResponse(status_code=404,content="id invalid")
        
    except:
        raise HTTPException(status_code=404,detail='file not found')
    
@app.post("/add_books/",tags=["books"])
async def add_books(books:book_req):
    data=jsonable_encoder(books)
    book_id=generate_id()
    data["id"]=book_id
    create_response_json(book_id,data,path2)
    return data

@app.get("/get_by_id/{book_id}",tags=['books'])
async def get_book_details(book_id:str):
    
        try:
            with open(path2,"r") as file:
                
                book_data=json.load(file)
                
                if book_id in book_data:
                    return book_data[book_id]
                else:
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="id not found")
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="file not found")

@app.delete("/delete_books/{book_id}",tags=['books'])
async def del_books(book_id:str):
    try:
        with open(path2,"r") as file1:
            k=json.load(file1)
            if book_id in k:
                k.pop(book_id)
                with open(path2,"w") as file2:
                    json.dump(k,file2,indent=4)
                return {"book":"removed successfully"}
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"book_id":"not found"})
    except Exception:
        raise HTTPException(status_code=404,detail='file not found')

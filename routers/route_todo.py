from fastapi import APIRouter
from fastapi import Response,Request,HTTPException,Depends
from fastapi.encoders import jsonable_encoder
from schemas import Todo,TodoBody,SuccessMsg
from database import db_create_todo,db_get_single_todo,db_get_todos,db_delete_todo,db_update_todo
from starlette.status import HTTP_201_CREATED,HTTP_200_OK
from typing import List
from pan import read_csv
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()


@router.post("/api/todo",response_model=Todo) #resで返却されるデータ型Todoを設定。schemas.py からimportしておく
#client->json（Todo）で渡ってくる#dataがjsonなので
async def create_todo(request: Request,response:Response,data:TodoBody, csrf_protect: CsrfProtect = Depends()):#reqとresの型はあらかじめfastapiで決まっている
  new_token = auth.verify_csrf_update_jwt(request,csrf_protect,request.headers)
  print("new_token",new_token)
  todo = jsonable_encoder(data) #dataのjson型をdict型に変換して
  res = await db_create_todo(todo) #dictで受け取ってdictで返す
  print("res",res)
  
  response.status_code= HTTP_201_CREATED
  response.set_cookie(
    key="access_token",value=f"Bearer{new_token}",httponly=True,samesite="none",secure=True
  )
  if res:
    return res
  raise HTTPException(
    status_code=404,detail="create task failed"
  )

@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request:Request):
  # auth.verify_jwt(request)
  res = await db_get_todos()
  return res

@router.get("/api/todo/{id}",response_model=Todo) #{id}のことをパスパラメータという
async def get_single_todo(id:str):
  res = await db_get_single_todo(id)
  if res:
    return res
  raise HTTPException(status_code=404,detail=f"Task of ID:{id} doesn't exist")



@router.put("/api/todo/{id}",response_model=Todo) 
async def update_todo(id:str,data:TodoBody):#リクエストをjsonで受け取る
  todo = jsonable_encoder(data) #dictに変換
  res = await db_update_todo(id,data) #dictに変換したdataをdatabase.pyに渡す。返却はdict
  if res:
    return res
  raise HTTPException(
    status_code=404,detail="create task failed"
  )


@router.delete("/api/todo/{id}",response_model=SuccessMsg) 
async def delete_todo(id:str):
  res = await db_delete_todo(id) 
  if res:
    return {"message": "Successfully deleted"}
  raise HTTPException(
    status_code=404,detail="Delete task failed"
  )

'''
@router.get("/api/csv")
async def get_csv():
  res = await read_csv()
  return res
'''
  
  
  

  
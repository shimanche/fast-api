from fastapi import APIRouter
from fastapi import Response,Request,HTTPException,Depends
from fastapi.encoders import jsonable_encoder
from schemas import Todo,TodoBody,SuccessMsg
from database import db_create_todo,db_get_single_todo,db_get_todos,db_delete_todo,db_update_todo
from starlette.status import HTTP_201_CREATED,HTTP_200_OK
from typing import List
# from pan import read_csv
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()


@router.post("/api/todo",response_model=Todo) #resで返却されるデータ型Todoを設定。schemas.py からimportしておく
#client->json（Todo）で渡ってくる#dataがjsonなので
async def create_todo(request: Request,response:Response,data:TodoBody, csrf_protect: CsrfProtect = Depends()):#reqとresの型はあらかじめfastapiで決まっている
  new_token = auth.verify_csrf_update_jwt(request,csrf_protect,request.headers)
  #csrfとjwtの認証が問題なければ以下を実行する。エラーがあれば例外処理で終了する
  print("new_token",new_token)
  todo = jsonable_encoder(data) #dataのjson型をdict型に変換して
  res = await db_create_todo(todo) #dictで受け取ってdictで返す
  print("res",res)
  
  response.status_code= HTTP_201_CREATED
  
  #新しく生成したnew_tokenでクッキーを更新する
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
  auth.verify_jwt(request)
  res = await db_get_todos()
  return res

@router.get("/api/todo/{id}",response_model=Todo) #{id}のことをパスパラメータという
async def get_single_todo(request: Request,response:Response,id:str):
  new_token,_ = auth.verify_update_jwt(request)
  print("async def get_single_todo =>",auth.verify_update_jwt(request))
  response.set_cookie(
    key="access_token",value=f"Bearer{new_token}",httponly=True,samesite="none",secure=True
  )  
  res = await db_get_single_todo(id)
  if res:
    return res
  raise HTTPException(status_code=404,detail=f"Task of ID:{id} doesn't exist")



@router.put("/api/todo/{id}",response_model=Todo) 
async def update_todo(request: Request,response:Response,id:str,data:TodoBody,csrf_protect: CsrfProtect = Depends()):#リクエストをjsonで受け取る
  new_token = auth.verify_csrf_update_jwt(request,csrf_protect,request.headers)
  todo = jsonable_encoder(data) #dictに変換
  res = await db_update_todo(id,data) #dictに変換したdataをdatabase.pyに渡す。返却はdict
  response.set_cookie(
  key="access_token",value=f"Bearer{new_token}",httponly=True,samesite="none",secure=True
)
  if res:
    return res
  raise HTTPException(
    status_code=404,detail="create task failed"
  )


@router.delete("/api/todo/{id}",response_model=SuccessMsg) 
async def delete_todo(request: Request,response:Response,id:str,data:TodoBody,csrf_protect: CsrfProtect = Depends()):
  new_token = auth.verify_csrf_update_jwt(request,csrf_protect,request.headers)
  res = await db_delete_todo(id) 
  response.set_cookie(
  key="access_token",value=f"Bearer{new_token}",httponly=True,samesite="none",secure=True
)
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
  
  
  

  
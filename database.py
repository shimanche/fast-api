from decouple import config
from fastapi import HTTPException
import motor.motor_asyncio
from typing import Union
from bson import ObjectId
from auth_utils import AuthJwtCsrf
import asyncio

MONGO_API_KEY = config('MONGO_API_KEY') #パッケージをインポートしてconfig('SECRET_KEY')のようにして.envから値を読み込む。

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.API_DB
collection_todo = database.todo
collection_user = database.user
auth = AuthJwtCsrf()

def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"]
    }
def user_serializer(user) -> dict:
  return{
    "id":str(user["_id"]),
    "email":user["email"],
  }

async def db_create_todo(data:dict) -> Union[dict, bool]: # 引数辞書型、返り値辞書型
  todo = await collection_todo.insert_one(data) #motorの返り値は insert_oneクラスのインスタンス
  new_todo = await collection_todo.find_one({"_id":todo.inserted_id }) #上記で作ったtodoのインスタンスに.inserted_idでアクセスするとidが取得できる
  #上記の返り値は、trueなら値。falseならNoneが返却される.ただし、値のidがMongoの特殊なobjectIDなのでそれを辞書型で返す関数を定義する

  if new_todo: 
    return todo_serializer(new_todo)
  return  False

async def db_get_todos() -> list:
  todos = []
  for todo in await collection_todo.find().to_list(length=100):
    todos.append(todo_serializer(todo))
  return todos

async def db_get_single_todo(id:str) -> Union[dict, bool]: # 引数辞書型、返り値辞書型
  todo = await collection_todo.find_one({"_id":ObjectId(id)})
  if todo: 
    return todo_serializer(todo)
  return  False

async def db_update_todo(id:str, data:dict) -> Union[dict, bool]: # 引数辞書型、返り値辞書型
  find_todo = await collection_todo.find_one({"_id":ObjectId(id)})
  if find_todo:
    update_todo = await collection_todo.update_one({"_id":ObjectId(id)},{"$set":data})
    if (update_todo.modified_count > 0):
        todo = await collection_todo.find_one({"_id":ObjectId(id)})
        return todo_serializer(todo)
  return  False

async def db_delete_todo(id:str) -> bool:
  find_todo = await collection_todo.find_one({"_id":ObjectId(id)})
  if find_todo:  
    deleteResult = await collection_todo.delete_one({"_id":ObjectId(id)})
    if (deleteResult.deleted_count > 0):
      return True
    return False

#登録できそうなら、dictでemail,passを含むdict : new user　を返す
async def db_signup(data:dict)->dict:
  email = data.get("email")
  password = data.get("password")
  overlap_user = await collection_user.find_one({"email": email})
  if overlap_user:
    raise HTTPException(status_code=400,detail='Email is already taken')
  if not password or len(email)<6:
    raise HTTPException(status_code=400,detail='Password too short')
  user = await collection_user.insert_one({"email":email,"password":auth.generate_hashed_pw(password)})
  new_user = await collection_user.find_one({"_id":user.inserted_id})
  return user_serializer(new_user)
  
#login出来そうならstr:tokenを返す
async def db_login(data:dict) -> str: 
  email = data.get("email")
  password = data.get("password")
  user = await collection_user.find_one({"email":email})
  if not user or not auth.verify_pw(password,user["password"]):
    raise HTTPException(status_code=401,detail='invalid email or password')
  token = auth.encode_jwt(user['email'])
  return token
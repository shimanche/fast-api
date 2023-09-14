from pydantic import BaseModel #データのモデルを定義することで、クラス変数に定義した型ヒントとインスタンス作成時に指定された値の型を比較し、正しい型なのかどうかをバリデーションしてくれます。
from typing import Optional
from decouple import config

CSRF_KEY = config('CSRF_KEY')

class CsrfSettings(BaseModel):
  secret_key: str = CSRF_KEY

class Todo(BaseModel): # endpointから返却されるデータの型を定義
  id:str
  title:str
  description:str

class TodoBody(BaseModel): # endpointへ渡すデータの型を定義
  title:str
  description:str
  
class SuccessMsg(BaseModel):
    message: str
    
class UserBody(BaseModel): #front->api
  email:str
  password:str
  
class UserInfo(BaseModel): #restApiのres
  id:Optional[str] = None #任意の値にしてくれるデフォルトはNone
  email:str
  
class Csrf(BaseModel):
  csrf_token:str

    

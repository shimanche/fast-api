import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime ,timedelta
from decouple import config

JWT_KEY = config('JWT_KEY')

class AuthJwtCsrf():
  pwd_ctx= CryptContext(schemes=["bcrypt"],deprecated="auto")
  secret_key = JWT_KEY
  
  def generate_hashed_pw(self,password)->str:
    return self.pwd_ctx.hash(password)
  
  def verify_pw(self,plain_pw,hashed_pw) ->bool:
    return self.pwd_ctx.verify(plain_pw,hashed_pw)
  
  def encode_jwt(self,email)->str:
    payload={
      'exp':datetime.utcnow() + timedelta(days=0,minutes=5), #jwtの有効期限
      'iat':datetime.utcnow(), #jwtの生成日時
      'sub':email
    }
    return jwt.encode(payload,self.secret_key,algorithm='HS256')
  
  #decode
  def decode_jwt(self,token)->str:
    try:
      payload=jwt.decode(token,self.secret_key,algorithms=['HS256'])
      return payload['sub']
    except jwt.ExpiredSignatureError:
      raise HTTPException(
        status_code=401,detail='The JWT has expired'
      )
    except jwt.InvalidTokenError as e: #jwtのフォーマットに準拠していないトークンや空のトークンが渡された時発生
      raise HTTPException(
        status_code=401,detail='JWT is not valid'
        
      )
      
  #jwt token　を検証してくれる関数
  def verify_jwt(self, request) ->str:
    token = request.cookies.get("access_token") #requestからaccesstokenを指定すると、jwttokenがくる
    if not token:
      raise HTTPException(
        status_code=401,detail='No JWT exist:may noto set yet or deleted'
      )
    _, _, value = token.partition(" ") #アンパック。。明示する必要がないものはアンダースコアで書くのが慣習
    subject = self.decode_jwt(value)
    return subject
    
  #jwtの検証と更新を検証してくれる関数
  def verify_update_jwt(self,request) -> tuple[str,str]: #更新されたjwtとsubjectをタプルで返す
    subject = self.verify_jwt(request)
    new_token = self.encode_jwt(subject)
    return new_token,subject
  
  #csrfトークンの検証、JWTの検証、JWTの更新をする関数
  def verify_csrf_update_jwt(self,request,csrf_protect,headers) ->str:
    csrf_token = csrf_protect.get_csrf_from_headers(headers)#リクエストヘッダーからcsrfトークンを取り出す
    csrf_protect.validate_csrf(csrf_token)#失敗したら例外が発生する、csrf_tokenを検証し、発生しない場合は次に進む
    subject = self.verify_jwt(request)#上記で失敗しないなら、これを実行。jwtjwtwを検証し、例外が発生しないなら次に進む
    new_token = self.encode_jwt(subject)#このsubjectからencodeで新しいjwtトークンを生成する
    return new_token
    
    
  
  
# uvicorn main:app --reload

from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import route_todo,route_auth
from schemas import SuccessMsg,CsrfSettings
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

app = FastAPI()
app.include_router(route_todo.router)
app.include_router(route_auth.router)
origins = ['http://localhost:3000'] #アクセスを許可するホワイトリスト
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@CsrfProtect.load_config
def get_csrf_config():
  return CsrfSettings()

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
  return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/",response_model=SuccessMsg) #作成したappインスタンスの後にRESTエンドポイントのメソッドのget
# @app.get("/") #作成したappインスタンスの後にRESTエンドポイントのメソッドのget
def root(): #pass（今はルート）にgetメソッドでアクセスがあったときにこの関数が実行される
  return {"message" : "hello world"} #dict型で返す

'''
@app.get("/") #作成したappインスタンスの後にRESTエンドポイントのメソッドのget
def read_root(): #pass（今はルート）にgetメソッドでアクセスがあったときにこの関数が実行される
  return {"message : hello world"}
'''
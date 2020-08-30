# Python Serverless Todo Demo

Python과 AWS Lambda 를 사용한 Todo RESTful API 서버 만들기 입니다. 

[변규현님(novemberde) Github](https://github.com/novemberde) 많이 참고하였습니다.

**변규현님께 감사드립니다.**

## Objective

Amazon Web Service 를 활용하여 Serverless architecture로 RESTful API 서버를 배포합니다.

[Crawler Demo](https://github.com/seunghokimj/python-serverless-crawler-demo) 를 참고하여 "Cloud9 시작하기", "S3 bucket 생성하기", "AWS Credentials 설정"  그리고 "Python 개발 환경 설정" 부분을 진행합니다.

## AWS Resources

AWS에서 사용하는 리소스는 다음과 같습니다.

- Cloud9: 코드 작성, 실행 및 디버깅을 위한 클라우드 기반 IDE.
- Lambda: 서버를 프로비저닝하거나 관리하지 않고도 코드를 실행할 수 있게 해주는 컴퓨팅 서비스. 서버리스 아키텍쳐의 핵심 서비스.
- DynamoDB: 완벽하게 관리되는 NoSQL 데이터베이스 서비스로, 원활한 확장성과 함께 빠르고 예측 가능한 성능을 제공.

## Cloud 9 시작하기
[Cloud9 설정 참고](https://github.com/seunghokimj/python-serverless-crawler-demo#cloud-9-%EC%8B%9C%EC%9E%91%ED%95%98%EA%B8%B0)

1. Cloud9 생성
    - Name: PythonServerless
2. Preferences
    - [ ] Region 설정
    - [ ] aws managed temporary credentials **off** 설정
    - [ ] Python 3 확인

## S3 Bucket 생성하기
[S3 Bucket 설정 참고](https://github.com/seunghokimj/python-serverless-crawler-demo#s3-bucket-%EC%83%9D%EC%84%B1%ED%95%98%EA%B8%B0)
- Bucket 생성
    - Bucket 이름: USERNAME-serverless-demo
    - 여기서 USERNAME을 수정합니다. e.g.) seungho-serverless-demo
 
## DynamoDB 테이블 생성하기
[DynamoDB 설정 참고](https://github.com/seunghokimj/python-serverless-crawler-demo#dynamodb-%ED%85%8C%EC%9D%B4%EB%B8%94-%EC%83%9D%EC%84%B1%ED%95%98%EA%B8%B0)

- DynamoDB 테이블 만들기
    - 테이블 이름: Todo
    - 파티션 키(Partition Key): userId
    - 정렬 키(Sort Key) 추가: createdAt 

## AWS Credentials 설정
[AWS Credentials 설정 참고](https://github.com/seunghokimj/python-serverless-crawler-demo#aws-credentials-%EC%84%A4%EC%A0%95)

- [ ] 관리자 사용자 추가
    - 실습이기 때문에 편의를 위해 관리자 사용자를 사용합니다. 
    - 실습이 끝난 후 반드시 사용자를 삭제합니다.
- [ ] [Cloud 9 에 AWS Credentials 적용](https://github.com/seunghokimj/python-serverless-crawler-demo#cloud9-%EC%97%90-aws-credentials-%EC%A0%81%EC%9A%A9)

## Python 개발 환경 설정
[Python 설정 참고](https://github.com/seunghokimj/python-serverless-crawler-demo#python-%EA%B0%9C%EB%B0%9C-%ED%99%98%EA%B2%BD-%EC%84%A4%EC%A0%95)

- [ ] Cloud9 일 때 .bash_profile 설정
- [ ] virtualenv 설정

## Todo RESTful API 서버 개발
본격적인 개발 실습 입니다.

파일 트리는 다음과 같습니다.

```txt
environment
└── serverless-todo  : 작업 디렉터리
    ├── app.py  : flask RESTful app
    ├── models.py: DynamoDB 모델
    ├── zappa_settings.json : Zappa config file
    └── requirements.txt : 개발을 위해 필요한 library 정보
```

먼저 터미널을 열어 serverless-todo 디렉터리를 생성하고 각 파일들을 편집합니다.

```sh
(venv) ec2-user:~/environment $ mkdir serverless-todo && cd serverless-todo
```

### serverless-todo/requirements.txt
```txt
Flask==1.1.2
Flask-RESTful==0.3.8
pynamodb==4.3.3
zappa==0.51.0
python-dateutil==2.6.1
Werkzeug==0.16.1

```

python은 requirements.txt 에 개발에 필요한 라이브러리를 기술합니다.

사용하는 라이브러리는 다음과 같습니다.

- Flask: 경량의 python web application framework
- Flask-RESTful: flask 를 RESTful API 서버로 간단히 만들어주는 도구  
- pynamodb: DynamoDB를 사용하기 쉽도록 Modeling하는 도구
- zappa: python serverless framework

requirements.txt에 있는 라이브러리들을 설치 합니다.

```sh
(venv) ec2-user:~/environment/serverless-todo $ pip install -r requirements.txt

```


### serverless-todo/zappa_settings.json
zappa 를 init 하면 zappa_settings.json 파일이 생성됩니다.

```sh
(venv) ec2-user:~/environment/serverless-todo $ zappa init
...
Does this look okay? (default 'y') [y/n]: y
...
```

**zappa_settings.json** 을 아래처럼 변경하여 저장합니다.

```json
{
    "dev": {
        "app_function": "app.app",
        "aws_region": "ap-northeast-2",
        "exclude": ["__pycache__", "images"],
        "memory_size": 128,
        "profile_name": "default",
        "project_name": "python-serverless-todo",
        "runtime": "python3.6",
        "s3_bucket": "YOUR_S3_BUCKET"  // 이 부분을 생성한 s3 이름으로 변경
    }
}
```

### serverless-todo/models.py

```python
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


class Todo(Model):
    class Meta:
        table_name = "Todo"
        region = 'ap-northeast-2'

    userId = UnicodeAttribute(hash_key=True)
    createdAt = UnicodeAttribute(range_key=True)
    updatedAt = UnicodeAttribute()
    title = UnicodeAttribute()
```

### serverless-todo/app.py
```python
import json
import datetime
from flask import Flask, make_response
from flask_restful import reqparse, abort, Api, Resource
from http import HTTPStatus

from models import Todo

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

```

터미널에서 flask 웹 서버를 실행해 봅니다.

`FLASK_ENV=development` 하면 소스코드를 변경할 때마다 서버를 자동 재시작 해줘서 편리합니다. 

```sh
(venv) ec2-user:~/environment/serverless-todo $ FLASK_APP=app.py FLASK_ENV=development flask run
 * Serving Flask app "app.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 177-226-789
```

### curl 을 사용한 테스트
[curl](https://github.com/curl/curl) URL syntax 로 지정된 데이터를 전송하기 위한 command-line 도구입니다.

[curl tutorial](https://curl.haxx.se/docs/manual.html)

방금 실행한 flask 웹서버를 테스트 해봅니다.

```sh
(venv) ec2-user:~/environment/serverless-todo $ curl localhost:5000
Hello, World!
```

### CRUD 작성
Todo 모델에 대한 CRUD(create, read, update, delete) 기능을 RESTful API 형태로 개발합니다.

**serverless-todo/app.py** 파일 

* RequestParser
```python
parser = reqparse.RequestParser()
parser.add_argument('userId', default='tester') # Frontend 와 편의를 맞추기 위해 userId 의 기본값을 tester 로 함
parser.add_argument('title')
parser.add_argument('createdAt')
```

* TodoList API 개발
```python
class TodoListResource(Resource):
    def get(self):
        pass

    def post(self):
        pass
```

* Todo API 개발
```python
class TodoResource(Resource):
    def get(self, created_at):
        pass
    def put(self, created_at):
        pass
    def delete(self, created_at):
        pass    
```

* Api resource routing

```python
api.add_resource(TodoResource, '/todo/<string:created_at>')
api.add_resource(TodoListResource, '/todo/')
```

* 한글 깨짐(encoding) 문제 해결

```python
@api.representation('application/json')
def json_out(data, code, headers=None):
    resp = make_response(json.dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp
```

#### CRUD test
* Todo 데이터 생성
```sh
(venv) ec2-user:~/environment/serverless-todo $ curl -d '{"userId":"tester", "title":"any title"}' -H "Content-Type: application/json" -X POST http://localhost:5000/todo/
{
    "userId": "tester",
    "title": "any title",
    "createdAt": "2020-08-29T18:04:04.341Z",
    "updatedAt": "2020-08-29T18:04:04.341Z"
}
```
* Todo list 읽기
```sh
(venv) ec2-user:~/environment/serverless-todo $ curl localhost:5000/todo/
[
    {
        "createdAt": "2020-08-29T18:04:04.341Z",
        "userId": "tester",
        "updatedAt": "2020-08-29T18:04:04.341Z",
        "title": "any title"
    },
    ...
]
```

## RESTful API 서버 배포하기
### Zappa deploy
```sh
(venv) ec2-user:~/environment/serverless-todo $ zappa deploy dev
Calling deploy for stage dev..
Downloading and installing dependencies..
 - markupsafe==1.1.1: Downloading
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 27.5k/27.5k [00:00<00:00, 9.70MB/s]
Packaging project as zip.
Uploading python-serverless-todo-dev-1598724889.zip (10.5MiB)..
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11.0M/11.0M [00:00<00:00, 13.5MB/s]
Scheduling..
Unscheduled 51a1f05ee1065e96ad02ba6c4ce2de1440443-handler.keep_warm_callback.
Scheduled 51a1f05ee1065e96ad02ba6c4ce2de1440443-handler.keep_warm_callback with expression rate(4 minutes)!
Uploading python-serverless-todo-dev-template-1598724899.json (1.7KiB)..
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1.70k/1.70k [00:00<00:00, 17.5kB/s]
Deploying API Gateway..
Deployment complete!: https://XXXXXXXX.execute-api.ap-northeast-2.amazonaws.com/dev
```

정상적으로 deploy 되었으면, [Lambda Console](https://ap-northeast-2.console.aws.amazon.com/lambda/home?region=ap-northeast-2#/functions) 에서 새로 생성된 `python-serverless-todo-dev` 함수를 확인 할 수 있습니다.

`Deployment complete!` 이후 나오는 API gateway 주소를 기억해주세요

## [postman](https://www.postman.com/) 으로 RESTful API 사용
postman 은 손쉽게 RESTful API를 사용할 수 있게 도와주는 툴입니다. 기능이 막강하여 RESTful API 서버 개발에 필수라고 할 수 있습니다.

* postman 설치

    [postman download](https://www.postman.com/downloads/) 페이지로 이동해서 postman 을 다운로드 받고 설치합니다.

* postman 실습

## S3를 통해 Static Website 호스팅
RESTful API 서버를 개발하고 curl 이나 postman CRUD를 실행해봤지만 text만 보이기 때문에 의미있는 기능을 개발한 것 같지 않습니다.

이번에는 static website를 하나의 앱이라고 생각하고 데이터만 서버에 요청하여 UI에 반영하려고 합니다.

실제 frontend 를 개발하는 것은 아니고, 이미 개발된 frontend 를 빌드하고 호스팅 합니다.

### Static Website 호스팅용 S3 Bucket 생성
Amazon S3는 파일을 저장하는 저장소 역할을 합니다. 파일을 저장하고 URL을 통해서 파일에 접근합니다. 그렇다면 URL로 접근하는 파일이 HTML, CSS, JAVASCRIPT로 작성되어 있다면 브라우저에서 사용이 가능하겠죠?

그래서 S3는 정적인 웹사이트 호스팅을 지원합니다.

[S3 Console](https://s3.console.aws.amazon.com/s3/home?region=ap-northeast-2) 에 접속하여 static website 버킷을 생성합니다.

* 버킷이름(Bucket name): USERNAME-serverless-static-web
* 리전(Region): 아시아 태평양(서울)
![create-static-s3-01](/images/create-static-s3-01.png)

* 모든 퍼블릭 엑세스 차단 해제
![create-static-s3-02](/images/create-static-s3-02.png)

생성한 버킷을 선택 > 속성 메뉴에 들어가서 정적 웹사이트 호스팅(Static Website Hosting)을 클릭하고 다음과 같이 입력합니다.

![setup-static-s3-01](/images/setup-static-s3-01.png)

* 인덱스 문서(Index document): index.html
* 오류 문서(Error document): index.html
![setup-static-s3-02](/images/setup-static-s3-02.png)


### static front 빌드
새 터미널에서 작업합니다.

```sh
# !! 여기서 사용하는 패키지 중에 하나가 node 9.x 이하로 지원됩니다.
ec2-user:~/environment $ nvm install 9
ec2-user:~/environment $ nvm use 9

# !! 여기서는 yarn으로 패키지를 설치. npm으로 설치하게 되면 Parcel bundler가 제대로 동작하지 않습니다.
ec2-user:~/environment $ npm i -g yarn

# web frontend 소스코드를 clone 합니다. 
ec2-user:~/environment $ git clone https://github.com/novemberde/serverless-todo-demo/

# frontend 소스코드가 있는 디렉터리로 이동합니다.
ec2-user:~/environment $ cd serverless-todo-demo/static-web-front/

# npm으로 package 설치합니다.
ec2-user:~/environment/serverless-todo-demo/static-web-front (master) $ yarn install 
```

**/home/ec2-user/environment/serverless-todo-demo/static-web-front/src/components/App.js** 파일을 수정합니다.

baseURL 값을 [zappa deploy](https://github.com/seunghokimj/python-serverless-todo-demo#zappa-deploy) 에서 배포한 API gateway 주소로 변경합니다.


```sh
# Static Website 빌드와 시작을 합니다.
ec2-user:~/environment/serverless-todo-demo/static-web-front $ npm start
> serverless-todo-demo-app@1.0.0 start /home/ec2-user/environment/serverless-todo-demo/static-web-front
> npx parcel src/index.html

Server running at http://localhost:1234 
  Built in 20.27s.

# control + c 버튼을 눌러 종료합니다.

# 빌드된 frontend 디렉터리로 이동합니다.
ec2-user:~/environment/serverless-todo-demo/static-web-front (master) $ cd dist/

# 빌드된 frontend 파일들을 S3에 복사합니다.
# USERNAME 은 수정합니다. 
ec2-user:~/environment/serverless-todo-demo/static-web-front/dist (master) $ aws s3 cp ./ s3://USERNAME-serverless-static-web/ --recursive --acl public-read  
```

### CORS 문제 해결
flask 의 `@app.after_request` 을 사용해서 CORS error 문제를 해결합니다.
```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
```


## 리소스 삭제하기

서버리스 앱은 내리는 것이 어렵지 않습니다.
간단한 Command 하나면 모든 스택이 내려갑니다.
Cloud9에서 새로운 터미널을 열고 다음과 같이 입력합니다.

```sh
(venv) ec2-user:~/environment/serverless-todo $ zappa undeploy dev
Calling undeploy for stage dev..
Are you sure you want to undeploy? [y/n] y
Deleting API Gateway..
Waiting for stack python-serverless-todo-dev to be deleted..
Unscheduling..
Unscheduled 51a1f05ee1065e96ad02ba6c4ce2de1440443-handler.keep_warm_callback.
Deleting Lambda function..
Done!
```

- [ ] IAM 사용자 삭제

    [IAM Console](https://console.aws.amazon.com/iam/home#/users)로 들어가서 오늘 생성한 관리자 사용자(python-serverless)를 삭제합니다.

- [ ] S3 버킷 삭제

    [S3 Console](https://s3.console.aws.amazon.com/s3/home?region=ap-northeast-2)로 들어가서 생성한 s3 버킷들(USERNAME-serverless-demo, USERNAME-serverless-static-web)을 삭제합니다.

- [ ] DynamoDB 테이블 삭제

    [DynamoDB Console](https://ap-northeast-2.console.aws.amazon.com/dynamodb/home?region=ap-northeast-2)로 들어가서 Table을 삭제합니다. 리전은 서울입니다.

- [ ] Cloud9 삭제

    [Cloud9 Console](https://ap-northeast-2.console.aws.amazon.com/cloud9/home?region=ap-northeast-2)로 들어가서 IDE를 삭제합니다. 리전은 서울입니다.



## References

- [https://aws.amazon.com/ko/cloud9/](https://aws.amazon.com/ko/cloud9/)
- [https://www.zappa.io/](https://www.zappa.io/)
- [https://www.crummy.com/software/BeautifulSoup/bs4/doc/](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [https://pynamodb.readthedocs.io](https://pynamodb.readthedocs.io)

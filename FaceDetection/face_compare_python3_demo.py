"""
face_compare_python3_demo.py - 讯飞人脸比对 API
增强版：添加超时设置、错误处理、请求限流
"""
import configparser
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests
import time


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema


def sha256base64(data):
    """SHA256 加密并 Base64 编码"""
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    """解析 URL"""
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    """组装鉴权 URL"""
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)


def gen_body(appid, img1_path, img2_path, server_id):
    """生成请求体"""
    with open(img1_path, 'rb') as f:
        img1_data = f.read()
    with open(img2_path, 'rb') as f:
        img2_data = f.read()

    body = {
        "header": {
            "app_id": appid,
            "status": 3
        },
        "parameter": {
            server_id: {
                "service_kind": "face_compare",
                "face_compare_result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json"
                }
            }
        },
        "payload": {
            "input1": {
                "encoding": "jpg",
                "status": 3,
                "image": str(base64.b64encode(img1_data), 'utf-8')
            },
            "input2": {
                "encoding": "jpg",
                "status": 3,
                "image": str(base64.b64encode(img2_data), 'utf-8')
            }
        }
    }
    return json.dumps(body)


# 全局变量：请求限流
_last_request_time = 0
_min_request_interval = 0.5  # 最小请求间隔 0.5 秒


def run(appid, apikey, apisecret, img1_path, img2_path, server_id='s67c9c78c'):
    """
    调用人脸比对 API
    :return: True-是同一个人，False-不是同一个人
    """
    global _last_request_time

    # 请求限流
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    if time_since_last < _min_request_interval:
        sleep_time = _min_request_interval - time_since_last
        time.sleep(sleep_time)

    _last_request_time = time.time()

    try:
        url = 'http://api.xf-yun.com/v1/private/{}'.format(server_id)
        request_url = assemble_ws_auth_url(url, "POST", apikey, apisecret)
        headers = {
            'content-type': "application/json",
            'host': 'api.xf-yun.com',
            'app_id': appid
        }

        # 添加超时设置：连接超时 5 秒，读取超时 10 秒
        response = requests.post(
            request_url,
            data=gen_body(appid, img1_path, img2_path, server_id),
            headers=headers,
            timeout=(5, 10)  # (connect_timeout, read_timeout)
        )

        # 检查 HTTP 状态码
        if response.status_code != 200:
            print(f"❌ API 返回错误状态码: {response.status_code}")
            return False

        resp_data = response.json()

        # 检查响应格式
        if 'payload' not in resp_data or 'face_compare_result' not in resp_data['payload']:
            print(f"❌ API 返回格式错误: {resp_data}")
            return False

        # 解析结果
        payload = resp_data['payload']
        result_text = base64.b64decode(payload['face_compare_result']['text']).decode('utf-8')
        data = json.loads(result_text)

        # 判断比对结果
        if data['ret'] == 0:
            score = data.get('score', 0)
            if score > 0.67:  # 相似度阈值
                print(f"   相似度: {score:.2%}")
                return True

        return False

    except requests.exceptions.Timeout:
        print("❌ API 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接失败")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


# 测试代码
if __name__ == '__main__':
    result = run(
        appid='ce3cff88',
        apisecret='NWM2Y2Y3OWI2YWNhZGU3ZGMyMTUyNjdh',
        apikey='0b08851356d9bf23e4a10c2f5cb56a6c',
        img1_path=r'FaceDetection/images/slice/face-1727252191.416481.jpg',
        img2_path=r'FaceDetection/images/users/person1.jpg'
    )

    if result:
        print("✅ 是同一个人")
    else:
        print("❌ 不是同一个人")
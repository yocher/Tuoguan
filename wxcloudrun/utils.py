import os
import hashlib
import logging
import requests
import xml.etree.ElementTree as ET
from functools import wraps
from flask import request
from wxcloudrun.response import make_err_response
from wxcloudrun.dao import get_parent_by_openid, get_teacher_by_openid, get_admin_by_username

logger = logging.getLogger('log')


# ==================== WeChat Authentication ====================

def get_openid_from_request():
    """
    从请求头中获取openid（WeChat Cloud Hosting自动注入）
    """
    return request.headers.get('X-WX-OPENID', request.headers.get('X-WX-FROM-OPENID', None))


def require_auth(role=None):
    """
    认证装饰器，验证用户身份
    :param role: 'parent', 'teacher', 'admin' 或 None（任意已认证用户）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            openid = get_openid_from_request()

            if not openid:
                return make_err_response('未授权访问')

            if role == 'parent':
                parent = get_parent_by_openid(openid)
                if not parent:
                    return make_err_response('家长身份验证失败')
                request.current_user = parent
                request.user_role = 'parent'
            elif role == 'teacher':
                teacher = get_teacher_by_openid(openid)
                if not teacher:
                    return make_err_response('教师身份验证失败')
                request.current_user = teacher
                request.user_role = 'teacher'
            elif role == 'admin':
                return make_err_response('管理员需要通过Web界面登录')
            else:
                parent = get_parent_by_openid(openid)
                teacher = get_teacher_by_openid(openid)
                if parent:
                    request.current_user = parent
                    request.user_role = 'parent'
                elif teacher:
                    request.current_user = teacher
                    request.user_role = 'teacher'
                else:
                    return make_err_response('用户身份验证失败')

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin_auth(f):
    """
    管理员认证装饰器（基于session）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'admin_id' not in session:
            return make_err_response('管理员未登录')
        return f(*args, **kwargs)
    return decorated_function


# ==================== WeChat API ====================

class WeChatAPI:
    """微信公众号API封装"""

    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret
        self.access_token = None

    def get_access_token(self):
        """获取access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.secret}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'access_token' in data:
                self.access_token = data['access_token']
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None

    def send_template_message(self, openid, template_id, data, miniprogram=None):
        """
        发送模板消息
        :param openid: 接收者openid
        :param template_id: 模板ID
        :param data: 模板数据
        :param miniprogram: 小程序信息 {'appid': '', 'pagepath': ''}
        """
        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}"

        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data
        }

        if miniprogram:
            payload["miniprogram"] = miniprogram

        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            if result.get('errcode') == 0:
                logger.info(f"模板消息发送成功: {openid}")
                return True
            else:
                logger.error(f"模板消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"模板消息发送异常: {e}")
            return False


def parse_wechat_xml(xml_data):
    """解析微信XML消息"""
    try:
        root = ET.fromstring(xml_data)
        msg = {}
        for child in root:
            msg[child.tag] = child.text
        return msg
    except Exception as e:
        logger.error(f"解析微信XML失败: {e}")
        return None


def verify_wechat_signature(signature, timestamp, nonce, token):
    """验证微信服务器签名"""
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    tmp_hash = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return tmp_hash == signature


# ==================== File Upload ====================

def upload_file_to_storage(file, folder='pickup_photos'):
    """
    上传文件到对象存储
    这里使用本地存储作为示例，实际应该使用云存储服务
    """
    try:
        if not file:
            return None

        filename = file.filename
        if not filename:
            return None

        ext = os.path.splitext(filename)[1]
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
            return None

        import uuid
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        upload_folder = os.path.join('uploads', folder)
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        file_url = f"/uploads/{folder}/{unique_filename}"
        return file_url
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return None


# ==================== Data Serialization ====================

def serialize_student(student):
    """序列化学生对象"""
    if not student:
        return None
    return {
        'id': student.id,
        'name': student.name,
        'student_number': student.student_number,
        'class_name': student.class_name,
        'grade': student.grade,
        'avatar_url': student.avatar_url,
        'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None
    }


def serialize_parent(parent):
    """序列化家长对象"""
    if not parent:
        return None
    return {
        'id': parent.id,
        'openid': parent.openid,
        'name': parent.name,
        'phone': parent.phone,
        'avatar_url': parent.avatar_url,
        'created_at': parent.created_at.strftime('%Y-%m-%d %H:%M:%S') if parent.created_at else None
    }


def serialize_teacher(teacher):
    """序列化教师对象"""
    if not teacher:
        return None
    return {
        'id': teacher.id,
        'openid': teacher.openid,
        'name': teacher.name,
        'phone': teacher.phone,
        'avatar_url': teacher.avatar_url,
        'created_at': teacher.created_at.strftime('%Y-%m-%d %H:%M:%S') if teacher.created_at else None
    }


def serialize_pickup_record(record):
    """序列化接送记录对象"""
    if not record:
        return None
    return {
        'id': record.id,
        'student_id': record.student_id,
        'student': serialize_student(record.student) if hasattr(record, 'student') else None,
        'teacher_id': record.teacher_id,
        'teacher': serialize_teacher(record.teacher) if hasattr(record, 'teacher') else None,
        'photo_url': record.photo_url,
        'pickup_time': record.pickup_time.strftime('%Y-%m-%d %H:%M:%S') if record.pickup_time else None,
        'notes': record.notes,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None
    }

from datetime import datetime
from flask import render_template, request, session
from run import app
from wxcloudrun.dao import *
from wxcloudrun.model import *
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from wxcloudrun.utils import *
import logging
import json
import os

logger = logging.getLogger('log')

# 初始化微信API
WECHAT_APPID = os.environ.get('WECHAT_APPID', '')
WECHAT_SECRET = os.environ.get('WECHAT_SECRET', '')
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', '')
TEMPLATE_ID = os.environ.get('WECHAT_TEMPLATE_ID', '')
MINIPROGRAM_APPID = os.environ.get('MINIPROGRAM_APPID', '')

wechat_api = WeChatAPI(WECHAT_APPID, WECHAT_SECRET)


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


# ==================== 管理员接口 ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        params = request.get_json()
        username = params.get('username')
        password = params.get('password')

        if not username or not password:
            return make_err_response('用户名和密码不能为空')

        admin = get_admin_by_username(username)
        if not admin:
            return make_err_response('用户名或密码错误')

        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if admin.password_hash != password_hash:
            return make_err_response('用户名或密码错误')

        session['admin_id'] = admin.id
        session['admin_username'] = admin.username

        return make_succ_response({
            'id': admin.id,
            'username': admin.username,
            'name': admin.name
        })
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        return make_err_response('登录失败')


@app.route('/api/admin/logout', methods=['POST'])
@require_admin_auth
def admin_logout():
    """管理员登出"""
    session.clear()
    return make_succ_empty_response()


@app.route('/api/admin/students', methods=['GET'])
@require_admin_auth
def admin_get_students():
    """获取所有学生列表"""
    try:
        class_name = request.args.get('class_name')
        if class_name:
            students = get_students_by_class(class_name)
        else:
            students = get_all_students()

        return make_succ_response([serialize_student(s) for s in students])
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return make_err_response('获取学生列表失败')


@app.route('/api/admin/students', methods=['POST'])
@require_admin_auth
def admin_create_student():
    """创建学生"""
    try:
        params = request.get_json()
        name = params.get('name')
        student_number = params.get('student_number')
        class_name = params.get('class_name')
        grade = params.get('grade')
        avatar_url = params.get('avatar_url')

        if not name or not student_number or not class_name:
            return make_err_response('学生姓名、学号和班级不能为空')

        existing = get_student_by_number(student_number)
        if existing:
            return make_err_response('学号已存在')

        student = Student(
            name=name,
            student_number=student_number,
            class_name=class_name,
            grade=grade,
            avatar_url=avatar_url
        )
        student = create_student(student)

        return make_succ_response(serialize_student(student))
    except Exception as e:
        logger.error(f"创建学生失败: {e}")
        return make_err_response('创建学生失败')


@app.route('/api/admin/students/<int:student_id>', methods=['PUT'])
@require_admin_auth
def admin_update_student(student_id):
    """更新学生信息"""
    try:
        student = get_student_by_id(student_id)
        if not student:
            return make_err_response('学生不存在')

        params = request.get_json()
        if 'name' in params:
            student.name = params['name']
        if 'class_name' in params:
            student.class_name = params['class_name']
        if 'grade' in params:
            student.grade = params['grade']
        if 'avatar_url' in params:
            student.avatar_url = params['avatar_url']

        student = update_student(student)
        return make_succ_response(serialize_student(student))
    except Exception as e:
        logger.error(f"更新学生失败: {e}")
        return make_err_response('更新学生失败')


@app.route('/api/admin/students/<int:student_id>', methods=['DELETE'])
@require_admin_auth
def admin_delete_student(student_id):
    """删除学生"""
    try:
        success = delete_student(student_id)
        if success:
            return make_succ_empty_response()
        else:
            return make_err_response('学生不存在')
    except Exception as e:
        logger.error(f"删除学生失败: {e}")
        return make_err_response('删除学生失败')


@app.route('/api/admin/parents', methods=['GET'])
@require_admin_auth
def admin_get_parents():
    """获取所有家长列表"""
    try:
        parents = get_all_parents()
        return make_succ_response([serialize_parent(p) for p in parents])
    except Exception as e:
        logger.error(f"获取家长列表失败: {e}")
        return make_err_response('获取家长列表失败')


@app.route('/api/admin/parents', methods=['POST'])
@require_admin_auth
def admin_create_parent():
    """创建家长"""
    try:
        params = request.get_json()
        openid = params.get('openid')
        name = params.get('name')
        phone = params.get('phone')

        if not openid:
            return make_err_response('openid不能为空')

        existing = get_parent_by_openid(openid)
        if existing:
            return make_err_response('该openid已存在')

        parent = Parent(openid=openid, name=name, phone=phone)
        parent = create_parent(parent)

        return make_succ_response(serialize_parent(parent))
    except Exception as e:
        logger.error(f"创建家长失败: {e}")
        return make_err_response('创建家长失败')


@app.route('/api/admin/teachers', methods=['GET'])
@require_admin_auth
def admin_get_teachers():
    """获取所有教师列表"""
    try:
        teachers = get_all_teachers()
        return make_succ_response([serialize_teacher(t) for t in teachers])
    except Exception as e:
        logger.error(f"获取教师列表失败: {e}")
        return make_err_response('获取教师列表失败')


@app.route('/api/admin/teachers', methods=['POST'])
@require_admin_auth
def admin_create_teacher():
    """创建教师"""
    try:
        params = request.get_json()
        openid = params.get('openid')
        name = params.get('name')
        phone = params.get('phone')

        if not openid or not name:
            return make_err_response('openid和姓名不能为空')

        existing = get_teacher_by_openid(openid)
        if existing:
            return make_err_response('该openid已存在')

        teacher = Teacher(openid=openid, name=name, phone=phone)
        teacher = create_teacher(teacher)

        return make_succ_response(serialize_teacher(teacher))
    except Exception as e:
        logger.error(f"创建教师失败: {e}")
        return make_err_response('创建教师失败')


@app.route('/api/admin/parent-student', methods=['POST'])
@require_admin_auth
def admin_bind_parent_student():
    """绑定家长和学生关系"""
    try:
        params = request.get_json()
        parent_id = params.get('parent_id')
        student_id = params.get('student_id')
        relationship = params.get('relationship')

        if not parent_id or not student_id:
            return make_err_response('家长ID和学生ID不能为空')

        parent = get_parent_by_id(parent_id)
        if not parent:
            return make_err_response('家长不存在')

        student = get_student_by_id(student_id)
        if not student:
            return make_err_response('学生不存在')

        create_parent_student_relation(parent_id, student_id, relationship)
        return make_succ_empty_response()
    except Exception as e:
        logger.error(f"绑定家长学生关系失败: {e}")
        return make_err_response('绑定失败')


@app.route('/api/admin/parent-student', methods=['DELETE'])
@require_admin_auth
def admin_unbind_parent_student():
    """解绑家长和学生关系"""
    try:
        params = request.get_json()
        parent_id = params.get('parent_id')
        student_id = params.get('student_id')

        if not parent_id or not student_id:
            return make_err_response('家长ID和学生ID不能为空')

        delete_parent_student_relation(parent_id, student_id)
        return make_succ_empty_response()
    except Exception as e:
        logger.error(f"解绑家长学生关系失败: {e}")
        return make_err_response('解绑失败')


# ==================== 教师接口 ====================

@app.route('/api/teacher/students', methods=['GET'])
@require_auth('teacher')
def teacher_get_students():
    """教师获取学生列表"""
    try:
        class_name = request.args.get('class_name')
        if class_name:
            students = get_students_by_class(class_name)
        else:
            students = get_all_students()

        return make_succ_response([serialize_student(s) for s in students])
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return make_err_response('获取学生列表失败')


@app.route('/api/teacher/pickup-records', methods=['POST'])
@require_auth('teacher')
def teacher_create_pickup_record():
    """教师创建接送记录"""
    try:
        student_id = request.form.get('student_id')
        notes = request.form.get('notes', '')
        photo = request.files.get('photo')

        if not student_id:
            return make_err_response('学生ID不能为空')

        if not photo:
            return make_err_response('照片不能为空')

        student = get_student_by_id(int(student_id))
        if not student:
            return make_err_response('学生不存在')

        photo_url = upload_file_to_storage(photo)
        if not photo_url:
            return make_err_response('照片上传失败')

        teacher = request.current_user
        pickup_record = PickupRecord(
            student_id=student.id,
            teacher_id=teacher.id,
            photo_url=photo_url,
            notes=notes
        )
        pickup_record = create_pickup_record(pickup_record)

        parents = get_parents_by_student_id(student.id)
        for parent in parents:
            miniprogram_data = {
                'appid': MINIPROGRAM_APPID,
                'pagepath': f'pages/pickup-detail/index?id={pickup_record.id}'
            }
            template_data = {
                'first': {'value': f'{student.name}已被接走', 'color': '#173177'},
                'keyword1': {'value': student.name, 'color': '#173177'},
                'keyword2': {'value': pickup_record.pickup_time.strftime('%Y-%m-%d %H:%M:%S'), 'color': '#173177'},
                'keyword3': {'value': teacher.name, 'color': '#173177'},
                'remark': {'value': '点击查看接送照片', 'color': '#173177'}
            }
            wechat_api.send_template_message(
                parent.openid,
                TEMPLATE_ID,
                template_data,
                miniprogram_data
            )

        return make_succ_response(serialize_pickup_record(pickup_record))
    except Exception as e:
        logger.error(f"创建接送记录失败: {e}")
        return make_err_response('创建接送记录失败')


@app.route('/api/teacher/pickup-records', methods=['GET'])
@require_auth('teacher')
def teacher_get_pickup_records():
    """教师获取接送记录列表"""
    try:
        limit = request.args.get('limit', type=int)
        records = get_all_pickup_records(limit)
        return make_succ_response([serialize_pickup_record(r) for r in records])
    except Exception as e:
        logger.error(f"获取接送记录失败: {e}")
        return make_err_response('获取接送记录失败')


@app.route('/api/teacher/avatar', methods=['POST'])
@require_auth('teacher')
def teacher_upload_avatar():
    """教师上传头像"""
    try:
        teacher = request.current_user
        avatar = request.files.get('avatar')

        if not avatar:
            return make_err_response('头像文件不能为空')

        avatar_url = upload_file_to_storage(avatar, folder='avatars')
        if not avatar_url:
            return make_err_response('头像上传失败')

        teacher.avatar_url = avatar_url
        teacher = update_teacher(teacher)

        return make_succ_response({'avatar_url': avatar_url})
    except Exception as e:
        logger.error(f"上传头像失败: {e}")
        return make_err_response('上传头像失败')


# ==================== 家长接口 ====================

@app.route('/api/parent/students', methods=['GET'])
@require_auth('parent')
def parent_get_students():
    """家长获取自己的学生列表"""
    try:
        parent = request.current_user
        students = get_students_by_parent_id(parent.id)
        return make_succ_response([serialize_student(s) for s in students])
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return make_err_response('获取学生列表失败')


@app.route('/api/parent/pickup-records', methods=['GET'])
@require_auth('parent')
def parent_get_pickup_records():
    """家长获取接送记录"""
    try:
        parent = request.current_user
        limit = request.args.get('limit', type=int)
        records = get_pickup_records_by_parent_openid(parent.openid, limit)
        return make_succ_response([serialize_pickup_record(r) for r in records])
    except Exception as e:
        logger.error(f"获取接送记录失败: {e}")
        return make_err_response('获取接送记录失败')


@app.route('/api/parent/pickup-records/<int:record_id>', methods=['GET'])
@require_auth('parent')
def parent_get_pickup_record_detail(record_id):
    """家长获取接送记录详情"""
    try:
        parent = request.current_user
        record = get_pickup_record_by_id(record_id)

        if not record:
            return make_err_response('记录不存在')

        student_ids = [s.id for s in get_students_by_parent_id(parent.id)]
        if record.student_id not in student_ids:
            return make_err_response('无权访问该记录')

        return make_succ_response(serialize_pickup_record(record))
    except Exception as e:
        logger.error(f"获取接送记录详情失败: {e}")
        return make_err_response('获取接送记录详情失败')


@app.route('/api/parent/avatar', methods=['POST'])
@require_auth('parent')
def parent_upload_avatar():
    """家长上传头像"""
    try:
        parent = request.current_user
        avatar = request.files.get('avatar')

        if not avatar:
            return make_err_response('头像文件不能为空')

        avatar_url = upload_file_to_storage(avatar, folder='avatars')
        if not avatar_url:
            return make_err_response('头像上传失败')

        parent.avatar_url = avatar_url
        parent = update_parent(parent)

        return make_succ_response({'avatar_url': avatar_url})
    except Exception as e:
        logger.error(f"上传头像失败: {e}")
        return make_err_response('上传头像失败')


# ==================== 通用接口 ====================

@app.route('/api/wechat/login', methods=['POST'])
def wechat_login():
    """微信小程序登录接口
    
    请求参数:
        code: 微信小程序 wx.login() 获取的 code
    
    返回数据:
        openid: 用户openid
        role: 用户角色 ('parent' 或 'teacher')
        user: 用户信息对象
        is_new_user: 是否为新用户（仅新用户返回）
    """
    try:
        params = request.get_json()
        if not params:
            return make_err_response('请求参数不能为空')
        
        code = params.get('code')

        if not code:
            return make_err_response('code不能为空')

        # 使用云托管环境，openid 会自动注入到请求头
        openid = request.headers.get('X-WX-OPENID')

        if not openid:
            # 如果没有自动注入，则调用微信接口获取
            miniprogram_secret = os.environ.get('MINIPROGRAM_SECRET', '')
            if not MINIPROGRAM_APPID or not miniprogram_secret:
                logger.error("小程序配置缺失: MINIPROGRAM_APPID 或 MINIPROGRAM_SECRET")
                return make_err_response('服务器配置错误，请联系管理员')

            import requests as http_requests
            url = 'https://api.weixin.qq.com/sns/jscode2session'
            try:
                response = http_requests.get(url, params={
                    'appid': MINIPROGRAM_APPID,
                    'secret': miniprogram_secret,
                    'js_code': code,
                    'grant_type': 'authorization_code'
                }, timeout=10)

                data = response.json()
                
                # 检查微信API返回的错误
                if 'errcode' in data:
                    error_msg = data.get('errmsg', '未知错误')
                    logger.error(f"微信登录API错误: errcode={data['errcode']}, errmsg={error_msg}")
                    if data['errcode'] == 40029:
                        return make_err_response('code无效或已过期，请重新登录')
                    elif data['errcode'] == 45011:
                        return make_err_response('登录频率过高，请稍后再试')
                    else:
                        return make_err_response(f'微信登录失败: {error_msg}')
                
                if 'openid' not in data:
                    logger.error(f"微信登录失败，未返回openid: {data}")
                    return make_err_response('微信登录失败，未获取到用户信息')

                openid = data['openid']
                session_key = data.get('session_key', '')
                logger.info(f"成功获取openid: {openid[:10]}...")
                
            except http_requests.exceptions.Timeout:
                logger.error("微信API请求超时")
                return make_err_response('网络请求超时，请稍后重试')
            except http_requests.exceptions.RequestException as e:
                logger.error(f"微信API请求异常: {e}")
                return make_err_response('网络请求失败，请稍后重试')
            except Exception as e:
                logger.error(f"调用微信API异常: {e}")
                return make_err_response('登录服务异常，请稍后重试')

        # 检查用户是否已存在
        try:
            parent = get_parent_by_openid(openid)
            teacher = get_teacher_by_openid(openid)
        except Exception as e:
            logger.error(f"查询用户信息失败: {e}")
            return make_err_response('查询用户信息失败')

        if parent:
            logger.info(f"家长用户登录: {openid[:10]}...")
            return make_succ_response({
                'openid': openid,
                'role': 'parent',
                'user': serialize_parent(parent)
            })
        elif teacher:
            logger.info(f"教师用户登录: {openid[:10]}...")
            return make_succ_response({
                'openid': openid,
                'role': 'teacher',
                'user': serialize_teacher(teacher)
            })
        else:
            # 新用户，自动创建家长账号
            try:
                new_parent = Parent(openid=openid)
                new_parent = create_parent(new_parent)
                logger.info(f"新用户登录，创建家长账号: {openid[:10]}...")
                
                return make_succ_response({
                    'openid': openid,
                    'role': 'parent',
                    'user': serialize_parent(new_parent),
                    'is_new_user': True
                })
            except Exception as e:
                logger.error(f"创建新用户失败: {e}")
                return make_err_response('创建用户失败，请稍后重试')
                
    except Exception as e:
        logger.error(f"微信登录失败: {e}", exc_info=True)
        return make_err_response('登录失败，请稍后重试')


@app.route('/api/user/info', methods=['GET'])
@require_auth()
def get_user_info():
    """获取当前用户信息"""
    try:
        user = request.current_user
        role = request.user_role

        if role == 'parent':
            return make_succ_response({
                'role': 'parent',
                'user': serialize_parent(user)
            })
        elif role == 'teacher':
            return make_succ_response({
                'role': 'teacher',
                'user': serialize_teacher(user)
            })
        else:
            return make_err_response('用户角色未知')
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return make_err_response('获取用户信息失败')


# ==================== 微信公众号事件接口 ====================

@app.route('/api/wechat/callback', methods=['GET', 'POST'])
def wechat_callback():
    """微信公众号事件回调"""
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        if verify_wechat_signature(signature, timestamp, nonce, WECHAT_TOKEN):
            return echostr
        else:
            return 'Invalid signature'

    elif request.method == 'POST':
        try:
            xml_data = request.data
            msg = parse_wechat_xml(xml_data)

            if not msg:
                return 'success'

            msg_type = msg.get('MsgType')
            event = msg.get('Event')
            openid = msg.get('FromUserName')

            if msg_type == 'event' and event == 'subscribe':
                existing_parent = get_parent_by_openid(openid)
                if not existing_parent:
                    parent = Parent(openid=openid)
                    create_parent(parent)
                    logger.info(f"新用户关注，创建家长记录: {openid}")

            return 'success'
        except Exception as e:
            logger.error(f"处理微信回调失败: {e}")
            return 'success'


# ==================== 静态文件服务 ====================

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传文件访问"""
    from flask import send_from_directory
    return send_from_directory('uploads', filename)


# ==================== 旧接口保留 ====================

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """
    params = request.get_json()

    if 'action' not in params:
        return make_err_response('缺少action参数')

    action = params['action']

    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

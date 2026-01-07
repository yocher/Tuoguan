# 学生接送通知系统后端

基于 Python Flask 的微信小程序和公众号统一后端服务，用于学生接送通知管理。

## 系统架构

### 认证方式
- **微信原生认证**：使用 openid 作为唯一身份标识
- **小程序**：WeChat Cloud Hosting 自动注入 openid（通过 X-WX-OPENID 请求头）
- **公众号**：通过事件回调获取 openid
- **管理员**：独立的 Web 界面，使用 session 认证

### 用户角色
1. **家长（Parent）**：通过小程序查看学生信息和接送记录
2. **教师（Teacher）**：通过小程序创建接送记录并上传照片
3. **管理员（Admin）**：通过 Web 界面管理学生、家长、教师和关联关系

### 核心功能
- 学生信息管理（管理员）
- 家长-学生多对多关联（管理员）
- 教师创建接送记录并上传照片
- 自动发送公众号模板消息通知家长
- 家长查看接送记录和照片
- 基于 openid 的严格权限控制

## 数据库设计

### 表结构

#### students（学生表）
- id: 主键
- name: 姓名
- student_number: 学号（唯一）
- class_name: 班级
- grade: 年级
- avatar_url: 头像URL
- created_at, updated_at: 时间戳

#### parents（家长表）
- id: 主键
- openid: 微信openid（唯一）
- name: 姓名
- phone: 电话
- created_at, updated_at: 时间戳

#### teachers（教师表）
- id: 主键
- openid: 微信openid（唯一）
- name: 姓名
- phone: 电话
- created_at, updated_at: 时间戳

#### admins（管理员表）
- id: 主键
- username: 用户名（唯一）
- password_hash: 密码哈希
- name: 姓名
- created_at, updated_at: 时间戳

#### parent_student（家长-学生关联表）
- id: 主键
- parent_id: 家长ID（外键）
- student_id: 学生ID（外键）
- relationship: 关系（如：父亲、母亲）
- created_at: 时间戳

#### pickup_records（接送记录表）
- id: 主键
- student_id: 学生ID（外键）
- teacher_id: 教师ID（外键）
- photo_url: 照片URL
- pickup_time: 接送时间
- notes: 备注
- created_at: 时间戳

## API 接口

### 管理员接口（需要 session 认证）

#### POST /api/admin/login
管理员登录
```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### POST /api/admin/logout
管理员登出

#### GET /api/admin/students
获取学生列表
- 查询参数：class_name（可选）

#### POST /api/admin/students
创建学生
```json
{
  "name": "张三",
  "student_number": "2024001",
  "class_name": "一年级1班",
  "grade": "一年级",
  "avatar_url": "https://..."
}
```

#### PUT /api/admin/students/{student_id}
更新学生信息

#### DELETE /api/admin/students/{student_id}
删除学生

#### GET /api/admin/parents
获取家长列表

#### POST /api/admin/parents
创建家长
```json
{
  "openid": "oXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "name": "李四",
  "phone": "13800138000"
}
```

#### GET /api/admin/teachers
获取教师列表

#### POST /api/admin/teachers
创建教师
```json
{
  "openid": "oXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "name": "王老师",
  "phone": "13900139000"
}
```

#### POST /api/admin/parent-student
绑定家长和学生
```json
{
  "parent_id": 1,
  "student_id": 1,
  "relationship": "父亲"
}
```

#### DELETE /api/admin/parent-student
解绑家长和学生

### 教师接口（需要 openid 认证）

#### GET /api/teacher/students
获取学生列表
- 查询参数：class_name（可选）

#### POST /api/teacher/pickup-records
创建接送记录（multipart/form-data）
- student_id: 学生ID
- photo: 照片文件
- notes: 备注（可选）

#### GET /api/teacher/pickup-records
获取接送记录列表
- 查询参数：limit（可选）

### 家长接口（需要 openid 认证）

#### GET /api/parent/students
获取自己的学生列表

#### GET /api/parent/pickup-records
获取接送记录列表
- 查询参数：limit（可选）

#### GET /api/parent/pickup-records/{record_id}
获取接送记录详情

### 通用接口

#### GET /api/user/info
获取当前用户信息和角色

### 微信公众号接口

#### GET/POST /api/wechat/callback
微信公众号事件回调
- GET: 验证服务器
- POST: 接收事件（如用户关注）

## 环境变量配置

```bash
# 数据库配置
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_password
MYSQL_ADDRESS=127.0.0.1:3306

# Session密钥
SECRET_KEY=your-secret-key-change-in-production

# 微信配置
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
WECHAT_TOKEN=your_wechat_token
WECHAT_TEMPLATE_ID=your_template_id
MINIPROGRAM_APPID=your_miniprogram_appid
```

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件或设置系统环境变量

### 3. 初始化数据库
```bash
python init_db.py
```

这将创建所有表并生成默认管理员账户：
- 用户名：admin
- 密码：admin123

**重要：请在生产环境中立即修改默认密码！**

### 4. 运行应用
```bash
python run.py 0.0.0.0 80
```

## 文件上传

照片上传到本地 `uploads/pickup_photos/` 目录。在生产环境中，建议使用云存储服务（如腾讯云 COS、阿里云 OSS）。

修改 `wxcloudrun/utils.py` 中的 `upload_file_to_storage` 函数以集成云存储。

## 安全注意事项

1. **修改默认密码**：初始化后立即修改管理员密码
2. **SECRET_KEY**：在生产环境使用强随机密钥
3. **HTTPS**：生产环境必须使用 HTTPS
4. **权限控制**：所有接口都有严格的权限验证
5. **SQL注入**：使用 SQLAlchemy ORM 防止 SQL 注入
6. **文件上传**：限制文件类型和大小（最大 16MB）

## 微信公众号配置

### 1. 服务器配置
在微信公众平台设置服务器地址：
```
https://your-domain.com/api/wechat/callback
```

### 2. 模板消息
需要在微信公众平台申请模板消息，包含以下字段：
- first: 标题
- keyword1: 学生姓名
- keyword2: 接送时间
- keyword3: 教师姓名
- remark: 备注

### 3. 小程序跳转
模板消息支持跳转到小程序页面，查看接送记录详情。

## 项目结构

```
.
├── config.py                 # 配置文件
├── run.py                    # 应用入口
├── init_db.py               # 数据库初始化脚本
├── requirements.txt         # Python依赖
├── wxcloudrun/
│   ├── __init__.py         # Flask应用初始化
│   ├── model.py            # 数据模型
│   ├── dao.py              # 数据访问层
│   ├── views.py            # 路由和视图
│   ├── utils.py            # 工具函数（认证、微信API、文件上传）
│   ├── response.py         # 响应格式化
│   └── templates/          # HTML模板
└── uploads/                # 上传文件目录
```

## 开发建议

### 添加新功能
1. 在 `model.py` 中定义数据模型
2. 在 `dao.py` 中添加数据访问方法
3. 在 `utils.py` 中添加序列化函数
4. 在 `views.py` 中添加路由和业务逻辑

### 测试
建议使用 Postman 或类似工具测试 API：
1. 先调用管理员登录接口获取 session
2. 创建学生、家长、教师
3. 绑定家长和学生关系
4. 模拟小程序请求（添加 X-WX-OPENID 请求头）

## 常见问题

### Q: 如何获取用户的 openid？
A:
- 小程序：WeChat Cloud Hosting 自动注入到请求头 X-WX-OPENID
- 公众号：用户关注时通过事件回调获取

### Q: 如何区分家长和教师？
A: 后端根据 openid 查询 parents 和 teachers 表，返回对应的角色和权限

### Q: 照片存储在哪里？
A: 默认存储在本地 uploads 目录，建议生产环境使用云存储

### Q: 如何修改管理员密码？
A: 直接在数据库中更新 admins 表的 password_hash 字段（使用 SHA256 哈希）

## License

[MIT](./LICENSE)

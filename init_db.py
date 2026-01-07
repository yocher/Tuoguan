#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建所有表和初始管理员账户
"""

import sys
import hashlib
from wxcloudrun import app, db
from wxcloudrun.model import Admin

def init_database():
    """初始化数据库"""
    with app.app_context():
        print("开始创建数据库表...")

        # 创建所有表
        db.create_all()

        print("数据库表创建成功！")

        # 检查是否已存在管理员
        existing_admin = Admin.query.filter_by(username='admin').first()
        if existing_admin:
            print("管理员账户已存在，跳过创建")
        else:
            # 创建默认管理员账户
            default_password = 'admin123'
            password_hash = hashlib.sha256(default_password.encode()).hexdigest()

            admin = Admin(
                username='admin',
                password_hash=password_hash,
                name='系统管理员'
            )

            db.session.add(admin)
            db.session.commit()

            print(f"默认管理员账户创建成功！")
            print(f"用户名: admin")
            print(f"密码: {default_password}")
            print("请在生产环境中立即修改默认密码！")

if __name__ == '__main__':
    try:
        init_database()
        print("\n数据库初始化完成！")
    except Exception as e:
        print(f"\n数据库初始化失败: {e}")
        sys.exit(1)

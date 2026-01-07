#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加头像字段
为 parents 和 teachers 表添加 avatar_url 字段
"""

import sys
from wxcloudrun import app, db

def migrate_add_avatar():
    """添加头像字段到家长和教师表"""
    with app.app_context():
        print("开始数据库迁移：添加头像字段...")

        try:
            # 为 parents 表添加 avatar_url 字段
            db.engine.execute(
                "ALTER TABLE parents ADD COLUMN avatar_url VARCHAR(500) DEFAULT NULL"
            )
            print("[OK] parents 表添加 avatar_url 字段成功")
        except Exception as e:
            if "Duplicate column name" in str(e) or "duplicate column" in str(e).lower():
                print("[OK] parents 表的 avatar_url 字段已存在，跳过")
            else:
                print(f"[ERROR] parents 表添加字段失败: {e}")
                raise

        try:
            # 为 teachers 表添加 avatar_url 字段
            db.engine.execute(
                "ALTER TABLE teachers ADD COLUMN avatar_url VARCHAR(500) DEFAULT NULL"
            )
            print("[OK] teachers 表添加 avatar_url 字段成功")
        except Exception as e:
            if "Duplicate column name" in str(e) or "duplicate column" in str(e).lower():
                print("[OK] teachers 表的 avatar_url 字段已存在，跳过")
            else:
                print(f"[ERROR] teachers 表添加字段失败: {e}")
                raise

if __name__ == '__main__':
    try:
        migrate_add_avatar()
        print("\n数据库迁移完成！")
    except Exception as e:
        print(f"\n数据库迁移失败: {e}")
        sys.exit(1)

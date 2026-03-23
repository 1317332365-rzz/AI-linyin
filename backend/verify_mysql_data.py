# -*- coding: utf-8 -*-
"""
验证MySQL数据迁移脚本
检查数据是否成功导入到MySQL
"""
import mysql.connector
from mysql.connector import Error


def verify_data():
    """验证MySQL中的数据"""
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'ai_gender_db'
    }
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("MySQL 数据验证报告")
        print("="*60)
        
        # 检查projects表
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        print(f"\n📊 项目总数: {count}")
        
        cursor.execute("SELECT id, owner, name, episode_no, video_provider FROM projects")
        projects = cursor.fetchall()
        for proj in projects:
            print(f"   - ID: {proj[0]}")
            print(f"     名称: {proj[2]}")
            print(f"     所有者: {proj[1]}")
            print(f"     剧集数: {proj[3]}")
            print(f"     视频提供商: {proj[4]}")
        
        # 检查assets表
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        print(f"\n🖼️  资源总数: {count}")
        
        # 检查shots表
        cursor.execute("SELECT COUNT(*) FROM shots")
        count = cursor.fetchone()[0]
        print(f"🎬 镜头总数: {count}")
        
        # 检查episode_scripts表
        cursor.execute("SELECT COUNT(*) FROM episode_scripts")
        count = cursor.fetchone()[0]
        print(f"📝 剧集脚本记录: {count}")
        
        # 检查project_script表
        cursor.execute("SELECT COUNT(*) FROM project_script")
        count = cursor.fetchone()[0]
        print(f"✍️  项目脚本记录: {count}")
        
        # 检查project_history表
        cursor.execute("SELECT COUNT(*) FROM project_history")
        count = cursor.fetchone()[0]
        print(f"⏱️  历史记录数: {count}")
        
        # 检查project_generated_data表
        cursor.execute("SELECT COUNT(*) FROM project_generated_data")
        count = cursor.fetchone()[0]
        print(f"🔧 生成数据记录: {count}")
        
        print("\n" + "="*60)
        print("✅ 数据验证完成!")
        print("="*60)
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ 验证失败: {e}")


if __name__ == '__main__':
    verify_data()

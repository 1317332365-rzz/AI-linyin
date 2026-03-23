# -*- coding: utf-8 -*-
"""
数据迁移脚本
将现有的JSON/SQLite数据迁移到MySQL数据库
"""
import json
import os
import sys
from modules.mysql_init import create_database
from modules.mysql_store import create_project, update_project

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))


def load_json_data():
    """从JSON文件加载数据"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'projects_db.json')
    
    if not os.path.exists(db_path):
        print(f"⚠️ 数据文件不存在: {db_path}")
        return []
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        projects = data.get('projects', [])
        print(f"✓ 从JSON文件加载了 {len(projects)} 个项目")
        return projects
    except Exception as e:
        print(f"❌ 加载JSON数据失败: {e}")
        return []


def migrate_to_mysql(projects):
    """将数据迁移到MySQL"""
    if not projects:
        print("⚠️ 没有项目数据需要迁移")
        return
    
    print(f"\n开始迁移 {len(projects)} 个项目到MySQL...")
    
    successful = 0
    failed = 0
    
    for project in projects:
        try:
            project_id = project.get('id')
            if not project_id:
                print(f"  ⚠️ 跳过没有ID的项目")
                failed += 1
                continue
            
            # 创建项目
            create_project(
                project_id,
                project.get('name', '未命名项目'),
                project.get('script_title', ''),
                project.get('episode_no', 1),
                project.get('owner', 'admin')
            )
            
            # 更新所有关联数据
            update_project(
                project_id,
                assets=project.get('assets', []),
                shots=project.get('shots', []),
                history=project.get('history', []),
                script=project.get('script', {}),
                generated_data=project.get('generated_data', []),
                episode_scripts=project.get('episode_scripts', {}),
            )
            
            print(f"  ✓ 项目 {project_id}({project.get('name', '未命名项目')}) 迁移成功")
            successful += 1
            
        except Exception as e:
            print(f"  ❌ 项目 {project.get('id', 'unknown')} 迁移失败: {e}")
            failed += 1
    
    print(f"\n迁移完成: {successful} 个成功, {failed} 个失败")
    return successful, failed


def main():
    """主函数"""
    print("=" * 60)
    print("AI视频生成平台 - 数据迁移脚本")
    print("=" * 60)
    
    # 第1步: 创建MySQL数据库和表
    print("\n[1/3] 创建MySQL数据库和表...")
    if not create_database():
        print("❌ 数据库创建失败，中止迁移")
        return False
    
    # 第2步: 加载JSON数据
    print("\n[2/3] 加载现有数据...")
    projects = load_json_data()
    
    # 第3步: 迁移数据
    print("\n[3/3] 迁移数据到MySQL...")
    migrate_to_mysql(projects)
    
    print("\n" + "=" * 60)
    print("✅ 数据迁移完成!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    main()

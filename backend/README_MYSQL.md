# AI视频生成平台 - MySQL集成指南

## 概览

本项目已完整集成MySQL数据库支持。您可以无缝切换在MySQL和文件系统存储之间，所有应用数据都能持久化到MySQL数据库中。

## 快速开始（5分钟）

### 环境要求
- MySQL 5.7 或更高版本
- Python 3.8 或更高版本
- 已安装的依赖包（见下文）

### 第一步：安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 第二步：配置MySQL连接
编辑 `backend/.env` 文件（或从 `.env.example` 复制）：
```env
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=ai_gender_db
```

### 第三步：初始化数据库
```bash
python modules/mysql_init.py
```

输出应显示：
```
✓ 数据库 ai_gender_db 创建成功或已存在
✓ 表 projects 创建成功
✓ 表 assets 创建成功
✓ 表 shots 创建成功
✓ 表 episode_scripts 创建成功
✓ 表 project_script 创建成功
✓ 表 project_history 创建成功
✓ 表 project_generated_data 创建成功

✅ 所有表创建成功!
```

### 第四步：迁移现有数据（可选）
如果您有现有的JSON/SQLite数据需要迁移到MySQL：
```bash
python migrate_to_mysql.py
```

### 第五步：启动应用
```bash
python app.py
```

## 文件说明

### 核心模块

| 文件 | 说明 | 功能 |
|------|------|------|
| `modules/mysql_init.py` | MySQL初始化 | 创建数据库和所有表 |
| `modules/mysql_store.py` | MySQL存储模块 | 提供数据访问API |
| `modules/storage_config.py` | 存储配置 | 动态选择存储后端 |
| `migrate_to_mysql.py` | 数据迁移脚本 | 将JSON数据迁移到MySQL |
| `verify_mysql_data.py` | 数据验证工具 | 验证数据完整性 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境配置（已包含MySQL设置） |
| `.env.example` | 配置示例 |
| `MYSQL_SETUP.md` | 详细设置指南 |
| `MYSQL_INTEGRATION_SUMMARY.md` | 集成总结 |

## 数据库架构

### 主要表

#### projects 表
存储项目的基本信息。

```sql
CREATE TABLE projects (
    id VARCHAR(255) PRIMARY KEY,              -- 项目ID
    owner VARCHAR(255) NOT NULL,              -- 项目所有者
    name VARCHAR(500),                        -- 项目名称
    script_title VARCHAR(500),                -- 脚本标题
    episode_no INT DEFAULT 1,                 -- 剧集数
    video_provider VARCHAR(50) DEFAULT 'openai', -- 视频提供商
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,    -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
```

#### assets 表
存储项目的资源（角色、场景等）。

```sql
CREATE TABLE assets (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    image_url LONGTEXT,
    name VARCHAR(500),
    prompt LONGTEXT,
    type VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

#### shots 表
存储视频镜头信息。

```sql
CREATE TABLE shots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    scene_no INT,
    title VARCHAR(500),
    duration VARCHAR(50),
    -- 其他镜头字段...
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

#### episode_scripts 表
存储剧集脚本。

#### project_script 表
存储项目脚本。

#### project_history 表
存储项目历史记录。

#### project_generated_data 表
存储生成的数据。

## API 使用示例

### 导入存储模块
```python
from modules.storage_config import (
    list_projects,
    get_project,
    create_project,
    update_project
)
```

### 获取项目列表
```python
# 获取所有项目
projects = list_projects()

# 获取特定用户的项目
projects = list_projects(owner='admin')
```

### 获取单个项目
```python
project = get_project('project_id', owner='admin')
if project:
    print(f"项目: {project['name']}")
    print(f"资源数: {len(project['assets'])}")
    print(f"镜头数: {len(project['shots'])}")
```

### 创建项目
```python
new_project = create_project(
    project_id='p_12345',
    name='我的项目',
    script_title='脚本标题',
    episode_no=5,
    owner='admin'
)
```

### 更新项目
```python
updated = update_project(
    'project_id',
    name='新名称',
    episode_no=10,
    assets=[{'id': 'a1', 'name': 'Asset 1', ...}],
    shots=[{'sceneNo': 1, 'title': 'Scene 1', ...}],
    script={'input': '脚本内容', 'duration': '3min', 'result': {...}}
)
```

## 切换存储后端

### 启用MySQL
编辑 `.env`：
```env
USE_MYSQL=true
```

### 继续使用文件系统
编辑 `.env`：
```env
USE_MYSQL=false
```

## 性能优化

### 已添加的索引
- `projects(owner)` - 加速用户查询
- `projects(updated_at)` - 加速排序
- `assets(project_id)` - 加速资源查询
- `shots(project_id)` - 加速镜头查询
- `episode_scripts(project_id, episode_key)` - 加速剧集查询

### 查询优化建议
1. 使用分页查询大数据集
2. 在必要时缓存热数据
3. 定期运行 `ANALYZE TABLE` 更新统计信息

## 备份和恢复

### 完整备份
```bash
mysqldump -u root -p ai_gender_db > backup.sql
```

### 定时备份脚本
```python
# 示例：每天午夜自动备份
import subprocess
import datetime

def backup_database():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.sql'
    cmd = f'mysqldump -u root -p ai_gender_db > {filename}'
    subprocess.run(cmd, shell=True)
```

### 恢复备份
```bash
mysql -u root -p ai_gender_db < backup.sql
```

## 故障排除

### 问题1：连接被拒绝
```
Error: MySQL Connection refused (ConnectionRefusedError)
```

**解决方案：**
1. 确认MySQL服务运行：`mysql -u root -p`
2. 检查 `.env` 中的配置正确
3. 确认防火墙未阻止3306端口

### 问题2：表不存在
```
Error: Table 'ai_gender_db.projects' doesn't exist
```

**解决方案：**
1. 运行初始化脚本：`python modules/mysql_init.py`
2. 验证数据库是否创建：`mysql -u root -p -e "USE ai_gender_db; SHOW TABLES;"`

### 问题3：权限错误
```
Error: Access denied for user 'root'@'localhost'
```

**解决方案：**
1. 验证用户名和密码
2. 检查MySQL用户权限
3. 重置MySQL root密码（如需要）

### 问题4：字符编码错误
```
Error: UnicodeDecodeError
```

**解决方案：**
- 确保表使用UTF-8MB4编码（已自动设置）
- 检查中文字符是否正确显示

## 监控和日志

### 查看MySQL日志
```bash
# Linux/Mac
tail -f /var/log/mysql/error.log

# Windows
type "C:\ProgramData\MySQL\MySQL Server 8.0\Data\error.log"
```

### 性能监控
```sql
-- 查看表的行数
SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES 
WHERE TABLE_SCHEMA='ai_gender_db';

-- 查看表大小
SELECT TABLE_NAME, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='ai_gender_db';

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
```

## 扩展功能

### 添加新表
1. 在 `mysql_init.py` 的 `create_database()` 函数中添加 CREATE TABLE 语句
2. 在 `mysql_store.py` 中添加对应的CRUD函数
3. 运行初始化脚本创建新表

### 添加自定义字段
1. 修改 `mysql_init.py` 中的 CREATE TABLE 语句
2. 更新 `mysql_store.py` 中的数据处理函数
3. 使用 ALTER TABLE 迁移现有数据

## 最佳实践

1. **定期备份** - 每天至少备份一次
2. **监控性能** - 定期检查慢查询
3. **清理数据** - 删除过期的导出文件
4. **验证数据** - 使用 `verify_mysql_data.py` 定期验证
5. **测试恢复** - 定期测试备份恢复流程
6. **记录更改** - 为大型修改保存SQL脚本

## 支持和文档

- **详细设置指南**: 查看 [MYSQL_SETUP.md](MYSQL_SETUP.md)
- **集成总结**: 查看 [MYSQL_INTEGRATION_SUMMARY.md](MYSQL_INTEGRATION_SUMMARY.md)
- **官方文档**: https://dev.mysql.com/doc/
- **Python MySQL驱动**: https://dev.mysql.com/doc/connector-python/en/

## 更新日志

### v1.0.0 (2026-03-20)
- ✅ 初始MySQL集成
- ✅ 完整的数据迁移脚本
- ✅ 动态存储后端切换
- ✅ 数据验证工具
- ✅ 完整文档和示例

## 许可证

MIT

---

**最后更新**: 2026年3月20日  
**维护人**: 开发团队

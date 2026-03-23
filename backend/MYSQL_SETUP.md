# MySQL数据库集成指南

## 概述
本项目已集成MySQL数据库支持。您可以将所有数据存储在MySQL数据库中，而不是使用JSON文件或SQLite。

## 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置MySQL连接
编辑 `.env` 文件（或创建从 `.env.example` 复制）：
```env
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=ai_gender_db
```

### 3. 创建数据库表
```bash
python -c "from modules.mysql_init import create_database; create_database()"
```

或直接运行：
```bash
python modules/mysql_init.py
```

输出应该显示：
```
✓ 数据库 ai_gender_db 创建成功或已存在
✓ 表 projects 创建成功
✓ 表 assets 创建成功
...
✅ 所有表创建成功!
```

### 4. 迁移现有数据（可选）
如果您有现有的JSON或SQLite数据，可以将其迁移到MySQL：
```bash
python migrate_to_mysql.py
```

### 5. 启动应用
```bash
python app.py
```

## 配置选项

### 使用MySQL
```env
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=ai_gender_db
```

### 继续使用文件系统
```env
USE_MYSQL=false
```

## 数据库架构

### 表结构

#### projects（项目表）
- `id` - 项目ID（主键）
- `owner` - 项目所有者
- `name` - 项目名称
- `script_title` - 脚本标题
- `episode_no` - 剧集数
- `video_provider` - 视频提供商
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### assets（资源表）
- `id` - 资源ID（主键）
- `project_id` - 所属项目ID
- `image_url` - 图像URL
- `name` - 资源名称
- `prompt` - 生成提示
- `type` - 资源类型

#### shots（镜头表）
- `id` - 镜头ID（主键）
- `project_id` - 所属项目ID
- `scene_no` - 场景序号
- `title` - 标题
- `duration` - 持续时间
- `start_frame_*` - 开始帧数据
- `end_frame_*` - 结束帧数据
- `video_url` - 视频URL
- `video_task_*` - 视频任务相关信息

#### episode_scripts（剧集脚本表）
- `id` - 记录ID（主键）
- `project_id` - 所属项目ID
- `episode_key` - 剧集标记
- `script_input` - 脚本输入
- `script_duration` - 脚本时长
- `script_result` - 脚本结果（JSON）
- `history` - 历史记录（JSON）

#### project_script（项目脚本表）
- `project_id` - 项目ID（主键）
- `script_input` - 脚本输入
- `script_duration` - 脚本时长
- `script_result` - 脚本结果（JSON）

#### project_history（项目历史表）
- `id` - 记录ID（主键）
- `project_id` - 所属项目ID
- `history_data` - 历史数据（JSON）

#### project_generated_data（生成数据表）
- `id` - 记录ID（主键）
- `project_id` - 所属项目ID
- `generated_data` - 生成的数据（JSON）

## 故障排除

### 连接错误
**问题**：`MySQL Connection refused`
- 检查MySQL服务是否运行：`mysql -u root -p`
- 检查主机名和端口是否正确
- 确认用户名和密码

### 数据库不存在
**问题**：`Unknown database 'ai_gender_db'`
- 运行初始化脚本：`python modules/mysql_init.py`

### 迁移失败
**问题**：数据迁移时出错
- 确认MySQL能够连接
- 检查现有JSON文件是否有效
- 查看错误日志了解具体问题

## API兼容性
MySQL存储后端与文件系统后端兼容，所有现有的API调用都无需修改。

## 性能监察
对于大型项目，您可以添加MySQL索引以提高查询性能：
```sql
-- 已在表创建时自动添加的索引
CREATE INDEX idx_owner ON projects(owner);
CREATE INDEX idx_updated_at ON projects(updated_at);
CREATE INDEX idx_project_id ON assets(project_id);
CREATE INDEX idx_project_id ON shots(project_id);
```

## 备份和还原

### 备份数据库
```bash
mysqldump -u root -p ai_gender_db > backup.sql
```

### 还原数据库
```bash
mysql -u root -p ai_gender_db < backup.sql
```

## 许可证
MIT

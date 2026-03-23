# AI-linyin

一个面向 **AI 漫剧/短剧内容生产** 的创作工具，提供从剧本拆解、分镜设计、角色与场景资产生成，到导演工作台、视频生成与最终导出的完整流程。

![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
## 项目简介

AI-linyin 致力于把“剧本 → 分镜 → 资产 → 视频 → 导出”这一套内容生产流程整合到一个工作台中，帮助创作者更高效地完成 AI 漫剧、AI 短剧、剧情视频等内容制作。
`使用的api中转站平台`
 ```
 https://www.jinluoyou.top/
 ```
当前项目采用前后端分离架构：

- **前端**：Vue 3 + Vite
- **后端**：Flask
- **数据存储**：支持文件存储，也支持切换到 MySQL
- **能力集成**：支持 LLM 配置、角色/场景生成、配音、视频生成、项目管理等

---

## 功能特性

### 1. 剧本与分镜
- 输入或整理剧本内容
- 解析剧本结构
- 生成分镜/镜头设计基础数据
- 支持按“集数”管理项目内容

### 2. 资产与选角
- 角色生成
- 场景生成
- 项目资产管理
- 角色、场景等素材的统一组织

### 3. 导演工作台
- Prompt 增强
- 视频生成任务发起
- 视频任务状态查询
- 配音/旁白生成

### 4. 导出阶段
- 最终视频导出
- 素材整合与输出管理

### 5. 系统配置
- LLM 配置管理
- 视频接口配置
- 多模型/多平台接入扩展能力

### 6. 项目管理
- 创建项目
- 项目列表查询
- 项目详情读取
- 项目更新与持久化

---

## 项目结构

```text
AI-linyin/
├─ ai-app/                  # 相关应用目录
├─ backend/                 # Flask 后端
│  ├─ data/                 # 本地数据
│  ├─ modules/              # 业务模块
│  ├─ tests/                # 测试目录
│  ├─ app.py                # 后端入口
│  ├─ requirements.txt      # Python 依赖
│  ├─ migrate_to_mysql.py   # 数据迁移脚本
│  ├─ sync_mysql_schema.py  # MySQL 结构同步
│  ├─ verify_mysql_data.py  # MySQL 数据校验
│  ├─ MYSQL_SETUP.md        # MySQL 配置说明
│  ├─ MYSQL_INTEGRATION_SUMMARY.md
│  └─ README_MYSQL.md
├─ frontend/                # Vue 前端
│  ├─ public/
│  ├─ src/
│  ├─ package.json
│  ├─ vite.config.js
│  └─ index.html
├─ image.png
├─ image-1.png
├─ image-2.png
├─ image-3.png
└─ README.md 
 

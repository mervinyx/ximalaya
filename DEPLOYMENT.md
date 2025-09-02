# 部署指南

本文档提供详细的GitHub上传和Zeabur部署步骤。

## 📋 部署前准备

### 1. 确认项目文件
确保项目包含以下文件：
- `app.py` - Flask应用主文件
- `ximalaya_crawler_final.py` - 爬虫核心代码
- `requirements.txt` - 依赖包列表
- `templates/` - HTML模板目录
- `uploads/` 和 `results/` - 文件目录（包含.gitkeep）
- `.gitignore` - Git忽略文件
- `README.md` - 项目说明
- `zeabur.json` - Zeabur配置文件

### 2. 检查依赖
确认 `requirements.txt` 包含所有必要依赖：
```
Flask>=2.3.0
pandas>=1.5.0
openpyxl>=3.1.0
selenium>=4.15.0
# ... 其他依赖
```

## 🚀 GitHub 上传步骤

### 步骤 1: 初始化Git仓库
```bash
# 在项目根目录执行
git init
```

### 步骤 2: 添加文件到Git
```bash
# 添加所有文件
git add .

# 检查状态
git status
```

### 步骤 3: 提交代码
```bash
git commit -m "Initial commit: 喜马拉雅主播信息爬虫Web应用"
```

### 步骤 4: 创建GitHub仓库
1. 访问 [GitHub](https://github.com)
2. 点击右上角 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `ximalaya-crawler`
   - Description: `喜马拉雅主播信息爬虫 Web 应用`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 步骤 5: 连接远程仓库
```bash
# 添加远程仓库（替换为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/ximalaya-crawler.git

# 推送代码
git branch -M main
git push -u origin main
```

## 🌐 Zeabur 部署步骤

### 方法一：GitHub集成部署（推荐）

#### 步骤 1: 访问Zeabur
1. 打开 [zeabur.com](https://zeabur.com)
2. 使用GitHub账户登录

#### 步骤 2: 创建新项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub"
3. 授权Zeabur访问你的GitHub仓库

#### 步骤 3: 选择仓库
1. 在仓库列表中找到 `ximalaya-crawler`
2. 点击 "Import"

#### 步骤 4: 配置部署
1. Zeabur会自动检测到这是一个Flask应用
2. 确认以下配置：
   - **Framework**: Flask
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Port**: 5002

#### 步骤 5: 部署
1. 点击 "Deploy"
2. 等待部署完成（通常需要2-5分钟）
3. 部署成功后会获得一个公网访问地址

### 方法二：模板部署

如果你的仓库是公开的，可以创建一键部署按钮：

1. 在README.md中添加部署按钮：
```markdown
[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates/YOUR_TEMPLATE_ID)
```

2. 用户点击按钮即可一键部署

## 🔧 部署后配置

### 1. 环境变量设置
在Zeabur控制台中，可以设置以下环境变量：
- `FLASK_ENV=production`
- `PYTHONPATH=.`

### 2. 域名配置
1. 在Zeabur项目设置中
2. 点击 "Domains"
3. 可以使用免费的 `.zeabur.app` 域名
4. 或绑定自定义域名

### 3. 监控和日志
- 在Zeabur控制台查看应用状态
- 查看部署日志和运行日志
- 监控资源使用情况

## 🚨 常见问题解决

### 问题1：依赖安装失败
**解决方案**：
- 检查 `requirements.txt` 格式
- 确保版本号兼容
- 查看构建日志中的错误信息

### 问题2：应用启动失败
**解决方案**：
- 检查 `app.py` 中的端口配置
- 确保 `if __name__ == '__main__':` 部分正确
- 查看运行日志

### 问题3：静态文件访问问题
**解决方案**：
- 确保 `templates/` 目录结构正确
- 检查Flask静态文件配置

### 问题4：Selenium在生产环境问题
**解决方案**：
- Zeabur支持Chrome浏览器
- 确保使用 `webdriver-manager` 自动管理驱动
- 在生产环境中使用headless模式

## 📊 性能优化建议

1. **资源限制**：
   - 合理设置爬虫并发数
   - 添加请求间隔避免被封

2. **缓存策略**：
   - 对重复请求进行缓存
   - 使用Redis缓存（如需要）

3. **错误处理**：
   - 完善异常捕获
   - 添加重试机制

## 🔄 更新部署

当代码有更新时：

```bash
# 提交更改
git add .
git commit -m "更新说明"
git push origin main
```

Zeabur会自动检测到代码更新并重新部署。

## 📞 技术支持

如果遇到部署问题：
1. 查看Zeabur官方文档
2. 检查项目的GitHub Issues
3. 联系技术支持

---

🎉 **恭喜！** 你的喜马拉雅爬虫Web应用现在已经成功部署到云端，可以通过公网访问了！
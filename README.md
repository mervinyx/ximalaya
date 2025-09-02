# 喜马拉雅主播信息爬虫 Web 应用

🎯 一个功能完整的Web应用，用于批量爬取喜马拉雅主播信息，支持Excel文件上传和结果下载。

## ✨ 功能特点

### 🌐 Web界面
- **现代化UI设计**：响应式界面，支持拖拽上传
- **实时进度显示**：爬虫执行过程可视化
- **批量处理**：支持一次性处理多个主播URL
- **文件管理**：自动化的文件上传、处理和下载

### 📊 数据处理
- **Excel支持**：支持.xlsx和.xls格式文件上传和下载
- **智能解析**：自动解析Excel第一列的URL列表
- **数据统计**：提取主播名称、等级、粉丝数、专辑总数、总播放量
- **错误处理**：完善的异常处理和用户反馈

### 🔧 技术特性
- **双引擎支持**：Selenium + Requests，确保稳定性
- **资源管理**：自动管理浏览器驱动，避免资源泄漏
- **并发安全**：支持多用户同时使用

## 🚀 快速开始

### 本地部署

1. **克隆项目**
```bash
git clone <your-repo-url>
cd ximalaya-crawler
```

2. **安装依赖**
```bash
pip install -r requirements_web.txt
```

3. **启动应用**
```bash
python app.py
```

4. **访问应用**
打开浏览器访问：http://localhost:5002

### 使用方法

1. **准备Excel文件**：在Excel第一列放入喜马拉雅主播URL
2. **上传文件**：拖拽或点击上传Excel文件
3. **执行爬虫**：点击"开始爬虫"按钮
4. **下载结果**：爬虫完成后下载包含主播信息的Excel文件

## 🌍 部署到 Zeabur

### 一键部署

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates)

### 手动部署

1. **推送到GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **在Zeabur部署**
   - 访问 [zeabur.com](https://zeabur.com)
   - 连接GitHub账户
   - 选择此项目仓库
   - 自动检测Flask应用并部署

3. **环境配置**
   - Zeabur会自动安装依赖
   - 应用将在几分钟内上线

## 📁 项目结构

```
ximalaya-crawler/
├── app.py                 # Flask Web应用主文件
├── ximalaya_crawler_final.py  # 爬虫核心代码
├── requirements_web.txt   # Web应用依赖
├── templates/            # HTML模板
│   ├── index.html       # 主页
│   └── crawl.html       # 爬虫执行页
├── uploads/             # 上传文件目录
├── results/             # 结果文件目录
└── README.md           # 项目说明
```

## 🔧 技术栈

- **后端**：Flask, Python 3.9+
- **前端**：HTML5, CSS3, JavaScript
- **数据处理**：pandas, openpyxl
- **爬虫引擎**：Selenium, BeautifulSoup, Requests
- **部署**：Zeabur, Docker支持

## 📋 数据输出格式

| 字段 | 说明 |
|------|------|
| 主播名称 | 主播的显示名称 |
| 主播等级 | 主播等级信息 |
| 粉丝数 | 主播粉丝数量 |
| 专辑总数 | 主播的专辑数量 |
| 总播放量 | 所有专辑播放量总和 |
| 爬取时间 | 数据爬取的时间戳 |
| 使用方法 | 使用的爬虫引擎 |

## 输出格式

数据以JSON格式保存，示例如下：

```json
{
  "主播名称": "张_小c",
  "主播等级": "等级7",
  "粉丝数": "2799",
  "专辑信息": [
    {
      "专辑名称": "给不起彩礼，只好娶了魔门圣女丨张_小c演播、【多播】",
      "播放量": "54.32万"
    },
    {
      "专辑名称": "我的姐姐是恶役千金大小姐【多播】",
      "播放量": "3.25万"
    },
    {
      "专辑名称": "神医弃女|暮玖&阑珊梦&全勇&泡芙先生领衔超人气多人有声剧",
      "播放量": "5198.89万"
    }
  ],
  "专辑总数": 23,
  "爬取时间": "2025-01-20 10:30:45",
  "使用方法": "selenium"
}
```

## ⚠️ 注意事项

1. **合规使用**：请遵守喜马拉雅的robots.txt和服务条款
2. **频率控制**：建议设置合理的请求间隔，避免对服务器造成压力
3. **数据用途**：仅用于学习和研究目的，请勿用于商业用途
4. **浏览器要求**：Selenium模式需要Chrome浏览器支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
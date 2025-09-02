from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
import pandas as pd
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import json
from ximalaya_crawler_final import XimalayaCrawlerFinal

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于flash消息

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_urls_from_excel(file_path):
    """从Excel文件第一列读取URL列表"""
    try:
        df = pd.read_excel(file_path)
        # 获取第一列的所有值，过滤空值
        urls = df.iloc[:, 0].dropna().tolist()
        # 过滤出有效的URL（包含http或https）
        valid_urls = []
        for url in urls:
            url_str = str(url).strip()
            if url_str.startswith(('http://', 'https://')):
                valid_urls.append(url_str)
        return valid_urls
    except Exception as e:
        print(f"读取Excel文件错误: {e}")
        return []

def save_results_to_excel(results, filename):
    """将爬虫结果保存为Excel文件"""
    try:
        # 准备数据
        data = []
        for result in results:
            if 'error' in result:
                # 处理错误情况
                data.append({
                    'URL': result.get('url', ''),
                    '主播名称': '爬取失败',
                    '主播等级': '',
                    '粉丝数': '',
                    '专辑总数': 0,
                    '总播放量': 0,
                    '错误信息': result.get('error', ''),
                    '爬取时间': result.get('爬取时间', ''),
                    '使用方法': result.get('使用方法', '')
                })
            else:
                # 处理成功情况
                data.append({
                    'URL': result.get('url', ''),
                    '主播名称': result.get('主播名称', ''),
                    '主播等级': result.get('主播等级', ''),
                    '粉丝数': result.get('粉丝数', ''),
                    '专辑总数': result.get('专辑总数', 0),
                    '总播放量': result.get('总播放量', 0),
                    '错误信息': '',
                    '爬取时间': result.get('爬取时间', ''),
                    '使用方法': result.get('使用方法', '')
                })
        
        # 创建DataFrame并保存
        df = pd.DataFrame(data)
        file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
        df.to_excel(file_path, index=False, engine='openpyxl')
        return file_path
    except Exception as e:
        print(f"保存Excel文件错误: {e}")
        return None

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 读取URL列表
        urls = read_urls_from_excel(file_path)
        if not urls:
            flash('Excel文件中没有找到有效的URL')
            return redirect(url_for('index'))
        
        return render_template('crawl.html', urls=urls, filename=filename, url_count=len(urls))
    else:
        flash('只支持Excel文件(.xlsx, .xls)')
        return redirect(url_for('index'))

@app.route('/crawl', methods=['POST'])
def start_crawl():
    """开始爬虫任务"""
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'error': '文件名缺失'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 400
    
    # 读取URL列表
    urls = read_urls_from_excel(file_path)
    if not urls:
        return jsonify({'error': 'Excel文件中没有找到有效的URL'}), 400
    
    # 初始化爬虫
    crawler = XimalayaCrawlerFinal(use_selenium=True)
    results = []
    
    try:
        for i, url in enumerate(urls):
            try:
                print(f"正在爬取第 {i+1}/{len(urls)} 个URL: {url}")
                result = crawler.crawl_anchor_info(url)
                result['url'] = url  # 添加URL到结果中
                results.append(result)
                
                # 添加延迟避免被封
                time.sleep(2)
                
            except Exception as e:
                print(f"爬取URL {url} 时出错: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    '爬取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    finally:
        # 关闭爬虫
        crawler.close()
    
    # 保存结果到Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_filename = f"crawl_results_{timestamp}.xlsx"
    result_path = save_results_to_excel(results, result_filename)
    
    if result_path:
        return jsonify({
            'success': True,
            'message': f'爬虫完成！共处理 {len(urls)} 个URL，成功 {len([r for r in results if "error" not in r])} 个',
            'result_file': result_filename,
            'total_urls': len(urls),
            'success_count': len([r for r in results if "error" not in r]),
            'error_count': len([r for r in results if "error" in r])
        })
    else:
        return jsonify({'error': '保存结果文件失败'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载结果文件"""
    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('文件不存在')
        return redirect(url_for('index'))

@app.route('/progress')
def get_progress():
    """获取爬虫进度（预留接口）"""
    # 这里可以实现实时进度更新
    return jsonify({'progress': 0})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
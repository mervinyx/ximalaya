#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
喜马拉雅主播信息爬虫工具 - 最终版
基于测试结果优化的版本
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from typing import Dict, Optional
import os

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("提示: 如需处理动态内容，请安装selenium: pip install selenium")

class XimalayaCrawlerFinal:
    def __init__(self, use_selenium=True, debug=False):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.debug = debug
        
        if not self.use_selenium:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
    
    def debug_print(self, message):
        """调试输出"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def get_page_content_selenium(self, url: str) -> Optional[str]:
        """使用selenium获取页面内容"""
        if not SELENIUM_AVAILABLE:
            print("错误: Selenium不可用，请安装: pip install selenium")
            return None
        
        try:
            self.debug_print(f"使用selenium访问: {url}")
            
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=375,667')  # 模拟手机屏幕
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(url)
            
            # 等待页面加载完成
            time.sleep(5)
            
            # 尝试等待关键元素加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except:
                self.debug_print("等待页面元素超时，继续处理")
            
            # 获取页面源码
            html_content = driver.page_source
            driver.quit()
            
            return html_content
            
        except Exception as e:
            print(f"Selenium获取页面失败: {e}")
            return None
    
    def get_page_content_requests(self, url: str) -> Optional[str]:
        """使用requests获取页面内容"""
        try:
            self.debug_print(f"使用requests访问: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def extract_anchor_name(self, soup: BeautifulSoup) -> str:
        """提取主播名称 - 优化版"""
        # 方法1: 查找页面标题中的主播名称
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # 从标题中提取主播名称 "【张_小c】有声作品全集"
            name_match = re.search(r'【([^】]+)】', title_text)
            if name_match:
                return name_match.group(1)
        
        # 方法2: 查找h1标签
        h1_elements = soup.find_all('h1')
        for h1 in h1_elements:
            text = h1.get_text(strip=True)
            if text and len(text) < 20 and not any(x in text for x in ['专辑', '播放', '万', '粉丝', '关注']):
                return text
        
        # 方法3: 查找包含主播名称的元素
        name_elements = soup.find_all(string=re.compile(r'^[\u4e00-\u9fa5_a-zA-Z0-9]{2,15}$'))
        for elem in name_elements:
            text = str(elem).strip()
            if text and len(text) < 20 and not any(x in text for x in ['专辑', '播放', '万', '粉丝', '关注', '打开', 'APP']):
                return text
        
        return "未找到主播名称"
    
    def extract_fans_count(self, soup: BeautifulSoup) -> str:
        """提取粉丝数 - 优化版"""
        # 查找包含"粉丝"的元素
        fans_elements = soup.find_all(string=re.compile(r'\d+.*粉丝'))
        for elem in fans_elements:
            text = str(elem)
            numbers = re.findall(r'\d+', text)
            if numbers:
                return numbers[0]
        
        # 查找数字+粉丝的模式
        all_text = soup.get_text()
        fans_match = re.search(r'(\d+)\s*粉丝', all_text)
        if fans_match:
            return fans_match.group(1)
        
        return "未找到粉丝数"
    
    def extract_album_titles(self, soup: BeautifulSoup) -> list:
        """
        提取专辑名称 - 只从"TA的专辑"区域提取
        """
        album_titles = []
        
        # 首先查找"TA的专辑"标题区域
        album_section = soup.find('div', class_='section-title _ka', string='TA的专辑')
        if not album_section:
            # 如果没找到确切匹配，尝试查找包含"专辑"的section-title
            album_section = soup.find('div', class_='section-title _ka')
            if album_section and '专辑' not in album_section.get_text():
                album_section = None
        
        if album_section:
            # 找到专辑区域的父容器
            album_container = album_section.parent
            if album_container:
                # 在专辑容器内查找专辑标题
                selectors = [
                    'h3',  # 常见的标题标签
                    'h2',  # 另一种标题标签
                    '[class*="title"]',  # 包含title的class
                    '.album-title',  # 专辑标题class
                    '.track-title',  # 音轨标题class
                    '.item-title',   # 项目标题class
                    'a[href*="album"]'  # 专辑链接
                ]
                
                for selector in selectors:
                     elements = album_container.select(selector)
                     for elem in elements:
                          title = elem.get_text(strip=True)
                          # 过滤条件：长度合理、不重复、不包含数字万（避免拼接的内容）
                          if (title and 5 < len(title) < 80 and 
                              title not in album_titles and 
                              not re.search(r'\d+\.?\d*万', title) and
                              ('丨' in title or '【' in title or '|' in title)):  # 专辑名称通常包含这些分隔符
                              album_titles.append(title)
        
        # 如果没有找到专辑区域，回退到原来的方法但更严格
        if not album_titles:
            # 查找包含专辑关键词的文本，但更严格筛选
            album_keywords = ['专辑', '有声小说', '多人剧']
            text_elements = soup.find_all(string=True)
            for text in text_elements:
                text_str = str(text).strip()
                if any(keyword in text_str for keyword in album_keywords) and len(text_str) > 10 and len(text_str) < 100:
                    if text_str not in album_titles:
                        album_titles.append(text_str)
        
        return album_titles if album_titles else ["未找到专辑名称"]
    
    def extract_play_counts(self, soup: BeautifulSoup) -> list:
        """
        提取播放量 - 只从"TA的专辑"区域提取
        """
        play_counts = []
        
        # 首先查找"TA的专辑"标题区域
        album_section = soup.find('div', class_='section-title _ka', string='TA的专辑')
        if not album_section:
            # 如果没找到确切匹配，尝试查找包含"专辑"的section-title
            album_section = soup.find('div', class_='section-title _ka')
            if album_section and '专辑' not in album_section.get_text():
                album_section = None
        
        if album_section:
            # 找到专辑区域的父容器
            album_container = album_section.parent
            if album_container:
                # 在专辑容器内查找播放量
                play_elements = album_container.find_all(string=re.compile(r'\d+\.?\d*万'))
                for elem in play_elements:
                    text = str(elem).strip()
                    # 查找数字.数字万的模式
                    play_match = re.search(r'(\d+\.\d+万)', text)
                    if play_match and play_match.group(1) not in play_counts:
                        play_counts.append(play_match.group(1))
                    else:
                        # 查找整数万的模式
                        play_match = re.search(r'(\d+万)', text)
                        if play_match and play_match.group(1) not in play_counts:
                            play_counts.append(play_match.group(1))
                
                # 查找包含播放图标的元素附近的播放量
                play_icon_elements = album_container.find_all('i', class_=re.compile(r'.*play.*', re.I))
                for icon in play_icon_elements:
                    parent = icon.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        play_match = re.search(r'(\d+\.?\d*万)', text)
                        if play_match and play_match.group(1) not in play_counts:
                            play_counts.append(play_match.group(1))
        
        # 如果没有找到专辑区域，回退到原来的方法
        if not play_counts:
            play_elements = soup.find_all(string=re.compile(r'\d+\.?\d*万'))
            for elem in play_elements:
                text = str(elem).strip()
                play_match = re.search(r'(\d+\.?\d*万)', text)
                if play_match and play_match.group(1) not in play_counts:
                    play_counts.append(play_match.group(1))
        
        return play_counts if play_counts else ["未找到播放量"]
    
    def extract_anchor_level(self, soup: BeautifulSoup) -> str:
        """提取主播等级 - 优化版"""
        # 查找等级相关的class
        level_elements = soup.find_all('i', class_=re.compile(r'.*vicon.*'))
        for elem in level_elements:
            classes = elem.get('class', [])
            for cls in classes:
                level_match = re.search(r'vicon-(\d+)', cls)
                if level_match:
                    return f"等级{level_match.group(1)}"
        
        # 查找包含"等级"的文本
        level_text = soup.find_all(string=re.compile(r'等级\d+'))
        if level_text:
            return str(level_text[0]).strip()
        
        return "未找到主播等级"
    
    def crawl_anchor_info(self, url: str) -> Dict[str, str]:
        """爬取主播信息"""
        print(f"开始爬取: {url}")
        
        # 优先使用selenium
        if self.use_selenium:
            html_content = self.get_page_content_selenium(url)
        else:
            html_content = self.get_page_content_requests(url)
        
        if not html_content:
            return {"error": "无法获取页面内容"}
        
        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取各项信息
        album_titles = self.extract_album_titles(soup)
        
        # 检查是否真的有专辑（排除"未找到专辑名称"这种情况）
        has_real_albums = album_titles and album_titles != ["未找到专辑名称"]
        
        total_play_count = 0
        if has_real_albums:
            play_counts = self.extract_play_counts(soup)
            
            # 计算所有专辑播放量的总和
            for play_count in play_counts:
                if play_count and play_count != "未知播放量":
                    # 提取数字部分并转换为数值
                    import re
                    numbers = re.findall(r'[\d.]+', str(play_count))
                    if numbers:
                        try:
                            count = float(numbers[0])
                            # 处理万、千等单位
                            if '万' in str(play_count):
                                count *= 10000
                            elif '千' in str(play_count):
                                count *= 1000
                            total_play_count += int(count)
                        except ValueError:
                            continue
        
        result = {
            "主播名称": self.extract_anchor_name(soup),
            "主播等级": self.extract_anchor_level(soup),
            "粉丝数": self.extract_fans_count(soup),
            "专辑总数": len(album_titles) if has_real_albums else 0,
            "总播放量": total_play_count,
            "爬取时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            "使用方法": "selenium" if self.use_selenium else "requests"
        }
        
        return result

    def close(self):
        """关闭selenium驱动"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                self.debug_print("Selenium驱动已关闭")
            except Exception as e:
                self.debug_print(f"关闭驱动时出错: {e}")

    def save_to_json(self, data: Dict, filename: str = "ximalaya_result.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")

def main():
    """主函数"""
    url = "https://m.ximalaya.com/zhubo/49364202"
    
    print("=== 喜马拉雅主播信息爬虫 - 最终版 ===")
    
    # 创建爬虫实例（默认使用selenium）
    crawler = XimalayaCrawlerFinal(use_selenium=True, debug=False)
    
    # 爬取信息
    result = crawler.crawl_anchor_info(url)
    
    # 打印结果
    print("\n=== 爬取结果 ===")
    for key, value in result.items():
        print(f"{key}: {value}")
    
    # 保存到文件
    crawler.save_to_json(result)
    
    return result

if __name__ == "__main__":
    main()
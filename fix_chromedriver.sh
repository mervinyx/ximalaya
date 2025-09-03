#!/bin/bash

# ChromeDriver版本修复脚本
# 用于解决Chrome和ChromeDriver版本不兼容问题

echo "🔧 ChromeDriver版本修复脚本"
echo "================================"

# 检查是否在Docker环境中
if [ -f /.dockerenv ]; then
    echo "✅ 检测到Docker环境"
    
    # 获取Chrome版本
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1-3)
    echo "📋 当前Chrome版本: $CHROME_VERSION"
    
    # 删除旧的ChromeDriver
    if [ -f /usr/local/bin/chromedriver ]; then
        echo "🗑️  删除旧的ChromeDriver..."
        rm -f /usr/local/bin/chromedriver
    fi
    
    # 下载匹配的ChromeDriver
    echo "⬇️  下载匹配的ChromeDriver..."
    CHROMEDRIVER_URL="https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    CHROMEDRIVER_VERSION=$(curl -s $CHROMEDRIVER_URL | grep -o '"version":"'$CHROME_VERSION'[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -z "$CHROMEDRIVER_VERSION" ]; then
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json" | grep -o '"'$CHROME_VERSION'":"[^"]*"' | cut -d'"' -f4)
    fi
    
    echo "📋 匹配的ChromeDriver版本: $CHROMEDRIVER_VERSION"
    
    # 下载并安装
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/
    chmod +x /usr/local/bin/chromedriver
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64
    
    echo "✅ ChromeDriver修复完成！"
    echo "📋 新的ChromeDriver版本: $(chromedriver --version)"
else
    echo "❌ 此脚本仅适用于Docker环境"
    echo "💡 请在Zeabur控制台重新部署项目以解决版本问题"
fi

echo "================================"
echo "🎉 修复完成！现在可以重新启动应用了。"
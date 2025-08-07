# Twitter推文爬取工具(不需api)

这是一个基于Selenium的Twitter推文爬取工具，可以自动搜索用户并获取其最新推文。

## 功能特点

- 🔍 自动搜索Twitter用户
- 📝 获取用户最新推文（目标50条）
- 📊 提取推文内容、日期、互动数据
- 🗂️ 支持JSON和TXT格式输出
- ⚡ 使用现有浏览器会话，避免重复登录
- 📅 智能排序：已知日期推文按时间排序，未知日期放在最后

## 系统要求

- Windows 10/11
- Python 3.7+
- Google Chrome浏览器
- 网络连接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用步骤

### 第一步：启动Chrome调试模式

**方法1：使用批处理文件（推荐）**
```bash
# 双击运行
start_chrome_debug.bat
```

**方法2：使用Python脚本**
```bash
python start_chrome.py
```

**方法3：手动命令行**
```bash
"C:\Users\David Wu\AppData\Local\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=chrome_debug_profile
```

### 第二步：在Chrome中登录Twitter

1. 在新打开的Chrome窗口中访问 https://x.com/home
2. 登录您的Twitter账户
3. 等待页面完全加载

### 第三步：运行爬取程序

```bash
python twitter_search_with_existing_browser.py
```

## 配置说明

### 目标用户列表

在 `twitter_search_with_existing_browser.py` 中修改 `target_usernames` 列表：

```python
target_usernames = [
    "sunyuchentron",
    "Defiqueen01",
    "ApeCryptos",
    "cryptodragon001",
    "Grandellaa",
    "CryptoAvenuee",
    "CryptoAs_TW",
    "specialist_005",
    "9ali9__",
    "CoinLabVerse"
]
```

### 推文数量设置

默认获取50条推文，可在调用时修改：

```python
result = search_service.search_user_and_get_tweets(username, max_tweets=50)
```

## 输出文件

程序运行完成后，会在 `results/` 目录下生成：

- `twitter_users_data.json` - JSON格式的完整数据
- `twitter_users_data.txt` - 可读的文本格式

### 数据格式

```json
{
  "username": "用户名",
  "display_name": "显示名称",
  "followers":"粉丝数",
  "description": "个人简介",
  "location": "位置",
  "verified": false,
  "scraped_at": "爬取时间",
  "url": "用户页面链接",
  "recent_tweets": [
    {
      "index": 1,
      "text": "推文内容",
      "date": "发布日期",
      "interactions": {
        "likes": "点赞数",
        "retweets": "转发数",
        "replies": "回复数",
        "views": "浏览数"
      },
      "length": "字符数"
    }
  ]
}
```

## 故障排除

### 问题1：无法连接到Chrome

**解决方案：**
1. 确保Chrome以调试模式启动
2. 检查端口9222是否被占用
3. 重启Chrome浏览器

### 问题2：找不到Chrome浏览器

**解决方案：**
1. 确保Chrome已正确安装
2. 检查Chrome路径是否正确
3. 使用完整路径启动

### 问题3：推文数量不足50条

**可能原因：**
- 用户实际推文数量少于50条
- 网络连接问题
- Twitter页面加载不完整

**解决方案：**
- 检查网络连接
- 增加等待时间
- 重新运行程序

### 问题4：排序问题

**已修复：**
- 已知日期的推文按时间顺序排列
- 未知日期的推文放在最后
- 支持多种日期格式识别

## 文件结构

```
twitter_selenium_crawl/
├── README.md                           # 本文件
├── requirements.txt                     # Python依赖
├── twitter_search_with_existing_browser.py  # 主程序
├── start_chrome_debug.bat              # Chrome启动脚本
├── start_chrome.py                     # Chrome启动Python脚本
├── services/
│   ├── __init__.py
│   └── twitter_search_service.py       # Twitter搜索服务
├── utils/
│   ├── __init__.py
│   └── browser_utils.py               # 浏览器工具
└── results/                           # 输出目录
    ├── twitter_users_data.json
    └── twitter_users_data.txt
```

## 技术改进

### 推文获取优化
- 减小滑动幅度：每次滚动400像素，确保不遗漏推文
- 增加滚动次数：最大500次滚动
- 优化等待时间：每次滚动后等待2秒
- 无新推文容忍度：连续50次无新推文才停止

### 日期识别优化
- 支持更多日期格式
- 改进排序逻辑
- 未知日期统一放在最后

### 排序逻辑优化
- 自定义排序函数
- 正确处理各种日期格式
- 确保时间顺序正确

## 注意事项

1. **Chrome版本**：建议使用最新版本的Chrome浏览器
2. **网络连接**：确保网络连接稳定
3. **Twitter登录**：确保在Chrome中已登录Twitter账户
4. **用户数据目录**：`chrome_debug_profile` 是独立的用户数据目录
5. **端口冲突**：如果9222端口被占用，可以修改为其他端口

## 常见问题

### Q: 为什么需要启动Chrome调试模式？
A: 调试模式允许Selenium连接到现有的Chrome会话，避免重复登录和验证码问题。

### Q: 可以修改目标用户列表吗？
A: 可以，在 `twitter_search_with_existing_browser.py` 中修改 `target_usernames` 列表。

### Q: 推文数量总是50条吗？
A: 不是，程序会尝试获取50条推文，但实际数量取决于用户发布的推文数量。

### Q: 如何处理网络错误？
A: 程序会自动重试，如果持续失败，请检查网络连接和Twitter页面状态。

---

**提示**：如果遇到问题，请先检查Chrome是否正确启动，然后确保在Chrome中已登录Twitter账户。 

# Twitter推文爬取工具(不需API) / Twitter Scraper Tool (No API Required)

[中文](#中文版) | [English](#english-version)

---

## 中文版

这是一个基于Selenium的Twitter推文爬取工具，采用模块化架构设计，可以自动搜索用户并获取其最新推文。

## 功能特点

- 🔍 自动搜索Twitter用户
- 📝 获取用户最新推文（目标50条）
- 📊 提取推文内容、日期、互动数据
- 👤 获取用户详细信息（粉丝数、简介、认证状态等）
- 🗂️ 支持JSON和TXT格式输出
- ⚡ 使用现有浏览器会话，避免重复登录
- 📅 智能排序：已知日期推文按时间排序，未知日期放在最后
- 🏗️ 模块化架构：功能分离，易于维护和扩展

### 近期更新（重要）

- ✅ 不足50条会持续尝试：默认开启“尽量凑够50条”，直到达到目标或命中保护阈值（总等待600s/最多滚动1000次/连续200次无新增）。
- ✅ 去重策略调整：以“文本 + 是否转发”为唯一键，因此同一文本的原创与转发会“都保留”（解决先原创后自转发被覆盖的问题）。
- ✅ 日期识别更严格：修复英文月份误匹配，避免出现“oon 26”“all 33”这类残片日期。
- ✅ 结果汇总增强：批处理结束会在控制台和 `results/twitter_users_data.txt` 顶部列出“未达到50条”的账号清单。
- ✅ 提供校验脚本：`scripts/check_recent_tweet_counts.py` 可快速统计各账号的条数分布与未达标账号。

## 系统要求

- **操作系统**: Windows 10/11
- **Python版本**: Python 3.7+
- **浏览器**: Google Chrome浏览器（最新版本）
- **网络连接**: 稳定的互联网连接
- **内存**: 建议4GB以上（用于浏览器和Python程序）

## 安装依赖

项目依赖包已优化，仅包含必要组件：

```bash
pip install -r requirements.txt
```

**主要依赖包**：
- `selenium==4.15.2` - 浏览器自动化框架
- `pandas==2.0.3` - 数据处理和分析

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

高级参数（在内部已启用“尽量凑够50条”策略，如需调整阈值可在代码中修改）：

```python
# services/twitter_search_service.py 内部调用（默认值）
tweets = self.tweet_extractor.get_user_tweets(
    max_tweets=50,
    wait_until_reach=True,
    max_total_wait_seconds=600,   # 总等待时间上限（秒）
    max_scroll_attempts=1000,     # 最大滚动次数
    max_no_new_tweets=200         # 连续无新增上限
)
```

## 输出文件

程序运行完成后，会在 `results/` 目录下生成：

- `twitter_users_data.json` - JSON格式的完整数据
- `twitter_users_data.txt` - 可读的文本格式

同时在程序末尾会输出“未达到50条”的账号，并写入 `twitter_users_data.txt` 顶部，便于快速复查。

### 结果校验脚本（可选）

```bash
python scripts/check_recent_tweet_counts.py
```

功能：统计每位用户 `recent_tweets` 的数量分布，并列出未达标（<50）账号。

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
- 如需包含24小时内推文，可在 `services/tweet_extractor.py` 中调整或取消相关过滤逻辑（搜索 `_is_today_tweet` 与其调用处）

### 问题4：排序问题

**已修复：**
- 已知日期的推文按时间顺序排列
- 未知日期的推文放在最后
- 支持多种日期格式识别

## 项目架构

### 模块化设计

项目采用模块化架构，将功能分离到不同的服务模块中：

- **BaseService**: 基础服务类，提供浏览器连接等通用功能
- **NavigationService**: 导航服务，负责页面跳转和验证
- **UserInfoExtractor**: 用户信息提取器，获取用户详细信息
- **TweetExtractor**: 推文提取器，获取和解析推文内容
- **DataProcessor**: 数据处理器，处理和格式化数据
- **TwitterSearchService**: 主搜索服务，整合所有功能模块

## 文件结构

```
twitter_selenium_crawl/
├── README.md                           # 项目说明文档
├── requirements.txt                     # Python依赖包
├── twitter_search_with_existing_browser.py  # 主程序入口
├── start_chrome_debug.bat              # Chrome启动脚本（Windows批处理）
├── start_chrome.py                     # Chrome启动Python脚本
├── services/                           # 核心服务模块
│   ├── __init__.py
│   ├── base_service.py                 # 基础服务类
│   ├── navigation_service.py           # 导航服务
│   ├── user_info_extractor.py          # 用户信息提取器
│   ├── tweet_extractor.py              # 推文提取器
│   ├── data_processor.py               # 数据处理器
│   └── twitter_search_service.py       # 主搜索服务
├── utils/                              # 工具函数
│   ├── __init__.py
│   └── browser_utils.py               # 浏览器连接工具
└── results/                           # 输出目录
    ├── twitter_users_data.json        # JSON格式数据
    └── twitter_users_data.txt         # 文本格式数据
```

## 技术特色

### 模块化架构优势
- **职责分离**: 每个模块专注于特定功能，便于维护
- **可扩展性**: 易于添加新功能或修改现有功能
- **代码复用**: 基础服务类提供通用功能
- **错误隔离**: 模块间相对独立，问题不会传播

### 推文获取优化
- 滚动幅度：每次滚动600像素
- 滚动上限：最大1000次滚动
- 等待时间：每次滚动后等待2秒
- 持续尝试：不足50条时继续尝试，直到达标或命中保护阈值（总等待600s/连续无新增200次/滚动1000次）
- 去重策略：以“文本 + 是否转发”为唯一键，原创与转发可共存

### 用户信息提取
- 完整的用户资料：显示名称、用户名、粉丝数、简介等
- 认证状态检测：自动识别认证用户
- 多重选择器：使用多种CSS选择器确保数据获取成功
- 错误处理：优雅处理缺失或异常数据

### 日期识别优化
- 支持多种日期格式：中文日期、英文缩写、相对时间等
- 修复英文月份误匹配，避免将普通单词尾部误识别为日期（如“oon 26”）
- 改进排序逻辑：智能排序确保时间顺序正确
- 未知日期处理：统一放在最后，避免排序混乱

### 数据输出优化
- 双格式输出：JSON（结构化）和TXT（可读性）
- 字符统计：每条推文包含字符数统计
- 索引编号：推文按顺序编号，便于引用
- 时间戳记录：记录数据爬取时间

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

## 开发指南

### 添加新功能模块

1. **创建新的服务类**：继承 `BaseService`
2. **实现必要方法**：确保与现有模块兼容
3. **在主服务中集成**：修改 `TwitterSearchService`
4. **更新配置**：如需要，修改主程序配置

### 修改现有功能

1. **定位相关模块**：根据功能类型找到对应的服务模块
2. **修改具体实现**：在相应的提取器或处理器中修改
3. **测试验证**：确保修改不影响其他功能

### 扩展数据格式

1. **修改提取器**：在相应的提取器中添加新字段
2. **更新数据处理**：在 `DataProcessor` 中处理新数据
3. **调整输出格式**：确保JSON和TXT输出包含新字段

### 代码规范

- 使用中文注释，便于理解
- 遵循Python PEP 8规范
- 添加适当的错误处理
- 包含必要的日志输出

---

**提示**：如果遇到问题，请先检查Chrome是否正确启动，然后确保在Chrome中已登录Twitter账户。如需开发相关帮助，请参考各模块的注释和docstring。

---

## English Version

A Selenium-based Twitter scraping tool with modular architecture design that automatically searches for users and retrieves their latest tweets.

## Features

- 🔍 Automatic Twitter user search
- 📝 Retrieve user's latest tweets (target: 50 tweets)
- 📊 Extract tweet content, dates, and interaction data
- 👤 Get detailed user information (followers, bio, verification status, etc.)
- 🗂️ Support for JSON and TXT format output
- ⚡ Use existing browser session to avoid repeated login
- 📅 Smart sorting: known dates sorted by time, unknown dates placed last
- 🏗️ Modular architecture: separated functionality for easy maintenance and extension

## System Requirements

- **Operating System**: Windows 10/11
- **Python Version**: Python 3.7+
- **Browser**: Google Chrome (latest version)
- **Network**: Stable internet connection
- **Memory**: 4GB+ recommended (for browser and Python program)

## Installation

Project dependencies are optimized with only essential components:

```bash
pip install -r requirements.txt
```

**Main Dependencies**:
- `selenium==4.15.2` - Browser automation framework
- `pandas==2.0.3` - Data processing and analysis

## Usage Steps

### Step 1: Start Chrome in Debug Mode

**Method 1: Using Batch File (Recommended)**
```bash
# Double-click to run
start_chrome_debug.bat
```

**Method 2: Using Python Script**
```bash
python start_chrome.py
```

**Method 3: Manual Command Line**
```bash
"C:\Users\David Wu\AppData\Local\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=chrome_debug_profile
```

### Step 2: Login to Twitter in Chrome

1. Visit https://x.com/home in the newly opened Chrome window
2. Login to your Twitter account
3. Wait for the page to fully load

### Step 3: Run the Scraping Program

```bash
python twitter_search_with_existing_browser.py
```

## Configuration

### Target User List

Modify the `target_usernames` list in `twitter_search_with_existing_browser.py`:

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

### Tweet Count Setting

Default retrieves 50 tweets, can be modified when calling:

```python
result = search_service.search_user_and_get_tweets(username, max_tweets=50)
```

## Output Files

After the program completes, files will be generated in the `results/` directory:

- `twitter_users_data.json` - Complete data in JSON format
- `twitter_users_data.txt` - Human-readable text format

### Data Format

```json
{
  "username": "username",
  "display_name": "display name",
  "followers": "follower count",
  "description": "bio",
  "location": "location",
  "verified": false,
  "scraped_at": "scraping time",
  "url": "user profile link",
  "recent_tweets": [
    {
      "index": 1,
      "text": "tweet content",
      "date": "publish date",
      "interactions": {
        "likes": "like count",
        "retweets": "retweet count",
        "replies": "reply count",
        "views": "view count"
      },
      "length": "character count"
    }
  ]
}
```

## Project Architecture

### Modular Design

The project uses modular architecture, separating functionality into different service modules:

- **BaseService**: Base service class providing common functionality like browser connection
- **NavigationService**: Navigation service for page jumping and verification
- **UserInfoExtractor**: User information extractor for detailed user info
- **TweetExtractor**: Tweet extractor for getting and parsing tweet content
- **DataProcessor**: Data processor for handling and formatting data
- **TwitterSearchService**: Main search service integrating all functional modules

## File Structure

```
twitter_selenium_crawl/
├── README.md                           # Project documentation
├── requirements.txt                     # Python dependencies
├── twitter_search_with_existing_browser.py  # Main program entry
├── start_chrome_debug.bat              # Chrome startup script (Windows batch)
├── start_chrome.py                     # Chrome startup Python script
├── services/                           # Core service modules
│   ├── __init__.py
│   ├── base_service.py                 # Base service class
│   ├── navigation_service.py           # Navigation service
│   ├── user_info_extractor.py          # User info extractor
│   ├── tweet_extractor.py              # Tweet extractor
│   ├── data_processor.py               # Data processor
│   └── twitter_search_service.py       # Main search service
├── utils/                              # Utility functions
│   ├── __init__.py
│   └── browser_utils.py               # Browser connection utilities
└── results/                           # Output directory
    ├── twitter_users_data.json        # JSON format data
    └── twitter_users_data.txt         # Text format data
```

## Technical Features

### Modular Architecture Advantages
- **Separation of Concerns**: Each module focuses on specific functionality for easy maintenance
- **Scalability**: Easy to add new features or modify existing ones
- **Code Reuse**: Base service class provides common functionality
- **Error Isolation**: Modules are relatively independent, preventing issue propagation

### Tweet Retrieval Optimization
- Reduced scroll amplitude: 400 pixels per scroll to ensure no tweets are missed
- Increased scroll count: maximum 500 scrolls
- Optimized wait time: 2 seconds after each scroll
- Smart stop mechanism: automatically stops scrolling after 50 consecutive attempts with no new tweets
- Smart deduplication: automatically identifies and removes duplicate tweets

### User Information Extraction
- Complete user profile: display name, username, follower count, bio, etc.
- Verification status detection: automatically identifies verified users
- Multiple selectors: uses various CSS selectors to ensure successful data retrieval
- Error handling: gracefully handles missing or abnormal data

### Date Recognition Optimization
- Support for multiple date formats: Chinese dates, English abbreviations, relative time, etc.
- Improved sorting logic: smart sorting ensures correct chronological order
- Unknown date handling: uniformly placed last to avoid sorting confusion

### Data Output Optimization
- Dual format output: JSON (structured) and TXT (readable)
- Character statistics: each tweet includes character count
- Index numbering: tweets numbered sequentially for easy reference
- Timestamp recording: records data scraping time

## Troubleshooting

### Issue 1: Cannot Connect to Chrome

**Solutions:**
1. Ensure Chrome is started in debug mode
2. Check if port 9222 is occupied
3. Restart Chrome browser

### Issue 2: Chrome Browser Not Found

**Solutions:**
1. Ensure Chrome is properly installed
2. Check if Chrome path is correct
3. Use full path to start

### Issue 3: Insufficient Tweet Count (Less than 50)

**Possible Causes:**
- User actually has fewer than 50 tweets
- Network connection issues
- Twitter page loading incomplete

**Solutions:**
- Check network connection
- Increase wait time
- Re-run the program

### Issue 4: Sorting Issues

**Fixed:**
- Known date tweets sorted chronologically
- Unknown date tweets placed last
- Support for multiple date format recognition

## Notes

1. **Chrome Version**: Recommend using the latest version of Chrome browser
2. **Network Connection**: Ensure stable network connection
3. **Twitter Login**: Ensure logged into Twitter account in Chrome
4. **User Data Directory**: `chrome_debug_profile` is an independent user data directory
5. **Port Conflicts**: If port 9222 is occupied, can modify to other ports

## FAQ

### Q: Why do I need to start Chrome in debug mode?
A: Debug mode allows Selenium to connect to existing Chrome sessions, avoiding repeated login and captcha issues.

### Q: Can I modify the target user list?
A: Yes, modify the `target_usernames` list in `twitter_search_with_existing_browser.py`.

### Q: Is the tweet count always 50?
A: No, the program tries to get 50 tweets, but actual count depends on the number of tweets the user has published.

### Q: How to handle network errors?
A: The program will automatically retry. If it continues to fail, check network connection and Twitter page status.

## Development Guide

### Adding New Feature Modules

1. **Create new service class**: Inherit from `BaseService`
2. **Implement necessary methods**: Ensure compatibility with existing modules
3. **Integrate in main service**: Modify `TwitterSearchService`
4. **Update configuration**: Modify main program configuration if needed

### Modifying Existing Features

1. **Locate relevant module**: Find corresponding service module based on feature type
2. **Modify specific implementation**: Make changes in appropriate extractor or processor
3. **Test and verify**: Ensure modifications don't affect other features

### Extending Data Formats

1. **Modify extractor**: Add new fields in corresponding extractor
2. **Update data processing**: Handle new data in `DataProcessor`
3. **Adjust output format**: Ensure JSON and TXT output include new fields

### Code Standards

- Use English comments for international collaboration
- Follow Python PEP 8 standards
- Add appropriate error handling
- Include necessary log output

---

**Tip**: If you encounter issues, first check if Chrome started correctly, then ensure you're logged into Twitter in Chrome. For development help, refer to comments and docstrings in each module. 

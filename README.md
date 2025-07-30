# Twitter个人简介爬虫 - Selenium版本

这是一个使用Selenium自动化浏览器爬取Twitter用户个人简介信息的Python项目，采用模块化设计。

## 项目结构

```
twitter_selenium_crawl/
├── main.py                 # 主入口文件
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── browser_utils.py    # 浏览器设置工具
│   └── file_utils.py       # 文件保存工具
├── services/               # 服务模块
│   ├── __init__.py
│   └── twitter_service.py  # Twitter爬取服务
├── results/                # 结果文件目录
│   ├── *.json             # JSON格式数据文件
│   ├── *.csv              # CSV格式数据文件
│   └── *.png              # 页面截图文件
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明
```

## 功能特点

- 使用Selenium模拟真实浏览器访问Twitter
- 爬取指定Twitter用户的完整个人资料信息
- 获取用户的个人简介文本和最近推文
- 支持动态加载内容的获取
- 保存数据为JSON和CSV格式
- 包含完善的错误处理和异常捕获
- 支持中文输出
- 模块化设计，便于维护和扩展

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境要求

- Python 3.7+
- Chrome浏览器
- ChromeDriver（与Chrome版本匹配）

### ChromeDriver安装

1. 下载ChromeDriver：https://chromedriver.chromium.org/
2. 将ChromeDriver添加到系统PATH，或放在项目目录中

## 使用方法

### 批量爬取

运行主程序进行批量爬取：

```bash
python main.py
```

### 单个用户爬取

爬取指定用户的信息：

```bash
python main.py sunyuchentron
```

### 自定义用户列表

修改`main.py`文件中的`target_usernames`列表来爬取其他用户：

```python
target_usernames = [
    "your_target_username1",
    "your_target_username2",
    # 添加更多用户名
]
```

## 模块说明

### utils.browser_utils
- `setup_driver()`: 配置Chrome浏览器驱动

### utils.file_utils
- `save_to_json()`: 保存数据为JSON格式
- `save_to_csv()`: 保存数据为CSV格式

### services.twitter_service
- `TwitterScraperService`: Twitter爬取服务类
  - `get_user_profile()`: 获取用户信息
  - `_extract_user_info()`: 提取用户基本信息
  - `_get_recent_tweets()`: 获取最近推文

## 输出信息

脚本会输出以下用户信息：

- 用户名 (@username)
- 显示名称
- **个人简介文本** (主要目标)
- 位置信息
- 粉丝数量
- 关注数量
- 推文数量
- 认证状态
- 账户创建时间
- 最近推文列表
- 爬取时间

## 数据保存

所有结果文件都会自动保存到`results/`目录中：

1. **JSON格式**: `results/twitter_profile_selenium_{username}_{timestamp}.json`
2. **CSV格式**: `results/twitter_profile_selenium_{username}_{timestamp}.csv`
3. **页面截图**: `results/twitter_profile_{username}_{timestamp}.png`
4. **批量数据**: `results/all_users_data_{timestamp}.json`

## 技术特点

- **Selenium自动化**: 使用Chrome浏览器模拟真实用户行为
- **动态内容获取**: 能够获取JavaScript动态加载的内容
- **无头模式**: 支持后台运行，不显示浏览器窗口
- **等待机制**: 智能等待页面元素加载完成
- **错误恢复**: 完善的异常处理和重试机制
- **模块化设计**: 清晰的代码结构，便于维护

## 注意事项

- 确保已安装Chrome浏览器和ChromeDriver
- 确保网络连接正常
- 某些用户可能设置了隐私保护，无法获取完整信息
- 建议遵守Twitter的使用条款和爬虫规范
- 避免频繁请求，以免被限制访问
- Selenium版本相比requests版本更稳定，但运行速度较慢

## 错误处理

脚本包含完善的错误处理机制：

- ChromeDriver启动失败
- 网络连接错误
- 用户不存在
- 页面元素未找到
- 数据解析错误
- 文件保存错误

## 依赖包说明

- `selenium`: 浏览器自动化框架
- `pandas`: 数据处理和CSV导出

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台使用条款。 
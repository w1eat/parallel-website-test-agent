# 5分钟快速开始

## 第1步：安装依赖

```bash
pip install browser-use python-dotenv playwright
playwright install chromium
```

## 第2步：运行简化版示例

```bash
python simple_parallel_example.py
```

选择 **1. 并行测试**

## 第3步：查看效果

程序会同时打开3个浏览器窗口，并行执行不同的测试任务：
- 浏览器1：测试登录功能
- 浏览器2：测试导航功能  
- 浏览器3：测试表单功能

## 第4步：运行完整版

修改`parallel_website_test_agent.py`中的URL：

```python
config = ParallelTestConfig(
    target_url="https://your-website.com",  # 改成你的网站
    username="admin",
    password="admin"
)
```

然后运行：

```bash
python parallel_website_test_agent.py
```

## 第5步：查看测试报告

```bash
cat parallel_test_report.json
```

## 速度对比

**顺序执行**（传统方式）：
```
测试1 → 测试2 → 测试3 → 测试4 → 测试5
总时间：10分钟
```

**并行执行**（本工具）：
```
测试1 ↘
测试2 → 同时执行 → 完成
测试3 ↗
总时间：2分钟
```

**速度提升：5倍！**

## 常见问题

**Q: 为什么要用并行？**  
A: 节省时间！5个测试并行执行，只需要最慢那个的时间。

**Q: 会不会冲突？**  
A: 不会！每个测试用独立的浏览器实例。

**Q: 如何修改测试内容？**  
A: 编辑`parallel_website_test_agent.py`中的`create_test_tasks()`方法。

## 下一步

- 阅读完整文档：[PARALLEL_TEST_README.md](PARALLEL_TEST_README.md)
- 自定义测试任务
- 调整并行数量
- 优化测试速度

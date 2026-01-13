# 并行网站自动化测试Agent使用指南

基于browser_use官方文档实现的**多线程并行**自动化测试工具，通过并行执行多个测试任务，大幅提升测试速度。

## 🚀 核心特性

### 1. 并行执行
- **5个Agent同时运行**：不同的测试任务并行执行
- **独立浏览器实例**：每个Agent使用独立的浏览器，互不干扰
- **速度提升5倍**：相比顺序执行，测试时间缩短至原来的1/5

### 2. 全面测试覆盖
- ✅ **页面探索**：自动发现和测试所有页面和导航
- ✅ **登录测试**：自动测试登录/退出功能
- ✅ **表单测试**：智能填充并测试所有表单
- ✅ **按钮测试**：测试所有交互元素
- ✅ **综合测试**：搜索、数据展示、文件上传等

### 3. 智能优化
- **Flash模式**：跳过LLM思考过程，加快执行速度
- **自动重试**：失败自动重试，提高成功率
- **详细日志**：实时输出测试进度和结果
- **JSON报告**：生成结构化的测试报告

## 📦 安装步骤

### 1. 安装依赖

```bash
pip install browser-use python-dotenv playwright
playwright install chromium
```

### 2. 配置环境变量

创建`.env`文件（如果使用ChatBrowserUse则不需要）：

```env
# 如果使用其他LLM，需要配置相应的API密钥
# OPENAI_API_KEY=your_key
# ANTHROPIC_API_KEY=your_key
```

## 🎯 快速开始

### 方法1：使用简化版（推荐新手）

```bash
python simple_parallel_example.py
```

选择"1. 并行测试"即可体验并行执行的速度优势。

### 方法2：使用完整版（推荐高级用户）

```bash
python parallel_website_test_agent.py
```

## 📝 代码说明

### 核心文件

#### 1. `parallel_website_test_agent.py` - 完整版

**特点**：
- 5个并行Agent
- 完整的测试覆盖
- 详细的日志记录
- JSON格式测试报告

**配置**：

```python
config = ParallelTestConfig(
    target_url="http://192.168.218.131:8000/",  # 目标网站
    username="admin",                            # 登录用户名
    password="admin"                             # 登录密码
)
```

**测试任务**：
1. **Agent-1**: 页面探索和导航测试
2. **Agent-2**: 登录功能测试
3. **Agent-3**: 表单功能测试
4. **Agent-4**: 按钮和交互元素测试
5. **Agent-5**: 综合功能测试

#### 2. `simple_parallel_example.py` - 简化版

**特点**：
- 3个并行Agent
- 简单易懂
- 快速上手

**使用**：

```python
# 并行测试
asyncio.run(test_with_parallel())

# 顺序测试（对比用）
asyncio.run(test_sequential())
```

## 🔧 自定义配置

### 修改目标URL

```python
config = ParallelTestConfig(
    target_url="https://your-website.com",  # 改为你的网站
    username="your_username",
    password="your_password"
)
```

### 调整并行数量

```python
config.num_parallel_agents = 3  # 减少到3个Agent
```

### 启用无头模式

```python
config.headless = True  # 不显示浏览器窗口
```

### 禁用Flash模式

```python
config.flash_mode = False  # 启用完整的LLM思考过程
```

## 📊 测试报告

测试完成后会生成`parallel_test_report.json`文件：

```json
{
  "start_time": "2026-01-13T10:00:00",
  "end_time": "2026-01-13T10:05:00",
  "target_url": "http://192.168.218.131:8000/",
  "total_tests": 5,
  "passed_tests": 4,
  "failed_tests": 1,
  "test_details": [
    {
      "timestamp": "2026-01-13T10:01:00",
      "agent_id": "Agent-1",
      "type": "exploration",
      "description": "页面探索和导航测试",
      "status": "passed",
      "details": {...}
    }
  ]
}
```

## 🎨 并行执行原理

### 架构图

```
主控制器 (ParallelWebsiteTestAgent)
    │
    ├── Agent-1 (Browser-1) → 页面探索
    ├── Agent-2 (Browser-2) → 登录测试
    ├── Agent-3 (Browser-3) → 表单测试
    ├── Agent-4 (Browser-4) → 按钮测试
    └── Agent-5 (Browser-5) → 综合测试
         │
         ↓
    asyncio.gather() 并行执行
         │
         ↓
    收集结果 → 生成报告
```

### 关键代码

```python
# 创建独立的浏览器实例
browsers = [
    Browser(user_data_dir=f'./test-profile-{i}')
    for i in range(5)
]

# 创建Agent任务
tasks = [
    self.run_single_agent(test_tasks[i], browsers[i])
    for i in range(len(test_tasks))
]

# 并行执行
results = await asyncio.gather(*tasks, return_exceptions=True)
```

## 💡 使用技巧

### 1. 速度对比

**顺序执行**：
- Agent-1: 2分钟
- Agent-2: 2分钟
- Agent-3: 2分钟
- Agent-4: 2分钟
- Agent-5: 2分钟
- **总计**: 10分钟

**并行执行**：
- 所有Agent同时运行
- **总计**: 2分钟（最慢的那个）

### 2. 适用场景

✅ **适合并行**：
- 独立的功能测试
- 不同页面的测试
- 无依赖关系的测试

❌ **不适合并行**：
- 有顺序依赖的测试
- 需要共享状态的测试
- 会互相影响的测试

### 3. 性能优化建议

1. **使用Flash模式**：跳过LLM思考，速度提升30%
2. **使用快速LLM**：ChatBrowserUse或Gemini Flash
3. **减少等待时间**：调整BrowserProfile参数
4. **启用无头模式**：减少GUI开销

```python
from browser_use import BrowserProfile

browser_profile = BrowserProfile(
    minimum_wait_page_load_time=0.1,  # 减少等待
    wait_between_actions=0.1,         # 加快操作
    headless=True,                     # 无头模式
)

agent = Agent(
    task=task,
    llm=ChatBrowserUse(),
    browser_profile=browser_profile,
    flash_mode=True,
)
```

## ⚠️ 注意事项

1. **资源消耗**：并行执行会占用更多CPU和内存
2. **浏览器实例**：每个Agent需要独立的浏览器实例
3. **网络限制**：注意目标网站的访问频率限制
4. **测试环境**：建议在测试环境而非生产环境运行
5. **数据隔离**：确保测试数据不会互相影响

## 🐛 故障排查

### 问题1：无法连接到网站

**解决方案**：
- 检查URL是否正确
- 确认网站可访问
- 检查防火墙设置

### 问题2：浏览器启动失败

**解决方案**：
```bash
playwright install chromium --force
```

### 问题3：测试冲突

**解决方案**：
- 确保每个Agent使用不同的user_data_dir
- 避免测试相同的资源
- 减少并行数量

### 问题4：内存不足

**解决方案**：
- 减少并行Agent数量
- 启用无头模式
- 增加系统内存

## 📚 进阶使用

### 自定义测试任务

```python
custom_tasks = [
    {
        "id": "custom_1",
        "agent_id": "Agent-Custom",
        "type": "custom_test",
        "description": "自定义测试",
        "task": "你的测试任务描述"
    }
]
```

### 添加更多Agent

```python
config.num_parallel_agents = 10  # 增加到10个
```

### 使用不同的LLM

```python
from browser_use import ChatOpenAI, ChatGoogle

# 使用OpenAI
llm = ChatOpenAI(model='gpt-4.1-mini')

# 使用Google Gemini
llm = ChatGoogle(model='gemini-2.0-flash-exp')

agent = Agent(task=task, llm=llm, browser=browser)
```

## 🔗 相关资源

- [Browser Use官方文档](https://docs.browser-use.com/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [并行Agent示例](https://docs.browser-use.com/examples/templates/parallel-browser)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**作者**: Manus AI  
**更新时间**: 2026-01-13

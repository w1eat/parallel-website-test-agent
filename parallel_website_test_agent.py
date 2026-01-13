"""
并行网站自动化测试Agent
基于browser_use实现，支持多线程并行测试，大幅提升测试速度
"""

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import os

load_dotenv()


class ParallelTestConfig:
    """并行测试配置"""
    
    def __init__(self, target_url: str, username: str = "admin", password: str = "admin"):
        self.target_url = target_url
        self.username = username
        self.password = password
        self.num_parallel_agents = 5  # 并行Agent数量
        self.headless = False  # 是否使用无头模式
        self.flash_mode = True  # 快速模式


class TestLogger:
    """测试日志记录器"""
    
    def __init__(self, output_file: str = "parallel_test_report.json"):
        self.output_file = output_file
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "target_url": None,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        self.lock = asyncio.Lock()
    
    async def log_test(self, agent_id: str, test_type: str, description: str, 
                      status: str, details: Dict = None):
        """记录单个测试（线程安全）"""
        async with self.lock:
            self.test_results["total_tests"] += 1
            if status == "passed":
                self.test_results["passed_tests"] += 1
            else:
                self.test_results["failed_tests"] += 1
            
            test_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "type": test_type,
                "description": description,
                "status": status,
                "details": details or {}
            }
            self.test_results["test_details"].append(test_entry)
            
            # 实时打印
            print(f"[{agent_id}] [{status.upper()}] {test_type}: {description}")
    
    def save_report(self):
        """保存测试报告"""
        self.test_results["end_time"] = datetime.now().isoformat()
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"测试报告已保存到: {self.output_file}")
        print(f"总测试数: {self.test_results['total_tests']}")
        print(f"通过: {self.test_results['passed_tests']}")
        print(f"失败: {self.test_results['failed_tests']}")
        print(f"{'='*60}")


class ParallelWebsiteTestAgent:
    """并行网站自动化测试Agent"""
    
    def __init__(self, config: ParallelTestConfig):
        self.config = config
        self.logger = TestLogger()
        self.logger.test_results["target_url"] = config.target_url
    
    def create_browsers(self) -> List[Browser]:
        """创建多个独立的浏览器实例"""
        browsers = []
        for i in range(self.config.num_parallel_agents):
            browser = Browser(
                user_data_dir=f'./test-profile-{i}',
                headless=self.config.headless,
            )
            browsers.append(browser)
        return browsers
    
    def create_test_tasks(self) -> List[Dict[str, Any]]:
        """创建测试任务列表"""
        url = self.config.target_url
        username = self.config.username
        password = self.config.password
        
        tasks = [
            {
                "id": "task_1",
                "agent_id": "Agent-1",
                "type": "exploration",
                "description": "页面探索和导航测试",
                "task": f"""
访问 {url} 并执行以下操作：
1. 等待页面完全加载
2. 获取页面标题和主要内容
3. 识别所有导航链接和菜单项
4. 点击前3个主要导航链接，验证页面是否正常加载
5. 返回主页
6. 总结页面结构和可用功能

请详细记录每一步的结果。
                """
            },
            {
                "id": "task_2",
                "agent_id": "Agent-2",
                "type": "login_test",
                "description": "登录功能测试",
                "task": f"""
访问 {url} 并测试登录功能：
1. 查找登录入口（登录按钮、登录链接或登录表单）
2. 如果需要先点击登录按钮才能看到表单，请先点击
3. 找到用户名和密码输入框
4. 填入用户名: {username}
5. 填入密码: {password}
6. 点击登录按钮
7. 验证登录是否成功（检查是否有欢迎信息、用户名显示或跳转到用户页面）
8. 如果登录成功，尝试找到并点击退出登录按钮

请详细记录登录过程和结果。
                """
            },
            {
                "id": "task_3",
                "agent_id": "Agent-3",
                "type": "form_test",
                "description": "表单功能测试",
                "task": f"""
访问 {url} 并测试所有表单功能：
1. 识别页面上的所有表单（除了登录表单）
2. 对于每个表单：
   - 识别所有输入字段
   - 根据字段类型智能填充测试数据：
     * email字段: test@example.com
     * 文本字段: 测试数据
     * 数字字段: 123
     * 日期字段: 当前日期
     * 下拉框: 选择第一个选项
     * 复选框: 勾选
   - 提交表单
   - 观察并记录提交结果
3. 如果遇到需要登录才能访问的表单，先使用 {username}/{password} 登录

请详细记录每个表单的测试结果。
                """
            },
            {
                "id": "task_4",
                "agent_id": "Agent-4",
                "type": "button_test",
                "description": "按钮和交互元素测试",
                "task": f"""
访问 {url} 并测试所有交互元素：
1. 识别页面上的所有按钮（不包括表单提交按钮）
2. 识别所有可点击的交互元素（下拉菜单、标签页、折叠面板等）
3. 逐个测试这些元素：
   - 点击按钮
   - 观察页面变化
   - 验证功能是否正常
4. 测试下拉菜单的展开和选择
5. 测试标签页的切换
6. 测试可折叠区域的展开/折叠

请详细记录每个交互元素的测试结果。
                """
            },
            {
                "id": "task_5",
                "agent_id": "Agent-5",
                "type": "comprehensive_test",
                "description": "综合功能测试",
                "task": f"""
访问 {url} 并执行综合测试：
1. 测试搜索功能（如果有）：
   - 找到搜索框
   - 输入测试关键词
   - 提交搜索
   - 验证搜索结果
2. 测试数据展示功能：
   - 查找数据表格或列表
   - 验证数据是否正确显示
   - 测试分页功能（如果有）
   - 测试排序功能（如果有）
3. 测试文件上传功能（如果有）
4. 测试任何其他特殊功能
5. 如果需要登录，使用 {username}/{password}

请详细记录所有测试结果。
                """
            }
        ]
        
        return tasks
    
    async def run_single_agent(self, task_info: Dict, browser: Browser) -> Dict:
        """运行单个Agent"""
        agent_id = task_info["agent_id"]
        task_type = task_info["type"]
        description = task_info["description"]
        task = task_info["task"]
        
        print(f"\n[{agent_id}] 开始执行: {description}")
        
        try:
            # 创建Agent
            agent = Agent(
                task=task,
                llm=ChatBrowserUse(),
                browser=browser,
                flash_mode=self.config.flash_mode,
                max_steps=50,
            )
            
            # 运行Agent
            result = await agent.run()
            
            # 记录成功
            await self.logger.log_test(
                agent_id=agent_id,
                test_type=task_type,
                description=description,
                status="passed",
                details={"result": str(result)[:500]}  # 限制长度
            )
            
            return {
                "agent_id": agent_id,
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            # 记录失败
            await self.logger.log_test(
                agent_id=agent_id,
                test_type=task_type,
                description=description,
                status="failed",
                details={"error": str(e)}
            )
            
            return {
                "agent_id": agent_id,
                "status": "error",
                "error": str(e)
            }
    
    async def run_parallel_tests(self):
        """运行并行测试"""
        print(f"\n{'='*60}")
        print(f"开始并行测试网站: {self.config.target_url}")
        print(f"并行Agent数量: {self.config.num_parallel_agents}")
        print(f"{'='*60}\n")
        
        # 创建浏览器实例
        print("正在创建浏览器实例...")
        browsers = self.create_browsers()
        
        # 创建测试任务
        print("正在创建测试任务...")
        test_tasks = self.create_test_tasks()
        
        try:
            # 并行运行所有Agent
            print(f"\n开始并行执行 {len(test_tasks)} 个测试任务...\n")
            
            tasks = [
                self.run_single_agent(test_tasks[i], browsers[i])
                for i in range(len(test_tasks))
            ]
            
            # 使用gather并行执行，return_exceptions=True确保一个失败不影响其他
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"\n{'='*60}")
            print("所有测试任务已完成！")
            print(f"{'='*60}\n")
            
            # 打印结果摘要
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
            error_count = len(results) - success_count
            
            print(f"成功: {success_count}")
            print(f"失败: {error_count}")
            
        except Exception as e:
            print(f"\n并行测试过程中发生错误: {e}")
        
        finally:
            # 保存测试报告
            self.logger.save_report()
            
            # 清理浏览器实例
            print("\n正在清理资源...")
            for browser in browsers:
                try:
                    await browser.close()
                except:
                    pass


async def main():
    """主函数"""
    # 配置测试参数
    config = ParallelTestConfig(
        target_url="http://192.168.218.131:8000/",
        username="admin",
        password="admin"
    )
    
    # 创建并运行测试Agent
    test_agent = ParallelWebsiteTestAgent(config)
    await test_agent.run_parallel_tests()


if __name__ == "__main__":
    asyncio.run(main())

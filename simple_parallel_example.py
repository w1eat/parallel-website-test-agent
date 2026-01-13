"""
简化版并行测试示例
快速上手使用
"""

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def test_with_parallel():
    """使用并行方式测试网站"""
    
    target_url = "http://192.168.218.131:8000/"
    username = "admin"
    password = "admin"
    
    # 创建3个独立的浏览器实例
    browsers = [
        Browser(user_data_dir=f'./temp-profile-{i}', headless=False)
        for i in range(3)
    ]
    
    # 定义3个不同的测试任务
    tasks_config = [
        {
            "name": "登录测试",
            "task": f"""
访问 {target_url}，找到登录表单，使用用户名 {username} 和密码 {password} 登录，
验证登录是否成功，然后退出登录。
            """
        },
        {
            "name": "导航测试",
            "task": f"""
访问 {target_url}，找到所有导航链接，点击前3个链接，
验证每个页面是否正常加载，记录页面标题。
            """
        },
        {
            "name": "表单测试",
            "task": f"""
访问 {target_url}，找到所有表单，智能填充表单字段并提交，
记录提交结果。如果需要登录，使用 {username}/{password}。
            """
        }
    ]
    
    # 创建3个Agent
    agents = [
        Agent(
            task=config["task"],
            browser=browsers[i],
            llm=ChatBrowserUse(),
            flash_mode=True,  # 快速模式
            max_steps=30,
        )
        for i, config in enumerate(tasks_config)
    ]
    
    print(f"\n{'='*60}")
    print(f"开始并行测试: {target_url}")
    print(f"{'='*60}\n")
    
    # 并行运行所有Agent
    tasks = [agent.run() for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}\n")
    
    # 打印结果
    for i, (config, result) in enumerate(zip(tasks_config, results)):
        print(f"\n[{config['name']}]")
        if isinstance(result, Exception):
            print(f"  状态: 失败")
            print(f"  错误: {result}")
        else:
            print(f"  状态: 成功")
            print(f"  结果: {str(result)[:200]}...")


async def test_sequential():
    """使用顺序方式测试网站（对比用）"""
    
    target_url = "http://192.168.218.131:8000/"
    username = "admin"
    password = "admin"
    
    print(f"\n{'='*60}")
    print(f"开始顺序测试: {target_url}")
    print(f"{'='*60}\n")
    
    # 顺序执行每个测试
    tasks_config = [
        {"name": "登录测试", "task": f"访问 {target_url}，使用 {username}/{password} 登录"},
        {"name": "导航测试", "task": f"访问 {target_url}，测试所有导航链接"},
        {"name": "表单测试", "task": f"访问 {target_url}，测试所有表单"},
    ]
    
    for config in tasks_config:
        print(f"\n执行: {config['name']}")
        agent = Agent(
            task=config["task"],
            llm=ChatBrowserUse(),
            flash_mode=True,
        )
        result = await agent.run()
        print(f"完成: {config['name']}")
    
    print(f"\n{'='*60}")
    print("顺序测试完成！")
    print(f"{'='*60}\n")


def main():
    """主菜单"""
    print("\n" + "="*60)
    print("网站自动化测试 - 并行执行示例")
    print("="*60)
    print("\n选择测试模式：")
    print("1. 并行测试（推荐，速度快）")
    print("2. 顺序测试（对比用）")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-2): ").strip()
    
    if choice == "1":
        asyncio.run(test_with_parallel())
    elif choice == "2":
        asyncio.run(test_sequential())
    elif choice == "0":
        print("退出程序")
    else:
        print("无效选项")


if __name__ == "__main__":
    main()

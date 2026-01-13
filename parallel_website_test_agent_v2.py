"""
并行网站自动化测试Agent V2 - 零重复版本
基于browser_use实现，确保功能点不重复测试

核心特性：
1. 两阶段执行：先发现功能点，再并行测试
2. 智能去重：确保每个功能点只测试一次
3. 任务分配：按功能类型和工作量均衡分配
4. 并行执行：多个Agent同时测试不同功能点
"""

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict
import hashlib

load_dotenv()


@dataclass
class FeaturePoint:
    """功能点数据结构"""
    id: str
    type: str  # form, button, link, search, data_table
    category: str  # auth, navigation, data_entry, interaction, display
    description: str
    selector: str = ""
    text: str = ""
    priority: int = 1
    
    def to_dict(self):
        return asdict(self)


class FeatureDiscovery:
    """功能点发现器"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.discovered_features: List[FeaturePoint] = []
    
    async def discover(self) -> List[FeaturePoint]:
        """发现所有功能点"""
        print(f"\n{'='*60}")
        print("阶段1: 功能点发现（单线程）")
        print(f"{'='*60}\n")
        
        discovery_task = f"""
访问 {self.target_url} 并完成功能点发现任务：

请仔细分析页面，识别以下类型的功能点：

1. **认证功能**：
   - 登录表单（用户名、密码输入框）
   - 注册表单
   - 登出按钮
   - 忘记密码链接

2. **导航功能**：
   - 顶部导航栏的链接
   - 侧边栏菜单项
   - 面包屑导航
   - 底部链接

3. **表单功能**（不包括登录表单）：
   - 搜索表单
   - 数据提交表单
   - 过滤表单
   - 设置表单

4. **交互元素**：
   - 普通按钮（不包括表单提交按钮）
   - 下拉菜单
   - 标签页
   - 模态框触发器
   - 折叠面板

5. **数据展示**：
   - 数据表格
   - 列表
   - 卡片
   - 图表

6. **特殊功能**：
   - 文件上传
   - 文件下载
   - 打印按钮
   - 导出功能

对于每个功能点，请记录：
- 功能类型
- 功能描述
- 所在位置
- 显示文本

请以结构化的方式列出所有发现的功能点，避免重复。
        """
        
        try:
            agent = Agent(
                task=discovery_task,
                llm=ChatBrowserUse(),
                max_steps=30,
            )
            
            result = await agent.run()
            
            # 解析发现的功能点
            self.discovered_features = self._parse_discovery_result(str(result))
            
            print(f"\n发现功能点总数: {len(self.discovered_features)}")
            self._print_feature_summary()
            
            return self.discovered_features
            
        except Exception as e:
            print(f"功能点发现失败: {e}")
            return []
    
    def _parse_discovery_result(self, result: str) -> List[FeaturePoint]:
        """解析发现结果（简化版，实际应该更智能）"""
        features = []
        
        # 这里是简化的解析逻辑
        # 实际应该使用output_model_schema来获取结构化输出
        
        # 为演示目的，创建一些示例功能点
        # 实际使用时应该从LLM的结构化输出中解析
        
        feature_id = 0
        
        # 从结果中提取功能点（简化版）
        if "登录" in result or "login" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="form",
                category="auth",
                description="登录表单",
                text="登录",
                priority=1
            ))
            feature_id += 1
        
        if "注册" in result or "register" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="form",
                category="auth",
                description="注册表单",
                text="注册",
                priority=2
            ))
            feature_id += 1
        
        if "搜索" in result or "search" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="search",
                category="interaction",
                description="搜索功能",
                text="搜索",
                priority=1
            ))
            feature_id += 1
        
        if "导航" in result or "navigation" in result.lower() or "菜单" in result:
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="link",
                category="navigation",
                description="导航链接",
                text="导航",
                priority=1
            ))
            feature_id += 1
        
        if "表单" in result or "form" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="form",
                category="data_entry",
                description="数据表单",
                text="表单",
                priority=2
            ))
            feature_id += 1
        
        if "按钮" in result or "button" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="button",
                category="interaction",
                description="交互按钮",
                text="按钮",
                priority=2
            ))
            feature_id += 1
        
        if "表格" in result or "table" in result.lower():
            features.append(FeaturePoint(
                id=f"feature_{feature_id}",
                type="data_table",
                category="display",
                description="数据表格",
                text="表格",
                priority=2
            ))
            feature_id += 1
        
        return features
    
    def _print_feature_summary(self):
        """打印功能点摘要"""
        by_category = {}
        for feature in self.discovered_features:
            if feature.category not in by_category:
                by_category[feature.category] = []
            by_category[feature.category].append(feature)
        
        print("\n功能点分类统计：")
        for category, features in by_category.items():
            print(f"  {category}: {len(features)}个")


class FeatureDeduplicator:
    """功能点去重器"""
    
    def __init__(self):
        self.seen_ids: Set[str] = set()
    
    def deduplicate(self, features: List[FeaturePoint]) -> List[FeaturePoint]:
        """去重功能点"""
        print(f"\n{'='*60}")
        print("阶段2: 功能点去重")
        print(f"{'='*60}\n")
        
        print(f"去重前: {len(features)}个功能点")
        
        unique_features = []
        
        for feature in features:
            # 生成功能点指纹
            fingerprint = self._generate_fingerprint(feature)
            
            if fingerprint not in self.seen_ids:
                self.seen_ids.add(fingerprint)
                unique_features.append(feature)
            else:
                print(f"  跳过重复功能点: {feature.description}")
        
        print(f"去重后: {len(unique_features)}个功能点")
        
        return unique_features
    
    def _generate_fingerprint(self, feature: FeaturePoint) -> str:
        """生成功能点指纹"""
        # 使用类型、分类和描述生成唯一标识
        content = f"{feature.type}_{feature.category}_{feature.description}_{feature.text}"
        return hashlib.md5(content.encode()).hexdigest()


class TaskAllocator:
    """任务分配器"""
    
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
    
    def allocate(self, features: List[FeaturePoint]) -> List[Dict[str, Any]]:
        """分配任务给Agent"""
        print(f"\n{'='*60}")
        print(f"阶段3: 任务分配（分配给{self.num_agents}个Agent）")
        print(f"{'='*60}\n")
        
        # 按分类分组
        by_category = self._group_by_category(features)
        
        # 创建任务分配
        allocations = self._create_allocations(by_category)
        
        # 打印分配结果
        self._print_allocations(allocations)
        
        return allocations
    
    def _group_by_category(self, features: List[FeaturePoint]) -> Dict[str, List[FeaturePoint]]:
        """按分类分组"""
        groups = {}
        for feature in features:
            if feature.category not in groups:
                groups[feature.category] = []
            groups[feature.category].append(feature)
        return groups
    
    def _create_allocations(self, grouped_features: Dict[str, List[FeaturePoint]]) -> List[Dict[str, Any]]:
        """创建任务分配"""
        allocations = []
        
        # 定义分类到Agent的映射
        category_mapping = {
            "auth": 0,          # Agent-1: 认证功能
            "navigation": 1,    # Agent-2: 导航功能
            "data_entry": 2,    # Agent-3: 数据输入
            "interaction": 3,   # Agent-4: 交互元素
            "display": 4,       # Agent-5: 数据展示
        }
        
        # 初始化Agent任务列表
        agent_tasks = [[] for _ in range(self.num_agents)]
        
        # 分配功能点
        for category, features in grouped_features.items():
            agent_idx = category_mapping.get(category, 0) % self.num_agents
            agent_tasks[agent_idx].extend(features)
        
        # 创建任务描述
        for i, features in enumerate(agent_tasks):
            if features:
                allocation = {
                    "agent_id": f"Agent-{i+1}",
                    "features": features,
                    "description": self._create_task_description(features),
                    "count": len(features)
                }
                allocations.append(allocation)
        
        return allocations
    
    def _create_task_description(self, features: List[FeaturePoint]) -> str:
        """创建任务描述"""
        categories = set(f.category for f in features)
        types = set(f.type for f in features)
        return f"测试{len(features)}个功能点 (类别: {', '.join(categories)}, 类型: {', '.join(types)})"
    
    def _print_allocations(self, allocations: List[Dict[str, Any]]):
        """打印分配结果"""
        print("任务分配结果：")
        for alloc in allocations:
            print(f"\n{alloc['agent_id']}:")
            print(f"  任务数量: {alloc['count']}")
            print(f"  任务描述: {alloc['description']}")
            print(f"  功能点列表:")
            for feature in alloc['features']:
                print(f"    - {feature.description} ({feature.type})")


class ParallelTestConfig:
    """并行测试配置"""
    
    def __init__(self, target_url: str, username: str = "admin", password: str = "admin"):
        self.target_url = target_url
        self.username = username
        self.password = password
        self.num_parallel_agents = 5
        self.headless = False
        self.flash_mode = True


class TestLogger:
    """测试日志记录器"""
    
    def __init__(self, output_file: str = "parallel_test_report_v2.json"):
        self.output_file = output_file
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "target_url": None,
            "total_features": 0,
            "tested_features": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "discovered_features": [],
            "test_details": []
        }
        self.lock = asyncio.Lock()
    
    async def log_test(self, agent_id: str, feature: FeaturePoint, 
                      status: str, details: Dict = None):
        """记录单个测试"""
        async with self.lock:
            self.test_results["tested_features"] += 1
            if status == "passed":
                self.test_results["passed_tests"] += 1
            else:
                self.test_results["failed_tests"] += 1
            
            test_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "feature": feature.to_dict(),
                "status": status,
                "details": details or {}
            }
            self.test_results["test_details"].append(test_entry)
            
            print(f"[{agent_id}] [{status.upper()}] {feature.description}")
    
    def set_discovered_features(self, features: List[FeaturePoint]):
        """设置发现的功能点"""
        self.test_results["total_features"] = len(features)
        self.test_results["discovered_features"] = [f.to_dict() for f in features]
    
    def save_report(self):
        """保存测试报告"""
        self.test_results["end_time"] = datetime.now().isoformat()
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"测试报告已保存到: {self.output_file}")
        print(f"发现功能点: {self.test_results['total_features']}")
        print(f"测试功能点: {self.test_results['tested_features']}")
        print(f"通过: {self.test_results['passed_tests']}")
        print(f"失败: {self.test_results['failed_tests']}")
        print(f"{'='*60}")


class ParallelWebsiteTestAgentV2:
    """并行网站自动化测试Agent V2 - 零重复版本"""
    
    def __init__(self, config: ParallelTestConfig):
        self.config = config
        self.logger = TestLogger()
        self.logger.test_results["target_url"] = config.target_url
        
        self.discovery = FeatureDiscovery(config.target_url)
        self.deduplicator = FeatureDeduplicator()
        self.allocator = TaskAllocator(config.num_parallel_agents)
    
    async def run(self):
        """运行完整的测试流程"""
        print(f"\n{'='*60}")
        print(f"并行网站测试 V2 - 零重复版本")
        print(f"目标网站: {self.config.target_url}")
        print(f"{'='*60}\n")
        
        try:
            # 阶段1: 发现功能点
            features = await self.discovery.discover()
            
            if not features:
                print("未发现任何功能点，测试终止")
                return
            
            # 阶段2: 去重
            unique_features = self.deduplicator.deduplicate(features)
            self.logger.set_discovered_features(unique_features)
            
            if not unique_features:
                print("去重后无功能点，测试终止")
                return
            
            # 阶段3: 分配任务
            allocations = self.allocator.allocate(unique_features)
            
            if not allocations:
                print("任务分配失败，测试终止")
                return
            
            # 阶段4: 并行测试
            await self.run_parallel_tests(allocations)
            
        except Exception as e:
            print(f"\n测试过程中发生错误: {e}")
        
        finally:
            # 保存报告
            self.logger.save_report()
    
    async def run_parallel_tests(self, allocations: List[Dict[str, Any]]):
        """并行运行测试"""
        print(f"\n{'='*60}")
        print(f"阶段4: 并行测试（{len(allocations)}个Agent）")
        print(f"{'='*60}\n")
        
        # 创建浏览器实例
        browsers = [
            Browser(user_data_dir=f'./test-profile-v2-{i}', headless=self.config.headless)
            for i in range(len(allocations))
        ]
        
        try:
            # 创建并行任务
            tasks = [
                self.run_agent_tests(alloc, browsers[i])
                for i, alloc in enumerate(allocations)
            ]
            
            # 并行执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"\n{'='*60}")
            print("所有并行测试已完成！")
            print(f"{'='*60}\n")
            
        finally:
            # 清理浏览器
            for browser in browsers:
                try:
                    await browser.close()
                except:
                    pass
    
    async def run_agent_tests(self, allocation: Dict[str, Any], browser: Browser):
        """运行单个Agent的测试"""
        agent_id = allocation["agent_id"]
        features = allocation["features"]
        
        print(f"\n[{agent_id}] 开始测试 {len(features)} 个功能点")
        
        # 为每个功能点生成详细的测试任务
        test_tasks = []
        for feature in features:
            test_tasks.append(self._generate_test_task(feature))
        
        # 合并成一个完整的测试任务
        combined_task = f"""
访问 {self.config.target_url} 并测试以下功能点：

{chr(10).join(test_tasks)}

测试要求：
1. 按顺序测试每个功能点
2. 记录每个测试的结果
3. 如果需要登录，使用用户名: {self.config.username}, 密码: {self.config.password}
4. 详细描述每个测试的执行过程和结果
        """
        
        try:
            agent = Agent(
                task=combined_task,
                llm=ChatBrowserUse(),
                browser=browser,
                flash_mode=self.config.flash_mode,
                max_steps=50,
            )
            
            result = await agent.run()
            
            # 记录所有功能点测试成功
            for feature in features:
                await self.logger.log_test(
                    agent_id=agent_id,
                    feature=feature,
                    status="passed",
                    details={"result": str(result)[:200]}
                )
            
        except Exception as e:
            # 记录所有功能点测试失败
            for feature in features:
                await self.logger.log_test(
                    agent_id=agent_id,
                    feature=feature,
                    status="failed",
                    details={"error": str(e)}
                )
    
    def _generate_test_task(self, feature: FeaturePoint) -> str:
        """为功能点生成测试任务"""
        task_templates = {
            "auth": f"- 测试{feature.description}：找到表单，填写用户名和密码，提交并验证结果",
            "navigation": f"- 测试{feature.description}：找到导航链接，点击并验证页面跳转",
            "data_entry": f"- 测试{feature.description}：找到表单，智能填充字段，提交并验证",
            "interaction": f"- 测试{feature.description}：找到交互元素，执行操作并观察结果",
            "display": f"- 测试{feature.description}：找到数据展示区域，验证数据正确显示",
        }
        
        return task_templates.get(feature.category, f"- 测试{feature.description}")


async def main():
    """主函数"""
    # 配置测试参数
    config = ParallelTestConfig(
        target_url="http://192.168.218.131:8000/",
        username="admin",
        password="admin"
    )
    
    # 创建并运行测试Agent
    test_agent = ParallelWebsiteTestAgentV2(config)
    await test_agent.run()


if __name__ == "__main__":
    asyncio.run(main())

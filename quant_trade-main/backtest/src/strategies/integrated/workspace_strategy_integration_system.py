#!/usr/bin/env python3
"""
Workspace策略整合系统

功能:
1. 扫描workspace中的所有策略文件
2. 分类和评估策略的有用性
3. 筛选高质量策略
4. 整合到quant_trade-main目录
5. 创建统一的策略接口
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

print("=" * 80)
print("📊 Workspace策略整合系统")
print("=" * 80)

# 配置
WORKSPACE_ROOT = Path("/Users/chengming/.openclaw/workspace")
QUANT_TRADE_MAIN = WORKSPACE_ROOT / "quant_trade-main"
TARGET_STRATEGY_DIR = QUANT_TRADE_MAIN / "backtest" / "src" / "strategies" / "integrated"
TARGET_INDICATOR_DIR = QUANT_TRADE_MAIN / "backtest" / "src" / "indicators"

# 创建目标目录
TARGET_STRATEGY_DIR.mkdir(parents=True, exist_ok=True)
TARGET_INDICATOR_DIR.mkdir(parents=True, exist_ok=True)

class StrategyScanner:
    """策略扫描器"""
    
    def __init__(self):
        self.strategy_files = []
        self.indicator_files = []
        self.other_files = []
        
    def scan_workspace(self) -> Dict[str, List]:
        """扫描workspace中的所有策略相关文件"""
        print(f"🔍 开始扫描workspace: {WORKSPACE_ROOT}")
        
        strategy_patterns = [
            "*strategy*.py",
            "*Strategy*.py",
            "*indicator*.py",
            "*Indicator*.py",
            "*.ipynb"  # Jupyter笔记本策略
        ]
        
        for pattern in strategy_patterns:
            for file_path in WORKSPACE_ROOT.rglob(pattern):
                if "__pycache__" in str(file_path):
                    continue
                if file_path.is_file():
                    self._classify_file(file_path)
        
        return {
            "strategies": self.strategy_files,
            "indicators": self.indicator_files,
            "other": self.other_files
        }
    
    def _classify_file(self, file_path: Path):
        """分类文件"""
        file_name = file_path.name.lower()
        file_str = str(file_path)
        
        # 分类逻辑
        if "strategy" in file_name or "Strategy" in file_name:
            self.strategy_files.append(str(file_path))
        elif "indicator" in file_name or "Indicator" in file_name:
            self.indicator_files.append(str(file_path))
        elif file_path.suffix == ".ipynb":
            self.strategy_files.append(str(file_path))
        else:
            self.other_files.append(str(file_path))
    
    def analyze_strategy_content(self, file_path: str) -> Dict[str, Any]:
        """分析策略文件内容"""
        path = Path(file_path)
        analysis = {
            "file_path": str(file_path),
            "file_name": path.name,
            "file_size": path.stat().st_size,
            "file_type": path.suffix,
            "lines": 0,
            "has_imports": False,
            "has_class_def": False,
            "has_function_def": False,
            "has_backtest": False,
            "has_ta_lib": False,
            "has_pandas": False,
            "has_numpy": False,
            "usefulness_score": 0,
            "category": "unknown"
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                analysis["lines"] = len(lines)
                
                # 分析内容特征
                analysis["has_imports"] = any("import" in line for line in lines[:50])
                analysis["has_class_def"] = any("class " in line for line in lines)
                analysis["has_function_def"] = any("def " in line for line in lines)
                analysis["has_backtest"] = any("backtest" in line.lower() for line in lines)
                analysis["has_ta_lib"] = any("talib" in line.lower() for line in lines)
                analysis["has_pandas"] = any("pandas" in line.lower() or "pd." in line for line in lines)
                analysis["has_numpy"] = any("numpy" in line.lower() or "np." in line for line in lines)
                
                # 计算有用性分数
                analysis["usefulness_score"] = self._calculate_usefulness_score(analysis)
                
                # 分类
                analysis["category"] = self._categorize_strategy(analysis, content)
                
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _calculate_usefulness_score(self, analysis: Dict) -> int:
        """计算有用性分数 (0-100)"""
        score = 0
        
        # 文件大小适当 (1-100KB)
        if 1000 <= analysis["file_size"] <= 100000:
            score += 20
        elif analysis["file_size"] > 100000:
            score += 10  # 太大可能包含不必要内容
        
        # 代码行数适当
        if 50 <= analysis["lines"] <= 2000:
            score += 20
        
        # 包含必要的导入
        if analysis["has_imports"]:
            score += 10
        
        # 包含类或函数定义
        if analysis["has_class_def"] or analysis["has_function_def"]:
            score += 20
        
        # 包含回测相关代码
        if analysis["has_backtest"]:
            score += 15
        
        # 使用TA-Lib
        if analysis["has_ta_lib"]:
            score += 15
        
        return min(score, 100)
    
    def _categorize_strategy(self, analysis: Dict, content: str) -> str:
        """分类策略类型"""
        content_lower = content.lower()
        
        if "moving average" in content_lower or "ma" in content_lower or "移动平均" in content:
            return "moving_average"
        elif "rsi" in content_lower:
            return "rsi"
        elif "macd" in content_lower:
            return "macd"
        elif "bollinger" in content_lower or "布林" in content:
            return "bollinger"
        elif "price action" in content_lower or "价格行为" in content:
            return "price_action"
        elif "tradingview" in content_lower:
            return "tradingview"
        elif "indicator" in content_lower or "指标" in content:
            return "indicator"
        elif "backtest" in content_lower or "回测" in content:
            return "backtest_framework"
        else:
            return "general"

class StrategyIntegrator:
    """策略整合器"""
    
    def __init__(self):
        self.integrated_count = 0
        self.skipped_count = 0
        
    def integrate_strategy(self, analysis: Dict, target_dir: Path) -> bool:
        """整合策略文件到目标目录"""
        source_path = Path(analysis["file_path"])
        target_path = target_dir / source_path.name
        
        # 检查是否已存在
        if target_path.exists():
            print(f"   ⚠️  已存在: {target_path.name}")
            return False
        
        # 根据策略类型选择目标目录
        if analysis["category"] == "indicator":
            target_path = TARGET_INDICATOR_DIR / source_path.name
            target_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 复制文件
            shutil.copy2(source_path, target_path)
            print(f"   ✅  整合: {source_path.name} → {target_path.relative_to(WORKSPACE_ROOT)}")
            
            # 如果是Python文件，可能需要添加导入适配
            if source_path.suffix == ".py":
                self._adapt_python_file(target_path, analysis)
            
            self.integrated_count += 1
            return True
            
        except Exception as e:
            print(f"   ❌  整合失败 {source_path.name}: {e}")
            return False
    
    def _adapt_python_file(self, file_path: Path, analysis: Dict):
        """适配Python文件，确保与quant_trade-main框架兼容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含必要的导入
            if "from backtest.src.strategies.base_strategy import BaseStrategy" not in content:
                # 添加基础策略导入（如果需要）
                lines = content.split('\n')
                new_lines = []
                import_added = False
                
                for line in lines:
                    new_lines.append(line)
                    if line.startswith("import") or line.startswith("from"):
                        # 在导入部分后添加基础导入
                        pass
                    elif not import_added and (line.strip() == "" or line.startswith("class") or line.startswith("def")):
                        # 在第一个类或函数定义前添加
                        new_lines.insert(len(new_lines) - 1, "\n# 整合适配 - 自动添加")
                        new_lines.insert(len(new_lines) - 1, "from backtest.src.strategies.base_strategy import BaseStrategy")
                        import_added = True
                
                if not import_added:
                    new_lines.insert(0, "from backtest.src.strategies.base_strategy import BaseStrategy")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                    
        except Exception as e:
            print(f"      ⚠️  适配失败 {file_path.name}: {e}")
    
    def create_unified_interface(self, target_dir: Path, strategies_info: List[Dict]):
        """创建统一策略接口"""
        interface_file = target_dir / "__init__.py"
        
        interface_content = """# 整合策略接口文件
# 自动生成于: {}

from backtest.src.strategies.base_strategy import BaseStrategy

# 可用策略列表
AVAILABLE_STRATEGIES = {{}}

# 策略工厂函数
def create_strategy(strategy_name: str, **kwargs):
    \"\"\"创建策略实例\"\"\"
    if strategy_name not in AVAILABLE_STRATEGIES:
        raise ValueError(f"未知策略: {{strategy_name}}")
    
    strategy_class = AVAILABLE_STRATEGIES[strategy_name]
    return strategy_class(**kwargs)

# 策略加载函数
def load_all_strategies():
    \"\"\"加载所有策略\"\"\"
    return list(AVAILABLE_STRATEGIES.keys())

""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 添加策略导入
        imports = []
        strategy_dict_entries = []
        
        for info in strategies_info:
            if info["category"] != "indicator" and info["file_name"].endswith(".py"):
                module_name = info["file_name"][:-3]  # 去掉.py
                class_name = self._extract_class_name(info)
                if class_name:
                    imports.append(f"from .{module_name} import {class_name}")
                    strategy_dict_entries.append(f'    "{module_name}": {class_name},')
        
        if imports:
            interface_content += "\n# 策略导入\n" + "\n".join(imports) + "\n\n"
            interface_content += "# 策略字典\nAVAILABLE_STRATEGIES = {\n" + "\n".join(strategy_dict_entries) + "\n}\n"
        
        try:
            with open(interface_file, 'w', encoding='utf-8') as f:
                f.write(interface_content)
            print(f"\n📁 创建统一接口: {interface_file.relative_to(WORKSPACE_ROOT)}")
        except Exception as e:
            print(f"❌ 创建接口失败: {e}")
    
    def _extract_class_name(self, info: Dict) -> Optional[str]:
        """从文件中提取类名"""
        try:
            with open(info["file_path"], 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith("class "):
                        # 提取类名
                        class_line = line.strip()
                        class_name = class_line.split("class ")[1].split("(")[0].strip()
                        return class_name
        except:
            pass
        return None

def main():
    """主函数"""
    print(f"工作空间根目录: {WORKSPACE_ROOT}")
    print(f"量化交易主目录: {QUANT_TRADE_MAIN}")
    print(f"目标策略目录: {TARGET_STRATEGY_DIR}")
    print(f"目标指标目录: {TARGET_INDICATOR_DIR}")
    print()
    
    # 1. 扫描策略文件
    scanner = StrategyScanner()
    scan_results = scanner.scan_workspace()
    
    print(f"📋 扫描结果:")
    print(f"   策略文件: {len(scan_results['strategies'])} 个")
    print(f"   指标文件: {len(scan_results['indicators'])} 个")
    print(f"   其他文件: {len(scan_results['other'])} 个")
    print()
    
    # 2. 分析策略文件
    print("🔬 分析策略文件...")
    analyzed_strategies = []
    for i, file_path in enumerate(scan_results["strategies"][:100]):  # 限制前100个
        print(f"  [{i+1}/{min(len(scan_results['strategies']), 100)}] 分析: {Path(file_path).name}")
        analysis = scanner.analyze_strategy_content(file_path)
        analyzed_strategies.append(analysis)
    
    # 3. 筛选高质量策略 (有用性分数 > 40)
    print("\n🎯 筛选高质量策略 (有用性分数 > 40)...")
    high_quality_strategies = [s for s in analyzed_strategies if s.get("usefulness_score", 0) > 40]
    print(f"   高质量策略数量: {len(high_quality_strategies)} / {len(analyzed_strategies)}")
    
    # 按类别分组
    categories = {}
    for strategy in high_quality_strategies:
        cat = strategy["category"]
        categories.setdefault(cat, []).append(strategy)
    
    print(f"\n📊 策略分类统计:")
    for cat, items in sorted(categories.items()):
        print(f"   {cat}: {len(items)} 个")
    
    # 4. 整合策略
    print("\n🔄 整合策略到 quant_trade-main...")
    integrator = StrategyIntegrator()
    
    integrated_strategies = []
    for strategy in high_quality_strategies:
        print(f"  📄 {Path(strategy['file_path']).name} (分数: {strategy['usefulness_score']}, 类别: {strategy['category']})")
        if integrator.integrate_strategy(strategy, TARGET_STRATEGY_DIR):
            integrated_strategies.append(strategy)
    
    # 5. 整合指标
    print("\n📈 整合指标文件...")
    for i, file_path in enumerate(scan_results["indicators"][:50]):  # 限制前50个指标
        print(f"  [{i+1}/{min(len(scan_results['indicators']), 50)}] 指标: {Path(file_path).name}")
        analysis = scanner.analyze_strategy_content(file_path)
        analysis["category"] = "indicator"
        integrator.integrate_strategy(analysis, TARGET_INDICATOR_DIR)
    
    # 6. 创建统一接口
    print("\n🔗 创建统一策略接口...")
    integrator.create_unified_interface(TARGET_STRATEGY_DIR, integrated_strategies)
    
    # 7. 生成报告
    print("\n📋 生成整合报告...")
    report = {
        "scan_time": datetime.now().isoformat(),
        "total_files_scanned": len(scan_results["strategies"]) + len(scan_results["indicators"]),
        "high_quality_strategies": len(high_quality_strategies),
        "integrated_strategies": integrator.integrated_count,
        "skipped_strategies": integrator.skipped_count,
        "categories": categories,
        "strategy_details": high_quality_strategies
    }
    
    report_file = WORKSPACE_ROOT / "strategy_integration_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 整合完成!")
    print(f"   扫描文件: {report['total_files_scanned']} 个")
    print(f"   高质量策略: {report['high_quality_strategies']} 个")
    print(f"   整合策略: {report['integrated_strategies']} 个")
    print(f"   跳过策略: {report['skipped_strategies']} 个")
    print(f"   报告文件: {report_file.relative_to(WORKSPACE_ROOT)}")
    print(f"   目标目录: {TARGET_STRATEGY_DIR.relative_to(WORKSPACE_ROOT)}")
    
    return report

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""手动测试翻译功能的脚本"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.translation import TranslationService


async def test_single_case(service: TranslationService, content: str, direction: str):
    """测试单个用例"""
    print(f"\n{'='*80}")
    print(f"翻译方向: {direction}")
    print(f"{'='*80}")
    print(f"输入:\n{content}\n")
    print(f"{'='*80}")
    print("输出:")
    print("-" * 80)

    result_chunks = []
    async for chunk in service.translate_stream(content, direction):
        # 实时打印
        print(chunk, end="", flush=True)
        result_chunks.append(chunk)

    full_result = "".join(result_chunks)
    print(f"\n{'='*80}\n")

    return full_result


async def test_all_cases():
    """测试所有用例"""
    service = TranslationService()

    # 加载测试用例
    test_cases_file = Path(__file__).parent / "test_cases.json"
    with open(test_cases_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    print("\n" + "=" * 80)
    print("开始测试: 产品→开发 翻译")
    print("=" * 80)

    for i, case in enumerate(test_data["product_to_dev"], 1):
        print(f"\n>>> 测试用例 {i}/{len(test_data['product_to_dev'])}: {case['description']}")
        await test_single_case(service, case["content"], "product_to_dev")

        # 避免请求过快
        if i < len(test_data["product_to_dev"]):
            print("等待2秒后继续...")
            await asyncio.sleep(2)

    print("\n" + "=" * 80)
    print("开始测试: 开发→产品 翻译")
    print("=" * 80)

    for i, case in enumerate(test_data["dev_to_product"], 1):
        print(f"\n>>> 测试用例 {i}/{len(test_data['dev_to_product'])}: {case['description']}")
        await test_single_case(service, case["content"], "dev_to_product")

        # 避免请求过快
        if i < len(test_data["dev_to_product"]):
            print("等待2秒后继续...")
            await asyncio.sleep(2)

    print("\n" + "=" * 80)
    print("所有测试完成!")
    print("=" * 80)


async def test_interactive():
    """交互式测试"""
    service = TranslationService()

    print("\n" + "=" * 80)
    print("职能沟通翻译助手 - 交互式测试")
    print("=" * 80)

    while True:
        print("\n请选择翻译方向:")
        print("1. 产品 → 开发")
        print("2. 开发 → 产品")
        print("0. 退出")

        choice = input("\n请输入选项 (0-2): ").strip()

        if choice == "0":
            print("退出测试")
            break

        if choice not in ["1", "2"]:
            print("无效选项,请重新选择")
            continue

        direction = "product_to_dev" if choice == "1" else "dev_to_product"
        direction_name = "产品 → 开发" if choice == "1" else "开发 → 产品"

        print(f"\n请输入内容 (翻译方向: {direction_name}):")
        content = input().strip()

        if not content:
            print("内容不能为空")
            continue

        await test_single_case(service, content, direction)


async def test_quick():
    """快速测试 - 只测试前3个用例"""
    service = TranslationService()

    # 加载测试用例
    test_cases_file = Path(__file__).parent / "test_cases.json"
    with open(test_cases_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    print("\n" + "=" * 80)
    print("快速测试: 产品→开发 (前3个用例)")
    print("=" * 80)

    for i, case in enumerate(test_data["product_to_dev"][:3], 1):
        print(f"\n>>> 测试用例 {i}/3: {case['description']}")
        await test_single_case(service, case["content"], "product_to_dev")
        if i < 3:
            await asyncio.sleep(2)

    print("\n" + "=" * 80)
    print("快速测试: 开发→产品 (前3个用例)")
    print("=" * 80)

    for i, case in enumerate(test_data["dev_to_product"][:3], 1):
        print(f"\n>>> 测试用例 {i}/3: {case['description']}")
        await test_single_case(service, case["content"], "dev_to_product")
        if i < 3:
            await asyncio.sleep(2)

    print("\n快速测试完成!")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python manual_test.py all       # 测试所有用例")
        print("  python manual_test.py quick     # 快速测试(前3个用例)")
        print("  python manual_test.py interactive  # 交互式测试")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "all":
        asyncio.run(test_all_cases())
    elif mode == "quick":
        asyncio.run(test_quick())
    elif mode == "interactive":
        asyncio.run(test_interactive())
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()

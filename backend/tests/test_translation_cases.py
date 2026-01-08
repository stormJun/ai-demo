"""测试翻译功能的测试用例"""
import asyncio
import json
from pathlib import Path

import pytest

from app.services.translation import TranslationService

# 加载测试用例
TEST_CASES_FILE = Path(__file__).parent / "test_cases.json"
with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f)


class TestProductToDev:
    """产品→开发 翻译测试"""

    @pytest.fixture
    def service(self):
        """创建翻译服务实例"""
        return TranslationService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_case",
        TEST_DATA["product_to_dev"],
        ids=[f"case_{case['id']}_{case['description']}" for case in TEST_DATA["product_to_dev"]],
    )
    async def test_product_to_dev_translation(self, service, test_case):
        """测试产品需求→技术方案的翻译"""
        content = test_case["content"]
        result_chunks = []

        # 收集所有流式输出
        async for chunk in service.translate_stream(content, "product_to_dev"):
            result_chunks.append(chunk)

        # 拼接完整结果
        full_result = "".join(result_chunks)

        # 基本验证
        assert len(full_result) > 0, f"测试用例 {test_case['id']} 返回结果为空"
        assert len(full_result) > len(content), f"测试用例 {test_case['id']} 翻译结果过短"

        # 检查是否包含技术相关关键词(至少包含一个)
        tech_keywords = [
            "技术",
            "架构",
            "方案",
            "实现",
            "开发",
            "数据",
            "性能",
            "算法",
            "接口",
            "模块",
            "工作量",
            "风险",
        ]
        has_tech_keyword = any(keyword in full_result for keyword in tech_keywords)
        assert has_tech_keyword, f"测试用例 {test_case['id']} 结果缺少技术关键词"

        # 打印结果用于人工检查
        print(f"\n{'='*80}")
        print(f"测试用例 {test_case['id']}: {test_case['description']}")
        print(f"{'='*80}")
        print(f"输入:\n{content}\n")
        print(f"输出:\n{full_result}\n")


class TestDevToProduct:
    """开发→产品 翻译测试"""

    @pytest.fixture
    def service(self):
        """创建翻译服务实例"""
        return TranslationService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_case",
        TEST_DATA["dev_to_product"],
        ids=[f"case_{case['id']}_{case['description']}" for case in TEST_DATA["dev_to_product"]],
    )
    async def test_dev_to_product_translation(self, service, test_case):
        """测试技术方案→业务价值的翻译"""
        content = test_case["content"]
        result_chunks = []

        # 收集所有流式输出
        async for chunk in service.translate_stream(content, "dev_to_product"):
            result_chunks.append(chunk)

        # 拼接完整结果
        full_result = "".join(result_chunks)

        # 基本验证
        assert len(full_result) > 0, f"测试用例 {test_case['id']} 返回结果为空"
        assert len(full_result) > len(content), f"测试用例 {test_case['id']} 翻译结果过短"

        # 检查是否包含业务价值关键词(至少包含一个)
        business_keywords = [
            "用户",
            "体验",
            "业务",
            "价值",
            "收益",
            "成本",
            "提升",
            "优化",
            "增长",
            "效率",
            "转化",
            "留存",
        ]
        has_business_keyword = any(keyword in full_result for keyword in business_keywords)
        assert has_business_keyword, f"测试用例 {test_case['id']} 结果缺少业务关键词"

        # 打印结果用于人工检查
        print(f"\n{'='*80}")
        print(f"测试用例 {test_case['id']}: {test_case['description']}")
        print(f"{'='*80}")
        print(f"输入:\n{content}\n")
        print(f"输出:\n{full_result}\n")


class TestStreamingBehavior:
    """测试流式输出行为"""

    @pytest.fixture
    def service(self):
        """创建翻译服务实例"""
        return TranslationService()

    @pytest.mark.asyncio
    async def test_streaming_is_incremental(self, service):
        """测试流式输出是否是增量的(非阻塞)"""
        content = "我们需要一个智能推荐功能,提升用户停留时长"
        chunks_count = 0
        first_chunk_time = None
        last_chunk_time = None

        import time

        start_time = time.time()

        async for chunk in service.translate_stream(content, "product_to_dev"):
            current_time = time.time()

            if chunks_count == 0:
                first_chunk_time = current_time - start_time
            last_chunk_time = current_time - start_time

            chunks_count += 1
            # 验证每个chunk不为空
            assert len(chunk) > 0, "流式输出包含空chunk"

        # 验证收到了多个chunk
        assert chunks_count > 1, f"流式输出chunk数量过少: {chunks_count}"

        # 验证首字响应时间 < 总时间(说明是流式的)
        assert first_chunk_time < last_chunk_time, "首字响应时间应该远小于总时间"

        print(f"\n流式输出统计:")
        print(f"  总chunk数: {chunks_count}")
        print(f"  首字响应: {first_chunk_time:.2f}秒")
        print(f"  总耗时: {last_chunk_time:.2f}秒")


class TestEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def service(self):
        """创建翻译服务实例"""
        return TranslationService()

    @pytest.mark.asyncio
    async def test_very_short_input(self, service):
        """测试极短输入"""
        content = "优化性能"
        result_chunks = []

        async for chunk in service.translate_stream(content, "product_to_dev"):
            result_chunks.append(chunk)

        full_result = "".join(result_chunks)
        assert len(full_result) > 0, "极短输入应该也能返回结果"

    @pytest.mark.asyncio
    async def test_long_input(self, service):
        """测试较长输入"""
        content = """我们需要开发一个全新的电商平台,包含以下功能模块:
1. 用户系统:注册、登录、个人中心、收货地址管理
2. 商品系统:商品列表、商品详情、分类浏览、搜索功能
3. 购物车:添加商品、修改数量、删除商品、结算
4. 订单系统:下单、支付、订单查询、退款退货
5. 营销系统:优惠券、满减活动、拼团、秒杀
6. 评价系统:商品评价、晒单、点赞评论
7. 客服系统:在线客服、工单系统
8. 后台管理:商品管理、订单管理、用户管理、数据统计
        """
        result_chunks = []

        async for chunk in service.translate_stream(content, "product_to_dev"):
            result_chunks.append(chunk)

        full_result = "".join(result_chunks)
        assert len(full_result) > 0, "长输入应该能返回结果"
        assert len(full_result) > len(content), "长输入的翻译结果应该更详细"

    @pytest.mark.asyncio
    async def test_special_characters(self, service):
        """测试特殊字符"""
        content = "需要支持emoji😀、特殊符号@#$%、英文ABC、数字123、换行\n测试"
        result_chunks = []

        async for chunk in service.translate_stream(content, "product_to_dev"):
            result_chunks.append(chunk)

        full_result = "".join(result_chunks)
        assert len(full_result) > 0, "包含特殊字符的输入应该能正常处理"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])

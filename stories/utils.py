import json
from django.http import JsonResponse
from django.core import serializers


class APIResponseMixin:
    """为函数视图添加 API 响应能力"""

    def render_to_api_response(self, context):
        """将上下文数据转换为 API 响应"""
        api_data = {}
        for key, value in context.items():
            if not key.startswith('view') and not key.startswith('_'):
                # 处理 QuerySet
                if hasattr(value, 'all'):
                    api_data[key] = list(value.values())
                else:
                    # 处理模型实例
                    if hasattr(value, '__dict__'):
                        api_data[key] = self.model_to_dict(value)
                    else:
                        api_data[key] = value
        return JsonResponse(api_data)

    def model_to_dict(self, instance):
        """将模型实例转换为字典"""
        if hasattr(instance, '__dict__'):
            data = {}
            for field in instance._meta.fields:
                field_name = field.name
                if field_name in ['password', 'secret_key']:  # 跳过敏感字段
                    continue
                data[field_name] = getattr(instance, field_name)
            return data
        return str(instance)
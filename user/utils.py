# utils.py - 修复连接测试
import oss2
from django.conf import settings
import uuid
from datetime import datetime


class OSSManager:
    def __init__(self):
        try:
            self.access_key_id = settings.ALIYUN_OSS_ACCESS_KEY_ID
            self.access_key_secret = settings.ALIYUN_OSS_ACCESS_KEY_SECRET
            self.endpoint = settings.ALIYUN_OSS_ENDPOINT
            self.bucket_name = settings.ALIYUN_OSS_BUCKET_NAME

            print(f"🔧 初始化OSS: {self.bucket_name}.{self.endpoint}")

            # 创建认证和Bucket实例
            self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

            # 简化连接测试
            self._simple_test_connection()

        except Exception as e:
            print(f"❌ OSS初始化失败: {e}")
            # 不抛出异常，允许继续运行
            self.bucket = None

    def _simple_test_connection(self):
        """简化连接测试"""
        try:
            # 直接尝试获取Bucket信息，不处理返回结果
            info = self.bucket.get_bucket_info()
            print(f"✅ OSS连接成功")

            # 测试上传权限（使用简单方法）
            test_key = f"test_connection_{uuid.uuid4().hex[:8]}.txt"
            try:
                self.bucket.put_object(test_key, "test")
                self.bucket.delete_object(test_key)
                print("✅ OSS读写权限正常")
            except:
                print("⚠️ OSS读写权限可能受限")

        except oss2.exceptions.NoSuchBucket:
            print(f"❌ Bucket不存在: {self.bucket_name}")
            # 不抛出异常，允许继续运行
        except oss2.exceptions.AccessDenied:
            print("❌ OSS访问被拒绝，请检查AccessKey权限")
            # 不抛出异常，允许继续运行
        except Exception as e:
            print(f"⚠️ OSS连接测试警告: {e}")
            # 不抛出异常，允许继续运行

    def upload_file(self, file, file_path):
        """上传文件到OSS"""
        if not self.bucket:
            print("❌ OSS未初始化，无法上传")
            return None

        try:
            print(f"📤 上传文件: {file_path}")

            # 重置文件指针
            if hasattr(file, 'seek'):
                file.seek(0)

            # 上传文件
            result = self.bucket.put_object(file_path, file)

            if result.status == 200:
                print(f"✅ 上传成功: {file_path}")
                return file_path
            else:
                print(f"❌ 上传失败，状态码: {result.status}")
                return None

        except oss2.exceptions.NoSuchBucket:
            print(f"❌ Bucket不存在: {self.bucket_name}")
            return None
        except oss2.exceptions.AccessDenied as e:
            print(f"❌ 权限拒绝: {e}")
            return None
        except Exception as e:
            print(f"❌ 上传异常: {e}")
            return None

    def get_file_url(self, file_path):
        """生成签名URL"""
        if not self.bucket:
            print("❌ OSS未初始化，返回默认头像")
            return settings.DEFAULT_AVATAR_URL

        try:
            if not file_path:
                return settings.DEFAULT_AVATAR_URL

            print(f"🔗 生成签名URL: {file_path}")

            # 直接生成签名URL，不检查文件是否存在
            signed_url = self.bucket.sign_url('GET', file_path, 24 * 3600)
            print(f"✅ 签名URL生成成功")

            return signed_url

        except oss2.exceptions.NoSuchBucket:
            print(f"❌ Bucket不存在: {self.bucket_name}")
            return settings.DEFAULT_AVATAR_URL
        except Exception as e:
            print(f"❌ 生成签名URL异常: {e}")
            return settings.DEFAULT_AVATAR_URL

    def generate_file_path(self, user_id, filename):
        """生成文件路径"""
        if '.' in filename:
            ext = filename.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'
        else:
            ext = 'jpg'

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        path = f"avatars/{user_id}/{timestamp}_{unique_id}.{ext}"
        return path

    def delete_file(self, file_path):
        """删除文件"""
        if not self.bucket:
            return False

        try:
            if file_path:
                self.bucket.delete_object(file_path)
                print(f"✅ 删除成功: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False


# 创建全局实例
oss_client = OSSManager()

import json
from django.http import JsonResponse


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


# 创建全局实例
api_mixin = APIResponseMixin()
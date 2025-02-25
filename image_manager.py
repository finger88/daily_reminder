import os
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

class ImageManager:
    """图片资源管理类
    
    负责管理应用的图片资源，包括：
    1. 统一存储在用户数据目录
    2. 图片缓存机制
    3. 提供统一的访问接口
    """
    
    def __init__(self):
        """初始化图片管理器
        
        - 创建应用数据目录
        - 初始化图片缓存
        - 设置默认图片配置
        """
        # 应用数据目录
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), '每日主题')
        self.images_dir = os.path.join(self.app_data_dir, 'images')
        
        # 创建必要的目录
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 图片缓存
        self._image_cache = {}
        
        # 默认图片名称
        self.default_image = '每日主题.png'
    
    def _get_today_image_names(self):
        """获取今日图片的可能文件名列表"""
        today = datetime.now().strftime('%m-%d')
        return [
            f"{today}.png",
            f"{today}.jpg",
            self.default_image
        ]
    
    def _clear_cache(self):
        """清理图片缓存"""
        self._image_cache.clear()
    
    def copy_images_from(self, src_dir):
        """从源目录复制图片到应用数据目录
        
        Args:
            src_dir: 源图片目录路径
        """
        if not os.path.exists(src_dir):
            raise FileNotFoundError(f"源目录不存在：{src_dir}")
            
        # 复制所有图片文件
        for filename in os.listdir(src_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                src_path = os.path.join(src_dir, filename)
                dst_path = os.path.join(self.images_dir, filename)
                shutil.copy2(src_path, dst_path)
    
    def get_image_path(self):
        """获取当前应显示的图片路径
        
        Returns:
            str: 图片文件路径，如果没有找到则返回None
        """
        for name in self._get_today_image_names():
            path = os.path.join(self.images_dir, name)
            if os.path.exists(path):
                return path
        return None
    
    def load_image(self, max_size=None):
        """加载并处理图片
        
        Args:
            max_size: 最大尺寸元组 (width, height)，默认为None
            
        Returns:
            tuple: (PIL.Image对象, 图片路径)
            如果加载失败返回 (None, None)
        """
        image_path = self.get_image_path()
        if not image_path:
            return None, None
            
        # 检查缓存
        cache_key = f"{image_path}_{max_size}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key], image_path
            
        try:
            # 加载图片
            img = Image.open(image_path)
            
            # 调整大小
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
            # 缓存处理后的图片
            self._image_cache[cache_key] = img
            return img, image_path
            
        except Exception as e:
            print(f"加载图片失败：{str(e)}")
            return None, None
    
    def create_photo_image(self, window, max_size=None):
        """创建Tkinter图片对象
        
        Args:
            window: Tkinter窗口对象
            max_size: 最大尺寸元组 (width, height)
            
        Returns:
            tuple: (PhotoImage对象, 错误消息)
            成功时错误消息为None
        """
        img, path = self.load_image(max_size)
        if not img:
            error_msg = f"无法加载图片，请确保以下文件之一存在：\n{', '.join(self._get_today_image_names())}"
            return None, error_msg
            
        try:
            photo = ImageTk.PhotoImage(img)
            return photo, None
        except Exception as e:
            return None, f"创建图片对象失败：{str(e)}"
    
    def cleanup(self):
        """清理资源
        
        - 清空图片缓存
        - 可以添加其他清理操作
        """
        self._clear_cache()
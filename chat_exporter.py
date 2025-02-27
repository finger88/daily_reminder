import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class ChatExporter:
    """对话记录导出工具
    
    功能：
    1. 记录对话内容
    2. 导出对话记录到文件
    3. 提供导出按钮集成到右键菜单
    """
    
    def __init__(self):
        """初始化导出工具
        
        - 创建导出目录
        - 初始化对话记录列表
        """
        # 导出文件保存目录
        self.export_dir = os.path.join(os.getenv('APPDATA'), '每日主题', 'chat_logs')
        os.makedirs(self.export_dir, exist_ok=True)
        
        # 对话记录列表
        self.chat_history = []
    
    def add_message(self, message, is_user=True):
        """添加一条对话记录
        
        Args:
            message: 对话内容
            is_user: 是否是用户消息，默认为True
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sender = '用户' if is_user else '系统'
        self.chat_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message
        })
    
    def export_chat(self):
        """导出对话记录到文件
        
        Returns:
            str: 导出文件的路径
        """
        if not self.chat_history:
            return None
            
        # 生成文件名
        filename = f"chat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('=== 每日主题对话记录 ===\n\n')
                for msg in self.chat_history:
                    f.write(f"[{msg['timestamp']}] {msg['sender']}:\n{msg['message']}\n\n")
            return filepath
        except Exception as e:
            print(f"导出对话记录失败：{str(e)}")
            return None
    
    def create_export_button(self, parent_menu):
        """创建导出按钮并添加到菜单
        
        Args:
            parent_menu: 父级菜单对象
        """
        parent_menu.add_command(
            label='导出对话记录',
            command=self._handle_export
        )
    
    def _handle_export(self):
        """处理导出操作"""
        filepath = self.export_chat()
        if filepath:
            messagebox.showinfo(
                '导出成功',
                f'对话记录已导出到：\n{filepath}'
            )
        else:
            messagebox.showwarning(
                '导出失败',
                '没有可导出的对话记录'
            )
    
    def clear_history(self):
        """清空对话记录"""
        self.chat_history.clear()
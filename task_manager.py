import os
import json
from datetime import datetime

class TaskManager:
    """
    事务管理器类
    
    负责管理应用的事务记录，包括：
    1. 按日期保存事务记录
    2. 提供事务的增删改查接口
    3. 统一的数据存储管理
    """
    
    def __init__(self):
        """
        初始化事务管理器
        
        - 创建应用数据目录
        - 初始化数据存储
        """
        # 应用数据目录
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), '每日事务')
        self.tasks_dir = os.path.join(self.app_data_dir, 'tasks')
        
        # 创建必要的目录
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # 当前日期的任务文件路径
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.current_file = os.path.join(self.tasks_dir, f"{self.current_date}.json")
        
        # 确保当前日期的任务文件存在
        if not os.path.exists(self.current_file):
            self._create_empty_task_file()
    
    def _create_empty_task_file(self):
        """创建空的任务文件"""
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': self.current_date,
                'tasks': []
            }, f, ensure_ascii=False, indent=4)
    
    def add_task(self, content):
        """添加新任务
        
        Args:
            content: 任务内容
            
        Returns:
            dict: 新添加的任务信息
        """
        # 读取当前任务文件
        with open(self.current_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建新任务
        task = {
            'id': len(data['tasks']) + 1,
            'content': content,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed': False
        }
        
        # 添加到任务列表
        data['tasks'].append(task)
        
        # 保存更新
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return task
    
    def get_tasks(self, date=None):
        """获取指定日期的任务列表
        
        Args:
            date: 日期字符串（YYYY-MM-DD），默认为当前日期
            
        Returns:
            list: 任务列表
        """
        if date is None:
            date = self.current_date
        
        file_path = os.path.join(self.tasks_dir, f"{date}.json")
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['tasks']
    
    def update_task(self, task_id, completed=None, content=None):
        """更新任务状态
        
        Args:
            task_id: 任务ID
            completed: 是否完成
            content: 更新的内容
            
        Returns:
            bool: 更新是否成功
        """
        with open(self.current_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 查找并更新任务
        for task in data['tasks']:
            if task['id'] == task_id:
                if completed is not None:
                    task['completed'] = completed
                if content is not None:
                    task['content'] = content
                break
        else:
            return False
        
        # 保存更新
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
    
    def delete_task(self, task_id):
        """删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 删除是否成功
        """
        with open(self.current_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 查找并删除任务
        original_length = len(data['tasks'])
        data['tasks'] = [task for task in data['tasks'] if task['id'] != task_id]
        
        if len(data['tasks']) == original_length:
            return False
        
        # 保存更新
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
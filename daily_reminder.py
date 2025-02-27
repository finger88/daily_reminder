import os
import sys
import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
import win32api
from PIL import Image, ImageTk
from image_manager import ImageManager
from task_manager import TaskManager

class FloatingBall:
    """
    每日主题悬浮球应用的主类
    
    功能特点：
    1. 创建一个半透明的悬浮窗口，显示在屏幕边缘
    2. 支持鼠标拖拽移动位置
    3. 自动贴边隐藏/显示
    4. 显示每日主题图片
    5. 支持开机自启动管理
    
    主要组件：
    - root: 主窗口对象
    - button: 悬浮球按钮
    - theme_window: 主题图片显示窗口
    """
    
    def __init__(self):
        """初始化悬浮球应用
        
        设置窗口属性：
        - 半透明（alpha=0.9）
        - 始终置顶
        - 无边框
        - 隐藏任务栏图标
        """
        self.root = tk.Tk()
        self.root.title("每日主题")
        
        # 设置窗口属性
        self.root.attributes('-topmost', True)  # 始终置顶
        self.root.attributes('-alpha', 0.9)  # 设置透明度
        
        # 隐藏任务栏图标
        self.root.wm_attributes('-toolwindow', True)  # 设置为工具窗口
        self.root.overrideredirect(True)  # 移除窗口边框
        
        # 创建主题按钮
        self.theme_button = tk.Button(self.root, text="每日\n主题", 
                              width=8, height=2,  
                              bg='#2196F3', fg='white',
                              relief='raised',
                              font=('Arial', 10, 'bold'),  
                              command=self.show_theme)
        self.theme_button.pack(padx=2, pady=2)
        
        # 创建事务按钮
        self.task_button = tk.Button(self.root, text="记录\n事务", 
                              width=8, height=2,  
                              bg='#4CAF50', fg='white',
                              relief='raised',
                              font=('Arial', 10, 'bold'),  
                              command=self.show_task_window)
        self.task_button.pack(padx=2, pady=2)
        
        # 绑定鼠标事件
        for button in [self.theme_button, self.task_button]:
            button.bind('<Button-1>', self.on_click)  # 左键点击
            button.bind('<B1-Motion>', self.on_move)  # 拖拽移动
            button.bind('<Enter>', self.on_enter)    # 鼠标进入
            button.bind('<Leave>', self.on_leave)    # 鼠标离开
        
        # 设置初始位置（屏幕右侧中间）
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+{self.screen_width-30}+{self.screen_height//2}")
        
        # 主题窗口引用（初始为None）
        self.theme_window = None
        
        # 初始化图片管理器
        self.image_manager = ImageManager()
        
        # 初始化事务管理器
        self.task_manager = TaskManager()
        
        # 事务窗口引用
        self.task_window = None
        
        # 自动隐藏相关变量
        self.is_hidden = False      # 是否处于隐藏状态
        self.hide_timer = None      # 隐藏定时器
        self.show_timer = None      # 显示定时器
        self.last_x = 0            # 上次鼠标X坐标
        self.last_y = 0            # 上次鼠标Y坐标
        self.dragging = False      # 是否正在拖拽
        self.fully_hidden = False  # 是否完全隐藏
        
        # 设置检测区域大小
        self.detection_range = 50  
        
        # 初始状态设为半隐藏
        self.root.after(1000, self.semi_hide_ball)
        
        # 启动鼠标位置监测
        self.check_mouse_position()
        
    def on_click(self, event):
        """处理鼠标点击事件
        
        - 记录拖拽状态和初始位置
        - 取消可能存在的隐藏/显示定时器
        """
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        if self.show_timer:
            self.root.after_cancel(self.show_timer)
            
    def on_move(self, event):
        """处理拖拽移动事件
        
        计算鼠标移动距离，更新窗口位置
        """
        if not self.dragging:
            return
        deltax = event.x - self.last_x
        deltay = event.y - self.last_y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def on_enter(self, event):
        """处理鼠标进入事件
        
        取消隐藏定时器，显示完整悬浮球
        """
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        if self.fully_hidden:
            self.show_ball()
            
    def on_leave(self, event):
        """处理鼠标离开事件
        
        如果不在拖拽状态，启动隐藏定时器
        """
        if not self.dragging:
            self.hide_timer = self.root.after(1000, self.semi_hide_ball)
            
    def semi_hide_ball(self):
        """半隐藏悬浮球
        
        根据悬浮球在屏幕的位置（左/右），将其隐藏一半
        """
        if self.dragging:
            return
            
        x = self.root.winfo_x()
        if x < self.screen_width // 2:
            target_x = -40  # 左边只隐藏一半
        else:
            target_x = self.screen_width - 40  # 右边只隐藏一半
            
        self.root.geometry(f"+{target_x}+{self.root.winfo_y()}")
        self.is_hidden = True
        
        # 启动完全隐藏计时器
        self.root.after(3000, self.fully_hide_ball)
        
    def show_ball(self):
        """完全显示悬浮球
        
        根据悬浮球在屏幕的位置（左/右），将其完全显示
        """
        if self.dragging:
            return
            
        x = self.root.winfo_x()
        if x < self.screen_width // 2:
            target_x = 0
        else:
            target_x = self.screen_width - 80
            
        self.root.geometry(f"+{target_x}+{self.root.winfo_y()}")
        self.is_hidden = False
        self.fully_hidden = False
        self.root.attributes('-alpha', 0.9)
        
    def show_prev_image(self):
        """显示上一张图片"""
        if self.total_images > 1:
            self.current_image_index = (self.current_image_index - 1) % self.total_images
            self.update_theme_image()
    
    def show_next_image(self):
        """显示下一张图片"""
        if self.total_images > 1:
            self.current_image_index = (self.current_image_index + 1) % self.total_images
            self.update_theme_image()
    
    def update_theme_image(self):
        """更新当前显示的图片"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_size = (int(screen_width * 0.8), int(screen_height * 0.8))
        
        # 加载新图片
        img = Image.open(self.available_images[self.current_image_index])
        img.thumbnail(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # 更新显示
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        if hasattr(self, 'image_counter'):
            self.image_counter.configure(text=f"{self.current_image_index + 1}/{self.total_images}")
    
    def show_theme(self):
        """显示每日主题图片
        
        主要功能：
        1. 创建新窗口显示主题图片
        2. 根据日期自动选择对应图片
        3. 自动调整图片大小适应屏幕
        4. 处理各种异常情况
        """
        if self.theme_window and self.theme_window.winfo_exists():
            self.theme_window.destroy()
            self.theme_window = None
            return
            
        self.theme_window = tk.Toplevel(self.root)
        self.theme_window.title("每日主题")
        self.theme_window.attributes('-topmost', True)
        
        # 设置主题窗口为普通窗口（有边框和最小化按钮）
        self.theme_window.overrideredirect(False)
        self.theme_window.wm_attributes('-toolwindow', False)
        
        try:
            # 获取程序运行路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                application_path = os.path.dirname(sys.executable)
                # 检查exe所在目录是否有daily_images文件夹
                if not os.path.exists(os.path.join(application_path, "daily_images")):
                    # 如果没有，尝试在上一级目录查找
                    parent_path = os.path.dirname(application_path)
                    if os.path.exists(os.path.join(parent_path, "daily_images")):
                        application_path = parent_path
            else:
                # 开发环境
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            # 复制图片到用户数据目录
            images_folder = os.path.join(application_path, "daily_images")
            if os.path.exists(images_folder):
                self.image_manager.copy_images_from(images_folder)
            
            # 创建图片显示窗口
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            display_size = (int(screen_width * 0.8), int(screen_height * 0.8))
            
            # 加载并显示图片
            photo, error_msg = self.image_manager.create_photo_image(self.theme_window, display_size)
            if error_msg:
                messagebox.showerror("错误", error_msg)
                self.theme_window.destroy()
                return
                
            # 获取所有可用图片
            self.current_image_index = 0
            self.available_images = self.image_manager.get_today_images()
            self.total_images = len(self.available_images)
            
            # 创建滚动区域
            canvas = tk.Canvas(self.theme_window, highlightthickness=0)
            scrollbar = tk.Scrollbar(self.theme_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            # 配置滚动区域
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # 创建并保存图片标签，添加边距
            self.image_label = tk.Label(scrollable_frame, image=photo)
            self.image_label.image = photo
            self.image_label.pack(padx=10, pady=10)

            # 更新滚动区域大小
            def _configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                # 确保内容居中
                canvas.configure(width=event.width)
            scrollable_frame.bind("<Configure>", _configure_scroll_region)

            # 创建导航栏（始终显示）
            nav_frame = tk.Frame(self.theme_window)
            nav_frame.pack(side=tk.BOTTOM, fill=tk.X)
            
            # 放置滚动区域和滚动条
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 创建一个内部框架用于居中对齐按钮
            inner_frame = tk.Frame(nav_frame)
            inner_frame.pack()
            
            prev_button = tk.Button(inner_frame, text="上一张", command=self.show_prev_image,
                                  state=tk.NORMAL if self.total_images > 1 else tk.DISABLED)
            prev_button.pack(side=tk.LEFT, padx=5)
            
            self.image_counter = tk.Label(inner_frame, text=f"1/{self.total_images}")
            self.image_counter.pack(side=tk.LEFT, padx=10)
            
            next_button = tk.Button(inner_frame, text="下一张", command=self.show_next_image,
                                  state=tk.NORMAL if self.total_images > 1 else tk.DISABLED)
            next_button.pack(side=tk.LEFT, padx=5)
            
            # 绑定键盘事件（仅在有多张图片时生效）
            if self.total_images > 1:
                self.theme_window.bind('<Left>', lambda e: self.show_prev_image())
                self.theme_window.bind('<Right>', lambda e: self.show_next_image())
            
            # 设置窗口大小和位置
            window_width = min(photo.width() + 40, screen_width * 0.9)  # 考虑滚动条宽度
            # 为导航栏预留足够的空间
            nav_height = 40 if self.total_images > 1 else 0
            window_height = min(photo.height() + 20 + nav_height, screen_height * 0.9)
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.theme_window.geometry(f"{int(window_width)}x{int(window_height)}+{x}+{y}")

            # 绑定鼠标滚轮事件
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            self.theme_window.bind_all("<MouseWheel>", _on_mousewheel)
            
        except Exception as e:
            error_msg = f"显示图片时发生错误：\n{str(e)}\n\n如果问题持续存在，请检查:\n1. 图片文件是否存在且未损坏\n2. 程序是否有足够的权限访问图片\n3. 系统内存是否充足"
            print(f"错误: {error_msg}")
            messagebox.showerror("错误", error_msg)
            if self.theme_window:
                self.theme_window.destroy()
    
    def add_to_startup(self):
        """添加程序到开机启动项
        
        1. 创建快捷方式到启动目录
        2. 复制必要的图片资源
        """
        startup_path = os.path.join(os.getenv('APPDATA'), 
                                  r'Microsoft\Windows\Start Menu\Programs\Startup',
                                  '每日主题.lnk')
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(startup_path)
            exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "daily_reminder.exe")
            # 修改工作目录为项目根目录（exe的上级目录）
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(os.path.dirname(exe_path))  # 使用exe的上级目录作为工作目录
            shortcut.save()
            
            # 复制图片文件夹到 exe 目录
            import shutil
            src_image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_images")
            dst_image_folder = os.path.join(os.path.dirname(exe_path), "daily_images")
            if os.path.exists(src_image_folder):
                if os.path.exists(dst_image_folder):
                    shutil.rmtree(dst_image_folder)
                shutil.copytree(src_image_folder, dst_image_folder)
            
            messagebox.showinfo("提示", "已添加到开机启动项，并复制图片文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"无法添加到开机启动项：{str(e)}")
                
    def on_release(self, event):
        """处理鼠标释放事件
        
        当鼠标释放时：
        1. 结束拖拽状态
        2. 延迟500ms后自动半隐藏悬浮球
        """
        self.dragging = False
        self.root.after(500, self.semi_hide_ball)
            
    def check_startup_status(self):
        """检查开机启动状态
        
        通过检查启动目录中是否存在快捷方式来判断
        返回：True表示已设置开机启动，False表示未设置
        """
        startup_path = os.path.join(os.getenv('APPDATA'),
                                  r'Microsoft\Windows\Start Menu\Programs\Startup',
                                  '每日主题.lnk')
        return os.path.exists(startup_path)

    def toggle_startup(self):
        """切换开机启动状态
        
        如果当前已设置开机启动则取消，否则添加到开机启动
        包含异常处理和用户提示
        """
        startup_path = os.path.join(os.getenv('APPDATA'),
                                  r'Microsoft\Windows\Start Menu\Programs\Startup',
                                  '每日主题.lnk')
        if self.check_startup_status():
            try:
                os.remove(startup_path)
                messagebox.showinfo("提示", "已取消开机启动")
            except Exception as e:
                messagebox.showerror("错误", f"无法取消开机启动：{str(e)}")
        else:
            self.add_to_startup()

    def show_task_window(self):
        """显示事务记录窗口
        
        主要功能：
        1. 创建新窗口用于记录事务
        2. 显示当天的事务列表
        3. 提供添加和管理事务的界面
        """
        if self.task_window and self.task_window.winfo_exists():
            self.task_window.destroy()
            self.task_window = None
            return
            
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title("每日事务")
        self.task_window.attributes('-topmost', True)
        
        # 设置窗口为普通窗口
        self.task_window.overrideredirect(False)
        self.task_window.wm_attributes('-toolwindow', False)
        
        # 创建输入框和按钮
        input_frame = tk.Frame(self.task_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.task_entry = tk.Entry(input_frame)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        add_button = tk.Button(input_frame, text="添加", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=5)
        
        history_button = tk.Button(input_frame, text="历史记录", command=self.show_history_window)
        history_button.pack(side=tk.LEFT, padx=5)
        
        # 创建任务列表
        self.task_listbox = tk.Listbox(self.task_window, width=40, height=15)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加右键菜单
        task_menu = tk.Menu(self.task_listbox, tearoff=0)
        task_menu.add_command(label="完成", command=lambda: self.toggle_task_status(True))
        task_menu.add_command(label="取消完成", command=lambda: self.toggle_task_status(False))
        task_menu.add_separator()
        task_menu.add_command(label="删除", command=self.delete_task)
        
        def show_task_menu(event):
            try:
                index = self.task_listbox.nearest(event.y)
                if index >= 0:
                    self.task_listbox.selection_clear(0, tk.END)
                    self.task_listbox.selection_set(index)
                    task_menu.post(event.x_root, event.y_root)
            except tk.TclError:
                pass
        
        self.task_listbox.bind('<Button-3>', show_task_menu)
        
        # 更新任务列表
        self.update_task_list()
        
        # 设置窗口位置
        window_width = 300
        window_height = 400
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        self.task_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def show_history_window(self):
        """显示历史记录窗口
        
        主要功能：
        1. 显示所有历史日期的任务记录
        2. 支持按日期范围筛选
        3. 支持导出历史记录
        """
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        history_window.attributes('-topmost', True)
        
        # 设置窗口为普通窗口
        history_window.overrideredirect(False)
        history_window.wm_attributes('-toolwindow', False)
        
        # 创建日期选择框
        date_frame = tk.Frame(history_window)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        dates = self.task_manager.get_history_dates()
        if not dates:
            tk.Label(history_window, text="暂无历史记录").pack(pady=20)
            return
            
        # 创建开始日期选择
        tk.Label(date_frame, text="开始日期：").pack(side=tk.LEFT)
        start_var = tk.StringVar(value=dates[-1])
        start_menu = tk.OptionMenu(date_frame, start_var, *dates)
        start_menu.pack(side=tk.LEFT, padx=5)
        
        # 创建结束日期选择
        tk.Label(date_frame, text="结束日期：").pack(side=tk.LEFT)
        end_var = tk.StringVar(value=dates[0])
        end_menu = tk.OptionMenu(date_frame, end_var, *dates)
        end_menu.pack(side=tk.LEFT, padx=5)
        
        # 创建历史记录列表
        history_frame = tk.Frame(history_window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        history_text = tk.Text(history_frame, wrap=tk.WORD, width=50, height=20)
        history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=history_text.yview)
        
        def update_history_display():
            """更新历史记录显示"""
            start_date = start_var.get()
            end_date = end_var.get()
            
            # 清空文本框
            history_text.delete('1.0', tk.END)
            
            # 获取历史记录
            history_tasks = self.task_manager.get_tasks_by_date_range(start_date, end_date)
            
            # 显示历史记录
            for date in sorted(history_tasks.keys(), reverse=True):
                history_text.insert(tk.END, f"=== {date} ===\n")
                for task in history_tasks[date]:
                    status = "[√]" if task['completed'] else "[ ]"
                    history_text.insert(tk.END, f"{status} {task['content']}\n")
                history_text.insert(tk.END, "\n")
        
        # 创建更新按钮
        update_button = tk.Button(date_frame, text="更新", command=update_history_display)
        update_button.pack(side=tk.LEFT, padx=10)
        
        # 初始显示历史记录
        update_history_display()
        
        # 设置窗口位置和大小
        window_width = 500
        window_height = 600
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        history_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def add_task(self):
        """添加新事务"""
        content = self.task_entry.get().strip()
        if content:
            self.task_manager.add_task(content)
            self.task_entry.delete(0, tk.END)
            self.update_task_list()
    
    def update_task_list(self):
        """更新事务列表显示"""
        self.task_listbox.delete(0, tk.END)
        tasks = self.task_manager.get_tasks()
        for task in tasks:
            status = "[√] " if task['completed'] else "[ ] "
            self.task_listbox.insert(tk.END, f"{status}{task['content']}")
            # 如果任务已完成，添加删除线效果
            if task['completed']:
                index = self.task_listbox.size() - 1
                self.task_listbox.itemconfig(index, fg='gray')
    
    def toggle_task_status(self, completed):
        """切换任务状态"""
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            tasks = self.task_manager.get_tasks()
            if index < len(tasks):
                task_id = tasks[index]['id']
                self.task_manager.update_task(task_id, completed=completed)
                self.update_task_list()
    
    def delete_task(self):
        """删除任务"""
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            tasks = self.task_manager.get_tasks()
            if index < len(tasks):
                task_id = tasks[index]['id']
                self.task_manager.delete_task(task_id)
                self.update_task_list()
    
    def fully_hide_ball(self):
        """完全隐藏悬浮球
        
        将悬浮球完全隐藏（透明度设为0）
        """
        if not self.dragging and self.is_hidden:
            self.fully_hidden = True
            self.root.attributes('-alpha', 0)
    
    def check_mouse_position(self):
        """检查鼠标位置
        
        定期检查鼠标位置，当鼠标靠近屏幕边缘时显示悬浮球
        """
        if self.fully_hidden:
            mouse_x = win32api.GetCursorPos()[0]
            screen_edge = 2
            
            # 检查鼠标是否在屏幕边缘
            if mouse_x <= screen_edge or mouse_x >= self.screen_width - screen_edge:
                self.show_ball()
        
        # 每50毫秒检查一次鼠标位置
        self.root.after(50, self.check_mouse_position)
    
    def run(self):
        """运行应用程序
        
        主要功能：
        1. 创建右键菜单，包含开机启动选项和退出选项
        2. 绑定鼠标右键和左键释放事件
        3. 启动主循环
        """
        menu = tk.Menu(self.root, tearoff=0)
        startup_var = tk.BooleanVar(value=self.check_startup_status())
        menu.add_checkbutton(label="开机启动", variable=startup_var, command=self.toggle_startup)
        menu.add_separator()
        menu.add_command(label="退出", command=self.root.quit)

        def show_menu(event):
            """显示右键菜单
            
            更新开机启动状态并显示菜单
            """
            startup_var.set(self.check_startup_status())  # 更新复选框状态
            menu.post(event.x_root, event.y_root)
            
        for button in [self.theme_button, self.task_button]:
            button.bind('<Button-3>', show_menu)
            button.bind('<ButtonRelease-1>', self.on_release)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingBall()
    app.run()

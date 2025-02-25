import os
import sys
import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
import win32api
from image_manager import ImageManager

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
        
        # 创建按钮
        self.button = tk.Button(self.root, text="每日\n主题", 
                              width=8, height=2,  
                              bg='#2196F3', fg='white',
                              relief='raised',
                              font=('Arial', 10, 'bold'),  
                              command=self.show_theme)
        self.button.pack(padx=2, pady=2)
        
        # 绑定鼠标事件
        self.button.bind('<Button-1>', self.on_click)  # 左键点击
        self.button.bind('<B1-Motion>', self.on_move)  # 拖拽移动
        self.button.bind('<Enter>', self.on_enter)    # 鼠标进入
        self.button.bind('<Leave>', self.on_leave)    # 鼠标离开
        
        # 设置初始位置（屏幕右侧中间）
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+{self.screen_width-30}+{self.screen_height//2}")
        
        # 主题窗口引用（初始为None）
        self.theme_window = None
        
        # 初始化图片管理器
        self.image_manager = ImageManager()
        
        # 自动隐藏相关变量
        self.is_hidden = False      # 是否处于隐藏状态
        self.hide_timer = None      # 隐藏定时器
        self.show_timer = None      # 显示定时器
        self.last_x = 0            # 上次鼠标X坐标
        self.last_y = 0            # 上次鼠标Y坐标
        self.dragging = False      # 是否正在拖拽
        
        # 设置检测区域大小
        self.detection_range = 50  
        
        # 初始状态设为半隐藏
        self.root.after(1000, self.semi_hide_ball)
        
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
                
            # 显示图片
            label = tk.Label(self.theme_window, image=photo)
            label.image = photo  # 保持引用防止被垃圾回收
            label.pack(padx=10, pady=10)
            
            # 设置窗口大小和位置
            window_width = photo.width() + 20
            window_height = photo.height() + 20
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.theme_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
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
            
        self.button.bind('<Button-3>', show_menu)
        self.button.bind('<ButtonRelease-1>', self.on_release)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingBall()
    app.run()

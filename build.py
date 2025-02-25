import os
import shutil
import subprocess

def clean_dist():
    """清理dist目录"""
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
        print('已清理dist目录')

def copy_resources():
    """复制资源文件到dist目录"""
    src_images = os.path.join(os.path.dirname(__file__), 'daily_images')
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    dist_images = os.path.join(dist_dir, 'daily_images')
    
    if os.path.exists(src_images):
        if os.path.exists(dist_images):
            shutil.rmtree(dist_images)
        shutil.copytree(src_images, dist_images)
        print('已复制图片资源')

def build_exe():
    """使用PyInstaller打包程序"""
    try:
        # 确保已安装pyinstaller
        subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
        
        # 打包命令
        subprocess.run([
            'pyinstaller',
            '--noconfirm',  # 覆盖已存在的文件
            '--noconsole',  # 不显示控制台窗口
            '--onefile',    # 打包成单个文件
            '--name', 'daily_reminder',
            'daily_reminder.py'
        ], check=True)
        
        print('打包完成')
        return True
    except subprocess.CalledProcessError as e:
        print(f'打包失败: {str(e)}')
        return False

def main():
    """主函数"""
    print('开始打包流程...')
    
    # 1. 清理dist目录
    clean_dist()
    
    # 2. 打包程序
    if build_exe():
        # 3. 复制资源文件
        copy_resources()
        print('\n打包流程完成！\n')
        print('提示：exe文件位于dist目录下')
    else:
        print('\n打包流程失败！')

if __name__ == '__main__':
    main()
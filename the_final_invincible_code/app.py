import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QAction, QMenu
from PyQt5.QtCore import QDir
from main import MainWindow
from editor import Editor, WelcomeWidget
from file_system import FileExplorer
from git_manager import GitManager
from style import Style
from mind_map import MindMap

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 应用深色主题
        Style.apply_dark_theme(self.app)
        
        self.main_window = MainWindow()
        
        # 初始化组件
        self.init_components()
        
        # 连接信号和槽
        self.connect_signals()
        
    def init_components(self):
        # 初始化文件浏览器
        self.file_explorer = FileExplorer()
        self.main_window.sidebar.removeTab(0)  # 移除占位符
        self.main_window.sidebar.insertTab(0, self.file_explorer, "文件")
        
        # 初始化Git管理器
        self.git_manager = GitManager()
        self.main_window.sidebar.removeTab(2)  # 移除Git占位符
        self.main_window.sidebar.insertTab(2, self.git_manager, "Git")
        
        # 设置Git仓库路径为当前工作目录
        current_dir = QDir.currentPath()
        self.git_manager.set_repo_path(current_dir)
        
        # 添加欢迎页面
        self.welcome_widget = WelcomeWidget()
        self.main_window.editor.add_tab(self.welcome_widget, "欢迎")
        
        # 确保状态栏显示
        self.main_window.statusBar.show()
        self.main_window.statusBar.showMessage("就绪")
        
        # 添加思维导图按钮到工具栏
        self.add_mind_map_button()
        
    def connect_signals(self):
        # 连接文件浏览器的双击信号
        self.file_explorer.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        
        # 连接标签关闭信号
        self.main_window.editor.main_container.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
        
        # 连接Git命令执行信号
        self.git_manager.git_command_executed.connect(self.on_git_command_executed)
        
        # 连接Git菜单项信号
        if hasattr(self.main_window, 'git_actions'):
            self.main_window.git_actions['init_repo'].triggered.connect(self.git_manager.init_repo)
            self.main_window.git_actions['status'].triggered.connect(self.git_manager.check_status)
            self.main_window.git_actions['add'].triggered.connect(self.git_manager.add_files)
            self.main_window.git_actions['commit'].triggered.connect(self.git_manager.commit_changes)
            self.main_window.git_actions['push'].triggered.connect(self.git_manager.push_changes)
            self.main_window.git_actions['pull'].triggered.connect(self.git_manager.pull_changes)
            self.main_window.git_actions['branch'].triggered.connect(self.git_manager.manage_branches)
            self.main_window.git_actions['log'].triggered.connect(self.git_manager.show_log)
    
    def on_git_command_executed(self, command, result):
        # 在状态栏显示Git命令执行信息
        self.main_window.statusBar.showMessage(f"执行: {command}")
        
        # 如果是目录切换，更新Git仓库路径
        if self.file_explorer.model.rootPath() != self.git_manager.current_repo_path:
            self.git_manager.set_repo_path(self.file_explorer.model.rootPath())
        
    def on_file_double_clicked(self, index):
        # 获取文件路径
        file_path = self.file_explorer.model.filePath(index)
        
        # 如果是文件，则打开
        import os
        if os.path.isfile(file_path):
            self.open_file(file_path)
    
    def open_file(self, file_path):
        # 创建编辑器
        editor = Editor()
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            editor.set_content(content)
            
            # 获取文件名
            import os
            file_name = os.path.basename(file_path)
            
            # 添加到编辑器
            index = self.main_window.editor.add_tab(editor, file_name)
            self.main_window.editor.set_current_widget(editor)
        except Exception as e:
            print(f"打开文件失败: {e}")
    
    def on_tab_close_requested(self, index):
        # 获取发送信号的标签页
        sender = self.app.sender()
        
        # 关闭标签页
        if hasattr(sender, 'removeTab'):
            sender.removeTab(index)
    
    def add_mind_map_button(self):
        # 添加思维导图按钮到工具栏
        mind_map_action = QAction("思维导图", self.main_window)
        mind_map_action.triggered.connect(self.create_mind_map)
        self.main_window.tool_bar.addAction(mind_map_action)
    
    def create_mind_map(self):
        # 创建思维导图
        mind_map = MindMap()
        
        # 添加到编辑器
        self.main_window.left_editor.addTab(mind_map, "思维导图")
        self.main_window.left_editor.setCurrentWidget(mind_map)
    
    def run(self):
        self.main_window.show()
        return self.app.exec_()

if __name__ == "__main__":
    app = Application()
    sys.exit(app.run())
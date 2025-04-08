import sys
from PyQt5.QtWidgets import QApplication, QAction, QMenu
from PyQt5.QtCore import QDir
from main import MainWindow
from editor import Editor, WelcomeWidget
from file_system import FileExplorer
from mind_map import MindMap

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
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
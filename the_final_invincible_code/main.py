import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QAction, QStatusBar, QTabWidget, QTreeView, QMenu, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from editor import Editor
from split_editor import SplitEditorManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("灵犀协作")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 创建主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建侧边栏
        self.create_sidebar()
        
        # 创建内容区域
        self.create_content_area()
        
    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        new_action = QAction("新建", self)
        new_action.setShortcut("Ctrl+N")
        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        undo_action = QAction("撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        redo_action = QAction("重做", self)
        redo_action.setShortcut("Ctrl+Y")
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        
        # 视图菜单
        view_menu = menu_bar.addMenu("视图")
        sidebar_action = QAction("侧边栏", self)
        sidebar_action.setCheckable(True)
        sidebar_action.setChecked(True)
        statusbar_action = QAction("状态栏", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(lambda checked: self.statusBar.setVisible(checked))
        
        view_menu.addAction(sidebar_action)
        view_menu.addAction(statusbar_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        about_action = QAction("关于", self)
        help_menu.addAction(about_action)
        
    def create_sidebar(self):
        # 创建侧边栏
        self.sidebar = QTabWidget()
        self.sidebar.setTabPosition(QTabWidget.West)
        self.sidebar.setMaximumWidth(300)
        
        # 文件浏览器标签
        self.file_explorer = QTreeView()
        self.sidebar.addTab(self.file_explorer, "文件")
        
        # 搜索标签
        self.search_widget = QWidget()
        self.sidebar.addTab(self.search_widget, "搜索")
        
        # 扩展标签
        self.extensions_widget = QWidget()
        self.sidebar.addTab(self.extensions_widget, "扩展")
        
        # 添加到主布局
        self.main_layout.addWidget(self.sidebar)
    
    def on_tab_dragged(self, tab_index, drop_pos):
        # 调用 SplitEditorManager 的 on_tab_dragged 方法处理标签拖拽逻辑
        current_widget = self.editor.main_container.tab_widget.widget(tab_index)
        self.editor.on_tab_dragged(tab_index, drop_pos)

    def create_content_area(self):
        # 创建内容区域
        self.editor = SplitEditorManager()
        self.editor.tabDragged.connect(self.on_tab_dragged)  # 修改此处为 tabDragged

        # 添加到主布局
        self.main_layout.addWidget(self.editor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import QDir, Qt, QModelIndex
from PyQt5.QtGui import QIcon, QFont
import os
from style import Style

class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # 创建标题
        self.title_label = QLabel("资源管理器")
        self.title_label.setStyleSheet(f"color: {Style.INACTIVE_TEXT}; font-weight: bold; padding: 5px;")
        
        # 创建搜索框
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(0, 5, 0, 5)
        self.search_layout.setSpacing(5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Style.DARKER_BG};
                color: {Style.TEXT_COLOR};
                border: 1px solid {Style.BORDER_COLOR};
                border-radius: 2px;
                padding: 4px 8px;
                selection-background-color: {Style.HIGHLIGHT_BG};
            }}
        """)
        
        self.search_button = QPushButton("搜索")
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Style.HIGHLIGHT_BG};
                color: {Style.HIGHLIGHT_TEXT};
                border: none;
                padding: 4px 8px;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: #1177bb;
            }}
            QPushButton:pressed {{
                background-color: #0e5384;
            }}
        """)
        self.search_button.setFixedWidth(60)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        
        # 创建树状视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
        
        # 设置树状视图样式
        self.tree_view.setStyleSheet(f"""
            QTreeView {{
                background-color: {Style.DARKER_BG};
                border: none;
                outline: none;
                padding: 2px;
            }}
            QTreeView::item {{
                padding: 4px;
                border: none;
            }}
            QTreeView::item:selected {{
                background-color: {Style.SELECTION_BG};
            }}
            QTreeView::item:hover:!selected {{
                background-color: #2a2d2e;
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(collapsed.png);
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(expanded.png);
            }}
        """)
        
        # 只显示文件名
        self.tree_view.setHeaderHidden(True)
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
        
        # 设置字体
        font = QFont()
        font.setFamily(Style.UI_FONT_FAMILY.split(',')[0].strip())
        font.setPointSize(Style.UI_FONT_SIZE)
        self.tree_view.setFont(font)
        
        # 添加到布局
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.tree_view)
        
        # 连接信号
        self.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        
    def on_file_double_clicked(self, index):
        # 获取文件路径
        file_path = self.model.filePath(index)
        
        # 如果是文件，则发出信号
        if os.path.isfile(file_path):
            # 这里可以发出信号，通知主窗口打开文件
            print(f"打开文件: {file_path}")
            
    def set_root_path(self, path):
        self.model.setRootPath(path)
        self.tree_view.setRootIndex(self.model.index(path))
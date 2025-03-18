from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import QDir, Qt, QModelIndex
import os

class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建搜索框
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件...")
        self.search_button = QPushButton("搜索")
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        
        # 创建树状视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
        
        # 只显示文件名
        self.tree_view.setHeaderHidden(True)
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
        
        # 添加到布局
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
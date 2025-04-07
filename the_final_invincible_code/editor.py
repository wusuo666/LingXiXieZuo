from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Editor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建编辑器
        self.text_edit = QPlainTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        
        # 添加到布局
        self.layout.addWidget(self.text_edit)
        
        # 设置初始内容
        self.text_edit.setPlainText("")
        
    def set_content(self, content):
        self.text_edit.setPlainText(content)
        
    def get_content(self):
        return self.text_edit.toPlainText()

class WelcomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 创建欢迎标签
        self.welcome_label = QLabel("欢迎使用灵犀协作")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 24px; color: #666;")
        
        # 添加到布局
        self.layout.addWidget(self.welcome_label)
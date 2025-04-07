from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextOption
from style import Style

class Editor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 创建编辑器
        self.text_edit = QPlainTextEdit()
        
        # 设置字体和颜色
        font = QFont()
        font.setFamily(Style.CODE_FONT_FAMILY.split(',')[0].strip())
        font.setPointSize(Style.CODE_FONT_SIZE)
        font.setFixedPitch(True)
        self.text_edit.setFont(font)
        
        # 设置编辑器样式
        self.text_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {Style.EDITOR_BG};
                color: {Style.TEXT_COLOR};
                border: none;
                selection-background-color: {Style.HIGHLIGHT_BG};
            }}
        """)
        
        # 设置行距和制表符宽度
        self.text_edit.setWordWrapMode(QTextOption.NoWrap)
        self.text_edit.setTabStopWidth(4 * self.text_edit.fontMetrics().width(' '))
        
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
        self.layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建欢迎标签
        self.welcome_label = QLabel("欢迎使用灵犀协作")
        self.welcome_label.setObjectName("welcome_label")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        
        # 创建副标题
        self.subtitle_label = QLabel("现代化的协作开发环境")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #858585; margin-top: 10px;")
        
        # 创建分隔线
        self.separator = QWidget()
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet(f"background-color: {Style.BORDER_COLOR}; margin: 20px 0px;")
        self.separator.setMaximumWidth(400)
        
        # 创建提示信息
        self.tip_label = QLabel("提示: 使用侧边栏文件浏览器打开文件，或创建新文件开始编辑")
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setStyleSheet("color: #858585; font-size: 12px;")
        
        # 添加到布局
        self.layout.addStretch(1)
        self.layout.addWidget(self.welcome_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addWidget(self.separator, 0, Qt.AlignCenter)
        self.layout.addWidget(self.tip_label)
        self.layout.addStretch(1)
        
        # 设置背景色
        self.setStyleSheet(f"background-color: {Style.EDITOR_BG};")
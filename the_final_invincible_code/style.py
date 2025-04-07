from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class Style:
    # 主题颜色 - 更新为更现代的VSCode风格
    DARK_BG = "#1e1e1e"  # 主背景色
    DARKER_BG = "#252526"  # 侧边栏背景色
    MENU_BG = "#333333"  # 菜单背景色
    HIGHLIGHT_BG = "#0e639c"  # 高亮背景色 - 更亮的蓝色
    SELECTION_BG = "#264f78"  # 选择背景色 - 更明显的选择色
    BORDER_COLOR = "#3d3d3d"  # 边框颜色 - 稍微亮一点
    ACCENT_COLOR = "#007acc"  # 强调色 - VSCode蓝
    
    # 文本颜色
    TEXT_COLOR = "#cccccc"  # 主文本颜色 - 稍微柔和一点
    INACTIVE_TEXT = "#8c8c8c"  # 非活动文本颜色
    HIGHLIGHT_TEXT = "#ffffff"  # 高亮文本颜色
    
    # 状态颜色
    ERROR_COLOR = "#f48771"  # 错误颜色
    WARNING_COLOR = "#cca700"  # 警告颜色
    SUCCESS_COLOR = "#89d185"  # 成功颜色
    INFO_COLOR = "#75beff"    # 信息颜色
    
    # 编辑器颜色
    EDITOR_BG = "#1e1e1e"  # 编辑器背景色
    LINE_NUMBER_COLOR = "#858585"  # 行号颜色
    CURRENT_LINE_BG = "#2c2c2c"  # 当前行背景色 - 稍微明显一点
    INDENT_GUIDE_COLOR = "#404040"  # 缩进指南颜色
    
    # 字体设置 - 增加字体大小和调整字体族
    CODE_FONT_FAMILY = "JetBrains Mono, Consolas, 'Courier New', monospace"
    CODE_FONT_SIZE = 11  # 增大代码字体
    UI_FONT_FAMILY = "Segoe UI, 'Microsoft YaHei UI', sans-serif"
    UI_FONT_SIZE = 10  # 增大UI字体
    
    @staticmethod
    def apply_dark_theme(app):
        """应用深色主题到整个应用"""
        # 创建深色调色板
        dark_palette = QPalette()
        
        # 设置颜色角色
        dark_palette.setColor(QPalette.Window, QColor(Style.DARK_BG))
        dark_palette.setColor(QPalette.WindowText, QColor(Style.TEXT_COLOR))
        dark_palette.setColor(QPalette.Base, QColor(Style.DARKER_BG))
        dark_palette.setColor(QPalette.AlternateBase, QColor(Style.DARK_BG))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(Style.DARK_BG))
        dark_palette.setColor(QPalette.ToolTipText, QColor(Style.TEXT_COLOR))
        dark_palette.setColor(QPalette.Text, QColor(Style.TEXT_COLOR))
        dark_palette.setColor(QPalette.Button, QColor(Style.DARK_BG))
        dark_palette.setColor(QPalette.ButtonText, QColor(Style.TEXT_COLOR))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor("#3794ff"))
        dark_palette.setColor(QPalette.Highlight, QColor(Style.HIGHLIGHT_BG))
        dark_palette.setColor(QPalette.HighlightedText, QColor(Style.HIGHLIGHT_TEXT))
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(Style.INACTIVE_TEXT))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(Style.INACTIVE_TEXT))
        
        # 应用调色板
        app.setPalette(dark_palette)
        
        # 设置应用字体
        app.setFont(QFont(Style.UI_FONT_FAMILY.split(',')[0].strip(), Style.UI_FONT_SIZE))
        
        # 设置应用样式表
        app.setStyleSheet("""
        /* 全局样式 */
        QWidget {
            background-color: #1e1e1e;
            color: #cccccc;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            font-size: 10pt;
            letter-spacing: 0.2px;
        }
        
        /* 菜单栏样式 */
        QMenuBar {
            background-color: #333333;
            color: #cccccc;
            border-bottom: 1px solid #3d3d3d;
            padding: 2px;
            spacing: 3px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 3px;
            margin: 1px 2px;
        }
        
        QMenuBar::item:selected {
            background-color: #505050;
        }
        
        QMenu {
            background-color: #252526;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            padding: 2px;
        }
        
        QMenu::item {
            padding: 6px 30px 6px 20px;
            border-radius: 2px;
            margin: 2px 4px;
        }
        
        QMenu::item:selected {
            background-color: #094771;
            color: #ffffff;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #3d3d3d;
            margin: 6px 4px;
        }
        
        /* 状态栏样式 */
        QStatusBar {
            background-color: #007acc;
            color: white;
            border-top: 1px solid #3d3d3d;
            padding: 2px 10px;
            font-size: 9pt;
        }
        
        /* 标签页样式 */
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #cccccc;
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            border: 1px solid #3d3d3d;
            border-bottom: none;
            min-width: 100px;
            margin-right: 2px;
            font-size: 10pt;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 2px solid #007acc;
            color: #ffffff;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #404040;
        }
        
        /* 侧边栏样式 */
        QTabWidget::tab-bar:left {
            alignment: left;
        }
        
        QTabWidget[tabPosition="West"] > QTabBar::tab {
            min-height: 36px;
            max-height: 36px;
            min-width: 36px;
            max-width: 36px;
            padding: 8px;
            margin: 4px 0px;
            border: none;
            border-left: 2px solid transparent;
            background-color: #252526;
            border-radius: 4px;
        }
        
        QTabWidget[tabPosition="West"] > QTabBar::tab:selected {
            border-left: 2px solid #007acc;
            background-color: #37373d;
        }
        
        QTabWidget[tabPosition="West"] > QTabBar::tab:hover:!selected {
            background-color: #2a2d2e;
        }
        
        QTabWidget[tabPosition="West"] > QTabBar {
            background-color: #252526;
            padding: 4px;
        }
        
        /* 树状视图样式 */
        QTreeView {
            background-color: #252526;
            border: none;
            outline: none;
            padding: 4px;
            font-size: 10pt;
        }
        
        QTreeView::item {
            padding: 6px;
            border: none;
            border-radius: 3px;
            margin: 1px 0px;
        }
        
        QTreeView::item:selected {
            background-color: #094771;
            color: #ffffff;
        }
        
        QTreeView::item:hover:!selected {
            background-color: #2a2d2e;
        }
        
        QTreeView::branch {
            background-color: transparent;
        }
        
        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {
            image: url(none);
            border-image: none;
        }
        
        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {
            image: url(none);
            border-image: none;
        }
        
        /* 编辑器样式 */
        QPlainTextEdit {
            background-color: #1e1e1e;
            color: #cccccc;
            border: none;
            border-radius: 2px;
            selection-background-color: #264f78;
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
            font-size: 11pt;
            line-height: 1.5;
            padding: 4px;
        }
        
        /* 按钮样式 */
        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            min-height: 24px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #1177bb;
        }
        
        QPushButton:pressed {
            background-color: #0e5384;
        }
        
        QPushButton:disabled {
            background-color: #3a3d41;
            color: #8c8c8c;
        }
        
        /* 输入框样式 */
        QLineEdit {
            background-color: #3c3c3c;
            color: #cccccc;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #264f78;
            font-size: 10pt;
            min-height: 20px;
        }
        
        /* 滚动条样式 */
        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            min-height: 30px;
            border-radius: 5px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #787878;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #1e1e1e;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #5a5a5a;
            min-width: 30px;
            border-radius: 5px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #787878;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* 分割器样式 */
        QSplitter::handle {
            background-color: #3d3d3d;
        }
        
        QSplitter::handle:horizontal {
            width: 1px;
            margin: 2px 0px;
        }
        
        QSplitter::handle:vertical {
            height: 1px;
            margin: 0px 2px;
        }
        
        /* 工具按钮样式 */
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 6px;
            color: #cccccc;
            border-radius: 3px;
            min-width: 24px;
            min-height: 24px;
        }
        
        QToolButton:hover {
            background-color: #3a3d41;
        }
        
        QToolButton:pressed {
            background-color: #094771;
            color: #ffffff;
        }
        
        /* 欢迎页样式 */
        QLabel#welcome_label {
            font-size: 24pt;
            color: #cccccc;
            font-weight: 300;
            letter-spacing: 0.5px;
        }
        """)
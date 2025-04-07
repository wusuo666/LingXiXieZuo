from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QToolButton, QMenu, QTabBar, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QMimeData, QPoint, QRect
from PyQt5.QtGui import QIcon, QDrag, QCursor
from editor import Editor

class SplitButton(QToolButton):
    """拆分按钮，用于在编辑器标签栏上显示拆分选项"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("⋮")
        self.setToolTip("拆分编辑器")
        self.setPopupMode(QToolButton.InstantPopup)
        
        # 创建菜单
        self.menu = QMenu(self)
        self.split_horizontal_action = self.menu.addAction("水平拆分")
        self.split_vertical_action = self.menu.addAction("垂直拆分")
        self.setMenu(self.menu)

class DraggableTabBar(QTabBar):
    """可拖拽的标签栏，用于实现标签页在不同编辑器容器之间的拖拽"""
    # 定义信号
    tab_drag_started = pyqtSignal(int, QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.drag_tab_index = -1
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setTabsClosable(True)
        self.setMovable(True)
    
    def mousePressEvent(self, event):
        """鼠标按下事件，记录拖拽起始位置和标签索引"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.drag_tab_index = self.tabAt(event.pos())
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，处理拖拽"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        # 如果没有有效的拖拽起始位置或标签索引，则返回
        if self.drag_start_pos is None or self.drag_tab_index < 0:
            return
        
        # 计算移动距离
        distance = (event.pos() - self.drag_start_pos).manhattanLength()
        
        # 增加校验：仅在拖拽距离超过阈值且未松开鼠标时触发拖拽
        if distance >= QApplication.startDragDistance():
            # 校验拖拽的目标位置是否有效
            target_pos = self.mapToGlobal(event.pos())
            if not self.parent().geometry().contains(self.parent().mapFromGlobal(target_pos)):
                return
            
            # 创建拖拽对象
            drag = QDrag(self)
            
            # 创建MIME数据
            mime_data = QMimeData()
            mime_data.setText(f"tab:{self.drag_tab_index}")
            drag.setMimeData(mime_data)
            
            # 发出拖拽开始信号
            self.tab_drag_started.emit(self.drag_tab_index, QCursor.pos())
            
            # 执行拖拽
            drag.exec_(Qt.MoveAction)
            
            # 重置拖拽状态
            self.drag_start_pos = None
            self.drag_tab_index = -1
        
        # 防止误触发其他逻辑
        super().mouseMoveEvent(event)

    def dropEvent(self, event):
        """拖拽放下事件"""
        # 如果是标签页拖拽，则接受
        if event.mimeData().hasText() and event.mimeData().text().startswith("tab:"):
            # 获取拖拽的标签索引
            drag_tab_index = int(event.mimeData().text().split(":")[1])
            # 获取放置的位置
            drop_index = self.tabAt(event.pos())
            if drop_index == -1:
                drop_index = self.count()
            # 发出信号通知父组件处理标签转移
            self.parent().window().on_tab_dragged(drag_tab_index, self.mapToGlobal(event.pos()))
            event.acceptProposedAction()

class EditorContainer(QWidget):
    """编辑器容器，用于管理拆分的编辑器"""
    # 定义信号
    split_requested = pyqtSignal(QWidget, Qt.Orientation)
    close_requested = pyqtSignal(QWidget)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 创建工具栏和标签页
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # 创建拆分按钮
        self.split_button = SplitButton()
        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.split_button)
        
        # 添加到布局
        self.layout.addLayout(self.toolbar_layout)
        self.layout.addWidget(self.tab_widget)
        
        # 设置接受拖放
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        
        # 连接信号
        self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.split_button.split_horizontal_action.triggered.connect(self.on_split_horizontal)
        self.split_button.split_vertical_action.triggered.connect(self.on_split_vertical)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith('tab:'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith('tab:'):
            tab_index = int(event.mimeData().text().split(':')[1])
            # 通过SplitEditorManager处理标签拖拽
            self.parent().window().on_tab_dragged(tab_index, self.mapToGlobal(event.pos()))
        
        # 创建工具栏
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # 创建拆分按钮
        self.split_button = SplitButton()
        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.split_button)
        
        # 添加到布局
        self.layout.addLayout(self.toolbar_layout)
        self.layout.addWidget(self.tab_widget)
        
        # 连接信号
        self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.split_button.split_horizontal_action.triggered.connect(self.on_split_horizontal)
        self.split_button.split_vertical_action.triggered.connect(self.on_split_vertical)
    
    def add_tab(self, widget, title):
        """添加标签页"""
        index = self.tab_widget.addTab(widget, title)
        return index
    
    def set_current_widget(self, widget):
        """设置当前标签页"""
        self.tab_widget.setCurrentWidget(widget)
    
    def on_tab_close_requested(self, index):
        """关闭标签页"""
        self.tab_widget.removeTab(index)
        
        # 如果没有标签页了，发出关闭信号
        if self.tab_widget.count() == 0:
            self.close_requested.emit(self)
    
    def on_split_horizontal(self):
        """水平拆分"""
        self.split_requested.emit(self, Qt.Horizontal)
    
    def on_split_vertical(self):
        """垂直拆分"""
        self.split_requested.emit(self, Qt.Vertical)
        


class SplitEditorManager(QSplitter):
    tabDragged = pyqtSignal(int, QPoint)
    """拆分编辑器管理器，用于管理所有拆分的编辑器容器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 创建主编辑器容器
        self.main_container = EditorContainer()
        self.layout.addWidget(self.main_container)
        
        # 创建可拖拽标签栏
        self.main_container.tab_widget.setTabBar(DraggableTabBar())
        self.main_container.tab_widget.tabBar().tab_drag_started.connect(self.on_tab_dragged)
        
        # 连接信号
        self.main_container.split_requested.connect(self.split_editor)
        self.main_container.close_requested.connect(self.close_editor)
        
        # 保存所有编辑器容器的引用
        self.containers = [self.main_container]
        
        # 保存所有拆分器的引用
        self.splitters = []
    
    def add_tab(self, widget, title):
        """添加标签页到当前活动的编辑器容器"""
        return self.main_container.add_tab(widget, title)
    
    def set_current_widget(self, widget):
        """设置当前标签页"""
        self.main_container.set_current_widget(widget)
    
    def split_editor(self, container, orientation):
        """拆分编辑器"""
        # 创建新的编辑器容器
        new_container = EditorContainer()
        new_container.split_requested.connect(self.split_editor)
        new_container.close_requested.connect(self.close_editor)
        
        # 创建可拖拽标签栏
        new_container.tab_widget.setTabBar(DraggableTabBar())
        new_container.tab_widget.tabBar().tab_drag_started.connect(self.on_tab_dragged)
        
        # 保存容器引用
        self.containers.append(new_container)
        
        # 获取容器的父部件
        parent = container.parent()
        
        # 如果父部件是拆分器
        if isinstance(parent, QSplitter):
            # 获取容器在拆分器中的索引
            index = parent.indexOf(container)
            
            # 如果拆分器的方向与请求的方向相同
            if parent.orientation() == orientation:
                # 直接在拆分器中添加新容器
                parent.insertWidget(index + 1, new_container)
            else:
                # 创建新的拆分器
                splitter = QSplitter(orientation)
                
                # 保存拆分器引用
                self.splitters.append(splitter)
                
                # 将容器从原拆分器中移除
                container.setParent(None)
                
                # 将容器和新容器添加到新拆分器中
                splitter.addWidget(container)
                splitter.addWidget(new_container)
                
                # 将新拆分器添加到原拆分器中
                parent.insertWidget(index, splitter)
        else:
            # 创建新的拆分器
            splitter = QSplitter(orientation)
            
            # 保存拆分器引用
            self.splitters.append(splitter)
            
            # 从布局中移除容器
            self.layout.removeWidget(container)
            
            # 将容器和新容器添加到拆分器中
            splitter.addWidget(container)
            splitter.addWidget(new_container)
            
            # 将拆分器添加到布局中
            self.layout.addWidget(splitter)
    
    def close_editor(self, container):
        """关闭编辑器容器"""
        # 如果只有一个容器，不允许关闭
        if len(self.containers) == 1:
            return
        
        # 从容器列表中移除
        self.containers.remove(container)
        
        # 获取容器的父部件
        parent = container.parent()
        
        # 如果父部件是拆分器
        if isinstance(parent, QSplitter):
            # 获取拆分器中的部件数量
            count = parent.count()
            
            # 如果拆分器中只有一个部件
            if count == 1:
                # 获取拆分器的父部件
                grandparent = parent.parent()
                
                # 如果祖父部件是拆分器
                if isinstance(grandparent, QSplitter):
                    # 获取拆分器在祖父拆分器中的索引
                    index = grandparent.indexOf(parent)
                    
                    # 从拆分器列表中移除
                    self.splitters.remove(parent)
                    
                    # 销毁拆分器
                    parent.setParent(None)
                    parent.deleteLater()
                else:
                    # 从拆分器列表中移除
                    self.splitters.remove(parent)
                    
                    # 从布局中移除拆分器
                    self.layout.removeWidget(parent)
                    
                    # 销毁拆分器
                    parent.setParent(None)
                    parent.deleteLater()
                    
                    # 将剩余的容器添加到布局中
                    self.layout.addWidget(self.containers[0])
            else:
                # 销毁容器
                container.setParent(None)
                container.deleteLater()
        else:
            # 销毁容器
            container.setParent(None)
            container.deleteLater()

    def on_tab_dragged(self, drag_tab_index, global_pos):
        """处理标签拖拽事件"""
        # 查找目标容器
        target_container = self.find_drop_container(global_pos)
        if target_container:
            # 获取源容器和标签内容
            src_container = self.find_tab_container(drag_tab_index)
            if src_container and src_container != target_container:  # 确保源和目标不同
                widget = src_container.tab_widget.widget(drag_tab_index)
                title = src_container.tab_widget.tabText(drag_tab_index)
                
                # 转移标签页
                src_container.tab_widget.removeTab(drag_tab_index)
                target_container.tab_widget.addTab(widget, title)
                target_container.tab_widget.setCurrentWidget(widget)
        else:
            # 如果未找到有效目标容器，忽略拖拽
            return

    def find_drop_container(self, global_pos):
        """根据全局坐标查找放置目标容器"""
        for container in self.containers:
            if container.geometry().contains(container.mapFromGlobal(global_pos)):
                return container
        return None

    def find_tab_container(self, tab_index):
        """查找包含指定标签索引的容器"""
        for container in self.containers:
            if tab_index < container.tab_widget.count():
                return container
        return None

    def find_parent_editor_container(self, widget):
        """向上查找EditorContainer父组件"""
        parent = widget.parent()
        while parent:
            if isinstance(parent, EditorContainer):
                return parent
            parent = parent.parent()
        return None

    def find_drop_container(self, global_pos):
        """改进的容器查找算法：考虑拆分器布局和可视化区域"""
        for container in reversed(self.containers):  # 从最上层开始查找
            # 转换坐标到容器坐标系
            local_rect = container.rect()
            global_rect = QRect(container.mapToGlobal(local_rect.topLeft()),
                              container.mapToGlobal(local_rect.bottomRight()))
            
            # 排除不可见或隐藏的容器
            if not container.isVisible() or global_rect.isEmpty():
                continue
            
            # 精确计算可拖放区域（标签栏+中央区域）
            tab_bar = container.tab_widget.tabBar()
            tab_bar_global_rect = QRect(tab_bar.mapToGlobal(tab_bar.rect().topLeft()),
                                      tab_bar.mapToGlobal(tab_bar.rect().bottomRight()))
            
            content_global_rect = QRect(container.mapToGlobal(QPoint(0, tab_bar.height())),
                                      container.mapToGlobal(QPoint(container.width(), container.height())))
            
            # 合并有效区域并检查坐标
            combined_rect = tab_bar_global_rect.united(content_global_rect)
            if combined_rect.contains(global_pos):
                return container
        return None
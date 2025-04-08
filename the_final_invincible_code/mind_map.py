from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem, QMenu, QInputDialog, QFileDialog, QMessageBox, QToolBar, QAction, QComboBox, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSizeF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QIcon, QPainter
import json
import os
from interaction_point import InteractionPoint

class MindMapNode:
    def __init__(self, text, pos, width=120, height=80, parent=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.text = text
        self.parent_node = None
        self.child_nodes = []
        self.lines = []
        self.shape_item = None
        self.text_item = None
        self.interaction_points = []
    
    def add_child(self, child_node):
        self.child_nodes.append(child_node)
        child_node.parent_node = self
    
    def add_line(self, line):
        self.lines.append(line)
    
    def get_data(self):
        # 返回节点数据用于保存
        data = {
            "text": self.text,
            "pos": {"x": self.pos.x(), "y": self.pos.y()},
            "width": self.width,
            "height": self.height,
            "shape_type": self.get_shape_type(),
            "children": []
        }
        for child in self.child_nodes:
            data["children"].append(child.get_data())
        return data
    
    def get_shape_type(self):
        return "base"

class EllipseNode(MindMapNode):
    def __init__(self, text, pos, width=120, height=80, parent=None):
        super().__init__(text, pos, width, height, parent)
        self.shape_item = QGraphicsEllipseItem(-width/2, -height/2, width, height)
        self.shape_item.setPos(pos)
        self.shape_item.setBrush(QBrush(QColor(255, 255, 200)))
        self.shape_item.setPen(QPen(Qt.black, 2))
        self.shape_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.shape_item.setFlag(QGraphicsItem.ItemIsSelectable)
        self.shape_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # 添加文字
        self.text_item = QGraphicsTextItem(text, self.shape_item)
        self.text_item.setPos(-width/2 + 10, -height/2 + 10)
        self.text_item.setFont(QFont("Arial", 10))
        
        # 存储原始对象的引用，用于事件处理
        self.shape_item.node = self
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.shape_item.scene():
            # 更新连接线的位置
            for line in self.lines:
                line.update_position()
        return value
    
    def get_shape_type(self):
        return "ellipse"

class RectNode(MindMapNode):
    def __init__(self, text, pos, width=120, height=80, parent=None):
        super().__init__(text, pos, width, height, parent)
        self.shape_item = QGraphicsRectItem(-width/2, -height/2, width, height)
        self.shape_item.setPos(pos)
        self.shape_item.setBrush(QBrush(QColor(200, 255, 200)))
        self.shape_item.setPen(QPen(Qt.black, 2))
        self.shape_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.shape_item.setFlag(QGraphicsItem.ItemIsSelectable)
        self.shape_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # 添加文字
        self.text_item = QGraphicsTextItem(text, self.shape_item)
        self.text_item.setPos(-width/2 + 10, -height/2 + 10)
        self.text_item.setFont(QFont("Arial", 10))
        
        # 存储原始对象的引用，用于事件处理
        self.shape_item.node = self
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.shape_item.scene():
            # 更新连接线的位置
            for line in self.lines:
                line.update_position()
        return value
    
    def get_shape_type(self):
        return "rect"

class MindMapLine(QGraphicsLineItem):
    def __init__(self, start_node, end_node, parent=None):
        super().__init__(parent)
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.black, 2))
        self.update_position()
        
        # 将线添加到节点
        start_node.add_line(self)
        end_node.add_line(self)
    
    def update_position(self):
        # 更新线的位置
        if hasattr(self.start_node, 'shape_item'):
            start_pos = self.start_node.shape_item.pos()
        else:
            start_pos = self.start_node.pos()
            
        if hasattr(self.end_node, 'shape_item'):
            end_pos = self.end_node.shape_item.pos()
        else:
            end_pos = self.end_node.pos()
            
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        
    def get_data(self):
        # 返回连线数据用于保存
        return {
            "start_node_id": id(self.start_node),
            "end_node_id": id(self.end_node)
        }

class FreeText(QGraphicsTextItem):
    def __init__(self, text, pos, parent=None):
        super().__init__(text, parent)
        self.setPos(pos)
        self.setFont(QFont("Arial", 10))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        
    def get_data(self):
        # 返回文本数据用于保存
        return {
            "text": self.toPlainText(),
            "pos": {"x": self.pos().x(), "y": self.pos().y()}
        }

class MindMap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 当前操作模式
        self.current_mode = "select"
        self.current_shape = "ellipse"
        self.node_width = 120
        self.node_height = 80
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建图形视图和场景
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.layout.addWidget(self.view)
        
        # 设置初始节点
        self.root_node = None
        self.create_root_node("中心主题")
        
        # 当前选中的节点
        self.selected_node = None
        
        # 文件路径
        self.current_file_path = None
        
        # 存储所有节点、连线和文本
        self.nodes = []
        self.lines = []
        self.texts = []
        
        # 连接事件
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
        
    def create_toolbar(self):
        # 创建工具栏
        self.toolbar = QToolBar()
        
        # 模式选择
        self.select_action = QAction("选择", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.select_action.triggered.connect(lambda: self.set_mode("select"))
        self.toolbar.addAction(self.select_action)
        
        self.node_action = QAction("创建节点", self)
        self.node_action.setCheckable(True)
        self.node_action.triggered.connect(lambda: self.set_mode("node"))
        self.toolbar.addAction(self.node_action)
        
        self.line_action = QAction("创建连线", self)
        self.line_action.setCheckable(True)
        self.line_action.triggered.connect(lambda: self.set_mode("line"))
        self.toolbar.addAction(self.line_action)
        
        self.text_action = QAction("添加文本", self)
        self.text_action.setCheckable(True)
        self.text_action.triggered.connect(lambda: self.set_mode("text"))
        self.toolbar.addAction(self.text_action)
        
        self.toolbar.addSeparator()
        
        # 形状选择
        shape_label = QLabel("形状: ")
        self.toolbar.addWidget(shape_label)
        
        self.shape_combo = QComboBox()
        self.shape_combo.addItem("椭圆形")
        self.shape_combo.addItem("矩形")
        self.shape_combo.currentIndexChanged.connect(self.shape_changed)
        self.toolbar.addWidget(self.shape_combo)
        
        self.toolbar.addSeparator()
        
        # 节点大小
        size_label = QLabel("大小: ")
        self.toolbar.addWidget(size_label)
        
        width_label = QLabel("宽度:")
        self.toolbar.addWidget(width_label)
        
        self.width_combo = QComboBox()
        for size in [80, 100, 120, 150, 200]:
            self.width_combo.addItem(str(size))
        self.width_combo.setCurrentText("120")
        self.width_combo.currentTextChanged.connect(self.size_changed)
        self.toolbar.addWidget(self.width_combo)
        
        height_label = QLabel("高度:")
        self.toolbar.addWidget(height_label)
        
        self.height_combo = QComboBox()
        for size in [60, 80, 100, 120, 150]:
            self.height_combo.addItem(str(size))
        self.height_combo.setCurrentText("80")
        self.height_combo.currentTextChanged.connect(self.size_changed)
        self.toolbar.addWidget(self.height_combo)
        
        self.toolbar.addSeparator()
        
        # 节点操作
        self.add_child_action = QAction("添加子节点", self)
        self.add_child_action.triggered.connect(self.add_child_node)
        self.toolbar.addAction(self.add_child_action)
        
        self.edit_action = QAction("编辑节点", self)
        self.edit_action.triggered.connect(self.edit_node)
        self.toolbar.addAction(self.edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_item)
        self.toolbar.addAction(self.delete_action)
        
        self.toolbar.addSeparator()
        
        # 文件操作
        self.save_action = QAction("保存", self)
        self.save_action.triggered.connect(self.save_mind_map)
        self.toolbar.addAction(self.save_action)
        
        self.load_action = QAction("加载", self)
        self.load_action.triggered.connect(self.load_mind_map)
        self.toolbar.addAction(self.load_action)
        
        self.layout.addWidget(self.toolbar)
        
    def set_mode(self, mode):
        self.current_mode = mode
        
        # 更新按钮状态
        self.select_action.setChecked(mode == "select")
        self.node_action.setChecked(mode == "node")
        self.line_action.setChecked(mode == "line")
        self.text_action.setChecked(mode == "text")
        
        # 更新鼠标样式
        if mode == "select":
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)
    
    def shape_changed(self, index):
        if index == 0:
            self.current_shape = "ellipse"
        else:
            self.current_shape = "rect"
    
    def size_changed(self):
        try:
            self.node_width = int(self.width_combo.currentText())
            self.node_height = int(self.height_combo.currentText())
        except ValueError:
            pass
    
    def create_root_node(self, text):
        # 创建根节点
        self.scene.clear()
        self.nodes = []
        self.lines = []
        self.texts = []
        
        if self.current_shape == "ellipse":
            self.root_node = EllipseNode(text, QPointF(0, 0), self.node_width, self.node_height)
        else:
            self.root_node = RectNode(text, QPointF(0, 0), self.node_width, self.node_height)
            
        self.scene.addItem(self.root_node.shape_item)
        self.nodes.append(self.root_node)
        
        # 添加交互点
        self.update_interaction_points(self.root_node)
        
        self.view.centerOn(self.root_node.shape_item)
        return self.root_node
    
    def create_node(self, text, pos, parent_node=None):
        # 创建节点
        if self.current_shape == "ellipse":
            node = EllipseNode(text, pos, self.node_width, self.node_height)
        else:
            node = RectNode(text, pos, self.node_width, self.node_height)
            
        self.scene.addItem(node.shape_item)
        self.nodes.append(node)
        
        # 添加交互点
        self.update_interaction_points(node)
        
        # 如果有父节点，创建连接线并建立关系
        if parent_node:
            parent_node.add_child(node)
            line = MindMapLine(parent_node, node)
            self.scene.addItem(line)
            self.lines.append(line)
        
        return node
        
    def create_free_node(self, pos):
        # 创建独立节点（不与其他节点相连）
        text, ok = QInputDialog.getText(self, "创建节点", "请输入节点内容:")
        if ok and text:
            node = self.create_node(text, pos)
            return node
        return None
        
    def create_free_text(self, pos):
        # 创建独立文本
        text, ok = QInputDialog.getText(self, "添加文本", "请输入文本内容:")
        if ok and text:
            text_item = FreeText(text, pos)
            self.scene.addItem(text_item)
            self.texts.append(text_item)
            return text_item
        return None
        
    def create_line(self, start_node, end_node):
        # 创建连接线
        line = MindMapLine(start_node, end_node)
        self.scene.addItem(line)
        self.lines.append(line)
        return line
        
    def update_interaction_points(self, node):
        # 清除旧的交互点
        scene = None
        for point in node.interaction_points:
            try:
                if point.scene():
                    scene = point.scene()
                    scene.removeItem(point)
            except RuntimeError:
                # 对象可能已被删除，忽略错误
                pass
        node.interaction_points.clear()
        
        # 添加新的交互点
        # 四角添加调整大小的交互点
        resize_positions = ['top_left', 'top_right', 'bottom_right', 'bottom_left']
        for pos in resize_positions:
            point = InteractionPoint(node, pos, InteractionPoint.RESIZE, node.shape_item)
            node.interaction_points.append(point)
        
        # 四边中点添加连接线的交互点
        connect_positions = ['top', 'right', 'bottom', 'left']
        for pos in connect_positions:
            point = InteractionPoint(node, pos, InteractionPoint.CONNECT, node.shape_item)
            node.interaction_points.append(point)
    
    def add_child_node(self):
        # 添加子节点
        items = self.scene.selectedItems()
        if items:
            item = items[0]
            # 检查是否是节点的形状项
            if hasattr(item, 'node'):
                parent_node = item.node
                # 计算新节点位置
                offset_x = 150
                offset_y = len(parent_node.child_nodes) * 80
                if len(parent_node.child_nodes) % 2 == 0:
                    offset_y = -offset_y
                new_pos = QPointF(parent_node.shape_item.pos().x() + offset_x, 
                                 parent_node.shape_item.pos().y() + offset_y)
                
                # 创建新节点
                text, ok = QInputDialog.getText(self, "添加子节点", "请输入节点内容:")
                if ok and text:
                    self.create_node(text, new_pos, parent_node)
    
    def edit_node(self):
        # 编辑节点或文本
        items = self.scene.selectedItems()
        if items:
            item = items[0]
            
            # 如果是节点
            if hasattr(item, 'node'):
                node = item.node
                text, ok = QInputDialog.getText(self, "编辑节点", "请输入节点内容:", text=node.text)
                if ok and text:
                    node.text = text
                    node.text_item.setPlainText(text)
            # 如果是独立文本
            elif isinstance(item, FreeText):
                text, ok = QInputDialog.getText(self, "编辑文本", "请输入文本内容:", text=item.toPlainText())
                if ok and text:
                    item.setPlainText(text)
    
    def delete_item(self):
        # 删除选中的项（节点、连线或文本）
        items = self.scene.selectedItems()
        if items:
            item = items[0]
            
            # 如果是节点
            if hasattr(item, 'node'):
                node = item.node
                if node != self.root_node:
                    self.delete_node(node)
            # 如果是连线
            elif isinstance(item, QGraphicsLineItem):
                # 从节点中移除连线
                for line in self.lines:
                    if line == item:
                        if line in line.start_node.lines:
                            line.start_node.lines.remove(line)
                        if line in line.end_node.lines:
                            line.end_node.lines.remove(line)
                        self.scene.removeItem(line)
                        self.lines.remove(line)
                        break
            # 如果是文本
            elif isinstance(item, FreeText):
                self.scene.removeItem(item)
                if item in self.texts:
                    self.texts.remove(item)
    
    def delete_node(self, node):
        # 删除节点
        # 递归删除子节点
        for child in node.child_nodes.copy():
            self.delete_node(child)
        
        # 删除连接线
        for line in node.lines.copy():
            if line in self.lines:
                self.lines.remove(line)
            self.scene.removeItem(line)
        
        # 从父节点中移除
        if node.parent_node:
            node.parent_node.child_nodes.remove(node)
        
        # 从节点列表中移除
        if node in self.nodes:
            self.nodes.remove(node)
        
        # 删除节点
        self.scene.removeItem(node.shape_item)
        item.start_node.lines.remove(line)
    
    def mousePressEvent(self, event):
        # 处理鼠标按下事件
        if event.button() == Qt.LeftButton:
            # 获取场景坐标
            scene_pos = self.view.mapToScene(event.pos())
            items = self.scene.items(scene_pos)
            
            # 根据当前模式处理
            if self.current_mode == "node":
                # 创建独立节点
                self.create_free_node(scene_pos)
            elif self.current_mode == "text":
                # 创建独立文本
                self.create_free_text(scene_pos)
            elif self.current_mode == "line":
                # 检查是否点击了交互点
                for item in items:
                    if isinstance(item, InteractionPoint) and item.point_type == InteractionPoint.CONNECT:
                        self.line_start_node = item.parent_node
                        self.line_start_point = item
                        return
                
                # 如果没有点击交互点，检查是否点击了节点
                for item in items:
                    if hasattr(item, 'node'):
                        self.line_start_node = item.node
                        self.line_start_point = None
                        return
            elif self.current_mode == "select":
                # 检查是否点击了调整大小的交互点
                for item in items:
                    if isinstance(item, InteractionPoint) and item.point_type == InteractionPoint.RESIZE:
                        self.resize_node = item.parent_node
                        self.resize_point = item
                        self.resize_start_pos = scene_pos
                        self.resize_start_width = item.parent_node.width
                        self.resize_start_height = item.parent_node.height
                        return
        
        # 调用父类方法
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        # 处理鼠标移动事件
        if hasattr(self, 'resize_node') and hasattr(self, 'resize_point'):
            # 调整节点大小
            scene_pos = self.view.mapToScene(event.pos())
            node = self.resize_node
            point = self.resize_point
            
            # 计算大小变化
            dx = scene_pos.x() - self.resize_start_pos.x()
            dy = scene_pos.y() - self.resize_start_pos.y()
            
            # 根据交互点位置调整大小
            new_width = self.resize_start_width
            new_height = self.resize_start_height
            
            if point.position in ["top_right", "bottom_right"]:
                new_width = max(60, self.resize_start_width + dx * 2)
            if point.position in ["top_left", "bottom_left"]:
                new_width = max(60, self.resize_start_width - dx * 2)
            if point.position in ["bottom_left", "bottom_right"]:
                new_height = max(40, self.resize_start_height + dy * 2)
            if point.position in ["top_left", "top_right"]:
                new_height = max(40, self.resize_start_height - dy * 2)
            
            # 更新节点大小
            if new_width != node.width or new_height != node.height:
                # 保存原始位置
                pos = node.shape_item.pos()
                
                # 移除旧形状
                scene = node.shape_item.scene()
                if scene:
                    scene.removeItem(node.shape_item)
                
                # 创建新形状
                node.width = new_width
                node.height = new_height
                
                if isinstance(node, EllipseNode):
                    node.shape_item = QGraphicsEllipseItem(-new_width/2, -new_height/2, new_width, new_height)
                else:  # RectNode
                    node.shape_item = QGraphicsRectItem(-new_width/2, -new_height/2, new_width, new_height)
                
                # 设置属性
                node.shape_item.setPos(pos)
                if isinstance(node, EllipseNode):
                    node.shape_item.setBrush(QBrush(QColor(255, 255, 200)))
                else:  # RectNode
                    node.shape_item.setBrush(QBrush(QColor(200, 255, 200)))
                node.shape_item.setPen(QPen(Qt.black, 2))
                node.shape_item.setFlag(QGraphicsItem.ItemIsMovable)
                node.shape_item.setFlag(QGraphicsItem.ItemIsSelectable)
                node.shape_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
                
                # 重新添加文字
                node.text_item = QGraphicsTextItem(node.text, node.shape_item)
                node.text_item.setPos(-new_width/2 + 10, -new_height/2 + 10)
                node.text_item.setFont(QFont("Arial", 10))
                
                # 存储原始对象的引用
                node.shape_item.node = node
                
                # 添加到场景
                scene.addItem(node.shape_item)
                
                # 更新交互点
                self.update_interaction_points(node)
                
                # 更新连接线
                for line in node.lines:
                    line.update_position()
            
            return
        
        # 调用父类方法
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        # 处理鼠标释放事件
        if event.button() == Qt.LeftButton:
            # 处理连线创建
            if self.current_mode == "line" and hasattr(self, 'line_start_node'):
                # 获取场景坐标
                scene_pos = self.view.mapToScene(event.pos())
                items = self.scene.items(scene_pos)
                
                # 检查是否释放在交互点上
                for item in items:
                    if isinstance(item, InteractionPoint) and item.point_type == InteractionPoint.CONNECT:
                        if item.parent_node != self.line_start_node:
                            # 创建连线
                            self.create_line(self.line_start_node, item.parent_node)
                            # 清除临时变量
                            delattr(self, 'line_start_node')
                            if hasattr(self, 'line_start_point'):
                                delattr(self, 'line_start_point')
                            return
                
                # 如果没有释放在交互点上，检查是否释放在节点上
                for item in items:
                    if hasattr(item, 'node') and item.node != self.line_start_node:
                        # 创建连线
                        self.create_line(self.line_start_node, item.node)
                        # 清除临时变量
                        delattr(self, 'line_start_node')
                        if hasattr(self, 'line_start_point'):
                            delattr(self, 'line_start_point')
                        return
                
                # 如果没有释放在有效目标上，清除临时变量
                if hasattr(self, 'line_start_node'):
                    delattr(self, 'line_start_node')
                if hasattr(self, 'line_start_point'):
                    delattr(self, 'line_start_point')
            
            # 处理调整大小
            if hasattr(self, 'resize_node'):
                delattr(self, 'resize_node')
            if hasattr(self, 'resize_point'):
                delattr(self, 'resize_point')
            if hasattr(self, 'resize_start_pos'):
                delattr(self, 'resize_start_pos')
            if hasattr(self, 'resize_start_width'):
                delattr(self, 'resize_start_width')
            if hasattr(self, 'resize_start_height'):
                delattr(self, 'resize_start_height')
        
        # 调用父类方法
        super().mouseReleaseEvent(event)
    
    def show_context_menu(self, pos):
        # 显示上下文菜单
        scene_pos = self.view.mapToScene(pos)
        items = self.scene.items(scene_pos)
        
        menu = QMenu(self)
        
        if items:
            item = items[0]
            # 节点菜单
            if hasattr(item, 'node'):
                node = item.node
                add_action = menu.addAction("添加子节点")
                edit_action = menu.addAction("编辑节点")
                delete_action = None
                if node != self.root_node:
                    delete_action = menu.addAction("删除节点")
                
                action = menu.exec_(self.view.mapToGlobal(pos))
                
                if action == add_action:
                    item.setSelected(True)
                    self.add_child_node()
                elif action == edit_action:
                    item.setSelected(True)
                    self.edit_node()
                elif delete_action and action == delete_action:
                    item.setSelected(True)
                    self.delete_item()
            # 文本菜单
            elif isinstance(item, FreeText):
                edit_action = menu.addAction("编辑文本")
                delete_action = menu.addAction("删除文本")
                
                action = menu.exec_(self.view.mapToGlobal(pos))
                
                if action == edit_action:
                    item.setSelected(True)
                    self.edit_node()
                elif action == delete_action:
                    item.setSelected(True)
                    self.delete_item()
            # 连线菜单
            elif isinstance(item, QGraphicsLineItem):
                delete_action = menu.addAction("删除连线")
                
                action = menu.exec_(self.view.mapToGlobal(pos))
                
                if action == delete_action:
                    item.setSelected(True)
                    self.delete_item()
        else:
            # 空白区域菜单
            new_map_action = menu.addAction("新建思维导图")
            add_node_action = menu.addAction("添加节点")
            add_text_action = menu.addAction("添加文本")
            
            action = menu.exec_(self.view.mapToGlobal(pos))
            
            if action == new_map_action:
                text, ok = QInputDialog.getText(self, "新建思维导图", "请输入中心主题:")
                if ok and text:
                    self.create_root_node(text)
            elif action == add_node_action:
                self.create_free_node(scene_pos)
            elif action == add_text_action:
                self.create_free_text(scene_pos)
    
    def save_mind_map(self):
        # 保存思维导图
        if not self.root_node:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存思维导图", "", "思维导图文件 (*.mindmap)")
        if file_path:
            try:
                # 准备数据
                data = {
                    "root": self.root_node.get_data(),
                    "nodes": [],
                    "texts": [],
                    "node_id_map": {}
                }
                
                # 保存独立节点（非根节点及其子节点）
                for node in self.nodes:
                    if node != self.root_node and not node.parent_node:
                        data["nodes"].append(node.get_data())
                
                # 保存独立文本
                for text in self.texts:
                    data["texts"].append(text.get_data())
                
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.current_file_path = file_path
                QMessageBox.information(self, "保存成功", "思维导图已保存。")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存思维导图时出错: {str(e)}")
    
    def load_mind_map(self):
        # 加载思维导图
        file_path, _ = QFileDialog.getOpenFileName(self, "加载思维导图", "", "思维导图文件 (*.mindmap)")
        if file_path:
            try:
                # 从文件加载数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 清除场景
                self.scene.clear()
                self.nodes = []
                self.lines = []
                self.texts = []
                
                # 加载根节点及其子节点
                if "root" in data:
                    self.load_node_recursive(data["root"], None)
                
                # 加载独立节点
                if "nodes" in data:
                    for node_data in data["nodes"]:
                        self.load_node_data(node_data)
                
                # 加载独立文本
                if "texts" in data:
                    for text_data in data["texts"]:
                        pos = QPointF(text_data["pos"]["x"], text_data["pos"]["y"])
                        text_item = FreeText(text_data["text"], pos)
                        self.scene.addItem(text_item)
                        self.texts.append(text_item)
                
                self.current_file_path = file_path
                if self.root_node:
                    self.view.centerOn(self.root_node.shape_item)
            except Exception as e:
                QMessageBox.critical(self, "加载失败", f"加载思维导图时出错: {str(e)}")
    
    def load_node_recursive(self, data, parent_node):
        # 递归加载节点
        pos = QPointF(data["pos"]["x"], data["pos"]["y"])
        width = data.get("width", 120)
        height = data.get("height", 80)
        shape_type = data.get("shape_type", "ellipse")
        
        # 根据形状类型创建节点
        if shape_type == "rect":
            node = RectNode(data["text"], pos, width, height)
        else:  # 默认为椭圆
            node = EllipseNode(data["text"], pos, width, height)
        
        self.scene.addItem(node.shape_item)
        self.nodes.append(node)
        
        # 添加交互点
        self.update_interaction_points(node)
        
        # 如果有父节点，创建连接线并建立关系
        if parent_node:
            parent_node.add_child(node)
            line = MindMapLine(parent_node, node)
            self.scene.addItem(line)
            self.lines.append(line)
        else:
            # 如果是根节点
            self.root_node = node
        
        # 加载子节点
        for child_data in data["children"]:
            self.load_node_recursive(child_data, node)
        
        return node
    
    def load_node_data(self, data):
        # 加载独立节点数据
        pos = QPointF(data["pos"]["x"], data["pos"]["y"])
        width = data.get("width", 120)
        height = data.get("height", 80)
        shape_type = data.get("shape_type", "ellipse")
        
        # 根据形状类型创建节点
        if shape_type == "rect":
            node = RectNode(data["text"], pos, width, height)
        else:  # 默认为椭圆
            node = EllipseNode(data["text"], pos, width, height)
        
        self.scene.addItem(node.shape_item)
        self.nodes.append(node)
        
        # 添加交互点
        self.update_interaction_points(node)
        
        # 加载子节点
        for child_data in data["children"]:
            child = self.load_node_recursive(child_data, node)
        
        return node
    
    def resize_node_to(self, node, new_width, new_height):
        # 保存原始位置
        pos = node.shape_item.pos()
        
        # 移除旧形状
        scene = node.shape_item.scene()
        if scene:
            scene.removeItem(node.shape_item)
        
        # 创建新形状
        node.width = new_width
        node.height = new_height
        
        if isinstance(node, EllipseNode):
            node.shape_item = QGraphicsEllipseItem(-new_width/2, -new_height/2, new_width, new_height)
        else:  # RectNode
            node.shape_item = QGraphicsRectItem(-new_width/2, -new_height/2, new_width, new_height)
        
        # 设置属性
        node.shape_item.setPos(pos)
        if isinstance(node, EllipseNode):
            node.shape_item.setBrush(QBrush(QColor(255, 255, 200)))
        else:  # RectNode
            node.shape_item.setBrush(QBrush(QColor(200, 255, 200)))
        node.shape_item.setPen(QPen(Qt.black, 2))
        node.shape_item.setFlag(QGraphicsItem.ItemIsMovable)
        node.shape_item.setFlag(QGraphicsItem.ItemIsSelectable)
        node.shape_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # 重新添加文字
        node.text_item = QGraphicsTextItem(node.text, node.shape_item)
        node.text_item.setPos(-new_width/2 + 10, -new_height/2 + 10)
        node.text_item.setFont(QFont("Arial", 10))
        
        # 存储原始对象的引用
        node.shape_item.node = node
        
        # 添加到场景
        scene.addItem(node.shape_item)
        
        # 更新交互点
        self.update_interaction_points(node)
        
        # 更新连接线
        for line in node.lines:
            line.update_position()
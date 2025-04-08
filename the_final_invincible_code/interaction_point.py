from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QCursor

class InteractionPoint(QGraphicsEllipseItem):
    # 交互点类型常量
    RESIZE = 0  # 调整大小的交互点
    CONNECT = 1  # 连接线的交互点
    
    def __init__(self, parent_node, position, point_type, parent=None):
        """
        创建交互点
        :param parent_node: 所属的节点
        :param position: 位置标识，如 'top_left', 'top', 'top_right' 等
        :param point_type: 交互点类型，RESIZE 或 CONNECT
        :param parent: 父图形项
        """
        # 交互点大小
        size = 8
        super().__init__(-size/2, -size/2, size, size, parent)
        
        self.parent_node = parent_node
        self.position = position
        self.point_type = point_type
        self.dragging = False
        self.start_pos = None
        
        # 设置外观
        if point_type == InteractionPoint.RESIZE:
            self.setBrush(QBrush(QColor(255, 0, 0)))  # 调整大小点为红色
        else:  # CONNECT
            self.setBrush(QBrush(QColor(0, 0, 255)))  # 连接点为蓝色
        
        self.setPen(QPen(Qt.black, 1))
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # 更新位置
        self.update_position()
    
    def update_position(self):
        """
        根据节点的大小和位置更新交互点的位置
        """
        node = self.parent_node
        width = node.width
        height = node.height
        
        # 根据位置标识设置交互点位置
        if self.position == 'top_left':
            self.setPos(-width/2, -height/2)
        elif self.position == 'top':
            self.setPos(0, -height/2)
        elif self.position == 'top_right':
            self.setPos(width/2, -height/2)
        elif self.position == 'right':
            self.setPos(width/2, 0)
        elif self.position == 'bottom_right':
            self.setPos(width/2, height/2)
        elif self.position == 'bottom':
            self.setPos(0, height/2)
        elif self.position == 'bottom_left':
            self.setPos(-width/2, height/2)
        elif self.position == 'left':
            self.setPos(-width/2, 0)
    
    def hoverEnterEvent(self, event):
        """鼠标悬停在交互点上时的事件处理"""
        # 改变鼠标样式
        if self.point_type == InteractionPoint.RESIZE:
            # 根据位置设置不同的调整大小光标
            if self.position in ['top_left', 'bottom_right']:
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            elif self.position in ['top_right', 'bottom_left']:
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
            else:
                self.setCursor(QCursor(Qt.SizeAllCursor))
        else:  # CONNECT
            self.setCursor(QCursor(Qt.CrossCursor))
        
        # 高亮显示
        self.setPen(QPen(Qt.white, 2))
        
        # 调用父类方法
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开交互点时的事件处理"""
        # 恢复鼠标样式
        self.unsetCursor()
        
        # 恢复外观
        self.setPen(QPen(Qt.black, 1))
        
        # 调用父类方法
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下交互点时的事件处理"""
        # 高亮显示
        self.setPen(QPen(Qt.yellow, 2))
        
        # 设置拖拽状态
        self.dragging = True
        self.start_pos = event.scenePos()
        
        # 调用父类方法
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动交互点时的事件处理"""
        if not self.dragging:
            # 如果没有拖拽状态，直接调用父类方法
            super().mouseMoveEvent(event)
            return
            
        try:
            # 获取场景中的MindMap对象
            scene = self.scene()
            if not scene or not scene.views():
                return
                
            view = scene.views()[0]
            if not view or not hasattr(view, 'parent') or not view.parent():
                return
                
            mind_map = view.parent()
            
            if self.point_type == InteractionPoint.RESIZE:
                # 调整大小
                current_pos = event.scenePos()
                dx = current_pos.x() - self.start_pos.x()
                dy = current_pos.y() - self.start_pos.y()
                
                # 设置调整大小的参数
                if not hasattr(mind_map, 'resize_node'):
                    mind_map.resize_node = self.parent_node
                    mind_map.resize_point = self
                    mind_map.resize_start_pos = self.start_pos
                    mind_map.resize_start_width = self.parent_node.width
                    mind_map.resize_start_height = self.parent_node.height
                
                # 根据交互点位置调整大小
                new_width = mind_map.resize_start_width
                new_height = mind_map.resize_start_height
                
                if self.position in ["top_right", "bottom_right"]:
                    new_width = max(60, mind_map.resize_start_width + dx * 2)
                if self.position in ["top_left", "bottom_left"]:
                    new_width = max(60, mind_map.resize_start_width - dx * 2)
                if self.position in ["bottom_left", "bottom_right"]:
                    new_height = max(40, mind_map.resize_start_height + dy * 2)
                if self.position in ["top_left", "top_right"]:
                    new_height = max(40, mind_map.resize_start_height - dy * 2)
                
                # 更新节点大小
                node = self.parent_node
                if new_width != node.width or new_height != node.height:
                    # 保存当前对象的引用，防止在resize_node_to过程中被删除
                    mind_map.current_interaction_point = self
                    # 调用resize_node_to方法调整节点大小
                    mind_map.resize_node_to(node, new_width, new_height)
                    # 不再继续处理事件，但保持拖拽状态
                    # 注意：不再重置dragging状态，以便继续调整大小
                    return
            elif self.point_type == InteractionPoint.CONNECT:
                # 连线模式
                if not hasattr(mind_map, 'line_start_node'):
                    mind_map.line_start_node = self.parent_node
                    mind_map.line_start_point = self
                    
                # 如果是连接点，可以显示临时连线以提供视觉反馈
                if hasattr(mind_map, 'temp_line'):
                    # 更新临时连线
                    start_pos = self.parent_node.shape_item.pos()
                    end_pos = event.scenePos()
                    mind_map.temp_line.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
                else:
                    # 创建临时连线
                    start_pos = self.parent_node.shape_item.pos()
                    end_pos = event.scenePos()
                    temp_line = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
                    temp_line.setPen(QPen(Qt.DashLine))
                    scene.addItem(temp_line)
                    mind_map.temp_line = temp_line
        except RuntimeError:
            # 对象可能已被删除，忽略错误
            self.dragging = False
            return
        
        # 如果没有特殊处理，调用父类方法
        try:
            super().mouseMoveEvent(event)
        except RuntimeError:
            # 忽略可能的运行时错误
            pass
    
    def mouseReleaseEvent(self, event):
        """鼠标释放交互点时的事件处理"""
        try:
            # 恢复外观，但保持高亮（因为鼠标可能仍在其上）
            self.setPen(QPen(Qt.white, 2))
            
            # 重置拖拽状态
            self.dragging = False
            self.start_pos = None
            
            # 调用父类方法
            super().mouseReleaseEvent(event)
        except RuntimeError:
            # 对象可能已被删除，忽略错误
            pass
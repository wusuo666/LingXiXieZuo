import os
import git
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox, QListWidget, QListWidgetItem, QSplitter, QToolBar, QAction, QStatusBar, QMessageBox, QDialog, QLineEdit, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal, QProcess, QTimer
from PyQt5.QtGui import QIcon, QColor, QMovie, QFont
import time
from style import Style

class GitManager(QWidget):
    """Git管理器，用于执行Git命令并显示结果"""
    
    # 定义信号
    git_command_executed = pyqtSignal(str, str)  # 命令, 结果
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_repo_path = None
        self.is_loading = False
        self.init_ui()
        
        # 初始化定时器，每30秒自动刷新状态
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh_status)
        self.refresh_timer.start(30000)  # 30秒刷新一次
        
    def init_ui(self):
        # 创建主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # 设置背景色
        self.setStyleSheet(f"background-color: {Style.DARKER_BG};")
        
        # 设置字体
        font = QFont()
        font.setFamily(Style.UI_FONT_FAMILY.split(',')[0].strip())
        font.setPointSize(Style.UI_FONT_SIZE)
        
        # 创建顶部信息区域
        self.info_layout = QHBoxLayout()
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(10)
        
        # 设置分支和仓库标签样式
        self.branch_label = QLabel("分支: 未选择")
        self.branch_label.setFont(font)
        self.branch_label.setStyleSheet(f"color: {Style.TEXT_COLOR}; padding: 2px 5px;")
        
        self.repo_label = QLabel("仓库: 未选择")
        self.repo_label.setFont(font)
        self.repo_label.setStyleSheet(f"color: {Style.TEXT_COLOR}; padding: 2px 5px;")
        
        # 创建加载动画标签
        self.loading_label = QLabel()
        self.loading_label.setFixedSize(20, 20)
        self.loading_label.setVisible(False)
        self.loading_label.setStyleSheet("background-color: transparent;")
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Style.DARKER_BG};
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: #007acc;
            }}
        """)
        
        self.info_layout.addWidget(self.branch_label)
        self.info_layout.addWidget(self.repo_label)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.loading_label)
        self.layout.addLayout(self.info_layout)
        self.layout.addWidget(self.progress_bar)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Vertical)
        
        # 创建文件状态区域
        self.status_widget = QWidget()
        self.status_layout = QVBoxLayout(self.status_widget)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(5)
        
        self.status_label = QLabel("文件状态:")
        self.status_label.setFont(font)
        self.status_label.setStyleSheet(f"color: {Style.INACTIVE_TEXT}; font-weight: bold; padding: 2px;")
        
        self.status_list = QListWidget()
        self.status_list.setFont(font)
        self.status_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Style.DARKER_BG};
                border: 1px solid {Style.BORDER_COLOR};
                border-radius: 2px;
                padding: 2px;
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {Style.BORDER_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {Style.SELECTION_BG};
            }}
            QListWidget::item:hover:!selected {{
                background-color: #2a2d2e;
            }}
        """)
        
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_list)
        
        # 创建命令执行结果区域
        self.output_widget = QWidget()
        self.output_layout = QVBoxLayout(self.output_widget)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setSpacing(5)
        
        self.output_label = QLabel("命令输出:")
        self.output_label.setFont(font)
        self.output_label.setStyleSheet(f"color: {Style.INACTIVE_TEXT}; font-weight: bold; padding: 2px;")
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont(Style.CODE_FONT_FAMILY.split(',')[0].strip(), Style.CODE_FONT_SIZE))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Style.EDITOR_BG};
                color: {Style.TEXT_COLOR};
                border: 1px solid {Style.BORDER_COLOR};
                border-radius: 2px;
                selection-background-color: {Style.HIGHLIGHT_BG};
            }}
        """)
        
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_text)
        
        # 添加到分割器
        self.splitter.addWidget(self.status_widget)
        self.splitter.addWidget(self.output_widget)
        self.layout.addWidget(self.splitter)
        
        # 创建操作工具栏
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {Style.DARKER_BG};
                border: none;
                border-top: 1px solid {Style.BORDER_COLOR};
                border-bottom: 1px solid {Style.BORDER_COLOR};
                spacing: 2px;
                padding: 2px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 2px;
                padding: 4px 8px;
                color: {Style.TEXT_COLOR};
            }}
            QToolButton:hover {{
                background-color: {Style.SELECTION_BG};
            }}
            QToolButton:pressed {{
                background-color: {Style.HIGHLIGHT_BG};
            }}
        """)
        
        # 创建操作按钮
        self.init_action = QAction("初始化仓库", self)
        self.status_action = QAction("状态", self)
        self.add_action = QAction("暂存更改", self)
        self.commit_action = QAction("提交", self)
        self.push_action = QAction("推送", self)
        self.pull_action = QAction("拉取", self)
        self.branch_action = QAction("分支", self)
        self.log_action = QAction("日志", self)
        
        # 设置按钮字体
        for action in [self.init_action, self.status_action, self.add_action, self.commit_action,
                      self.push_action, self.pull_action, self.branch_action, self.log_action]:
            action.setFont(font)
        
        self.toolbar.addAction(self.init_action)
        self.toolbar.addAction(self.status_action)
        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.commit_action)
        self.toolbar.addAction(self.push_action)
        self.toolbar.addAction(self.pull_action)
        self.toolbar.addAction(self.branch_action)
        self.toolbar.addAction(self.log_action)
        
        self.layout.addWidget(self.toolbar)
        
        # 连接信号
        self.init_action.triggered.connect(self.init_repo)
        self.status_action.triggered.connect(self.check_status)
        self.add_action.triggered.connect(self.add_files)
        self.commit_action.triggered.connect(self.commit_changes)
        self.push_action.triggered.connect(self.push_changes)
        self.pull_action.triggered.connect(self.pull_changes)
        self.branch_action.triggered.connect(self.manage_branches)
        self.log_action.triggered.connect(self.show_log)
        
    def set_repo_path(self, path):
        """设置当前仓库路径"""
        self.current_repo_path = path
        self.repo_label.setText(f"仓库: {os.path.basename(path)}")
        self.update_branch_info()
        self.check_status()
    
    def update_branch_info(self):
        """更新分支信息"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.branch_label.setText("分支: 未选择")
            return
            
        try:
            # 使用GitPython获取当前分支
            repo = git.Repo(self.current_repo_path)
            branch_name = repo.active_branch.name
            self.branch_label.setText(f"分支: {branch_name}")
        except (git.exc.InvalidGitRepositoryError, git.exc.GitCommandError) as e:
            self.branch_label.setText("分支: 未知")
            self.log_output(f"获取分支信息失败: {str(e)}")
        except Exception as e:
            self.branch_label.setText("分支: 错误")
            self.log_output(f"获取分支信息失败: {str(e)}")
    
    def is_git_repo(self, path):
        """检查路径是否为Git仓库"""
        try:
            git.Repo(path)
            return True
        except git.exc.InvalidGitRepositoryError:
            return False
    
    def run_git_command(self, args):
        """运行Git命令"""
        if not self.current_repo_path:
            return False, "未选择仓库"
        
        # 显示加载动画
        self.show_loading(True)
            
        try:
            # 获取仓库对象
            repo = git.Repo(self.current_repo_path)
            
            # 构建Git命令
            git_cmd = repo.git
            
            # 执行命令
            method_name = args[0] if args else ""
            params = args[1:] if len(args) > 1 else []
            
            # 使用getattr动态调用方法
            if hasattr(git_cmd, method_name):
                method = getattr(git_cmd, method_name)
                result = method(*params)
                success = True
            else:
                # 对于不支持的命令，使用自定义方法执行
                result = git_cmd.execute(["git"] + args)
                success = True
            
            # 隐藏加载动画
            self.show_loading(False)
            
            # 更新状态（除非当前命令就是status）
            if method_name != "status":
                self.update_branch_info()
                self.update_status_list_with_repo(repo)
                
            return success, result
        except git.exc.GitCommandError as e:
            # 隐藏加载动画
            self.show_loading(False)
            return False, str(e)
        except Exception as e:
            # 隐藏加载动画
            self.show_loading(False)
            return False, str(e)
    
    def log_output(self, text):
        """在输出区域显示文本"""
        self.output_text.append(text)
        # 发出信号
        self.git_command_executed.emit(" ".join(["git"] + (getattr(self, "_last_command", []))), text)
    
    def init_repo(self):
        """初始化Git仓库"""
        if not self.current_repo_path:
            self.log_output("错误: 未选择仓库路径")
            return
            
        if self.is_git_repo(self.current_repo_path):
            self.log_output("当前目录已经是Git仓库")
            return
            
        self._last_command = ["init"]
        try:
            # 使用GitPython初始化仓库
            git.Repo.init(self.current_repo_path)
            self.log_output("Git仓库初始化成功")
            self.update_branch_info()
        except Exception as e:
            self.log_output(f"Git仓库初始化失败: {str(e)}")
    
    def check_status(self):
        """检查仓库状态"""
        if not self.current_repo_path:
            self.log_output("错误: 未选择仓库路径")
            return
            
        if not self.is_git_repo(self.current_repo_path):
            self.log_output("当前目录不是Git仓库")
            return
            
        self._last_command = ["status"]
        try:
            # 使用GitPython获取仓库状态
            repo = git.Repo(self.current_repo_path)
            
            # 获取状态输出
            status_output = repo.git.status()
            self.log_output(status_output)
            
            # 更新状态列表
            self.update_status_list_with_repo(repo)
        except Exception as e:
            self.log_output(f"获取状态失败: {str(e)}")
    
    def update_status_list(self, status_output):
        """更新文件状态列表（基于命令输出）"""
        self.status_list.clear()
        
        # 解析git status输出
        modified_files = []
        untracked_files = []
        staged_files = []
        
        for line in status_output.splitlines():
            line = line.strip()
            if "modified:" in line:
                modified_files.append(line.split("modified:")[-1].strip())
            elif "new file:" in line:
                staged_files.append(line.split("new file:")[-1].strip())
            elif "Untracked files:" in status_output and line and not line.startswith("#") and ":" not in line:
                if line not in ["Untracked files:", "(use \"git add <file>...\" to include in what will be committed)", ""]:
                    untracked_files.append(line)
        
        # 添加到列表
        for file in staged_files:
            item = QListWidgetItem(f"[已暂存] {file}")
            item.setForeground(QColor("green"))
            self.status_list.addItem(item)
            
        for file in modified_files:
            item = QListWidgetItem(f"[已修改] {file}")
            item.setForeground(QColor("blue"))
            self.status_list.addItem(item)
            
        for file in untracked_files:
            item = QListWidgetItem(f"[未跟踪] {file}")
            item.setForeground(QColor("red"))
            self.status_list.addItem(item)
    
    def update_status_list_with_repo(self, repo):
        """使用GitPython直接获取文件状态"""
        self.status_list.clear()
        
        # 获取未跟踪文件
        untracked_files = repo.untracked_files
        
        # 获取修改的文件
        modified_files = [item.a_path for item in repo.index.diff(None)]
        
        # 获取已暂存的文件
        staged_files = [item.a_path for item in repo.index.diff('HEAD')]
        
        # 添加到列表
        for file in staged_files:
            item = QListWidgetItem(f"[已暂存] {file}")
            item.setForeground(QColor("green"))
            self.status_list.addItem(item)
            
        for file in modified_files:
            item = QListWidgetItem(f"[已修改] {file}")
            item.setForeground(QColor("blue"))
            self.status_list.addItem(item)
            
        for file in untracked_files:
            item = QListWidgetItem(f"[未跟踪] {file}")
            item.setForeground(QColor("red"))
            self.status_list.addItem(item)
    
    def add_files(self):
        """添加文件到暂存区"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
            
        self._last_command = ["add", "."]
        try:
            repo = git.Repo(self.current_repo_path)
            repo.git.add('.')
            self.log_output("文件已添加到暂存区")
            self.check_status()
        except Exception as e:
            self.log_output(f"添加文件失败: {str(e)}")
    
    def commit_changes(self):
        """提交更改"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
        
        # 创建提交对话框
        commit_dialog = QDialog(self)
        commit_dialog.setWindowTitle("提交更改")
        commit_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(commit_dialog)
        dialog_layout.addWidget(QLabel("提交信息:"))
        
        message_input = QLineEdit()
        dialog_layout.addWidget(message_input)
        
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        commit_button = QPushButton("提交")
        commit_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(commit_button)
        dialog_layout.addLayout(button_layout)
        
        cancel_button.clicked.connect(commit_dialog.reject)
        commit_button.clicked.connect(commit_dialog.accept)
        
        if commit_dialog.exec_():
            commit_message = message_input.text()
            if not commit_message:
                commit_message = "更新代码"
            
            self._last_command = ["commit", "-m", commit_message]
            try:
                repo = git.Repo(self.current_repo_path)
                repo.git.commit('-m', commit_message)
                self.log_output(f"提交成功: {commit_message}")
                self.check_status()
            except Exception as e:
                self.log_output(f"提交失败: {str(e)}")
    
    def push_changes(self):
        """推送更改"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
            
        self._last_command = ["push"]
        try:
            repo = git.Repo(self.current_repo_path)
            origin = repo.remote(name='origin')
            push_info = origin.push()
            self.log_output(f"推送成功: {push_info[0].summary}")
        except Exception as e:
            self.log_output(f"推送失败: {str(e)}")
    
    def pull_changes(self):
        """拉取更改"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
            
        self._last_command = ["pull"]
        try:
            repo = git.Repo(self.current_repo_path)
            origin = repo.remote(name='origin')
            pull_info = origin.pull()
            self.log_output(f"拉取成功: {pull_info[0].note}")
            self.check_status()
        except Exception as e:
            self.log_output(f"拉取失败: {str(e)}")
    
    def manage_branches(self):
        """管理分支"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
            
        self._last_command = ["branch"]
        try:
            repo = git.Repo(self.current_repo_path)
            branches = repo.branches
            branch_list = "\n".join([f"{'* ' if b.name == repo.active_branch.name else '  '}{b.name}" for b in branches])
            self.log_output(f"分支列表:\n{branch_list}")
        except Exception as e:
            self.log_output(f"获取分支列表失败: {str(e)}")
    
    def show_log(self):
        """显示提交日志"""
        if not self.current_repo_path or not self.is_git_repo(self.current_repo_path):
            self.log_output("错误: 未选择有效的Git仓库")
            return
            
        self._last_command = ["log", "--oneline", "--graph", "--decorate", "--all", "-n", "10"]
        try:
            repo = git.Repo(self.current_repo_path)
            log_output = repo.git.log('--oneline', '--graph', '--decorate', '--all', '-n', '10')
            self.log_output(f"提交日志:\n{log_output}")
        except Exception as e:
            self.log_output(f"获取提交日志失败: {str(e)}")
    
    def show_loading(self, show=True):
        """显示或隐藏加载动画"""
        self.is_loading = show
        self.progress_bar.setVisible(show)
        
        if show:
            # 创建加载动画
            self.progress_bar.setValue(0)
            # 如果需要旋转图标，可以使用QMovie
            # movie = QMovie("path/to/loading.gif")
            # self.loading_label.setMovie(movie)
            # movie.start()
            # self.loading_label.setVisible(True)
        else:
            # 停止加载动画
            self.progress_bar.setValue(100)
            # self.loading_label.clear()
            # self.loading_label.setVisible(False)
    
    def auto_refresh_status(self):
        """定时自动刷新仓库状态"""
        if self.current_repo_path and self.is_git_repo(self.current_repo_path) and not self.is_loading:
            try:
                # 静默更新，不显示加载动画
                repo = git.Repo(self.current_repo_path)
                self.update_branch_info()
                self.update_status_list_with_repo(repo)
            except Exception as e:
                # 静默处理错误
                print(f"自动刷新状态失败: {str(e)}")
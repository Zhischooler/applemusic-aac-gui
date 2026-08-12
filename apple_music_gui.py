#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Apple Music AAC Downloader GUI
基于 gamdl 和 wenfeng110402/AppleMusic-Downloader 思路构建
支持配置文件持久化（封面尺寸、歌词、转FLAC）- 界面功能暂未启用
使用 PySide6 作为 GUI 框架
"""

import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QProgressBar, QLabel,
    QFileDialog, QComboBox, QCheckBox, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox, QSpinBox
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont


# ============================
# 配置文件管理
# ============================
CONFIG_FILE = "config.txt"

def load_config():
    """加载配置文件，返回字典"""
    config = {
        "coversize": "600x600",
        "downloadlyrics": True,
        "m4atoflac": False
    }
    if not os.path.exists(CONFIG_FILE):
        return config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "coversize":
                    config["coversize"] = value
                elif key == "downloadlyrics":
                    config["downloadlyrics"] = value.lower() == "true"
                elif key == "m4atoflac":
                    config["m4atoflac"] = value.lower() == "true"
    except Exception as e:
        print(f"读取配置文件失败: {e}")
    return config

def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"coversize:{config['coversize']}\n")
            f.write(f"downloadlyrics:{str(config['downloadlyrics']).lower()}\n")
            f.write(f"m4atoflac:{str(config['m4atoflac']).lower()}\n")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


# ============================
# 下载线程类 (后台运行 gamdl)
# ============================
class DownloadThread(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal(bool, str)

    def __init__(self, url, cookies_path, output_dir, quality, 
                 lyrics, cover_size, remux_flac, concurrent):
        super().__init__()
        self.url = url
        self.cookies_path = cookies_path
        self.output_dir = output_dir
        self.quality = quality          # 保留但暂不使用
        self.lyrics = lyrics
        self.cover_size = cover_size
        self.remux_flac = remux_flac
        self.concurrent = concurrent   # 保留但暂不使用
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        # 基础命令（使用当前 gamdl 支持的参数）
        cmd = [
            "gamdl",
            "--cookies-path", self.cookies_path,
            "--output-path", self.output_dir,
        ]

        # 注意：其他选项（音质、封面、歌词、转FLAC）因版本变更已暂时移除
        # 如需启用，请运行 `gamdl --help` 查看当前支持选项并修改此处

        # 最后添加目标 URL
        cmd.append(self.url)

        # 执行命令
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            while True:
                if self._is_cancelled:
                    process.kill()
                    self.finished_signal.emit(False, "下载已取消")
                    return
                line = process.stdout.readline()
                if not line:
                    break
                self.log_signal.emit(line.strip())
                # 简单进度指示
                if "Downloading" in line:
                    self.progress_signal.emit(50)
                if "Finished" in line or "Downloaded" in line:
                    self.progress_signal.emit(100)
            process.wait()
            if process.returncode == 0:
                self.finished_signal.emit(True, "下载完成")
            else:
                self.finished_signal.emit(False, f"下载失败，返回码 {process.returncode}")
        except Exception as e:
            self.log_signal.emit(f"错误: {str(e)}")
            self.finished_signal.emit(False, f"异常: {str(e)}")


# ============================
# 主窗口
# ============================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Music AAC 下载器")
        self.setMinimumSize(800, 600)
        self.download_thread = None
        self.task_list = []
        self.current_task_index = 0

        # 加载配置
        self.config = load_config()

        self.init_ui()

        # 将配置填充到界面
        self.apply_config_to_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # -------------------------
        # 1. 配置区域
        # -------------------------
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout(config_group)

        # Cookies
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(QLabel("Cookies文件:"))
        self.cookies_line = QLineEdit()
        self.cookies_line.setPlaceholderText("请选择 Netscape 格式的 cookies.txt")
        cookies_layout.addWidget(self.cookies_line)
        self.cookies_btn = QPushButton("浏览")
        self.cookies_btn.clicked.connect(self.browse_cookies)
        cookies_layout.addWidget(self.cookies_btn)
        config_layout.addLayout(cookies_layout)

        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText("请选择下载保存路径")
        output_layout.addWidget(self.output_line)
        self.output_btn = QPushButton("浏览")
        self.output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_btn)
        config_layout.addLayout(output_layout)

        # 下载选项（界面保留，但实际功能暂未启用）
        option_layout = QHBoxLayout()
        option_layout.addWidget(QLabel("音质:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["aac_best", "aac_256", "aac_128", "aac_64", "aac_48"])
        self.quality_combo.setCurrentIndex(1)
        option_layout.addWidget(self.quality_combo)

        option_layout.addWidget(QLabel("并发数:"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setValue(3)
        option_layout.addWidget(self.concurrent_spin)

        self.lyrics_check = QCheckBox("下载歌词")
        self.lyrics_check.stateChanged.connect(self.on_setting_changed)
        option_layout.addWidget(self.lyrics_check)

        self.flac_check = QCheckBox("转FLAC")
        self.flac_check.stateChanged.connect(self.on_setting_changed)
        option_layout.addWidget(self.flac_check)

        option_layout.addWidget(QLabel("封面尺寸:"))
        self.cover_size_line = QLineEdit()
        self.cover_size_line.setPlaceholderText("如 600x600")
        self.cover_size_line.setFixedWidth(100)
        self.cover_size_line.textChanged.connect(self.on_setting_changed)
        option_layout.addWidget(self.cover_size_line)

        option_layout.addStretch()
        config_layout.addLayout(option_layout)

        main_layout.addWidget(config_group)

        # -------------------------
        # 2. 任务区域
        # -------------------------
        task_group = QGroupBox("任务管理")
        task_layout = QVBoxLayout(task_group)

        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入 Apple Music 链接 (歌曲/专辑/歌单/艺人)")
        url_input_layout.addWidget(self.url_input)
        self.add_btn = QPushButton("添加到队列")
        self.add_btn.clicked.connect(self.add_task)
        url_input_layout.addWidget(self.add_btn)
        task_layout.addLayout(url_input_layout)

        self.task_list_widget = QListWidget()
        self.task_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        task_layout.addWidget(self.task_list_widget)

        task_control_layout = QHBoxLayout()
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        task_control_layout.addWidget(self.remove_btn)
        self.clear_btn = QPushButton("清空队列")
        self.clear_btn.clicked.connect(self.clear_tasks)
        task_control_layout.addWidget(self.clear_btn)
        task_control_layout.addStretch()
        self.start_btn = QPushButton("开始下载")
        self.start_btn.clicked.connect(self.start_download)
        task_control_layout.addWidget(self.start_btn)
        self.cancel_btn = QPushButton("取消当前")
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)
        task_control_layout.addWidget(self.cancel_btn)
        task_layout.addLayout(task_control_layout)

        main_layout.addWidget(task_group)

        # -------------------------
        # 3. 进度和日志
        # -------------------------
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        progress_layout.addWidget(self.log_text)

        main_layout.addWidget(progress_group)

        self.log_message("程序已启动，配置已加载。")

    # ---------- 配置加载/保存 ----------
    def apply_config_to_ui(self):
        self.cover_size_line.setText(self.config.get("coversize", "600x600"))
        self.lyrics_check.setChecked(self.config.get("downloadlyrics", True))
        self.flac_check.setChecked(self.config.get("m4atoflac", False))

    def on_setting_changed(self):
        self.config["coversize"] = self.cover_size_line.text().strip()
        self.config["downloadlyrics"] = self.lyrics_check.isChecked()
        self.config["m4atoflac"] = self.flac_check.isChecked()
        save_config(self.config)

    # ---------- 辅助方法 ----------
    def log_message(self, msg):
        self.log_text.append(msg)

    def browse_cookies(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Cookies 文件", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.cookies_line.setText(file_path)

    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_line.setText(dir_path)

    def add_task(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入有效的 Apple Music 链接")
            return
        if "apple.com" not in url and "music.apple.com" not in url:
            QMessageBox.warning(self, "提示", "链接似乎不是 Apple Music 链接，请确认")
        item = QListWidgetItem(url)
        self.task_list_widget.addItem(item)
        self.task_list.append(url)
        self.url_input.clear()
        self.log_message(f"已添加任务: {url}")

    def remove_selected(self):
        selected = self.task_list_widget.selectedItems()
        for item in selected:
            row = self.task_list_widget.row(item)
            self.task_list_widget.takeItem(row)
            del self.task_list[row]

    def clear_tasks(self):
        self.task_list_widget.clear()
        self.task_list.clear()
        self.log_message("队列已清空")

    # ---------- 下载控制 ----------
    def start_download(self):
        if not self.task_list:
            QMessageBox.information(self, "提示", "队列为空，请先添加任务")
            return
        cookies = self.cookies_line.text().strip()
        if not cookies or not os.path.isfile(cookies):
            QMessageBox.warning(self, "错误", "请选择有效的 Cookies 文件")
            return
        output_dir = self.output_line.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "错误", "请选择输出目录")
            return

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self.current_task_index = 0
        self.download_next()

    def download_next(self):
        if self.current_task_index >= len(self.task_list):
            self.finish_download_all()
            return
        url = self.task_list[self.current_task_index]
        self.log_message(f"开始下载 [{self.current_task_index+1}/{len(self.task_list)}]: {url}")
        self.progress_bar.setValue(0)

        quality = self.quality_combo.currentText()
        lyrics = self.lyrics_check.isChecked()
        cover_size = self.cover_size_line.text().strip()
        remux_flac = self.flac_check.isChecked()
        concurrent = self.concurrent_spin.value()
        output_dir = self.output_line.text().strip()
        cookies = self.cookies_line.text().strip()

        self.download_thread = DownloadThread(
            url, cookies, output_dir, quality,
            lyrics, cover_size, remux_flac, concurrent
        )
        self.download_thread.log_signal.connect(self.log_message)
        self.download_thread.progress_signal.connect(self.progress_bar.setValue)
        self.download_thread.finished_signal.connect(self.on_task_finished)
        self.download_thread.start()

    def on_task_finished(self, success, message):
        self.log_message(f"任务结束: {message}")
        if success:
            self.current_task_index += 1
            self.download_next()
        else:
            reply = QMessageBox.question(
                self, "下载失败",
                f"任务失败: {message}\n是否继续下一个任务？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.current_task_index += 1
                self.download_next()
            else:
                self.finish_download_all()

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.log_message("正在取消下载...")

    def finish_download_all(self):
        self.log_message("所有任务处理完毕。")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.download_thread = None
        self.progress_bar.setValue(0)


# ============================
# 程序入口
# ============================
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
# app/updater.py
import os
import sys
import time
import tempfile
import subprocess
import pyzipper
import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QApplication


class DownloadUpdateWorker(QObject):
    """Worker chạy ngầm, tích hợp thuật toán Bypass Google Drive Virus Scan"""
    progress = Signal(int)
    status = Signal(str)  # <-- Bổ sung Signal báo trạng thái bằng Text
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url

    def _get_confirm_token(self, response):
        """Hàm dùng BeautifulSoup moi mã xác nhận ẩn từ trang HTML của Google"""
        soup = BeautifulSoup(response.text, 'html.parser')
        inputs = soup.find_all('input')
        payload = {}
        for tag in inputs:
            name = tag.get('name')
            value = tag.get('value')
            if name:
                payload[name] = value
        return payload

    def run(self):
        try:
            self.status.emit("⏳ Đang kết nối máy chủ Google Drive...")
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")

            # 1. Xử lý đường link để bóc tách ID file
            file_id = self.download_url
            if "drive.google.com" in self.download_url and "id=" in self.download_url:
                file_id = self.download_url.split("id=")[1].split("&")[0]
            elif "/d/" in self.download_url:
                file_id = self.download_url.split("/d/")[1].split("/")[0]

            # 2. Thuật toán vượt rào Google Drive bằng Session
            URL = "https://drive.usercontent.google.com/download"
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            response = session.get(URL, params={'id': file_id}, stream=True)
            params = self._get_confirm_token(response)

            if params:
                response = session.get(URL, params=params, stream=True)

            # 3. Tải và ghi file
            CHUNK_SIZE = 32768
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            last_percent = -1

            if 'text/html' in response.headers.get('Content-Type', ''):
                raise Exception("Google Drive vẫn chặn tải xuống. File có thể bị giới hạn lượt tải.")

            self.status.emit("⬇️ Đang tải dữ liệu bản cập nhật...")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded_size / total_size) * 100)
                            if percent > last_percent:
                                self.progress.emit(percent)
                                last_percent = percent

            # 4. Giải nén file
            self.status.emit("📦 Đang giải nén tệp tin hệ thống... Vui lòng chờ!")
            extract_path = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_path, exist_ok=True)
            with pyzipper.AESZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path, pwd=b"pttb")

            self.status.emit("✅ Hoàn tất tải và giải nén!")
            self.finished.emit(extract_path)

        except Exception as e:
            self.error.emit(str(e))


class AutoUpdater(QObject):
    """Trình quản lý giao diện và kịch bản cập nhật"""

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget

    def prompt_and_update(self, update_info):
        """Hiển thị bảng hỏi người dùng có muốn cập nhật không"""
        version = update_info.get("latest_version", "Mới")
        notes = update_info.get("release_notes", "Cải thiện hiệu năng và sửa lỗi hệ thống.")
        download_url = update_info.get("download_url")

        if not download_url:
            QMessageBox.warning(self.parent_widget, "Lỗi cập nhật", "Không tìm thấy đường dẫn tải về trong cấu hình.")
            return

        msg = f"Đã có phiên bản mới: {version}\n\nNội dung cập nhật:\n{notes}\n\nBạn có muốn tải xuống và cài đặt ngay không?"
        reply = QMessageBox.question(
            self.parent_widget, "Có bản cập nhật mới", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.start_download(download_url)

    def start_download(self, url):
        """Kích hoạt luồng tải file với thanh tiến trình và trạng thái Text"""
        self.progress_dialog = QProgressDialog(self.parent_widget)
        self.progress_dialog.setWindowTitle("Trình cập nhật phần mềm")
        self.progress_dialog.setLabelText("Đang khởi động...")
        self.progress_dialog.setRange(0, 100)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setModal(True)
        self.progress_dialog.setCancelButton(None)

        self.thread = QThread()
        self.worker = DownloadUpdateWorker(url)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        # Móc dây điện: % nhảy thì thanh UI nhảy, Text thay đổi thì Label thay đổi
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.status.connect(self.progress_dialog.setLabelText)

        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)

        self.thread.start()
        self.progress_dialog.show()

    def on_download_error(self, err):
        self.progress_dialog.close()
        QMessageBox.critical(self.parent_widget, "Lỗi Tải xuống", f"Đã xảy ra lỗi khi tải bản cập nhật:\n{err}")

    def on_download_finished(self, extract_path):
        self.progress_dialog.close()
        reply = QMessageBox.question(
            self.parent_widget, "Sẵn sàng Cài đặt",
            "Đã tải và giải nén xong bản cập nhật.\nPhần mềm cần đóng để chép file và khởi động lại.\n\nBắt đầu cài đặt ngay?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.apply_update_and_restart(extract_path)

    def apply_update_and_restart(self, extract_path):
        """Kịch bản thay thế file cũ với Thông báo an tâm cho User"""

        # [UX CỰC XỊN]: Bật Popup chặn màn hình, giấu nút OK đi để User không bấm tắt được
        msg = QMessageBox(self.parent_widget)
        msg.setWindowTitle("Đang cài đặt")
        msg.setText(
            "⚙️ Đang chép đè tệp tin hệ thống và khởi động lại...\nQuá trình này mất khoảng vài giây. Vui lòng chờ!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()

        # [BÍ KÍP]: Ép PyQt/PySide vẽ cái bảng này lên ngay lập tức, nếu không gọi cái này nó sẽ bị kẹt trắng xóa
        QApplication.processEvents()

        # Giữ nguyên bảng đó trên màn hình 1.5 giây cho người dùng đọc được chữ
        time.sleep(1.5)

        # Chạy file Batch ngầm để copy đè
        current_dir = os.getcwd()

        if getattr(sys, 'frozen', False):
            script_args = f'"{sys.executable}"'
        else:
            script_args = f'"{sys.executable}" "{sys.argv[0]}"'

        bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
xcopy /s /y /i "{extract_path}\\*" "{current_dir}\\"
rmdir /s /q "{os.path.dirname(extract_path)}"
start "" {script_args}
del "%~f0"
"""
        bat_path = os.path.join(tempfile.gettempdir(), "update_taxapp.bat")
        with open(bat_path, "w") as f:
            f.write(bat_content)

        subprocess.Popen(
            ["cmd.exe", "/c", bat_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Đóng cái rụp
        sys.exit(0)
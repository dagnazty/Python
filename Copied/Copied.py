import sys
import os
import logging
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    logging.error("Exception Traceback: " + ''.join(traceback.format_tb(exc_traceback)))

sys.excepthook = handle_exception

class ClipboardWatcher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.previous_clipboard_content = self.clipboard.text()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_download_finished)
        self.copied_text_display = CopiedTextDisplay()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.label = QtWidgets.QLabel("Copied!", self)
        self.label.setStyleSheet("""
            QLabel {
                color : white;
                border: 1px solid white;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setGeometry(20, 10, 80, 30)

        effect = QtWidgets.QGraphicsDropShadowEffect(self.label)
        effect.setBlurRadius(0)
        effect.setColor(QtGui.QColor("black"))
        effect.setOffset(1, 1)
        self.label.setGraphicsEffect(effect)

    def on_clipboard_change(self):
        mime = self.clipboard.mimeData()
        if mime.hasImage():
            try:
                image = self.clipboard.image()
                self.copied_text_display.update_image(image)
            except Exception as e:
                print("Error processing image:", e)
        elif mime.hasUrls():
            try:
                urls = mime.urls()
                if urls:
                    first_url = urls[0]
                if first_url.isLocalFile():
                    local_path = first_url.toLocalFile()
                    if os.path.isfile(local_path):
                        if local_path.endswith('.gif'):
                            self.copied_text_display.update_image(local_path, is_gif=True)
                        elif local_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                            self.copied_text_display.update_image(local_path)
                        else:
                            self.copied_text_display.update_text(f"File: {local_path}")
                    elif os.path.isdir(local_path):
                        self.copied_text_display.update_text(f"Folder: {local_path}")
                else:
                    remote_url = first_url.toString()
                    self.copied_text_display.update_text(f"URL: {remote_url}")
            except Exception as e:
                print("Error handling URL:", e)
        elif mime.hasText():
            text = self.clipboard.text()
            self.show_bubble()
            self.copied_text_display.update_text(text)

    def download_gif(self, url):
        try:
            request = QNetworkRequest(QtCore.QUrl(url))
            self.network_manager.get(request)
        except Exception as e:
            print("Error downloading GIF:", e)

    def on_download_finished(self, reply):
        if reply.error():
            print("Error downloading GIF:", reply.errorString())
            return
        try:
            data = reply.readAll()
            self.update_image(data, is_gif=True)
            image = QtGui.QImage()
            image.loadFromData(data)
            self.copied_text_display.update_image(image, is_gif=True)
        except Exception as e:
            print("Error processing downloaded GIF:", e)

    def show_bubble(self):
        cursor_pos = QtGui.QCursor.pos()
        self.move(cursor_pos.x(), cursor_pos.y())
        self.setWindowOpacity(0.75)
        self.show()

        QtCore.QTimer.singleShot(500, self.start_fade_animation)

    def start_fade_animation(self):
        self.fade_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)  # Duration of fade
        self.fade_animation.setStartValue(0.75)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.hide_bubble)
        self.fade_animation.start()

    def hide_bubble(self):
        self.hide()

class CopiedTextDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.movie = None
        self.is_frame_changed_connected = False
        self.fixed_width = 250  
        self.fixed_height = 150  
        self.clear_button_height = 20  
        self.initUI()

    def initUI(self):
        try:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)

            self.display_label = QtWidgets.QLabel(self)
            self.display_label.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.display_label, 1)  

            self.gif_label = QtWidgets.QLabel(self)  
            self.gif_label.hide()
            self.layout.addWidget(self.gif_label, 1)  

            self.textArea = QtWidgets.QTextEdit(self)
            self.textArea.setStyleSheet("""
                QTextEdit {
                    color: white;
                    background-color: rgba(0, 0, 0, 150);
                    border: 1px solid white;
                    border-radius: 10px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: white;
                    width: 10px;
                    margin: 10px 0 10px 0;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: grey;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                }
            """)
            self.textArea.setReadOnly(True)
            self.textArea.hide()
            self.layout.addWidget(self.textArea, 1)  
          
            self.clearButton = QtWidgets.QPushButton("Clear", self)
            self.clearButton.clicked.connect(self.clear_contents)
            self.clearButton.setFixedHeight(self.clear_button_height)
            self.layout.addWidget(self.clearButton)

            self.setFixedSize(self.fixed_width, self.fixed_height + self.clear_button_height)
            self.hide()
        except Exception as e:
            print("Error initializing UI:", e)
    
    def update_image(self, image, is_gif=False):
        self.textArea.hide()
        self.display_label.hide()
        self.gif_label.hide()

        if self.movie and self.is_frame_changed_connected:
            self.movie.frameChanged.disconnect(self.resize_to_gif)
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
            self.is_frame_changed_connected = False

        if is_gif:
            self.movie = QMovie(image)
            self.movie.setCacheMode(QMovie.CacheAll)
            self.movie.frameChanged.connect(self.resize_to_gif)
            self.is_frame_changed_connected = True

            self.gif_label.setMovie(self.movie)
            self.movie.start()
            self.gif_label.show()
        else:
            if isinstance(image, str):
                pixmap = QPixmap(image)
            else:
                pixmap = QPixmap.fromImage(image)

            scaled_pixmap = pixmap.scaled(self.fixed_width, self.fixed_height, QtCore.Qt.KeepAspectRatio)
            self.display_label.setPixmap(scaled_pixmap)
            self.display_label.setFixedSize(scaled_pixmap.size())
            self.display_label.show()

        self.show()
        self.adjustSizeAndPosition()

    def resize_to_gif(self, frame_number):
        if not self.movie or not self.is_frame_changed_connected:
            return

        current_frame = self.movie.currentPixmap()
        scaled_frame = current_frame.scaled(self.fixed_width, self.fixed_height, QtCore.Qt.KeepAspectRatio)
        self.gif_label.setPixmap(scaled_frame)
        self.gif_label.setFixedSize(scaled_frame.size())

        self.centerContent()

    def centerContent(self):
        content_width = self.gif_label.width() if self.gif_label.isVisible() else self.display_label.width()
        content_height = self.gif_label.height() if self.gif_label.isVisible() else self.display_label.height()
        
        label_x = (self.fixed_width - content_width) // 2
        label_y = (self.fixed_height - content_height) // 2

        if self.gif_label.isVisible():
            self.gif_label.move(label_x, label_y)
        else:
            self.display_label.move(label_x, label_y)

    def update_text(self, text):
        self.display_label.hide()
        self.gif_label.hide()
        
        if self.movie:
            self.movie.stop()
            if self.is_frame_changed_connected:
                self.movie.frameChanged.disconnect(self.resize_to_gif)
                self.is_frame_changed_connected = False
            self.movie.deleteLater() 
            self.movie = None

        self.textArea.setText(text)
        self.textArea.show()

        self.setFixedSize(self.fixed_width, self.fixed_height + self.clear_button_height)

        self.show()
        self.adjustSizeAndPosition()

    def clear_contents(self):
        if self.movie and self.is_frame_changed_connected:
            self.movie.frameChanged.disconnect(self.resize_to_gif)
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
            self.is_frame_changed_connected = False

        self.display_label.clear()
        self.display_label.hide()
        self.gif_label.clear()
        self.gif_label.hide()
        self.textArea.clear()
        self.textArea.hide()

        self.hide()

    def adjustSizeAndPosition(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        taskbarHeight = 40  

        x_position = screen.width() - self.width() - 10
        y_position = screen.height() - self.height() - taskbarHeight - 10 

        self.move(x_position, y_position)
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    watcher = ClipboardWatcher()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

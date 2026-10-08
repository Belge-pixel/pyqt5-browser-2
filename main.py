import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import images_rc
from browser import Browser
from wifi import auto_connect_wifi


QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

auto_connect_wifi()

app = QApplication(sys.argv)

window = Browser()
window.show()

sys.exit(app.exec_())
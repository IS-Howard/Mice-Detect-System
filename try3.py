import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SelectROI(QWidget):

    def __init__(self):
        super().__init__()

        self.image = QImage('your_image.jpg')  # replace with your own image path
        self.selection = QRect(QPoint(100, 100), QPoint(400, 400))
        self.start_point = None
        self.end_point = None

        self.initUI()

    def initUI(self):

        #self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Select ROI')
        self.show()

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)

        if self.image is not None:
            qp.drawImage(QPoint(0, 0), self.image)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        qp.setPen(pen)

        if self.selection is not None:
            qp.drawRect(self.selection)

        if self.start_point is not None and self.end_point is not None:
            qp.drawRect(QRect(self.start_point, self.end_point))

        qp.end()

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            selection = QRect(self.start_point, event.pos())
            self.selection = selection

            # record the coordinates of the top-left and bottom-right corners of the ROI
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = event.pos().x(), event.pos().y()

            print(f'Top-left corner: ({x1}, {y1})')
            print(f'Bottom-right corner: ({x2}, {y2})')

            # reset the start/end points
            self.start_point = None
            self.end_point = None
            self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = SelectROI()
    sys.exit(app.exec_())
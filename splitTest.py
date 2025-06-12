import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QSplitter, QTextEdit
)
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("70/30 Split Demo")

        # Use a simple horizontal layout
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Create a QSplitter with horizontal orientation => left-right panes
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left and right widgets – can be any QWidget (here we use QTextEdit for demo)
        leftWidget = QTextEdit("Left Panel (70%)")
        rightWidget = QTextEdit("Right Panel (30%)")

        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)

        # Set initial sizes so the left widget is about 70% of the width and right 30%
        splitter.setSizes([700, 300])  # total = 1000 => 70% vs 30%

        self.resize(1000, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
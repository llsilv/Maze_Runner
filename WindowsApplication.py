import sys, time, serial
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal


data = [[0, 0, 0, 0, 0, 0, False],[0, 0, 0, 0, 0, 0, False]]
hHeader = ["Motor 1 / X", "Motor 2 / Y"]
vHeader = ["Joystick","Position","Intended Speed", "Actual Speed", "Temperature", "Driver Temp.", "Collision"]


number_of_squares = 20 #squares in 1 row
SizeOfSquares = int(500 / number_of_squares)
HalfOfSize = int(SizeOfSquares / 2) #range from middle point to edge

xCheese = HalfOfSize + SizeOfSquares * 15 
yCheese = HalfOfSize + SizeOfSquares * 10



class SerialThread(QtCore.QThread):
    SerialUpdate = pyqtSignal()
    
    def __init__(self, MyWindow):
        QtCore.QThread.__init__(self)

        self.portname = 'COM3'
        self.baudrate = 9600
        self.running = True

    def run(self):
        running = True
         
        try:
            ser = serial.Serial("COM3", baudrate = 9600, timeout = 0.1)
            time.sleep(0.1)
            ser.flushInput()
        except:
            ser = None
        if not ser:
            print("can't open port")
            running = False
        while running:
            s = ser.readline().decode("utf-8").split(";")
            counter = 0
            index = 0

            for item in s:
                if item == "" or item == None:
                    break

                if counter > 6:
                    index = 1
                    counter = 0
                #print(item)

                data[index][counter] = item
                if counter == 6:
                    data[1][6] = item
                counter += 1
                self.SerialUpdate.emit() #kbs

        if ser:
            ser.close()
            ser = None



class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, vHeader, hHeader):
        super(TableModel, self).__init__()

        self._hHeader = hHeader
        self._vHeader = vHeader

    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = data[index.row()][index.column()]

            if isinstance(value, float):
                return "%.2f" % value

            return value

    def rowCount(self, index):
        return len(data)

    def columnCount(self, index):
        return len(data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return (self._hHeader[section])

            if orientation == Qt.Vertical:
                return (self._vHeader[section])



class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.setGeometry(200, 200, 800, 650)
        self.setWindowTitle("Maze Runner")
        layout = QtWidgets.QVBoxLayout()

        
        self.serth = SerialThread(self)
        self.serth.start()

        self.table = QtWidgets.QTableView()
        self.model = TableModel(data, hHeader, vHeader)
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(500, 500)
        canvas.fill(QtGui.QColor('#CD853F'))
        self.label.setPixmap(canvas)
        layout.addWidget(self.label)
        self.setLayout(layout) 

        self.draw_board(SizeOfSquares, HalfOfSize, number_of_squares)
        self.draw_cheese(xCheese, yCheese, SizeOfSquares)

        
        self.serth.SerialUpdate.connect(self.update_function) #kbs



    def update_function(self): #kbs
        #Insert code to update w/e ui here

        self.xMouse = SizeOfSquares * float(data[0][1])
        self.yMouse = SizeOfSquares * float(data[1][1])
        self.draw_mouse(int(self.xMouse), int(self.yMouse))
        self.model.layoutChanged.emit()



    def draw_board(self, SizeOfSquares, HalfOfSize, number_of_squares):

        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(SizeOfSquares)
        pen.setColor(QtGui.QColor("#FFDEAD"))
        painter.setPen(pen)
        x_position = y_position = HalfOfSize

        for m in range(number_of_squares):
            for n in range(number_of_squares):
                if n % 2 == 0:
                    painter.drawPoint(x_position, y_position)
                x_position += SizeOfSquares
            x_position = HalfOfSize
            y_position += SizeOfSquares
            if m % 2 == 0:
                x_position = HalfOfSize * 3
        painter.end()

    def draw_cheese(self, xCheese, yCheese, SizeOfSquares):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(SizeOfSquares)
        pen.setColor(QtGui.QColor("yellow"))
        painter.setPen(pen)
        painter.drawPoint(xCheese, yCheese)
        painter.end()

    def draw_mouse(self, xMouse, yMouse):

        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(1)
        painter.setPen(pen)
        pen.setColor(QtGui.QColor("#778899"))
        painter.setPen(pen)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("#778899"))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.drawRoundedRect(xMouse, yMouse, SizeOfSquares, SizeOfSquares, 100, 100)
        painter.end()
        self.update()
    

def window():
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
        

window()

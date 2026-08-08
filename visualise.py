import sys
from wsgiref import headers
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsItem, QLabel
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QRectF, QPoint, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygon
from PyQt6 import uic
import math
import get_data
from pyqttooltip import Tooltip, TooltipPlacement

# What data to use for radar chart for each position
radar_data = {
    "FW": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead", "Touches", "TouAtt3rd", "DriSucc"],
    "MF": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead"],
    "DF": ["TklDri","PasHigh", "PasPress", "PasTotCmp%", "PasTotCmp", "PasProg","TklWon", "PaswHead", "PresSucc", "CarTotDist", "Int", "BlkSh"],
    "GK": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead"]
}



def make_polygon(num_sides, size):
    straight_line_up = (0, size)
    list_of_points = [straight_line_up]
    rotation_angle = 360 / num_sides
    current_x, current_y = straight_line_up
    
    for i in range(num_sides-1):
        previous_x, previous_y = current_x, current_y
        current_x = previous_x * math.cos(math.radians(rotation_angle)) + previous_y * math.sin(math.radians(rotation_angle))
        current_y = -previous_x * math.sin(math.radians(rotation_angle)) + previous_y * math.cos(math.radians(rotation_angle))
        list_of_points.append((current_x, current_y))
    
    return list_of_points

class Radar(QGraphicsItem):
    def __init__(self, dict_of_stats=None, view=None, size=200):
        super().__init__()
        self.dict_of_stats = dict_of_stats
        self.view = view
        self.size = size
        self.label_list = []

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)  # required

    def paint(self, painter, option, widget):
        #painter.setBrush(QBrush(QColor("purple")))
        #painter.drawEllipse(0, 0, 100, 100)
        #painter.drawText(10, 50, "Custom!")

        # Paint radar shape
        polygon_size = self.size
        num_sides = len(self.dict_of_stats) if self.dict_of_stats else 6
        list_of_points = make_polygon(num_sides, polygon_size)
        polygon_points = [QPoint(int(x), int(y)) for x, y in list_of_points]
        polygon= QPolygon(polygon_points)
        painter.drawPolygon(polygon)

        # Paint stats shape if we have stats to show
        if self.dict_of_stats:
            """
            for label in self.label_list:
                label.setHidden(True)
                label.deleteLater()
            self.label_list.clear();
            """
            text_dist_from_edge = 20
            list_of_stat_names = list(self.dict_of_stats.keys())
            stats_points = [] # list of points (q points) to draw the stats shape at, in the same order as list_of_stat_names
            for i in range(len(list_of_points)):
                position = list_of_points[i]
                # Draw text
                text_x = 0
                text_y = 0
                if position[0] < 0:
                    text_x = position[0] - text_dist_from_edge
                else:
                    text_x = position[0] + text_dist_from_edge
                if position[1] < 0:
                    text_y = position[1] - text_dist_from_edge
                else:
                    text_y = position[1] + text_dist_from_edge
                
                stat_name = list_of_stat_names[i]
                painter.drawText(int(text_x), int(text_y), str(stat_name))

                # Get stat value and calculate where to draw the stat point
                data_value = self.dict_of_stats[stat_name]
                # multiply positions by normalised stat value to get stat point position
                stat_x = position[0] * data_value
                stat_y = position[1] * data_value
                stats_points.append(QPoint(int(stat_x), int(stat_y)))
                """
                # Add label 
                rounded_data_value = round(data_value, 2)
                label = QLabel(str(rounded_data_value), parent=self.view.viewport());
                label_pos = self.view.mapFromScene(QPointF(int(stat_x), int(stat_y)))
                label.move(label_pos)
                self.label_list.append(label)
                label.show()
                """
            stats_polygon = QPolygon(stats_points)
            painter.setBrush(QBrush(QColor(255, 0, 0, 100)))  # Red with some transparency
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPolygon(stats_polygon)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('visMainWindow.ui', self)
        self.currentDataType = "raw"
        self.statFilter.addItems(get_data.GetHeaderList()[1:])  # Exclude the first column (ID)
        self.operationSelection.addItems([">", "<", "=", ">=", "<="])
        self.filterValueInput.setPlaceholderText("Enter value for filter...")
        self.scene = QGraphicsScene()
        shape = Radar()
        self.scene.addItem(shape)
        w = self.statsRadar.width()
        h = self.statsRadar.height()
        self.scene.setSceneRect(-w/2, -h/2, w, h)
        self.statsRadar.centerOn(0, 0)
        self.statsRadar.setScene(self.scene)

        # Set up buttons
        self.loadRawDataButton.clicked.connect(self.loadRawData)
        self.loadNormalisedDataButton.clicked.connect(self.loadNormalisedData)
        self.loadNormalisedDataButtonPerLeague.clicked.connect(self.loadNormalisedPerLeagueData)
        self.loadNormalisedDataButtonPerLeaguePerPos.clicked.connect(self.loadNormalisedPerLeaguePerPos)
        self.playerTable.clicked.connect(self.onPlayerTableClicked)

        # Set up the table model and proxy model for sorting and filtering
        data = get_data.GetRawData()
        self.model = TableModel(data)
        self.proxy_model = CustomProxyModel()
        self.proxy_model.setFilterKeyColumn(1)  # Search just names.
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSourceModel(self.model)

        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)  

        self.playerTable.setModel(self.proxy_model)

        self.playerTable.setSortingEnabled(True)

        self.searchBar.setPlaceholderText("Type to filter...")

        self.searchBar.textChanged.connect(
            self.proxy_model.setFilterFixedString
        )

        self.applyFiltersButton.clicked.connect(
            lambda: self.proxy_model.applyFilter(
                self.statFilter.currentIndex(), self.operationSelection.currentText(), self.filterValueInput.text()
                )
                )

        self.label_list = []
    
    def onPlayerTableClicked(self, index):
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        rowData = get_data.GetRowData(row, self.currentDataType)
        headers = get_data.GetHeaderList()
        player_position_index = headers.index("Pos")
        data_to_get = radar_data[rowData[player_position_index]]  # Get the list of stats to get for the player's position
        data_name_and_value = {}
        for data_name in data_to_get:
            stat_index = headers.index(data_name)
            stat_value = rowData[stat_index]
            data_name_and_value[data_name] = stat_value
        
        self.scene.clear()          # remove all items
        for label in self.label_list:
                label.setHidden(True)
                label.deleteLater()
        self.label_list.clear();
        polygon_size = 200
        shape = Radar(data_name_and_value, self.statsRadar, polygon_size)
        self.scene.addItem(shape)
        self.statsRadar.setScene(self.scene)
        dict_of_stats = data_name_and_value
        num_sides = len(dict_of_stats) if dict_of_stats else 6
        list_of_points = make_polygon(num_sides, polygon_size)
        for i in range(len(list_of_points)):
                position = list_of_points[i]
                print(f"Position {i}: {position}")
                # Get stat value and calculate where to draw the stat point
                list_of_stat_names = list(dict_of_stats.keys())
                stat_name = list_of_stat_names[i]
                data_value = dict_of_stats[stat_name]
                # multiply positions by normalised stat value to get stat point position
                stat_x = position[0] * data_value
                stat_y = position[1] * data_value

                # Add label 
                rounded_data_value = round(data_value, 2)
                label = QLabel(str(rounded_data_value), parent=self.statsRadar.viewport());
                label_pos = self.statsRadar.mapFromScene(QPointF(int(stat_x), int(stat_y)))
                label.move(label_pos)
                self.label_list.append(label)
                label.show()
        # ... re-add your items ...
        self.statsRadar.viewport().update()  # force repaint
        
    def loadRawData(self):
        self.model.update_data(get_data.GetRawData())
        self.currentDataType = "raw"
    
    def loadNormalisedData(self):
        self.model.update_data(get_data.GetNormalisedData())
        self.currentDataType = "normalised"
    
    def loadNormalisedPerLeagueData(self):
        self.model.update_data(get_data.GetNormalisedPerLeagueData())
        self.currentDataType = "normalised_per_league"
    
    def loadNormalisedPerLeaguePerPos(self):
        self.model.update_data(get_data.GetNormalisedPerLeaguePerPosData())
        self.currentDataType = "normalised_per_league_per_pos"
    

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = get_data.GetHeaderList()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        # Column headers
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

        # Row headers
        if orientation == Qt.Orientation.Vertical:
            return str(section + 1)

        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def update_data(self, new_data):
        self.layoutAboutToBeChanged.emit()
        self._data = new_data
        self.layoutChanged.emit()

class CustomProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._stat_index_filter = None
        self._operation = None
        self._value = None
    
    def applyFilter(self, statIndex, operation, value):
        operation_functions = {">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            "=": lambda x, y: x == y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y
        }

        self._stat_index_filter = statIndex+1  # +1 to account for ID column
        self._operation = operation_functions.get(operation)
        if value.isdigit():
            self._value = float(value)
        else:
            self._value = value
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()

        # Search bar filter (column 1 = name)
        search_text = self.filterRegularExpression().pattern()
        if search_text:
            name_index = model.index(source_row, 1, source_parent)
            name = model.data(name_index, Qt.ItemDataRole.DisplayRole) or ""
            if search_text.lower() not in name.lower():
                return False
        
        # Stat filter (column specified by _stat_index_filter)
        if self._stat_index_filter != None and self._operation != None and self._value != None:
            stat_index = model.index(source_row, self._stat_index_filter, source_parent)
            stat = model.data(stat_index, Qt.ItemDataRole.DisplayRole)
            try:
                if self._operation:
                    if isinstance(self._value, str):
                        stat = float(stat)
                    if not self._operation(stat, self._value):
                        return False
            except (ValueError, TypeError):
                pass


        return True

# 5. Run your application's event loop
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

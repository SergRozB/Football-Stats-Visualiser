import sys
from warnings import filters
from wsgiref import headers
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsItem, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QRectF, QPoint, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygon
from PyQt6 import uic
import math
import get_data
from pyqttooltip import Tooltip, TooltipPlacement
from statistics_dict import STATS

# What data to use for radar chart for each position
radar_data = {
    "FW": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead", "Touches", "TouAtt3rd", "DriSucc"],
    "MF": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead"],
    "DF": ["TklDri","PasHigh", "PasPress", "PasTotCmp%", "PasTotCmp", "PasProg","TklWon", "PaswHead", "PresSucc", "CarTotDist", "Int", "BlkSh"],
    "GK": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead"],
    "Default": ["Goals", "Shots", "SoT", "Pas3rd","TklWon", "PaswHead"]
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
    def __init__(self, dict_of_stats=None, view=None, size=200, currentDataType="raw", filters=[]):
        super().__init__()
        self.dict_of_stats = dict_of_stats
        self.view = view
        self.size = size
        self.label_list = []
        self.currentDataType = currentDataType
        self.filters = filters  

    def setCurrentDataType(self, data_type):
        self.currentDataType = data_type

    def setFilters(self, filters):
        self.filters = filters

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
                if self.currentDataType == "raw":
                    if len(self.filters) > 0:
                        # Apply filters to the data_value if needed
                        percentile = get_data.GetPercentile(stat_name, data_value, self.currentDataType, self.filters)
                    else:
                        percentile = get_data.GetPercentile(stat_name, data_value, self.currentDataType)

                    stat_x = position[0] * percentile
                    stat_y = position[1] * percentile

                else:
                    percentile = data_value
                    if len(self.filters) > 0:
                        # Apply filters to the data_value if needed
                        percentile = get_data.GetPercentile(stat_name, data_value, self.currentDataType, self.filters)

                    stat_x = position[0] * percentile
                    stat_y = position[1] * percentile
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
        uic.loadUi('Football-Stats-Visualiser/visMainWindow.ui', self)

        # Filter stuff
        self.filterTabIndex = 1
        self.filterNum = 0
        self.filterList = []
        self.addFilterButton.clicked.connect(self.addFilter)
        self.clearFiltersButton.clicked.connect(self.clearFilters)
        self.toggleCurrentRadarFiltersButton.clicked.connect(self.toggleRadarFilters)
        self.toggleDataLabelFiltersButton.clicked.connect(self.toggleDataLabelFilter)

        self.showIfFiltersAppliedToDataLabel.setText("Filters Applied to Data Label: False")
        self.toggleDataLabelFiltersButton.setEnabled(False)  # Disable the button when filters are not applied
        self.toggleDataLabelFiltersButton.setStyleSheet("background-color : dark grey")  # Change the button color to dark grey when disabled

        self.applyFiltersToRadar = False
        self.applyFiltersToDataLabel = False


        self.currentDataType = "raw"
        self.currentlySelectedPlayerID = None
        self.scene = QGraphicsScene()
        self.shape = Radar()
        self.scene.addItem(self.shape)
        w = self.statsRadar.width()
        h = self.statsRadar.height()
        self.scene.setSceneRect(-w/2, -h/2, w, h)
        self.statsRadar.centerOn(0, 0)
        self.statsRadar.setScene(self.scene)

        # Set up other buttons
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
            lambda: self.proxy_model.applyFilters(
                self.filterList
                )
                )

        self.label_list = []

        # Miscellaneous UI setup
        self.currentLoadedDataLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dataRadarOptions = ["Preset"] + ["Add new radar"] 
        self.dataRadarTypeOptions.addItems(dataRadarOptions)

    def toggleRadarFilters(self):
        self.applyFiltersToRadar = not self.applyFiltersToRadar
        if self.applyFiltersToRadar:
            self.showIfFiltersAppliedToRadar.setText("Filters Applied: True")
            self.toggleDataLabelFiltersButton.setEnabled(True)  # Enable the button when filters are applied
            self.toggleDataLabelFiltersButton.setStyleSheet("background-color : white")  # Change the button color to light grey when enabled

        else:
            self.showIfFiltersAppliedToRadar.setText("Filters Applied: False")
            self.toggleDataLabelFiltersButton.setEnabled(False)  # Disable the button when filters are not applied
            self.toggleDataLabelFiltersButton.setStyleSheet("background-color : dark grey")  # Change the button color to dark grey when disabled
            self.showIfFiltersAppliedToDataLabel.setText("Filters Applied to Data Label: False")
            self.applyFiltersToDataLabel = False

        self.reloadRadarTableOnDataChange(self.currentDataType, apply_filters_to_radar=self.applyFiltersToRadar)

    def toggleDataLabelFilter(self):
        self.applyFiltersToDataLabel = not self.applyFiltersToDataLabel
        if self.applyFiltersToDataLabel:
            self.showIfFiltersAppliedToDataLabel.setText("Filters Applied to Data Label: True")
        else:
            self.showIfFiltersAppliedToDataLabel.setText("Filters Applied to Data Label: False")
        self.reloadRadarTableOnDataChange(self.currentDataType, apply_filters_to_radar=self.applyFiltersToRadar)

    def addFilter(self):
        new_stat_filter = QComboBox()
        new_operation_selection = QComboBox()
        new_filter_value_input = QLineEdit()
        remove_filter_button = QPushButton("Remove")
        self.filterList.append((new_stat_filter, new_operation_selection, new_filter_value_input))

        all_headers_raw = get_data.GetHeaderList()[1:]
        all_headers_readable = [STATS.get(header, header) for header in all_headers_raw]
        new_stat_filter.addItems(all_headers_readable)  # Exclude the first column (ID)
        new_operation_selection.addItems([">", "<", "=", ">=", "<="])
        new_filter_value_input.setPlaceholderText("Enter value for filter...")

        self.filterLayout.addWidget(new_stat_filter, self.filterNum, 0)
        self.filterLayout.addWidget(new_operation_selection, self.filterNum, 1)
        self.filterLayout.addWidget(new_filter_value_input, self.filterNum, 2)
        self.filterLayout.addWidget(remove_filter_button, self.filterNum, 3)
        self.filterNum += 1

        # Connect the remove button to a function that removes the filter
        remove_filter_button.clicked.connect(lambda: self.removeFilter(new_stat_filter, new_operation_selection, new_filter_value_input, remove_filter_button))

    def removeFilter(self, stat_filter, operation_selection, filter_value_input, remove_button):
        # Remove the filter from the layout
        self.filterLayout.removeWidget(stat_filter)
        self.filterLayout.removeWidget(operation_selection)
        self.filterLayout.removeWidget(filter_value_input)
        self.filterLayout.removeWidget(remove_button)

        # Delete the widgets
        stat_filter.deleteLater()
        operation_selection.deleteLater()
        filter_value_input.deleteLater()
        remove_button.deleteLater()

        # Remove the filter from the list
        filter_to_remove = (stat_filter, operation_selection, filter_value_input)
        self.filterList.remove(filter_to_remove)
        self.filterNum -= 1

    def clearFilters(self):
        while self.filterLayout.count():
            item = self.filterLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.filterList.clear()
        self.filterNum = 0

    def onPlayerTableClicked(self, index, apply_filters_to_radar=False):
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        rowData = get_data.GetRowData(row, self.currentDataType)
        self.currentlySelectedPlayerID = rowData[0]  # Store the selected player's ID
        headers = get_data.GetHeaderList()
        
        player_position_index = headers.index("Pos")
        data_to_get = radar_data.get(rowData[player_position_index], radar_data["Default"])  # Get the list of stats to get for the player's position
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
        if apply_filters_to_radar:
            filters = self.proxy_model.proxyModelFiltersList
        else:
            filters = []
        self.shape = Radar(data_name_and_value, self.statsRadar, polygon_size, self.currentDataType, filters)
        self.scene.addItem(self.shape)
        self.statsRadar.setScene(self.scene)
        dict_of_stats = data_name_and_value
        num_sides = len(dict_of_stats) if dict_of_stats else 6
        list_of_points = make_polygon(num_sides, polygon_size)

        # Calculate where to add labels for each stat point
        for i in range(len(list_of_points)):
                position = list_of_points[i]
                # Get stat value and calculate where to draw the stat point
                list_of_stat_names = list(dict_of_stats.keys())
                stat_name = list_of_stat_names[i]
                data_value = dict_of_stats[stat_name]
                # multiply positions by normalised stat value to get stat point position
                percentile = get_data.GetPercentile(stat_name, data_value, data_type=self.currentDataType, filters=filters)
                stat_x = position[0] * percentile
                stat_y = position[1] * percentile

                # Add label 
                if self.applyFiltersToDataLabel:
                    # Apply filters to the data_value if needed
                    data_value = percentile  # Use the percentile value if filters are applied
                rounded_data_value = round(data_value, 2)
                label = QLabel(str(rounded_data_value), parent=self.statsRadar.viewport());
                label_pos = self.statsRadar.mapFromScene(QPointF(int(stat_x), int(stat_y)))
                label.move(label_pos)
                self.label_list.append(label)
                label.show()
        # ... re-add your items ...
        self.statsRadar.viewport().update()  # force repaint

    # This function reloads the radar table when the data type of the table changes, ensuring that the currently selected player's stats are displayed correctly based on the new data type and any applied filters.
    def reloadRadarTableOnDataChange(self, stat_type_name, apply_filters_to_radar=False):
        self.shape.setCurrentDataType(stat_type_name)
        print(f"Reloading radar table for player ID: {self.currentlySelectedPlayerID} with data type: {stat_type_name}")
        table_row_index = get_data.GetRowIndexByPlayerID(
            self.currentlySelectedPlayerID, self.currentDataType) if self.currentlySelectedPlayerID else -2
        if table_row_index == -1:
            print(f"Player ID '{self.currentlySelectedPlayerID}' not found in the {self.currentDataType} dataset.")
        elif table_row_index == -2:
            print("No player is currently selected.")
        else:
            source_model = self.proxy_model.sourceModel()
            source_idx = source_model.index(table_row_index, 0)
            index = self.proxy_model.mapFromSource(source_idx)  # Get the proxy index of the currently selected player
            self.onPlayerTableClicked(index, apply_filters_to_radar)  # Pass the index and filter application flag to the method

    def loadRawData(self):
        self.model.update_data(get_data.GetRawData())
        stat_type_name = "raw"
        self.currentDataType = stat_type_name
        if self.currentlySelectedPlayerID:
            self.reloadRadarTableOnDataChange(stat_type_name)
        self.currentLoadedDataLabel.setText("Currently loaded data: Raw Data")
    
    def loadNormalisedData(self):
        self.model.update_data(get_data.GetNormalisedData())
        stat_type_name = "normalised"
        self.currentDataType = stat_type_name
        if self.currentlySelectedPlayerID:
            self.reloadRadarTableOnDataChange(stat_type_name)
        self.currentLoadedDataLabel.setText("Currently loaded data: Raw Data")
    
    def loadNormalisedPerLeagueData(self):
        self.model.update_data(get_data.GetNormalisedPerLeagueData())
        stat_type_name = "normalised_per_league"
        self.currentDataType = stat_type_name
        if self.currentlySelectedPlayerID:
            self.reloadRadarTableOnDataChange(stat_type_name)
        self.currentLoadedDataLabel.setText("Currently loaded data: Normalised Per League Data")
    
    def loadNormalisedPerLeaguePerPos(self):
        self.model.update_data(get_data.GetNormalisedPerLeaguePerPosData())
        stat_type_name = "normalised_per_league_per_pos"
        self.currentDataType = stat_type_name
        if self.currentlySelectedPlayerID:
            self.reloadRadarTableOnDataChange(stat_type_name)
        self.currentLoadedDataLabel.setText("Currently loaded data: Normalised Per League and Position Data")
    

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
        self.proxyModelFiltersList = []  # List to hold the filters
    
    def applyFilters(self, filterList):
        operation_functions = {
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            "=": lambda x, y: x == y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y
        }

        self.proxyModelFiltersList.clear()  # Clear existing filters
        print(f"Applying filters: {filterList}")
        for statFilterButton, operationSelectionButton, filterValueInputButton in filterList:
            statFilter = statFilterButton.currentIndex()
            operationText = operationSelectionButton.currentText()
            filterValueInput = filterValueInputButton.text()

            stat_index_filter = statFilter + 1  # +1 to account for ID column
            operation = operation_functions.get(operationText)
            if filterValueInput.isdigit():
                value = float(filterValueInput)
            else:
                value = filterValueInput
            self.proxyModelFiltersList.append((stat_index_filter, (operation, operationText), value))
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
        for stat_index_filter, (operation, operation_text), value in self.proxyModelFiltersList:
            if stat_index_filter != None and operation != None and value != None:
                stat_index = model.index(source_row, stat_index_filter, source_parent)
                stat = model.data(stat_index, Qt.ItemDataRole.DisplayRole)
                try:
                    if operation:
                        if isinstance(value, str):
                            stat = float(stat)
                        if not operation(stat, value):
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

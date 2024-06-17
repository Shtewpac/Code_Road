
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QSpinBox, QFileDialog, QListWidget, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QInputDialog


class GearGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gear Generator")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Animation controls
        animation_controls = QHBoxLayout()
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_animation)
        animation_controls.addWidget(self.start_stop_button)
        animation_controls.addWidget(QPushButton("Freeze"))
        animation_controls.addWidget(QPushButton("Reset"))

        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed (RPM):"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(3)
        speed_layout.addWidget(self.speed_slider)
        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setRange(1, 10)
        self.speed_spinbox.setValue(3)
        speed_layout.addWidget(self.speed_spinbox)

        main_layout.addLayout(animation_controls)
        main_layout.addLayout(speed_layout)

        # Gear list
        gear_list_layout = QHBoxLayout()
        self.gear_list = QListWidget()
        self.gear_list.currentRowChanged.connect(self.update_gear_properties)
        gear_list_layout.addWidget(self.gear_list)

        gear_controls = QVBoxLayout()
        gear_controls.addWidget(QPushButton("Add New", clicked=self.add_gear))
        gear_controls.addWidget(QPushButton("Remove", clicked=self.remove_gear))
        gear_controls.addWidget(QPushButton("Clear", clicked=self.clear_gears))
        gear_list_layout.addLayout(gear_controls)

        main_layout.addLayout(gear_list_layout)

        # Gear properties
        gear_properties_layout = QHBoxLayout()
        gear_properties_label = QLabel("Gear Properties:")
        gear_properties_label.setStyleSheet("font-weight: bold;")
        gear_properties_layout.addWidget(gear_properties_label)

        self.gear_properties_table = QTableWidget(0, 3)
        self.gear_properties_table.setHorizontalHeaderLabels(["Property", "Value", "Unit"])
        gear_properties_layout.addWidget(self.gear_properties_table)

        main_layout.addLayout(gear_properties_layout)

        # Visibility and gear type controls
        visibility_layout = QHBoxLayout()
        visibility_label = QLabel("Visibility:")
        visibility_layout.addWidget(visibility_label)
        self.visibility_combo = QComboBox()
        self.visibility_combo.addItems(["All", "Same Layer", "Object"])
        visibility_layout.addWidget(self.visibility_combo)

        gear_type_layout = QHBoxLayout()
        gear_type_label = QLabel("Gear Type:")
        gear_type_layout.addWidget(gear_type_label)
        self.gear_type_combo = QComboBox()
        self.gear_type_combo.addItems(["Spur", "Helical", "Bevel", "Worm"])
        gear_type_layout.addWidget(self.gear_type_combo)

        main_layout.addLayout(visibility_layout)
        main_layout.addLayout(gear_type_layout)

        # Connection properties
        connection_properties_layout = QHBoxLayout()
        connection_properties_label = QLabel("Connection Properties:")
        connection_properties_label.setStyleSheet("font-weight: bold;")
        connection_properties_layout.addWidget(connection_properties_label)

        connection_properties_grid = QVBoxLayout()
        parent_gear_layout = QHBoxLayout()
        parent_gear_layout.addWidget(QLabel("Parent Gear #:"))
        self.parent_gear_spinbox = QSpinBox()
        self.parent_gear_spinbox.setRange(0, 100)
        parent_gear_layout.addWidget(self.parent_gear_spinbox)
        parent_gear_layout.addWidget(QPushButton("Select"))
        connection_properties_grid.addLayout(parent_gear_layout)

        axle_connection_layout = QHBoxLayout()
        axle_connection_layout.addWidget(QLabel("Axle Connection:"))
        self.axle_connection_combo = QComboBox()
        self.axle_connection_combo.addItems(["Fixed", "Revolute", "Prismatic"])
        axle_connection_layout.addWidget(self.axle_connection_combo)
        connection_properties_grid.addLayout(axle_connection_layout)

        connection_angle_layout = QHBoxLayout()
        connection_angle_layout.addWidget(QLabel("Connection Angle:"))
        self.connection_angle_spinbox = QSpinBox()
        self.connection_angle_spinbox.setRange(0, 360)
        connection_angle_layout.addWidget(self.connection_angle_spinbox)
        connection_angle_layout.addWidget(QLabel("deg"))
        connection_properties_grid.addLayout(connection_angle_layout)

        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("X Position:"))
        self.x_position_spinbox = QSpinBox()
        self.x_position_spinbox.setRange(0, 1000)
        position_layout.addWidget(self.x_position_spinbox)
        position_layout.addWidget(QLabel("mm"))
        position_layout.addWidget(QLabel("Y Position:"))
        self.y_position_spinbox = QSpinBox()
        self.y_position_spinbox.setRange(0, 1000)
        position_layout.addWidget(self.y_position_spinbox)
        position_layout.addWidget(QLabel("mm"))
        connection_properties_grid.addLayout(position_layout)

        connection_properties_layout.addLayout(connection_properties_grid)
        main_layout.addLayout(connection_properties_layout)

        # Export button
        main_layout.addWidget(QPushButton("Export", clicked=self.export_file))

        # 3D rendering area
        # Implement this using a library like PyOpenGL or Blender's Python API

    def toggle_animation(self):
        if self.start_stop_button.text() == "Start":
            self.start_stop_button.setText("Stop")
            # Start animation code here
        else:
            self.start_stop_button.setText("Start")
            # Stop animation code here

    def add_gear(self):
        gear_name, ok = QInputDialog.getText(self, "Add Gear", "Enter Gear Name:")
        if ok:
            self.gear_list.addItem(gear_name)
            self.update_gear_properties()

    def remove_gear(self):
        selected_items = self.gear_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.gear_list.takeItem(self.gear_list.row(item))
            self.update_gear_properties()

    def clear_gears(self):
        self.gear_list.clear()
        self.update_gear_properties()

    def update_gear_properties(self):
        current_row = self.gear_list.currentRow()
        self.gear_properties_table.clearContents()
        self.gear_properties_table.setRowCount(0)

        if current_row >= 0:
            gear_properties = [
                ("Name", self.gear_list.item(current_row).text(), ""),
                ("Module (M)", "2", ""),
                ("Number of Teeth (N)", "13", ""),
                ("Base Diameter (D)", "26", "mm"),
            ]

            self.gear_properties_table.setRowCount(len(gear_properties))
            for row, (prop, value, unit) in enumerate(gear_properties):
                self.gear_properties_table.setItem(row, 0, QTableWidgetItem(prop))
                self.gear_properties_table.setItem(row, 1, QTableWidgetItem(str(value)))
                self.gear_properties_table.setItem(row, 2, QTableWidgetItem(unit))

    def export_file(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            # Export 3D file code here

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gear_generator = GearGenerator()
    gear_generator.show()
    sys.exit(app.exec_())
unknown
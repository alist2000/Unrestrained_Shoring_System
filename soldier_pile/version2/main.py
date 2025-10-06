import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QLineEdit, QLabel, QPushButton, QComboBox, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox, QDialog, QDialogButtonBox)
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QBrush, QColor, QPolygonF

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsLineItem, \
    QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF
from PySide6.QtCore import Qt, QPointF
from database import sections_dict
from input import handle_input


class ShoringPreview(QGraphicsView):
    def __init__(self, soil_profile, parent=None):
        super().__init__(parent)
        self.soil_profile = soil_profile
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

    def update_preview(self):
        self.scene.clear()

        # Define some constants
        scale = 10  # pixels per foot
        width = 300
        retaining_height = sum(layer.height for layer in self.soil_profile.layers)
        embedment_depth = self.calculate_embedment_depth()  # You need to implement this method
        total_height = (retaining_height + embedment_depth) * scale

        # Draw pile
        pile = self.scene.addRect(width / 2 - 5, 0, 10, total_height, QPen(Qt.black), QBrush(Qt.gray))

        # Draw soil layers
        y = 0
        for layer in self.soil_profile.layers:
            height = layer.height * scale
            # Behind pile (active pressure)
            self.scene.addRect(0, y, width / 2 - 5, height, QPen(Qt.black), QBrush(QColor(255, 200, 200)))
            # In front of pile (passive pressure)
            self.scene.addRect(width / 2 + 5, y, width / 2 - 5, height, QPen(Qt.black), QBrush(QColor(200, 255, 200)))
            y += height

        # Draw embedment depth
        embedment_rect = self.scene.addRect(0, y, width, embedment_depth * scale, QPen(Qt.black),
                                            QBrush(QColor(200, 200, 255)))

        # Draw pressure diagrams (simplified)
        active_pressure = self.scene.addPolygon(QPolygonF([
            QPointF(width / 2 - 5, 0),
            QPointF(width / 4, total_height),
            QPointF(width / 2 - 5, total_height)
        ]), QPen(Qt.red))

        passive_pressure = self.scene.addPolygon(QPolygonF([
            QPointF(width / 2 + 5, retaining_height * scale),
            QPointF(3 * width / 4, total_height),
            QPointF(width / 2 + 5, total_height)
        ]), QPen(Qt.blue))

        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def calculate_embedment_depth(self):
        # This is a placeholder. You need to implement the actual calculation
        # based on your soil mechanics principles and design requirements
        return 5  # Example: 5 feet embedment depth

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


# Strategy Pattern for Soil Theories
class SoilTheory:
    def get_parameters(self):
        raise NotImplementedError


class UserDefinedTheory(SoilTheory):
    def __init__(self):
        self.distribution_type = "Triangle"
        self.h1 = 0
        self.h2 = 0
        self.sigma_a = 0

    def get_parameters(self):
        return ['EFP Active', 'EFP Passive', 'Distribution Type']

    def set_distribution(self, distribution_type, h1=0, h2=0, sigma_a=0):
        self.distribution_type = distribution_type
        self.h1 = h1
        self.h2 = h2
        self.sigma_a = sigma_a

    def get_distribution_params(self):
        return {
            "type": self.distribution_type,
            "h1": self.h1,
            "h2": self.h2,
            "sigma_a": self.sigma_a
        }


class RankineTheory(SoilTheory):
    def get_parameters(self):
        return ['φ', 'γ', 'c']


class CoulombTheory(SoilTheory):
    def get_parameters(self):
        return ['φ', 'γ', 'c', 'δ']


# Factory Pattern for Soil Theories
class SoilTheoryFactory:
    @staticmethod
    def create_theory(theory_name):
        theory_name = theory_name.lower().replace(" ", "")
        if "userdefined" in theory_name:
            return UserDefinedTheory()
        elif "rankine" in theory_name:
            return RankineTheory()
        elif "coulomb" in theory_name:
            return CoulombTheory()
        else:
            raise ValueError(f"Invalid theory name: {theory_name}")


# Model
class SoilLayer:
    def __init__(self, height, properties):
        self.height = height
        self.properties = properties


class SoilProfile(QObject):
    layer_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layers = []
        self.theory = UserDefinedTheory()

    def set_theory(self, theory_name):
        self.theory = SoilTheoryFactory.create_theory(theory_name)
        self.layers.clear()
        self.layer_changed.emit()

    def add_layer(self, height, properties):
        if isinstance(self.theory, UserDefinedTheory) and len(self.layers) >= 1:
            raise ValueError("User Defined theory allows only one layer")

        if isinstance(self.theory, UserDefinedTheory):
            distribution_type = properties.get('Distribution Type', 'Triangle')
            h1 = properties.get('H1', 0)
            h2 = properties.get('H2', 0)
            sigma_a = properties.get('Sigma a', 0)
            self.theory.set_distribution(distribution_type, h1, h2, sigma_a)

        self.layers.append(SoilLayer(height, properties))
        self.layer_changed.emit()

    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
            self.layer_changed.emit()

    def update_layer(self, index, height, properties):
        if 0 <= index < len(self.layers):
            self.layers[index] = SoilLayer(height, properties)
            self.layer_changed.emit()

    def to_dict(self):
        theory_dict = {
            "name": self.theory.__class__.__name__,
        }
        if isinstance(self.theory, UserDefinedTheory):
            theory_dict.update(self.theory.get_distribution_params())

        return {
            "theory": theory_dict,
            "layers": [
                {
                    "height": layer.height,
                    "properties": layer.properties
                } for layer in self.layers
            ]
        }


# View
class LayerPropertyDialog(QDialog):
    def __init__(self, layer, theory, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.theory = theory
        self.setWindowTitle("Layer Properties")
        self.layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.height_input = QLineEdit(str(self.layer.height))
        self.form.addRow("Height (m):", self.height_input)

        self.property_inputs = {}
        for param in self.theory.get_parameters():
            if param == 'Distribution Type':
                self.distribution_combo = QComboBox()
                self.distribution_combo.addItems(["Triangle", "Trapezoidal"])
                self.distribution_combo.currentTextChanged.connect(self.update_distribution_inputs)
                self.form.addRow(f"{param}:", self.distribution_combo)
            else:
                self.property_inputs[param] = QLineEdit(str(self.layer.properties.get(param, '')))
                self.form.addRow(f"{param}:", self.property_inputs[param])

        self.distribution_inputs = {}
        self.distribution_form = QFormLayout()
        self.layout.addLayout(self.form)
        self.layout.addLayout(self.distribution_form)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        if isinstance(self.theory, UserDefinedTheory):
            self.distribution_combo.setCurrentText(self.theory.distribution_type)
            self.update_distribution_inputs(self.theory.distribution_type)

    def update_distribution_inputs(self, distribution_type):
        for i in reversed(range(self.distribution_form.rowCount())):
            self.distribution_form.removeRow(i)

        self.distribution_inputs.clear()

        if distribution_type == "Trapezoidal":
            for param in ["H1", "H2", "Sigma a"]:
                self.distribution_inputs[param] = QLineEdit()
                self.distribution_form.addRow(f"{param}:", self.distribution_inputs[param])

    def get_values(self):
        height = float(self.height_input.text())
        properties = {param: float(input.text()) for param, input in self.property_inputs.items()}

        if isinstance(self.theory, UserDefinedTheory):
            distribution_type = self.distribution_combo.currentText()
            properties['Distribution Type'] = distribution_type
            if distribution_type == "Trapezoidal":
                for param, input in self.distribution_inputs.items():
                    properties[param] = float(input.text())

        return height, properties


class SoilLayerWidget(QGroupBox):
    def __init__(self, soil_profile):
        super().__init__("Soil Layers")
        self.soil_profile = soil_profile
        self.soil_profile.layer_changed.connect(self.update_view)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.layer_list = QListWidget()
        self.layer_list.itemDoubleClicked.connect(self.edit_layer)
        layout.addWidget(self.layer_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Layer")
        self.remove_button = QPushButton("Remove Layer")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_layer)
        self.remove_button.clicked.connect(self.remove_layer)

        self.update_view()

    def update_view(self):
        self.layer_list.clear()
        for i, layer in enumerate(self.soil_profile.layers):
            properties_str = ", ".join(f"{k}: {v}" for k, v in layer.properties.items())
            if isinstance(self.soil_profile.theory, UserDefinedTheory):
                distribution_params = self.soil_profile.theory.get_distribution_params()
                properties_str += f", Distribution: {distribution_params['type']}"
                if distribution_params['type'] == 'Trapezoidal':
                    properties_str += f", H1: {distribution_params['h1']}, H2: {distribution_params['h2']}, Sigma a: {distribution_params['sigma_a']}"
            self.layer_list.addItem(f"Layer {i + 1}: {layer.height} m - {properties_str}")

    def add_layer(self):
        dialog = LayerPropertyDialog(SoilLayer(0, {}), self.soil_profile.theory, self)
        if dialog.exec():
            try:
                height, properties = dialog.get_values()
                self.soil_profile.add_layer(height, properties)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))

    def remove_layer(self):
        current_row = self.layer_list.currentRow()
        if current_row >= 0:
            self.soil_profile.remove_layer(current_row)

    def edit_layer(self, item):
        index = self.layer_list.row(item)
        layer = self.soil_profile.layers[index]
        dialog = LayerPropertyDialog(layer, self.soil_profile.theory, self)
        if dialog.exec():
            try:
                height, properties = dialog.get_values()
                self.soil_profile.update_layer(index, height, properties)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))


class SoilVisualization(QGraphicsView):
    def __init__(self, soil_profile):
        super().__init__()
        self.soil_profile = soil_profile
        self.soil_profile.layer_changed.connect(self.update_view)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

    def update_view(self):
        self.scene.clear()

        # Define some constants
        scale = 10  # pixels per foot
        width = 400
        margin = 50
        retaining_height = sum(layer.height for layer in self.soil_profile.layers)
        embedment_depth = self.calculate_embedment_depth()
        total_height = (retaining_height + embedment_depth) * scale

        # Draw pile
        pile = QGraphicsRectItem(width / 2 - 5, margin, 10, total_height)
        pile.setBrush(QBrush(Qt.gray))
        self.scene.addItem(pile)

        # Draw soil layers
        y = margin
        for i, layer in enumerate(self.soil_profile.layers):
            height = layer.height * scale

            # Behind pile (active pressure)
            active_rect = QGraphicsRectItem(margin, y, width / 2 - margin - 5, height)
            active_rect.setBrush(QBrush(self.get_soil_color(i)))
            self.scene.addItem(active_rect)

            # Layer text
            text = QGraphicsTextItem(f"Layer {i + 1}\nHeight: {layer.height} m")
            text.setPos(margin + 5, y + 5)
            self.scene.addItem(text)

            y += height

        # Draw embedment depth
        embedment_rect = QGraphicsRectItem(margin, y, width - 2 * margin, embedment_depth * scale)
        embedment_rect.setBrush(QBrush(self.get_soil_color(-1)))  # Use the color of the last layer
        self.scene.addItem(embedment_rect)

        # Draw passive side (only in embedment depth)
        passive_rect = QGraphicsRectItem(width / 2 + 5, y, width / 2 - margin - 5, embedment_depth * scale)
        passive_rect.setBrush(QBrush(self.get_soil_color(-1)))
        self.scene.addItem(passive_rect)

        # Draw pressure diagrams (simplified)
        active_pressure = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 - 5, margin),
            QPointF(width / 4, margin + total_height),
            QPointF(width / 2 - 5, margin + total_height)
        ]))
        active_pressure.setPen(QPen(Qt.red))
        self.scene.addItem(active_pressure)

        passive_pressure = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 + 5, margin + retaining_height * scale),
            QPointF(3 * width / 4, margin + total_height),
            QPointF(width / 2 + 5, margin + total_height)
        ]))
        passive_pressure.setPen(QPen(Qt.blue))
        self.scene.addItem(passive_pressure)

        # Draw ground level line
        ground_line = QGraphicsLineItem(margin, margin, width - margin, margin)
        ground_line.setPen(QPen(Qt.black, 2))
        self.scene.addItem(ground_line)

        # Add labels
        self.add_label("Ground Level", width - margin + 5, margin)
        self.add_label(f"Retaining Height: {retaining_height} m", width + 5, margin + retaining_height * scale / 2)

        self.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def get_soil_color(self, index):
        colors = [QColor(255, 200, 200), QColor(200, 255, 200), QColor(200, 200, 255),
                  QColor(255, 255, 200), QColor(255, 200, 255), QColor(200, 255, 255)]
        return colors[index % len(colors)]

    def add_label(self, text, x, y):
        label = QGraphicsTextItem(text)
        label.setPos(x, y)
        label.setRotation(270)
        self.scene.addItem(label)

    def calculate_embedment_depth(self):
        # This is a placeholder. Implement the actual calculation based on your requirements.
        return 5  # Example: 5 feet embedment depth

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class GeometricalSoilPropertiesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.soil_profile = SoilProfile()

        layout = QHBoxLayout(self)

        control_layout = QVBoxLayout()
        layout.addLayout(control_layout)

        theory_combo = QComboBox()
        theory_combo.addItems(["User Defined", "Rankine", "Coulomb"])
        theory_combo.currentTextChanged.connect(self.soil_profile.set_theory)
        control_layout.addWidget(QLabel("Theory:"))
        control_layout.addWidget(theory_combo)

        self.layer_widget = SoilLayerWidget(self.soil_profile)
        control_layout.addWidget(self.layer_widget)

        self.visualization = SoilVisualization(self.soil_profile)
        layout.addWidget(self.visualization)


import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QLineEdit, QLabel, QPushButton, QComboBox, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox, QDialog, QDialogButtonBox,
                               QScrollArea)
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, Signal, QObject


class SurchargeLoad:
    def __init__(self, load_type, properties):
        self.load_type = load_type
        self.properties = properties


class SurchargeProfile(QObject):
    load_changed = Signal()

    def __init__(self):
        super().__init__()
        self.loads = []
        self.ka_surcharge = 1.0

    def add_load(self, load_type, properties):
        self.loads.append(SurchargeLoad(load_type, properties))
        self.load_changed.emit()

    def remove_load(self, index):
        if 0 <= index < len(self.loads):
            del self.loads[index]
            self.load_changed.emit()

    def update_load(self, index, load_type, properties):
        if 0 <= index < len(self.loads):
            self.loads[index] = SurchargeLoad(load_type, properties)
            self.load_changed.emit()

    def set_ka_surcharge(self, value):
        self.ka_surcharge = value
        self.load_changed.emit()

    def to_dict(self):
        return {
            "ka_surcharge": self.ka_surcharge,
            "loads": [
                {
                    "load_type": load.load_type,
                    "properties": load.properties
                } for load in self.loads
            ]
        }


class SurchargeLoadDialog(QDialog):
    def __init__(self, load=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Surcharge Load")
        self.layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.load_type_combo = QComboBox()
        self.load_type_combo.addItems(["Uniform", "Point Load", "Line Load", "Strip Load"])
        self.load_type_combo.currentTextChanged.connect(self.update_form)
        self.form.addRow("Load Type:", self.load_type_combo)

        self.property_inputs = {}
        self.layout.addLayout(self.form)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        if load:
            self.load_type_combo.setCurrentText(load.load_type)
            self.update_form(load.load_type)
            for key, value in load.properties.items():
                if key in self.property_inputs:
                    self.property_inputs[key].setText(str(value))
        else:
            self.update_form("Uniform")

    def update_form(self, load_type):
        for i in reversed(range(1, self.form.rowCount())):
            self.form.removeRow(i)

        self.property_inputs.clear()
        common_fields = ["q", "Surcharge Effect Depth"]

        if load_type == "Uniform":
            fields = common_fields
        elif load_type in ["Point Load", "Line Load"]:
            fields = common_fields + ["l"]
        elif load_type == "Strip Load":
            fields = common_fields + ["l1", "l2"]

        for field in fields:
            self.property_inputs[field] = QLineEdit()
            self.form.addRow(f"{field}:", self.property_inputs[field])

    def get_values(self):
        load_type = self.load_type_combo.currentText()
        properties = {field: float(input.text()) for field, input in self.property_inputs.items()}
        return load_type, properties


class SurchargeWidget(QGroupBox):
    def __init__(self, surcharge_profile):
        super().__init__("Surcharge Loads")
        self.surcharge_profile = surcharge_profile
        self.surcharge_profile.load_changed.connect(self.update_view)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.ka_surcharge_input = QLineEdit(str(self.surcharge_profile.ka_surcharge))
        self.ka_surcharge_input.textChanged.connect(self.update_ka_surcharge)
        layout.addWidget(QLabel("Ka Surcharge:"))
        layout.addWidget(self.ka_surcharge_input)

        self.load_list = QListWidget()
        self.load_list.itemDoubleClicked.connect(self.edit_load)
        layout.addWidget(self.load_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Load")
        self.remove_button = QPushButton("Remove Load")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_load)
        self.remove_button.clicked.connect(self.remove_load)

        self.update_view()

    def update_view(self):
        self.load_list.clear()
        for i, load in enumerate(self.surcharge_profile.loads):
            self.load_list.addItem(f"Load {i + 1}: {load.load_type}")

    def add_load(self):
        dialog = SurchargeLoadDialog(parent=self)
        if dialog.exec():
            load_type, properties = dialog.get_values()
            self.surcharge_profile.add_load(load_type, properties)

    def remove_load(self):
        current_row = self.load_list.currentRow()
        if current_row >= 0:
            self.surcharge_profile.remove_load(current_row)

    def edit_load(self, item):
        index = self.load_list.row(item)
        load = self.surcharge_profile.loads[index]
        dialog = SurchargeLoadDialog(load, parent=self)
        if dialog.exec():
            load_type, properties = dialog.get_values()
            self.surcharge_profile.update_load(index, load_type, properties)

    def update_ka_surcharge(self, value):
        try:
            self.surcharge_profile.set_ka_surcharge(float(value))
        except ValueError:
            pass


class LaggingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        self.ph_max_input = QLineEdit()
        layout.addRow("Ph max:", self.ph_max_input)

        self.fb_input = QLineEdit()
        layout.addRow("Fb:", self.fb_input)

        self.timber_size_combo = QComboBox()
        self.timber_size_combo.addItems(["2 x 12", "3 x 12", "4 x 12"])  # Add more sizes as needed
        layout.addRow("Timber Size:", self.timber_size_combo)

    def to_dict(self):
        return {
            "ph_max": self.ph_max_input.text(),
            "fb": self.fb_input.text(),
            "timber_size": self.timber_size_combo.currentText()
        }


from PySide6.QtWidgets import QFileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shoring System Design")
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.general_info_tab = self.create_general_info_tab()
        self.general_properties_tab = self.create_general_properties_tab()
        self.geo_soil_tab = GeometricalSoilPropertiesTab()
        # self.shoring_preview = ShoringPreview(self.geo_soil_tab.soil_profile)
        # main_layout.addWidget(self.shoring_preview)

        # Connect the layer_changed signal to update the preview
        # self.geo_soil_tab.soil_profile.layer_changed.connect(self.shoring_preview.update_preview)
        self.surcharge_tab = self.create_surcharge_tab()
        self.lagging_tab = LaggingTab()

        self.tab_widget.addTab(self.geo_soil_tab, "Geometrical and Soil Properties")
        self.tab_widget.addTab(self.surcharge_tab, "Surcharge")
        self.tab_widget.addTab(self.lagging_tab, "Lagging")

        button_layout = QHBoxLayout()
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(calculate_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_data)
        button_layout.addWidget(load_button)

        main_layout.addLayout(button_layout)

    def create_general_info_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        fields = ["Title", "Job No", "Designer", "Checker", "Company", "Client", "Unit", "Date", "Comment"]
        self.general_info_inputs = {}
        for field in fields:
            self.general_info_inputs[field] = QLineEdit()
            layout.addRow(field, self.general_info_inputs[field])

        self.tab_widget.addTab(tab, "General Information")
        return tab

    def create_general_properties_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        fields = ["FS", "E", "Pile Spacing", "Fy", "Allowable Deflection"]
        self.general_properties_inputs = {}

        for field in fields:
            self.general_properties_inputs[field] = QLineEdit()
            layout.addRow(field, self.general_properties_inputs[field])

        # Sections combo
        self.sections_combo = QComboBox()
        layout.addRow("Sections", self.sections_combo)

        # Populate sections from sections_dict
        for section_name in sections_dict.keys():
            self.sections_combo.addItem(section_name)

        # Alternatively, you can do a sorted list:
        # for section_name in sorted(sections_dict.keys()):
        #     self.sections_combo.addItem(section_name)

        self.tab_widget.addTab(tab, "General Properties")
        return tab

    def create_surcharge_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        self.surcharge_profile = SurchargeProfile()
        self.surcharge_widget = SurchargeWidget(self.surcharge_profile)
        layout.addWidget(self.surcharge_widget)

        return tab

    def calculate(self):
        """
        Gathers all user data (including selected steel section) and prints or stores it.
        """
        # 1. Collect general info from tab "General Information"
        general_info_data = {field: input.text() for field, input in self.general_info_inputs.items()}
        # 2. Collect general properties from tab "General Properties"
        gen_props_data = {}
        for field, input_widget in self.general_properties_inputs.items():
            gen_props_data[field] = input_widget.text()

        # 3. Identify which steel section the user picked
        selected_section = self.sections_combo.currentText()
        # Retrieve that shape's properties from sections_dict
        steel_props = sections_dict.get(selected_section, {})

        # 4. Collect soil data
        soil_data = self.geo_soil_tab.soil_profile.to_dict()  # from your existing code

        # 5. Collect surcharge data
        surcharge_data = self.surcharge_profile.to_dict()  # from your existing code

        # 6. Collect lagging data
        lagging_data = self.lagging_tab.to_dict()  # from your existing code

        # 7. Combine everything into a single dictionary
        all_data = data = {
            "general_info": general_info_data,
            "general_properties": gen_props_data,
            "selected_section": selected_section,
            "section_properties": steel_props,
            "soil_profile": soil_data,
            "surcharge": surcharge_data,
            "lagging": lagging_data
        }

        # 8. Print or save the combined data
        # For now, let's just print to the console.
        import json
        print(json.dumps(all_data, indent=2))
        handle_input(data)

    def get_all_data(self):
        return {
            "general_info": {field: input.text() for field, input in self.general_info_inputs.items()},
            "general_properties": {field: input.text() for field, input in self.general_properties_inputs.items()},
            "sections": self.sections_combo.currentText(),
            "soil_profile": self.geo_soil_tab.soil_profile.to_dict(),
            "surcharge": self.surcharge_profile.to_dict(),
            "lagging": self.lagging_tab.to_dict()
        }

    def save_data(self):
        data = self.get_all_data()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
            self.populate_ui_with_data(data)

    def populate_ui_with_data(self, data):
        # Populate General Info
        for field, value in data['general_info'].items():
            if field in self.general_info_inputs:
                self.general_info_inputs[field].setText(value)

        # Populate General Properties
        for field, value in data['general_properties'].items():
            if field in self.general_properties_inputs:
                self.general_properties_inputs[field].setText(value)

        # Set Sections
        index = self.sections_combo.findText(data['sections'])
        if index >= 0:
            self.sections_combo.setCurrentIndex(index)

        # Populate Soil Profile
        theory_name = data['soil_profile']['theory']
        try:
            self.geo_soil_tab.soil_profile.set_theory(theory_name.get("name"))
        except ValueError:
            QMessageBox.warning(self, "Warning",
                                f"Unknown soil theory: {theory_name}. Using User Defined theory instead.")
            self.geo_soil_tab.soil_profile.set_theory("User Defined")

        for layer in data['soil_profile']['layers']:
            self.geo_soil_tab.soil_profile.add_layer(layer['height'], layer['properties'])

        # Populate Surcharge
        self.surcharge_profile.set_ka_surcharge(data['surcharge']['ka_surcharge'])
        for load in data['surcharge']['loads']:
            self.surcharge_profile.add_load(load['load_type'], load['properties'])

        # Populate Lagging
        self.lagging_tab.ph_max_input.setText(data['lagging']['ph_max'])
        self.lagging_tab.fb_input.setText(data['lagging']['fb'])
        index = self.lagging_tab.timber_size_combo.findText(data['lagging']['timber_size'])
        if index >= 0:
            self.lagging_tab.timber_size_combo.setCurrentIndex(index)

        # Update views
        self.geo_soil_tab.layer_widget.update_view()
        self.geo_soil_tab.visualization.update_view()
        self.surcharge_widget.update_view()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

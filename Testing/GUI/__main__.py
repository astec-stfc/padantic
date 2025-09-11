import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QComboBox,
)

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="../../../padantic-clara/CLARA/layouts.yaml",
    section_file="../../../padantic-clara/CLARA/sections.yaml",
    yaml_dir="../../../padantic-clara/CLARA/YAML/",
)


class ElementWidget(QWidget):
    def __init__(self, element):
        super().__init__()

        self.element = element

        self.layout = QVBoxLayout()

        self.name_label = QLabel(f"Name: {self.element.name}")
        self.type_label = QLabel(f"Type: {self.element.type}")
        self.position_label = QLabel(f"Position: {self.physical.position}")

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.position_label)

        self.setLayout(self.layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pydantic Model Comparator")

        self.layout = QVBoxLayout()

        self.model_a_layout = QVBoxLayout()
        self.model_b_layout = QVBoxLayout()

        self.element_a_dropdown = QComboBox()
        self.element_a_dropdown.addItems(
            [element for element in machine.get_all_elements()]
        )
        self.model_a_layout.addWidget(self.element_a_dropdown)

        self.element_b_dropdown = QComboBox()
        self.element_b_dropdown.addItems(
            [element for element in machine.get_all_elements()]
        )
        self.model_b_layout.addWidget(self.element_b_dropdown)

        # self.compare_button = QPushButton("Compare Models")
        # self.compare_button.clicked.connect(self.compare_models)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        self.models_layout = QHBoxLayout()
        self.models_layout.addLayout(self.model_a_layout)
        self.models_layout.addLayout(self.model_b_layout)

        self.layout.addLayout(self.models_layout)
        # self.layout.addWidget(self.compare_button)
        self.layout.addWidget(self.result_text)

        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

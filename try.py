from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QInputDialog,QMessageBox
import sys

class Item:
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender
        self.checked = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.items = []

        # UI elements
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.gender_combobox = QComboBox()
        self.gender_combobox.addItems(["Male", "Female", "Other"])
        self.add_button = QPushButton("Add Item")
        self.remove_button = QPushButton("Remove Selected Items")
        self.filter_button = QPushButton("Filter Items")
        self.show_selected_button = QPushButton("Show Selected Items")
        self.list_widget = QListWidget()

        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Age:"))
        input_layout.addWidget(self.age_input)
        input_layout.addWidget(QLabel("Gender:"))
        input_layout.addWidget(self.gender_combobox)
        input_layout.addWidget(self.add_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.filter_button)
        button_layout.addWidget(self.show_selected_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Signals
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.filter_button.clicked.connect(self.filter_items)
        self.show_selected_button.clicked.connect(self.show_selected_items)
        self.list_widget.itemChanged.connect(self.update_check_state)

        # preset items
        self.add_item(["mark","20","Male"])
        self.add_item(["cindy","15","Female"])
        self.add_item(["bob","27","Male"])
        self.add_item(["steve","15","Male"])
        self.add_item(["lisa","10","Female"])


    def update_check_state(self, item):
        row = self.list_widget.row(item)
        self.items[row].checked = item.checkState() == 2

    def add_item(self, attr=None):
        if not attr:
            name = self.name_input.text().strip()
            age = self.age_input.text().strip()
            gender = self.gender_combobox.currentText().strip()
        else:
            name = attr[0]
            age = attr[1]
            gender = attr[2]

        if name and age and gender:
            item = Item(name, age, gender)
            self.items.append(item)
            list_item = QListWidgetItem(f"{item.name} ({item.age}, {item.gender})")
            list_item.setCheckState(2 if item.checked else 0)
            self.list_widget.addItem(list_item)

    def remove_item(self):
        remove_indices = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                remove_indices.append(i)

        for i in reversed(remove_indices):
            self.list_widget.takeItem(i)
            del self.items[i]

    def filter_items(self):
        age_range, ok = QInputDialog.getText(self, "Filter Items", "Enter age range (e.g. 20-30):")
        if ok:
            age_range = age_range.strip()
            if age_range:
                age_range = age_range.split("-")
                min_age = int(age_range[0])
                max_age = int(age_range[1]) if len(age_range) > 1 and age_range[1] else float("inf")
                # self.list_widget.clear()
                # for item in self.items:
                #     if min_age <= int(item.age) <= max_age:
                #         list_item = QListWidgetItem(f"{item.name} ({item.age}, {item.gender})")
                #         list_item.setCheckState(2 if item.checked else 0)
                #         self.list_widget.addItem(list_item)
                #     else:
                #         item.checked = False
        gender, ok = QInputDialog.getItem(self, "Show Selected Items", "Select gender:", ["", "Male", "Female", "Other"])
        self.list_widget.clear()
        for item in self.items:
            age_pass = True
            gender_pass = True
            if age_range and min_age <= int(item.age) <= max_age:
                age_pass = False
            if gender and item.gender != gender:
                gender_pass = False
            if age_pass and gender_pass:
                list_item = QListWidgetItem(f"{item.name} ({item.age}, {item.gender})")
                list_item.setCheckState(2 if item.checked else 0)
                self.list_widget.addItem(list_item)
            else:
                item.checked = False

    def show_selected_items(self):
        selected_items = []
        for item in self.items:
            if item.checked:
                selected_items.append(item)

        if selected_items:
            selected_items_str = "\n".join([f"{item.name}: {item.age}, {item.gender}" for item in selected_items])
            QMessageBox.information(self, "Selected Items", selected_items_str)
        else:
            QMessageBox.information(self, "Selected Items", "No items selected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
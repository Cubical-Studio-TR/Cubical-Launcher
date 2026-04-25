import sys, os, json, subprocess
try:
    import minecraft_launcher_lib
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QComboBox, QLineEdit, QPushButton, 
                                 QLabel, QListWidget, QFrame, QListWidgetItem, QRadioButton, QButtonGroup)
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QColor
except ImportError:
    print("[CMD] Gerekli kütüphaneler eksik.")
    sys.exit()

class LaunchThread(QThread):
    status_update = Signal(str)
    finished = Signal()

    def __init__(self, version, username, base_dir, mod_type):
        super().__init__()
        self.version = version; self.username = username
        self.base_dir = base_dir; self.mod_type = mod_type

    def run(self):
        try:
            target_version = self.version
            if "FORGE" not in target_version and "FABRIC" not in target_version:
                if self.mod_type == "Forge":
                    self.status_update.emit("FORGE KURULUYOR...")
                    forge_ver = minecraft_launcher_lib.forge.find_forge_version(self.version)
                    if forge_ver:
                        minecraft_launcher_lib.forge.install_forge_version(forge_ver, self.base_dir)
                        target_version = forge_ver
                elif self.mod_type == "Fabric":
                    self.status_update.emit("FABRIC KURULUYOR...")
                    minecraft_launcher_lib.fabric.install_fabric(self.version, self.base_dir)
                    for v in minecraft_launcher_lib.utils.get_installed_versions(self.base_dir):
                        if "fabric" in v['id'].lower() and self.version in v['id']:
                            target_version = v['id']; break

            self.status_update.emit("MOTOR ATEŞLENİYOR...")
            minecraft_launcher_lib.install.install_minecraft_version(target_version, self.base_dir)
            options = {"username": self.username, "uuid": "0", "token": "0", "jvmArguments": ["-Xmx4G"]}
            command = minecraft_launcher_lib.command.get_minecraft_command(target_version, self.base_dir, options)
            subprocess.Popen(command)
            self.status_update.emit("OYUN AÇILDI")
        except Exception as e:
            self.status_update.emit(f"HATA: {str(e)[:20]}")
        self.finished.emit()

class CubiLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cubi Launcher V28")
        self.setFixedSize(950, 750)
        self.base_dir = os.path.join(os.getenv('APPDATA'), ".cubilauncher")
        self.acc_file = os.path.join(self.base_dir, "accounts.json")
        if not os.path.exists(self.base_dir): os.makedirs(self.base_dir)

        self.setStyleSheet("""
            * { font-family: 'Segoe UI'; font-weight: 900; color: #00d4ff; }
            QMainWindow { background-color: #050a14; }
            QListWidget { background-color: #0a1221; border: 3px solid #00d4ff; }
            QListWidget::item:selected { background-color: #00d4ff; color: #000; }
            QLineEdit, QComboBox { background-color: #0a1221; border: 2px solid #00d4ff; padding: 8px; }
            QPushButton { background-color: #112240; border: 2px solid #00d4ff; padding: 10px; }
            QPushButton:hover { background-color: #00d4ff; color: #050a14; }
            #PlayBtn { background-color: #005f73; font-size: 30px; color: white; border-radius: 10px; }
            #PlayBtn:disabled { background-color: #222; border-color: #444; color: #666; }
        """)

        self.init_ui()
        self.load_accounts()
        self.refresh_versions()

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # SOL: HESAP YÖNETİCİSİ
        side = QFrame(); side.setFixedWidth(280); s_lay = QVBoxLayout(side)
        s_lay.addWidget(QLabel("HESAP YÖNETİCİSİ"))
        self.acc_list = QListWidget(); s_lay.addWidget(self.acc_list)
        self.u_in = QLineEdit(); self.u_in.setPlaceholderText("Kullanıcı Adı..."); s_lay.addWidget(self.u_in)
        btn_add = QPushButton("HESABI KAYDET"); btn_add.clicked.connect(self.add_acc); s_lay.addWidget(btn_add)
        btn_del = QPushButton("HESABI SİL"); btn_del.clicked.connect(self.delete_acc); s_lay.addWidget(btn_del)
        s_lay.addStretch()

        # SAĞ: SİSTEM
        main_v = QVBoxLayout()
        
        mode_group = QFrame(); mode_group.setStyleSheet("border: 1px solid #112240;")
        mode_lay = QVBoxLayout(mode_group)
        self.radio_offline = QRadioButton("YÜKLÜ SÜRÜMLER (OFFLINE)"); self.radio_offline.setChecked(True)
        self.radio_online = QRadioButton("TÜM SÜRÜMLER (ONLINE)")
        self.installed_box = QComboBox(); self.all_ver_box = QComboBox(); self.all_ver_box.setEnabled(False)
        self.radio_offline.toggled.connect(self.toggle_modes)
        mode_lay.addWidget(self.radio_offline); mode_lay.addWidget(self.installed_box)
        mode_lay.addWidget(self.radio_online); mode_lay.addWidget(self.all_ver_box)
        
        main_v.addWidget(QLabel("VERİ YOLU"))
        self.path_disp = QLineEdit(self.base_dir); self.path_disp.setReadOnly(True); main_v.addWidget(self.path_disp)
        main_v.addStretch()
        main_v.addWidget(QLabel("SÜRÜM SEÇİMİ"))
        main_v.addWidget(mode_group)
        
        main_v.addWidget(QLabel("MOTOR TİPİ"))
        self.type_box = QComboBox(); self.type_box.addItems(["Vanilla", "Forge", "Fabric"]); main_v.addWidget(self.type_box)
        
        self.status = QLabel("BAŞLATMAYA HAZIR"); self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.play_btn = QPushButton("BAŞLAT"); self.play_btn.setObjectName("PlayBtn")
        self.play_btn.setFixedHeight(100); self.play_btn.clicked.connect(self.launch)
        main_v.addWidget(self.status); main_v.addWidget(self.play_btn)

        layout.addWidget(side); layout.addLayout(main_v)

    def toggle_modes(self):
        is_off = self.radio_offline.isChecked()
        self.installed_box.setEnabled(is_off); self.all_ver_box.setEnabled(not is_off)

    def add_acc(self):
        name = self.u_in.text().strip()
        if name and self.acc_list.count() < 7:
            item = QListWidgetItem(name); item.setForeground(QColor("#00d4ff"))
            self.acc_list.addItem(item); self.save_accounts(); self.u_in.clear()

    def delete_acc(self):
        curr = self.acc_list.currentRow()
        if curr >= 0: self.acc_list.takeItem(curr); self.save_accounts()

    def save_accounts(self):
        accs = [self.acc_list.item(i).text() for i in range(self.acc_list.count())]
        with open(self.acc_file, "w") as f: json.dump(accs, f)

    def load_accounts(self):
        if os.path.exists(self.acc_file):
            try:
                with open(self.acc_file, "r") as f:
                    for a in json.load(f):
                        item = QListWidgetItem(a); item.setForeground(QColor("#00d4ff"))
                        self.acc_list.addItem(item)
            except: pass

    def refresh_versions(self):
        self.installed_box.clear()
        v_path = os.path.join(self.base_dir, "versions")
        if os.path.exists(v_path):
            for v_dir in os.listdir(v_path):
                tag = "NORMAL"
                if "forge" in v_dir.lower(): tag = "FORGE"
                elif "fabric" in v_dir.lower(): tag = "FABRIC"
                
                if os.path.exists(os.path.join(v_path, v_dir, f"{v_dir}.jar")):
                    self.installed_box.addItem(f"{v_dir} [{tag}]", v_dir)
        try:
            v_list = [x['id'] for x in minecraft_launcher_lib.utils.get_version_list() if x['type'] == 'release']
            self.all_ver_box.addItems(v_list)
        except: self.status.setText("İNTERNET YOK")

    def launch(self):
        # 🛡️ KRİTİK KONTROLLER
        if self.acc_list.count() == 0:
            self.status.setText("HATA: HESAP YOK!")
            return
        if not self.acc_list.currentItem():
            self.status.setText("HATA: HESAP SEÇ!")
            return
        
        if self.radio_offline.isChecked():
            version = self.installed_box.currentData()
        else:
            version = self.all_ver_box.currentText()
            
        if not version or version == "":
            self.status.setText("HATA: SÜRÜM YOK!")
            return

        self.play_btn.setEnabled(False)
        self.status.setText("SİSTEM ÇALIŞIYOR...")
        self.thread = LaunchThread(version, self.acc_list.currentItem().text(), self.base_dir, self.type_box.currentText())
        self.thread.status_update.connect(self.status.setText)
        self.thread.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CubiLauncher(); w.show()
    sys.exit(app.exec())
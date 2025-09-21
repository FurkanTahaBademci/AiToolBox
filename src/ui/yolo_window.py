"""
YOLO Analiz Penceresi
YOLO formatındaki dosyaları analiz etmek için ayrı pencere
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QPushButton, QLabel, QLineEdit, QTextEdit, 
                            QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                            QTabWidget, QWidget, QProgressBar, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from ..core.yolo_analyzer import YoloAnalyzer
from ..utils.helpers import app_logger
from .styles import AppStyles

class YoloAnalysisWorker(QThread):
    """YOLO analizi için worker thread"""
    
    progress_updated = pyqtSignal(int)
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.analyzer = YoloAnalyzer()
    
    def run(self):
        try:
            self.progress_updated.emit(10)
            results = self.analyzer.analyze_folder(self.folder_path)
            self.progress_updated.emit(100)
            self.analysis_completed.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))

class YoloAnalysisWindow(QDialog):
    """YOLO analiz penceresi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = YoloAnalyzer()
        self.current_results = None
        self.worker = None
        
        self.setWindowTitle("🎯 YOLO Format Analizi")
        self.setFixedSize(900, 700)
        self.setModal(True)
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """UI'ı oluştur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title_label = QLabel("🎯 YOLO Format Analizi")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {AppStyles.COLORS['primary']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Klasör seçimi
        folder_group = self.create_folder_selection_group()
        layout.addWidget(folder_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Sonuçlar tabı
        self.results_tabs = QTabWidget()
        self.setup_results_tabs()
        layout.addWidget(self.results_tabs)
        
        # Kontrol butonları
        buttons_layout = self.create_buttons_layout()
        layout.addLayout(buttons_layout)
        
    def create_folder_selection_group(self):
        """Klasör seçimi grubunu oluştur"""
        group = QGroupBox("📁 Analiz Klasörü")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("YOLO .txt dosyalarının bulunduğu klasörü seçin...")
        self.folder_path_edit.setReadOnly(True)
        
        browse_button = QPushButton("📁 Klasör Seç")
        browse_button.clicked.connect(self.browse_folder)
        
        analyze_button = QPushButton("🔍 Analiz Et")
        analyze_button.clicked.connect(self.start_analysis)
        
        layout.addWidget(self.folder_path_edit)
        layout.addWidget(browse_button)
        layout.addWidget(analyze_button)
        
        return group
        
    def setup_results_tabs(self):
        """Sonuç tablarını oluştur"""
        # Genel istatistikler tabı
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout(self.general_tab)
        self.general_text = QTextEdit()
        self.general_text.setReadOnly(True)
        self.general_layout.addWidget(self.general_text)
        self.results_tabs.addTab(self.general_tab, "📊 Genel İstatistikler")
        
        # Sınıf detayları tabı
        self.class_tab = QWidget()
        self.class_layout = QVBoxLayout(self.class_tab)
        self.class_table = QTableWidget()
        self.class_layout.addWidget(self.class_table)
        self.results_tabs.addTab(self.class_tab, "🏷️ Sınıf Detayları")
        
        # Dosya detayları tabı
        self.files_tab = QWidget()
        self.files_layout = QVBoxLayout(self.files_tab)
        self.files_table = QTableWidget()
        self.files_layout.addWidget(self.files_table)
        self.results_tabs.addTab(self.files_tab, "📄 Dosya Detayları")
        
        # Hatalar tabı
        self.errors_tab = QWidget()
        self.errors_layout = QVBoxLayout(self.errors_tab)
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.errors_layout.addWidget(self.errors_text)
        self.results_tabs.addTab(self.errors_tab, "⚠️ Hatalar")
        
    def create_buttons_layout(self):
        """Kontrol butonlarını oluştur"""
        layout = QHBoxLayout()
        
        export_csv_button = QPushButton("💾 CSV Dışa Aktar")
        export_csv_button.clicked.connect(self.export_csv)
        
        close_button = QPushButton("❌ Kapat")
        close_button.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(export_csv_button)
        layout.addWidget(close_button)
        
        return layout
        
    def browse_folder(self):
        """Klasör seçme diyalogu"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "YOLO Dosyalarının Bulunduğu Klasörü Seçin",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.folder_path_edit.setText(folder)
            
    def start_analysis(self):
        """Analizi başlat"""
        folder_path = self.folder_path_edit.text().strip()
        
        if not folder_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek klasörü seçin!")
            return
            
        if not os.path.exists(folder_path):
            QMessageBox.critical(self, "Hata", "Seçilen klasör mevcut değil!")
            return
        
        # Progress bar'ı göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Worker thread'i başlat
        self.worker = YoloAnalysisWorker(folder_path)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.analysis_completed.connect(self.on_analysis_completed)
        self.worker.error_occurred.connect(self.on_analysis_error)
        self.worker.start()
        
    def on_analysis_completed(self, results):
        """Analiz tamamlandığında çağrılır"""
        self.current_results = results
        self.progress_bar.setVisible(False)
        self.display_results(results)
        
        # Sonuç mesajını farklılaştır
        if results['total_files'] == 0:
            QMessageBox.warning(
                self, 
                "Uyarı", 
                "Seçilen klasörde hiç .txt dosyası bulunamadı!\n\n"
                "YOLO format dosyalarının .txt uzantılı olduğundan emin olun."
            )
        elif results['total_objects'] == 0:
            QMessageBox.information(
                self, 
                "Bilgi", 
                f"Analiz tamamlandı!\n\n"
                f"📁 Toplam dosya: {results['total_files']}\n"
                f"⚠️ Hiçbir dosyada nesne bulunamadı"
            )
        else:
            QMessageBox.information(
                self, 
                "Başarılı", 
                f"Analiz tamamlandı!\n\n"
                f"📁 Toplam dosya: {results['total_files']}\n"
                f"🎯 Toplam nesne: {results['total_objects']}\n"
                f"🏷️ Farklı sınıf: {len(results['class_counts'])}"
            )
        
    def on_analysis_error(self, error_message):
        """Analiz hatası oluştuğunda çağrılır"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Analiz Hatası", f"Analiz sırasında hata oluştu:\n\n{error_message}")
        
    def display_results(self, results):
        """Sonuçları görüntüle"""
        self.display_general_stats(results)
        self.display_class_details(results)
        self.display_file_details(results)
        self.display_errors(results)
        
    def display_general_stats(self, results):
        """Genel istatistikleri görüntüle"""
        stats_text = f"""
📊 YOLO Analiz Raporu
{'='*50}

📁 Dosya İstatistikleri:
• Toplam dosya sayısı: {results['total_files']}
• Nesne içeren dosyalar: {results['files_with_objects']}
• Boş dosyalar: {results['empty_files']}

🎯 Nesne İstatistikleri:
• Toplam nesne sayısı: {results['total_objects']:,}
• Dosya başına ortalama: {results['avg_objects_per_file']}
• Farklı sınıf sayısı: {len(results['class_counts'])}

🏷️ Sınıf Dağılımı:"""

        if results['most_common_class']:
            most_class, most_count = results['most_common_class']
            stats_text += f"\n• En çok bulunan sınıf: Class {most_class} ({most_count:,} adet)"
            
        if results['least_common_class']:
            least_class, least_count = results['least_common_class']
            stats_text += f"\n• En az bulunan sınıf: Class {least_class} ({least_count:,} adet)"

        if results['error_files']:
            stats_text += f"\n\n⚠️ Hatalar:\n• {len(results['error_files'])} dosyada hata tespit edildi"

        self.general_text.setPlainText(stats_text)
        
    def display_class_details(self, results):
        """Sınıf detaylarını tablo halinde görüntüle"""
        class_counts = results['class_counts']
        class_percentages = results['class_percentages']
        
        self.class_table.setRowCount(len(class_counts))
        self.class_table.setColumnCount(3)
        self.class_table.setHorizontalHeaderLabels(['Sınıf ID', 'Nesne Sayısı', 'Yüzde (%)'])
        
        for row, class_id in enumerate(sorted(class_counts.keys())):
            count = class_counts[class_id]
            percentage = class_percentages[class_id]
            
            self.class_table.setItem(row, 0, QTableWidgetItem(f"Class {class_id}"))
            self.class_table.setItem(row, 1, QTableWidgetItem(f"{count:,}"))
            self.class_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.2f}%"))
            
        self.class_table.resizeColumnsToContents()
        
    def display_file_details(self, results):
        """Dosya detaylarını görüntüle"""
        file_details = results.get('file_details', {})  # Güvenli erişim
        
        if not file_details:
            # Boş durum için tablo başlıklarını ayarla
            self.files_table.setRowCount(1)
            self.files_table.setColumnCount(2)
            self.files_table.setHorizontalHeaderLabels(['Dosya Adı', 'Nesne Sayısı'])
            self.files_table.setItem(0, 0, QTableWidgetItem("Hiç dosya bulunamadı"))
            self.files_table.setItem(0, 1, QTableWidgetItem("-"))
            self.files_table.resizeColumnsToContents()
            return
        
        self.files_table.setRowCount(len(file_details))
        self.files_table.setColumnCount(2)
        self.files_table.setHorizontalHeaderLabels(['Dosya Adı', 'Nesne Sayısı'])
        
        for row, (filename, count) in enumerate(sorted(file_details.items())):
            self.files_table.setItem(row, 0, QTableWidgetItem(filename))
            self.files_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
        self.files_table.resizeColumnsToContents()
        
    def display_errors(self, results):
        """Hataları görüntüle"""
        error_files = results['error_files']
        
        if not error_files:
            self.errors_text.setPlainText("✅ Hiçbir dosyada hata bulunamadı!")
            return
            
        error_text = "⚠️ Aşağıdaki dosyalarda hatalar tespit edildi:\n\n"
        
        for error_info in error_files:
            error_text += f"📄 {error_info['file']}\n"
            error_text += f"   ❌ Hata: {error_info['error']}\n\n"
            
        self.errors_text.setPlainText(error_text)
        
    def export_csv(self):
        """CSV olarak dışa aktar"""
        if not self.current_results:
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapmalısınız!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSV Raporu Kaydet",
            "yolo_analiz_raporu.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.analyzer.export_to_csv(file_path, self.current_results)
                QMessageBox.information(self, "Başarılı", f"Rapor kaydedildi:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Rapor kaydedilirken hata oluştu:\n{str(e)}")
                
    def apply_styles(self):
        """Stilleri uygula"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppStyles.COLORS['white']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: {AppStyles.COLORS['white']};
            }}
            QPushButton {{
                background-color: {AppStyles.COLORS['primary']};
                color: {AppStyles.COLORS['white']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: {AppStyles.COLORS['primary_darker']};
            }}
            QLineEdit {{
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: {AppStyles.COLORS['white']};
            }}
            QLineEdit:focus {{
                border-color: {AppStyles.COLORS['primary']};
            }}
            QTextEdit, QTableWidget {{
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 6px;
                background-color: {AppStyles.COLORS['white']};
                font-family: 'Consolas', monospace;
            }}
            QTabWidget::pane {{
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 6px;
                background-color: {AppStyles.COLORS['white']};
            }}
            QTabBar::tab {{
                background-color: {AppStyles.COLORS['gray_100']};
                border: 2px solid {AppStyles.COLORS['gray_300']};
                padding: 8px 16px;
                margin-right: 2px;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {AppStyles.COLORS['white']};
                border-color: {AppStyles.COLORS['primary']};
            }}
        """)

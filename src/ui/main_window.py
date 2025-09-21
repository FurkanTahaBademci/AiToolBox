"""
Ana uygulama arayüzü
Modern ve kullanıcı dostu AI ToolBox
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                            QLineEdit, QSpinBox, QFileDialog, QProgressBar,
                            QGroupBox, QFrame, QMessageBox, QTextEdit, QSplitter, QComboBox, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

# Kendi modüllerimizi import et
from .styles import AppStyles
from .components import ModernButton, StatusLabel, InfoCard, ProgressCard, VideoInfoCard
from .yolo_window import YoloAnalysisWindow
from ..core.video_processor import VideoProcessor, VideoAnalyzer
from ..utils.helpers import app_logger, FileUtils, TimeUtils, ConfigManager

class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        
        # Uygulama değişkenleri
        self.video_path = ""
        self.output_path = ""
        self.video_info = None
        self.video_processor = VideoProcessor()
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.load_settings()
        
        # UI kurulumu
        self.init_ui()
        self.setup_connections()
        self.apply_styles()
        
        # Varsayılan değerleri yükle
        self.load_default_values()
        
        app_logger.info("Ana uygulama penceresi başlatıldı")
    
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("AI ToolBox v1.0.0")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Menü bar oluştur
        self.create_menu_bar()
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık alanı
        self.create_header(main_layout)
        
        # Ana içerik alanı (splitter ile böl)
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel (kontroller)
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Sağ panel (info ve log)
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Splitter oranları
        content_splitter.setStretchFactor(0, 3)  # Sol panel daha geniş
        content_splitter.setStretchFactor(1, 2)  # Sağ panel (log alanı) daha geniş
        
        main_layout.addWidget(content_splitter)
        
        # Alt kontrol çubuğu
        self.create_bottom_controls(main_layout)
    
    def create_menu_bar(self):
        """Menü barını oluştur"""
        menubar = self.menuBar()
        
        # Araçlar menüsü
        tools_menu = menubar.addMenu('🔧 Araçlar')
        
        # Video Frame Çıkarma (araç)
        video_action = tools_menu.addAction('🎬 Video Frame Çıkarma')
        video_action.setStatusTip('Video dosyalarından frame çıkarma aracı')
        video_action.triggered.connect(self.show_main_tool)
        
        tools_menu.addSeparator()
        
        # YOLO Analizi (araç)
        yolo_action = tools_menu.addAction('🎯 YOLO Format Analizi')
        yolo_action.setStatusTip('YOLO format dosyalarını analiz et')
        yolo_action.triggered.connect(self.open_yolo_analyzer)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('❓ Yardım')
        
        about_action = help_menu.addAction('ℹ️ Hakkında')
        about_action.triggered.connect(self.show_about)
    
    def create_header(self, main_layout):
        """Başlık alanını oluştur"""
        header_layout = QHBoxLayout()
        
        # Başlık
        self.title_label = QLabel("🤖 AI ToolBox")
        self.title_label.setStyleSheet(AppStyles.get_title_label_style())
        
        # Versiyon
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_500']};
                font-size: 12px;
                font-style: italic;
            }}
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        
        main_layout.addLayout(header_layout)
    
    def create_left_panel(self):
        """Sol panel (kontroller) oluştur"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Video seçimi
        left_layout.addWidget(self.create_video_selection_group())
        
        # Çıktı seçimi
        left_layout.addWidget(self.create_output_selection_group())
        
        # Frame ayarları
        left_layout.addWidget(self.create_frame_settings_group())
        
        left_layout.addStretch()
        
        return left_widget
    
    def create_right_panel(self):
        """Sağ panel (info ve log) oluştur"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        
        # Video bilgi kartı
        self.video_info_card = VideoInfoCard()
        right_layout.addWidget(self.video_info_card)
        
        # İlerleme kartı
        self.progress_card = ProgressCard()
        right_layout.addWidget(self.progress_card)
        
        # Log alanı
        right_layout.addWidget(self.create_log_group())
        
        return right_widget
    
    def create_video_selection_group(self):
        """Video seçimi grubunu oluştur"""
        group = QGroupBox("📁 Video Dosyası Seçimi")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Dosya seçim satırı
        file_layout = QHBoxLayout()
        
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setPlaceholderText("Lütfen işlemek istediğiniz video dosyasını seçin...")
        self.video_path_edit.setReadOnly(True)
        
        self.select_video_btn = ModernButton("📂 Video Seç", "secondary")
        self.select_video_btn.setFixedWidth(150)
        
        file_layout.addWidget(self.video_path_edit)
        file_layout.addWidget(self.select_video_btn)
        
        layout.addLayout(file_layout)
        
        return group
    
    def create_output_selection_group(self):
        """Çıktı seçimi grubunu oluştur"""
        group = QGroupBox("💾 Çıktı Konumu")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Klasör seçim satırı
        folder_layout = QHBoxLayout()
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Frame'lerin kaydedileceği klasörü seçin...")
        self.output_path_edit.setReadOnly(True)
        
        self.select_output_btn = ModernButton("📁 Klasör Seç", "secondary")
        self.select_output_btn.setFixedWidth(150)
        
        folder_layout.addWidget(self.output_path_edit)
        folder_layout.addWidget(self.select_output_btn)
        
        layout.addLayout(folder_layout)
        
        return group
    
    def create_frame_settings_group(self):
        """Frame ayarları grubunu oluştur"""
        group = QGroupBox("⚙️ Frame İşleme Ayarları")
        group.setMinimumHeight(400)  # Minimum yükseklik ayarı
        layout = QGridLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)  # Daha fazla margin
        
        # Frame aralığı
        layout.addWidget(QLabel("Frame Aralığı:"), 0, 0)
        self.frame_interval_spin = QSpinBox()
        self.frame_interval_spin.setMinimum(1)
        self.frame_interval_spin.setMaximum(10000)
        self.frame_interval_spin.setValue(int(self.settings.get('default_frame_interval', 30)))
        self.frame_interval_spin.setSuffix(" frame")
        self.frame_interval_spin.setToolTip("Her kaç frame'de bir görüntü alınacağını belirler")
        self.frame_interval_spin.setFixedHeight(35)  # Yükseklik ayarı
        layout.addWidget(self.frame_interval_spin, 0, 1)
        
        # Başlangıç frame
        layout.addWidget(QLabel("Başlangıç Frame:"), 1, 0)
        self.start_frame_spin = QSpinBox()
        self.start_frame_spin.setMinimum(0)
        self.start_frame_spin.setMaximum(9999999)
        self.start_frame_spin.setValue(0)
        self.start_frame_spin.setToolTip("İşlemenin başlayacağı frame numarası")
        self.start_frame_spin.setFixedHeight(35)  # Yükseklik ayarı
        layout.addWidget(self.start_frame_spin, 1, 1)
        
        # Bitiş frame
        layout.addWidget(QLabel("Bitiş Frame:"), 2, 0)
        self.end_frame_spin = QSpinBox()
        self.end_frame_spin.setMinimum(0)
        self.end_frame_spin.setMaximum(9999999)
        self.end_frame_spin.setValue(0)
        self.end_frame_spin.setSpecialValueText("Video sonuna kadar")
        self.end_frame_spin.setToolTip("İşlemenin biteceği frame numarası (0 = video sonu)")
        self.end_frame_spin.setFixedHeight(35)  # Yükseklik ayarı
        layout.addWidget(self.end_frame_spin, 2, 1)
        
        # Çıktı formatı
        layout.addWidget(QLabel("Çıktı Formatı:"), 3, 0)
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["JPEG (.jpg)", "PNG (.png)", "BMP (.bmp)"])
        self.output_format_combo.setCurrentText("JPEG (.jpg)")
        self.output_format_combo.setToolTip("Çıktı dosyalarının formatını seçin")
        self.output_format_combo.setFixedHeight(35)  # Yükseklik ayarı
        layout.addWidget(self.output_format_combo, 3, 1)
        
        # Çıktı kalitesi
        layout.addWidget(QLabel("Çıktı Kalitesi:"), 4, 0)
        self.output_quality_spin = QSpinBox()
        self.output_quality_spin.setMinimum(1)
        self.output_quality_spin.setMaximum(100)
        self.output_quality_spin.setValue(int(self.settings.get('jpeg_quality', 95)))
        self.output_quality_spin.setSuffix("%")
        self.output_quality_spin.setToolTip("Görüntü kalitesi (JPEG ve PNG için)")
        self.output_quality_spin.setFixedHeight(35)  # Yükseklik ayarı
        layout.addWidget(self.output_quality_spin, 4, 1)
        
        # Tahmin edilen frame sayısı
        self.estimated_frames_label = QLabel("Tahmini çıktı: Hesaplanıyor...")
        self.estimated_frames_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_900']};
                font-style: normal;
                font-weight: bold;
                font-size: 14px;
                padding: 15px 16px;
                background-color: {AppStyles.COLORS['gray_100']};
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 6px;
                min-height: 50px;
            }}
        """)
        layout.addWidget(self.estimated_frames_label, 5, 0, 1, 2)
        
        return group
    
    def create_log_group(self):
        """Log grubunu oluştur"""
        group = QGroupBox("📋 İşlem Logları")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Log kontrolleri
        log_controls = QHBoxLayout()
        
        clear_log_btn = ModernButton("🗑️ Temizle", "secondary")
        clear_log_btn.setFixedHeight(35)
        clear_log_btn.setFixedWidth(120)
        clear_log_btn.clicked.connect(self.clear_logs)
        
        log_controls.addStretch()
        log_controls.addWidget(clear_log_btn)
        
        layout.addLayout(log_controls)
        
        # Log metni
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(250)
        self.log_text.setMinimumHeight(200)
        self.log_text.setPlaceholderText("İşlem logları burada görünecek...")
        layout.addWidget(self.log_text)
        
        return group
    
    def create_bottom_controls(self, main_layout):
        """Alt kontrol çubuğunu oluştur"""
        controls_layout = QHBoxLayout()
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        
        # Kontrol butonları
        self.start_btn = ModernButton("▶️ İşlemi Başlat", "primary")
        self.start_btn.setEnabled(False)
        self.start_btn.setFixedWidth(150)
        
        self.stop_btn = ModernButton("⏹️ Durdur", "danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedWidth(130)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(controls_layout)
    
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        # Buton bağlantıları
        self.select_video_btn.clicked.connect(self.select_video)
        self.select_output_btn.clicked.connect(self.select_output)
        self.start_btn.clicked.connect(self.start_processing)
        self.stop_btn.clicked.connect(self.stop_processing)
        
        # SpinBox değişim bağlantıları
        self.frame_interval_spin.valueChanged.connect(self.update_estimated_frames)
        self.start_frame_spin.valueChanged.connect(self.update_estimated_frames)
        self.end_frame_spin.valueChanged.connect(self.update_estimated_frames)
        self.output_format_combo.currentTextChanged.connect(self.on_format_changed)
        self.output_quality_spin.valueChanged.connect(self.on_quality_changed)
        
        # Video processor bağlantıları
        self.video_processor.progress_updated.connect(self.update_progress)
        self.video_processor.status_updated.connect(self.update_status)
        self.video_processor.log_updated.connect(self.add_log)
        self.video_processor.frame_processed.connect(self.on_frame_processed)
        self.video_processor.finished.connect(self.processing_finished)
    
    def apply_styles(self):
        """Stilleri uygula"""
        self.setStyleSheet(AppStyles.get_complete_stylesheet())
    
    def load_default_values(self):
        """Varsayılan değerleri yükle"""
        # Son kullanılan dizinleri ayarla
        last_video_dir = self.settings.get('last_video_dir', os.path.expanduser('~'))
        last_output_dir = self.settings.get('last_output_dir', os.path.expanduser('~'))
        
        app_logger.info(f"Varsayılan dizinler yüklendi: Video={last_video_dir}, Çıktı={last_output_dir}")
    
    def select_video(self):
        """Video dosyası seç"""
        last_dir = self.settings.get('last_video_dir', os.path.expanduser('~'))
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Video Dosyası Seçin", 
            last_dir,
            "Video Dosyaları (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.m4v *.3gp);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            # Dosya doğrulama
            is_valid, message = FileUtils.validate_video_file(file_path)
            if not is_valid:
                QMessageBox.warning(self, "Geçersiz Dosya", f"Seçilen dosya geçerli değil:\n{message}")
                return
            
            self.video_path = file_path
            self.video_path_edit.setText(file_path)
            
            # Son dizini kaydet
            self.settings['last_video_dir'] = os.path.dirname(file_path)
            self.config_manager.save_settings(self.settings)
            
            self.analyze_video()
            self.check_ready_state()
            
            app_logger.info(f"Video dosyası seçildi: {file_path}")
    
    def select_output(self):
        """Çıktı klasörü seç"""
        last_dir = self.settings.get('last_output_dir', os.path.expanduser('~'))
        
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "Çıktı Klasörünü Seçin", 
            last_dir
        )
        
        if folder_path:
            self.output_path = folder_path
            self.output_path_edit.setText(folder_path)
            
            # Son dizini kaydet
            self.settings['last_output_dir'] = folder_path
            self.config_manager.save_settings(self.settings)
            
            self.check_ready_state()
            
            app_logger.info(f"Çıktı klasörü seçildi: {folder_path}")
    
    def analyze_video(self):
        """Seçilen videoyu analiz et"""
        try:
            self.add_log("🔍 Video dosyası analiz ediliyor...", "info")
            
            self.video_info = VideoAnalyzer.analyze_video(self.video_path)
            
            if self.video_info:
                # Video bilgi kartını güncelle
                self.video_info_card.update_video_info(
                    self.video_info['frame_count'],
                    self.video_info['fps'],
                    self.video_info['width'],
                    self.video_info['height'],
                    self.video_info['duration']
                )
                
                # SpinBox maksimum değerlerini ayarla
                self.end_frame_spin.setMaximum(self.video_info['frame_count'])
                self.start_frame_spin.setMaximum(self.video_info['frame_count'] - 1)
                
                # Tahmini frame sayısını güncelle
                self.update_estimated_frames()
                
                self.add_log(
                    f"✅ Video analizi tamamlandı: "
                    f"{self.video_info['frame_count']} frame, "
                    f"{self.video_info['fps']:.1f} FPS, "
                    f"{self.video_info['resolution']}, "
                    f"{TimeUtils.seconds_to_time_string(self.video_info['duration'])}",
                    "success"
                )
                
            else:
                self.add_log("❌ Video analiz edilemedi!", "error")
                QMessageBox.critical(self, "Hata", "Video dosyası analiz edilemedi!\nDosya bozuk olabilir.")
                
        except Exception as e:
            self.add_log(f"❌ Video analiz hatası: {str(e)}", "error")
            app_logger.error(f"Video analiz hatası: {e}")
    
    def update_estimated_frames(self):
        """Tahmini çıktı frame sayısını güncelle"""
        if not self.video_info:
            self.estimated_frames_label.setText("Tahmini çıktı: Video seçin")
            return
        
        try:
            start = self.start_frame_spin.value()
            end = self.end_frame_spin.value()
            interval = self.frame_interval_spin.value()
            
            if end == 0:
                end = self.video_info['frame_count']
            
            if start >= end:
                self.estimated_frames_label.setText("⚠️ Geçersiz aralık!")
                self.estimated_frames_label.setStyleSheet(f"""
                    QLabel {{
                        color: {AppStyles.COLORS['danger']};
                        font-weight: bold;
                        font-size: 14px;
                        padding: 12px;
                        background-color: #ffe6e6;
                        border: 2px solid {AppStyles.COLORS['danger']};
                        border-radius: 6px;
                    }}
                """)
                return
            
            estimated_count = len(range(start, end, interval))
            
            self.estimated_frames_label.setText(
                f"📊 Tahmini çıktı: {estimated_count:,} frame "
                f"({start:,} → {end:,}, her {interval} frame'de 1)"
            )
            self.estimated_frames_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppStyles.COLORS['success']};
                    font-style: normal;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px;
                    background-color: #e8f5e8;
                    border: 2px solid {AppStyles.COLORS['success']};
                    border-radius: 6px;
                }}
            """)
            
        except Exception as e:
            app_logger.error(f"Tahmini frame hesaplama hatası: {e}")
    
    def check_ready_state(self):
        """Başlatma durumunu kontrol et"""
        ready = bool(self.video_path and self.output_path and self.video_info)
        self.start_btn.setEnabled(ready)
        
        if ready:
            self.progress_card.update_progress(-1, "Başlatmaya hazır", "ready")
        else:
            missing = []
            if not self.video_path:
                missing.append("video dosyası")
            if not self.output_path:
                missing.append("çıktı klasörü")
            
            self.progress_card.update_progress(-1, f"Eksik: {', '.join(missing)}", "warning")
    
    def start_processing(self):
        """Video işlemeyi başlat"""
        try:
            # Parametreleri doğrula
            start_frame = self.start_frame_spin.value()
            end_frame = self.end_frame_spin.value()
            interval = self.frame_interval_spin.value()
            
            if not os.path.exists(self.output_path):
                QMessageBox.warning(self, "Hata", "Çıktı klasörü mevcut değil!")
                return
            
            # Frame aralığını doğrula
            if self.video_info:
                is_valid, corrected_start, corrected_end, error_msg = VideoAnalyzer.validate_frame_range(
                    start_frame, end_frame if end_frame > 0 else self.video_info['frame_count'], 
                    self.video_info['frame_count']
                )
                
                if error_msg:
                    self.add_log(f"⚠️ {error_msg}", "warning")
                    self.start_frame_spin.setValue(corrected_start)
                    self.end_frame_spin.setValue(corrected_end)
            
            # UI'yi işlem moduna geçir
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Video processor'ı başlat
            self.video_processor.set_parameters(
                self.video_path,
                self.output_path,
                interval,
                self.start_frame_spin.value(),
                self.end_frame_spin.value(),
                self.get_selected_format(),
                self.output_quality_spin.value()
            )
            
            self.add_log("🚀 Video işleme başlatıldı!", "info")
            self.video_processor.start()
            
            app_logger.info("Video işleme başlatıldı")
            
        except Exception as e:
            self.add_log(f"❌ Başlatma hatası: {str(e)}", "error")
            app_logger.error(f"İşlem başlatma hatası: {e}")
            self.processing_finished(False, str(e))
    
    def stop_processing(self):
        """Video işlemeyi durdur"""
        if self.video_processor.isRunning():
            self.video_processor.stop_processing()
            self.add_log("⏹️ İşlem durduruluyor...", "warning")
    
    def update_progress(self, value):
        """İlerleme çubuğunu güncelle"""
        self.progress_bar.setValue(value)
        self.progress_card.update_progress(value, "", "processing")
    
    def update_status(self, message, status_type):
        """Durum mesajını güncelle"""
        self.progress_card.update_progress(-1, message, status_type)
    
    def add_log(self, message, level="info"):
        """Log mesajı ekle"""
        timestamp = f"[{TimeUtils.seconds_to_time_string(0)}]"
        
        # Renk kodları
        color_map = {
            "info": AppStyles.COLORS['gray_700'],
            "success": AppStyles.COLORS['success'],
            "warning": AppStyles.COLORS['warning'],
            "error": AppStyles.COLORS['danger']
        }
        
        color = color_map.get(level, AppStyles.COLORS['gray_700'])
        
        # HTML formatında log ekle
        html_message = f"""
        <div style="color: {color}; margin: 2px 0; font-family: {AppStyles.FONTS['family_mono']};">
            <span style="color: {AppStyles.COLORS['gray_500']};">{timestamp}</span> {message}
        </div>
        """
        
        self.log_text.append(html_message)
        
        # Logger'a da ekle
        if level == "error":
            app_logger.error(message)
        elif level == "warning":
            app_logger.warning(message)
        else:
            app_logger.info(message)
    
    def on_frame_processed(self, frame_number, filename):
        """Frame işlendiğinde çağrılır"""
        # Her 50 frame'de bir detaylı log (performans için)
        if frame_number % 50 == 0:
            self.add_log(f"📸 Frame {frame_number} kaydedildi: {filename}", "success")
    
    def clear_logs(self):
        """Log alanını temizle"""
        self.log_text.clear()
        self.add_log("🗑️ Log alanı temizlendi", "info")
    
    def on_format_changed(self, format_text):
        """Çıktı formatı değiştiğinde çağrılır"""
        # Format değişimini logla
        format_name = format_text.split(' ')[0]
        self.add_log(f"🎨 Çıktı formatı değiştirildi: {format_name}", "info")
        
        # PNG için kalite açıklamasını güncelle
        if "PNG" in format_text:
            self.output_quality_spin.setToolTip("PNG sıkıştırma kalitesi (düşük=küçük dosya, yüksek=kaliteli)")
        elif "JPEG" in format_text:
            self.output_quality_spin.setToolTip("JPEG kalitesi (düşük=küçük dosya, yüksek=kaliteli)")
        else:
            self.output_quality_spin.setToolTip("Bu format için kalite ayarı uygulanmaz")
    
    def on_quality_changed(self, quality):
        """Kalite değiştiğinde çağrılır"""
        if quality % 10 == 0:  # Sadece 10'un katlarında log
            self.add_log(f"🎯 Çıktı kalitesi: %{quality}", "info")
        
        # Ayarları kaydet
        self.settings['jpeg_quality'] = str(quality)
        self.config_manager.save_settings(self.settings)
    
    def get_selected_format(self):
        """Seçili formatı döndür"""
        format_text = self.output_format_combo.currentText()
        if "JPEG" in format_text:
            return "jpg"
        elif "PNG" in format_text:
            return "png"
        elif "BMP" in format_text:
            return "bmp"
        return "jpg"  # Varsayılan
    
    def processing_finished(self, success, message):
        """İşlem tamamlandığında çağrılır"""
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            self.progress_card.update_progress(100, "İşlem tamamlandı! ✅", "ready")
            
            # Başarı mesajı göster
            reply = QMessageBox.information(
                self, 
                "İşlem Tamamlandı", 
                f"{message}\n\nÇıktı klasörünü açmak ister misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.startfile(self.output_path)  # Windows
                
        else:
            self.progress_card.update_progress(-1, "İşlem başarısız ❌", "error")
            QMessageBox.critical(self, "İşlem Hatası", message)
        
        app_logger.info(f"İşlem tamamlandı. Başarılı: {success}")
    
    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        if self.video_processor.isRunning():
            reply = QMessageBox.question(
                self, 
                "İşlem Devam Ediyor", 
                "Video işleme devam ediyor. Uygulamayı kapatmak istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.video_processor.stop_processing()
                self.video_processor.wait(3000)  # 3 saniye bekle
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
        app_logger.info("Uygulama kapatıldı")
    
    def show_main_tool(self):
        """Ana video frame çıkarma aracını göster (zaten aktif)"""
        self.statusBar().showMessage("Video Frame Çıkarma aracı aktif", 2000)
    
    def open_yolo_analyzer(self):
        """YOLO analiz penceresini aç"""
        try:
            yolo_window = YoloAnalysisWindow(self)
            yolo_window.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"YOLO analiz penceresi açılırken hata oluştu:\n{str(e)}")
            app_logger.error(f"YOLO penceresi açma hatası: {e}")
    
    def show_about(self):
        """Hakkında diyalogu göster"""
        QMessageBox.about(self, "Hakkında", 
            """🤖 AI ToolBox v1.0.0
            
Modern PyQt5 tabanlı AI araçları koleksiyonu.

Mevcut Araçlar:
• Video dosyalarından frame çıkarma
• YOLO format dosya analizi
• Toplu işlem desteği
• Modern ve kullanıcı dostu arayüz

© 2025 AI ToolBox""")

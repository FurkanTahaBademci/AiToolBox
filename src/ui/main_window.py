"""
Ana uygulama arayüzü
Modern ve kullanıcı dostu AI ToolBox
"""

import sys
import os
import time
import importlib.util
import random
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                            QLineEdit, QSpinBox, QFileDialog, QProgressBar,
                            QGroupBox, QFrame, QMessageBox, QTextEdit, QSplitter, 
                            QComboBox, QAction, QStackedWidget, QCheckBox)
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
        self.setGeometry(100, 100, 1400, 900)  # Daha büyük pencere boyutu
        self.setMinimumSize(1200, 800)  # Minimum boyutu da arttır
        
        # Menü bar oluştur
        self.create_menu_bar()
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sol sidebar menü
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Ana içerik alanı
        self.main_content = QWidget()
        main_layout.addWidget(self.main_content)
        
        # Ana içerik layout'ı
        content_layout = QVBoxLayout(self.main_content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık alanı
        self.create_header(content_layout)
        
        # Ana içerik alanı için stacked widget
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Video extractor sayfası
        video_page = self.create_video_extractor_page()
        self.content_stack.addWidget(video_page)
        
        # YOLO analyzer sayfası
        yolo_page = self.create_yolo_analyzer_page()
        self.content_stack.addWidget(yolo_page)
        
        # Image-TXT matcher sayfası
        matcher_page = self.create_image_txt_matcher_page()
        self.content_stack.addWidget(matcher_page)
        
        # Image augmentation sayfası
        augment_page = self.create_image_augmentation_page()
        self.content_stack.addWidget(augment_page)
        
        # Varsayılan olarak video frame extractor'ı göster
        self.current_tool = "video_extractor"
        self.content_stack.setCurrentIndex(0)
        
        # Alt kontrol çubuğu
        self.create_bottom_controls(content_layout)
    
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
    
    def create_sidebar(self):
        """Sol sidebar menüyü oluştur"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {AppStyles.COLORS['surface']};
                border-right: 2px solid {AppStyles.COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 20, 15, 20)
        
        # Başlık
        title = QLabel("🤖 AI ToolBox")
        title.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['primary']};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 20px;
                padding: 10px;
            }}
        """)
        layout.addWidget(title)
        
        # Araçlar başlığı
        tools_label = QLabel("ARAÇLAR")
        tools_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_500']};
                font-size: 11px;
                font-weight: bold;
                margin: 20px 0 10px 0;
                padding-left: 5px;
            }}
        """)
        layout.addWidget(tools_label)
        
        # Menü butonları
        self.menu_buttons = {}
        
        # Video Frame Extractor
        video_btn = self.create_menu_button("🎬", "Video Frame Çıkarma", "video_extractor", True)
        self.menu_buttons["video_extractor"] = video_btn
        layout.addWidget(video_btn)
        
        # YOLO Analyzer
        yolo_btn = self.create_menu_button("🎯", "YOLO Format Analizi", "yolo_analyzer", False)
        self.menu_buttons["yolo_analyzer"] = yolo_btn
        layout.addWidget(yolo_btn)
        
        # Image-TXT Matcher
        matcher_btn = self.create_menu_button("🖼️", "Resim-TXT Eşleştirme", "image_txt_matcher", False)
        self.menu_buttons["image_txt_matcher"] = matcher_btn
        layout.addWidget(matcher_btn)
        
        # Image Augmentation
        augment_btn = self.create_menu_button("🎨", "Görüntü Augmentasyon", "image_augmentation", False)
        self.menu_buttons["image_augmentation"] = augment_btn
        layout.addWidget(augment_btn)
        
        # Ayırıcı
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"QFrame {{ color: {AppStyles.COLORS['border']}; }}")
        layout.addWidget(separator)
        
        # Ayarlar ve yardım
        settings_label = QLabel("AYARLAR")
        settings_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_500']};
                font-size: 11px;
                font-weight: bold;
                margin: 20px 0 10px 0;
                padding-left: 5px;
            }}
        """)
        layout.addWidget(settings_label)
        
        # Hakkında
        about_btn = self.create_menu_button("❓", "Hakkında", "about", False)
        layout.addWidget(about_btn)
        
        layout.addStretch()
        return sidebar
    
    def create_menu_button(self, icon, text, tool_id, is_active=False):
        """Menü butonu oluştur"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        
        active_style = f"""
            QPushButton {{
                background-color: {AppStyles.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['primary_dark']};
            }}
        """
        
        inactive_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {AppStyles.COLORS['text']};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.COLORS['hover']};
            }}
        """
        
        btn.setStyleSheet(active_style if is_active else inactive_style)
        btn.clicked.connect(lambda: self.switch_tool(tool_id))
        
        return btn
    
    def switch_tool(self, tool_id):
        """Araç değiştir"""
        if tool_id == self.current_tool:
            return
            
        # Buton stillerini güncelle
        for btn_id, button in self.menu_buttons.items():
            is_active = btn_id == tool_id
            active_style = f"""
                QPushButton {{
                    background-color: {AppStyles.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {AppStyles.COLORS['primary_dark']};
                }}
            """
            
            inactive_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {AppStyles.COLORS['text']};
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    text-align: left;
                    padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {AppStyles.COLORS['hover']};
                }}
            """
            
            button.setStyleSheet(active_style if is_active else inactive_style)
        
        # Aracı değiştir
        self.current_tool = tool_id
        
        # Başlığı güncelle ve sayfa değiştir
        if tool_id == "video_extractor":
            self.tool_title.setText("🎬 Video Frame Çıkarma")
            self.content_stack.setCurrentIndex(0)  # Video extractor sayfası
            self.statusBar().showMessage("Video Frame Çıkarma aracı aktif", 2000)
        elif tool_id == "yolo_analyzer":
            self.tool_title.setText("🎯 YOLO Format Analizi")
            self.content_stack.setCurrentIndex(1)  # YOLO analyzer sayfası
            self.statusBar().showMessage("YOLO Format Analizi aracı aktif", 2000)
        elif tool_id == "image_txt_matcher":
            self.tool_title.setText("🖼️ Resim-TXT Eşleştirme")
            self.content_stack.setCurrentIndex(2)  # Image-TXT matcher sayfası
            self.statusBar().showMessage("Resim-TXT Eşleştirme aracı aktif", 2000)
        elif tool_id == "image_augmentation":
            self.tool_title.setText("🎨 Görüntü Augmentasyon")
            self.content_stack.setCurrentIndex(3)  # Image augmentation sayfası
            self.statusBar().showMessage("Görüntü Augmentasyon aracı aktif", 2000)
        elif tool_id == "about":
            self.show_about()
            # About'tan sonra önceki aracı aktif tut
            if hasattr(self, 'previous_tool'):
                self.switch_tool(self.previous_tool)
            else:
                self.switch_tool("video_extractor")

    def create_video_extractor_page(self):
        """Video extractor sayfasını oluştur"""
        page = QWidget()
        
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
        content_splitter.setStretchFactor(1, 1)  # Sağ panel daha dar
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(content_splitter)
        
        return page
    
    def create_yolo_analyzer_page(self):
        """YOLO analyzer sayfasını oluştur"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # YOLO analiz araçlarını içe aktar
        from ..ui.yolo_window import YoloAnalysisWindow
        
        # YOLO widget'ını oluştur ama pencere olarak değil widget olarak
        self.yolo_widget = self.create_yolo_analysis_widget()
        layout.addWidget(self.yolo_widget)
        
        return page
    
    def create_image_txt_matcher_page(self):
        """Resim-TXT eşleştirme sayfasını oluştur"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Image-TXT matcher widget'ını oluştur
        self.matcher_widget = self.create_image_txt_matcher_widget()
        layout.addWidget(self.matcher_widget)
        
        return page
    
    def create_image_augmentation_page(self):
        """Görüntü augmentasyon sayfasını oluştur"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Image augmentation widget'ını oluştur
        self.augment_widget = self.create_image_augmentation_widget()
        layout.addWidget(self.augment_widget)
        
        return page
    
    def create_image_augmentation_widget(self):
        """Görüntü augmentasyon widget'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)  # Spacing'i arttır
        layout.setContentsMargins(20, 20, 20, 20)  # Margin'leri ekle
        
        # Kaynak ve hedef klasörler
        folders_group = QGroupBox("📁 Klasör Ayarları")
        folders_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                min-height: 120px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        folders_layout = QVBoxLayout(folders_group)
        
        # Kaynak klasör
        source_layout = QHBoxLayout()
        source_label = QLabel("Kaynak Klasör:")
        source_label.setFixedWidth(100)
        
        self.augment_source_input = QLineEdit()
        self.augment_source_input.setPlaceholderText("Augmentasyon uygulanacak resimlerin klasörü...")
        self.augment_source_input.setStyleSheet(AppStyles.get_input_style())
        
        self.augment_source_btn = QPushButton("📁 Gözat")
        self.augment_source_btn.setStyleSheet(AppStyles.get_button_style())
        self.augment_source_btn.clicked.connect(self.browse_augment_source)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.augment_source_input)
        source_layout.addWidget(self.augment_source_btn)
        folders_layout.addLayout(source_layout)
        
        # Hedef klasör
        target_layout = QHBoxLayout()
        target_label = QLabel("Hedef Klasör:")
        target_label.setFixedWidth(100)
        
        self.augment_target_input = QLineEdit()
        self.augment_target_input.setPlaceholderText("Augmentasyon sonuçlarının kaydedileceği klasör...")
        self.augment_target_input.setStyleSheet(AppStyles.get_input_style())
        
        self.augment_target_btn = QPushButton("📁 Gözat")
        self.augment_target_btn.setStyleSheet(AppStyles.get_button_style())
        self.augment_target_btn.clicked.connect(self.browse_augment_target)
        
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.augment_target_input)
        target_layout.addWidget(self.augment_target_btn)
        folders_layout.addLayout(target_layout)
        
        layout.addWidget(folders_group)
        
        # Augmentasyon efektleri seçimi
        effects_group = QGroupBox("🎨 Augmentasyon Efektleri")
        effects_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
                min-height: 300px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        effects_layout = QVBoxLayout(effects_group)
        
        # Efekt checkboxları - 3 sütun halinde
        self.effect_checkboxes = {}
        
        # Automold efektleri
        effects_data = [
            ("random_brightness", "🔆 Rastgele Parlaklık", "Görüntü parlaklığını rastgele değiştirir"),
            ("add_shadow", "🌑 Gölge Ekleme", "Görüntüye rastgele gölgeler ekler"),
            ("add_snow", "❄️ Kar Efekti", "Kar yağışı efekti ekler"),
            ("add_rain", "🌧️ Yağmur Efekti", "Yağmur damlacıkları ekler"),
            ("add_fog", "🌫️ Sis Efekti", "Sisli hava koşulları simüle eder"),
            ("add_gravel", "🪨 Çakıl Taşı", "Yol yüzeyine çakıl taşları ekler"),
            ("add_sun_flare", "☀️ Güneş Parıltısı", "Güneş ışığı parıltısı efekti"),
            ("add_speed", "💨 Hız Bulanıklığı", "Hareket bulanıklığı efekti"),
            ("add_autumn", "🍂 Sonbahar Renkleri", "Sonbahar renk tonlarını uygular"),
            ("random_flip", "🔄 Rastgele Çevirme", "Görüntüyü rastgele çevirir"),
            # ("add_manhole", "🕳️ Rögar Kapağı", "Yol yüzeyine rögar kapağı ekler"),  # Geçici olarak devre dışı
            ("correct_exposure", "📸 Pozlama Düzeltme", "Görüntü pozlamasını iyileştirir")
        ]
        
        # 3 sütunlu grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)  # Grid elemanları arası boşluğu arttır
        grid_layout.setContentsMargins(20, 20, 20, 20)  # Margin'leri arttır
        
        for i, (effect_key, effect_name, effect_desc) in enumerate(effects_data):
            row = i // 3
            col = i % 3
            
            checkbox = QCheckBox(effect_name)
            checkbox.setToolTip(effect_desc)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {AppStyles.COLORS['text']};
                    font-size: 14px;
                    spacing: 10px;
                    padding: 8px;
                    min-height: 30px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    margin-right: 8px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 2px solid {AppStyles.COLORS['border']};
                    border-radius: 4px;
                    background-color: {AppStyles.COLORS['background']};
                }}
                QCheckBox::indicator:checked {{
                    border: 2px solid {AppStyles.COLORS['primary']};
                    border-radius: 4px;
                    background-color: {AppStyles.COLORS['primary']};
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEuNSA1TDQuNSA4TDguNSAyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
                }}
            """)
            
            self.effect_checkboxes[effect_key] = checkbox
            grid_layout.addWidget(checkbox, row, col)
        
        # Grid layout'u center'a hizala
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        
        # Grid'i effects_layout'a ekle
        effects_layout.addWidget(grid_widget)
        
        # Hızlı seçim butonları
        quick_select_layout = QHBoxLayout()
        quick_select_layout.setSpacing(15)  # Buton arası boşluğu arttır
        quick_select_layout.setContentsMargins(20, 15, 20, 15)
        
        select_all_btn = QPushButton("✅ Tümünü Seç")
        select_all_btn.setStyleSheet(AppStyles.get_button_style())
        select_all_btn.clicked.connect(self.select_all_effects)
        
        clear_all_btn = QPushButton("❌ Tümünü Temizle")
        clear_all_btn.setStyleSheet(AppStyles.get_button_style())
        clear_all_btn.clicked.connect(self.clear_all_effects)
        
        weather_effects_btn = QPushButton("🌦️ Hava Durumu")
        weather_effects_btn.setStyleSheet(AppStyles.get_button_style())
        weather_effects_btn.clicked.connect(self.select_weather_effects)
        
        road_effects_btn = QPushButton("🛣️ Yol Efektleri")
        road_effects_btn.setStyleSheet(AppStyles.get_button_style())
        road_effects_btn.clicked.connect(self.select_road_effects)
        
        quick_select_layout.addWidget(select_all_btn)
        quick_select_layout.addWidget(clear_all_btn)
        quick_select_layout.addWidget(weather_effects_btn)
        quick_select_layout.addWidget(road_effects_btn)
        quick_select_layout.addStretch()
        
        effects_layout.addLayout(quick_select_layout)
        layout.addWidget(effects_group)
        
        # İşlem ayarları
        settings_group = QGroupBox("⚙️ İşlem Ayarları")
        settings_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                min-height: 120px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        settings_layout = QVBoxLayout(settings_group)
        
        # Resim formatları ve işlem modu
        settings_row1 = QHBoxLayout()
        
        formats_label = QLabel("Resim Formatları:")
        self.augment_formats_input = QLineEdit("jpg,jpeg,png,bmp")
        self.augment_formats_input.setPlaceholderText("jpg,jpeg,png,bmp")
        self.augment_formats_input.setStyleSheet(AppStyles.get_input_style())
        
        mode_label = QLabel("İşlem Modu:")
        self.augment_mode_combo = QComboBox()
        self.augment_mode_combo.addItems(["Her efekt için ayrı dosya", "Rastgele bir efekt uygula"])
        self.augment_mode_combo.setStyleSheet(AppStyles.get_input_style())
        
        settings_row1.addWidget(formats_label)
        settings_row1.addWidget(self.augment_formats_input)
        settings_row1.addWidget(mode_label)
        settings_row1.addWidget(self.augment_mode_combo)
        
        settings_layout.addLayout(settings_row1)
        
        # Alt dizinler ve isim prefix
        settings_row2 = QHBoxLayout()
        
        self.augment_subdirs_cb = QCheckBox("Alt dizinleri de işle")
        self.augment_subdirs_cb.setChecked(True)
        
        prefix_label = QLabel("Dosya Öneki:")
        self.augment_prefix_input = QLineEdit("aug_")
        self.augment_prefix_input.setPlaceholderText("aug_")
        self.augment_prefix_input.setStyleSheet(AppStyles.get_input_style())
        self.augment_prefix_input.setFixedWidth(100)
        
        settings_row2.addWidget(self.augment_subdirs_cb)
        settings_row2.addStretch()
        settings_row2.addWidget(prefix_label)
        settings_row2.addWidget(self.augment_prefix_input)
        
        settings_layout.addLayout(settings_row2)
        layout.addWidget(settings_group)
        
        # İşlem butonları
        buttons_layout = QHBoxLayout()
        
        self.augment_preview_btn = QPushButton("👁️ Önizleme")
        self.augment_preview_btn.setStyleSheet(AppStyles.get_button_style())
        self.augment_preview_btn.clicked.connect(self.preview_augmentation)
        self.augment_preview_btn.setEnabled(False)
        
        self.augment_process_btn = QPushButton("🎨 Augmentasyon Uygula")
        self.augment_process_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.augment_process_btn.clicked.connect(self.process_augmentation)
        self.augment_process_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.augment_preview_btn)
        buttons_layout.addWidget(self.augment_process_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Sonuçlar bölümü
        results_group = QGroupBox("📊 İşlem Sonuçları")
        results_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                min-height: 250px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        results_layout = QVBoxLayout(results_group)
        
        self.augment_results_text = QTextEdit()
        self.augment_results_text.setPlaceholderText("İşlem sonuçları burada görünecek...")
        self.augment_results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppStyles.COLORS['gray_100']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-family: {AppStyles.FONTS['family_mono']};
                font-size: 13px;
                color: {AppStyles.COLORS['text']};
            }}
        """)
        self.augment_results_text.setMinimumHeight(300)  # Minimum yüksekliği arttır
        
        results_layout.addWidget(self.augment_results_text)
        layout.addWidget(results_group)
        
        # Input değişikliklerini dinle
        self.augment_source_input.textChanged.connect(self.on_augment_folders_changed)
        self.augment_target_input.textChanged.connect(self.on_augment_folders_changed)
        
        return widget
    
    def create_image_txt_matcher_widget(self):
        """Resim-TXT eşleştirme widget'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Klasör seçimi bölümü
        folder_group = QGroupBox("📁 Klasör ve Ayarlar")
        folder_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        folder_layout = QVBoxLayout(folder_group)
        
        # Klasör seçim alanı
        folder_select_layout = QHBoxLayout()
        
        self.matcher_folder_input = QLineEdit()
        self.matcher_folder_input.setPlaceholderText("Resim ve TXT dosyalarının bulunduğu klasörü seçin...")
        self.matcher_folder_input.setStyleSheet(AppStyles.get_input_style())
        
        self.matcher_browse_btn = QPushButton("📁 Gözat")
        self.matcher_browse_btn.setStyleSheet(AppStyles.get_button_style())
        self.matcher_browse_btn.clicked.connect(self.browse_matcher_folder)
        
        folder_select_layout.addWidget(self.matcher_folder_input)
        folder_select_layout.addWidget(self.matcher_browse_btn)
        folder_layout.addLayout(folder_select_layout)
        
        # Resim formatları seçimi
        format_layout = QHBoxLayout()
        
        format_label = QLabel("Resim Formatları:")
        format_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['text']};
                font-weight: 500;
                font-size: 13px;
            }}
        """)
        
        self.image_formats_input = QLineEdit("jpg,jpeg,png,bmp,tiff,webp")
        self.image_formats_input.setPlaceholderText("jpg,jpeg,png,bmp,tiff,webp")
        self.image_formats_input.setStyleSheet(AppStyles.get_input_style())
        self.image_formats_input.setToolTip("Virgülle ayırarak resim formatlarını girin (örn: jpg,png,bmp)")
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.image_formats_input)
        folder_layout.addLayout(format_layout)
        
        # Alt dizinleri dahil et seçeneği
        self.include_subdirs_cb = QCheckBox("Alt dizinleri de tara")
        self.include_subdirs_cb.setChecked(True)
        self.include_subdirs_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {AppStyles.COLORS['text']};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
        """)
        folder_layout.addWidget(self.include_subdirs_cb)
        
        # Analiz ve oluşturma butonları
        button_layout = QHBoxLayout()
        
        self.matcher_analyze_btn = QPushButton("🔍 Analiz Et")
        self.matcher_analyze_btn.setStyleSheet(AppStyles.get_button_style())
        self.matcher_analyze_btn.clicked.connect(self.analyze_image_txt_matching)
        self.matcher_analyze_btn.setEnabled(False)
        
        self.matcher_create_btn = QPushButton("📄 Eksik TXT Dosyalarını Oluştur")
        self.matcher_create_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.matcher_create_btn.clicked.connect(self.create_missing_txt_files)
        self.matcher_create_btn.setEnabled(False)
        
        button_layout.addWidget(self.matcher_analyze_btn)
        button_layout.addWidget(self.matcher_create_btn)
        folder_layout.addLayout(button_layout)
        
        layout.addWidget(folder_group)
        
        # Sonuçlar bölümü
        results_group = QGroupBox("📊 Analiz Sonuçları")
        results_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        results_layout = QVBoxLayout(results_group)
        
        # Sonuç metni
        self.matcher_results_text = QTextEdit()
        self.matcher_results_text.setPlaceholderText("Analiz sonuçları burada görünecek...")
        self.matcher_results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppStyles.COLORS['gray_100']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 6px;
                padding: 10px;
                font-family: {AppStyles.FONTS['family_mono']};
                font-size: 12px;
                color: {AppStyles.COLORS['text']};
            }}
        """)
        self.matcher_results_text.setMinimumHeight(300)
        
        results_layout.addWidget(self.matcher_results_text)
        layout.addWidget(results_group)
        
        # Folder input değişikliğini dinle
        self.matcher_folder_input.textChanged.connect(self.on_matcher_folder_changed)
        
        return widget
    
    def browse_matcher_folder(self):
        """Resim-TXT eşleştirme klasörü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Resim ve TXT Dosyalarının Bulunduğu Klasörü Seçin",
            self.matcher_folder_input.text() or os.path.expanduser("~")
        )
        
        if folder:
            self.matcher_folder_input.setText(folder)
    
    def on_matcher_folder_changed(self):
        """Klasör seçimi değiştiğinde"""
        folder_path = self.matcher_folder_input.text().strip()
        has_folder = bool(folder_path and os.path.exists(folder_path))
        self.matcher_analyze_btn.setEnabled(has_folder)
        
        # Oluştur butonunu sadece analiz yapıldıktan sonra aktif et
        if not has_folder:
            self.matcher_create_btn.setEnabled(False)
    
    def analyze_image_txt_matching(self):
        """Resim ve TXT dosyalarını analiz et"""
        folder_path = self.matcher_folder_input.text().strip()
        
        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir klasör seçin!")
            return
        
        try:
            # Analiz kodunu çalıştır
            self.run_image_txt_analysis(folder_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz sırasında hata oluştu:\n{str(e)}")
            app_logger.error(f"Resim-TXT analiz hatası: {str(e)}")
    
    def run_image_txt_analysis(self, folder_path):
        """Resim-TXT analiz işlemini gerçekleştir"""
        # Resim formatlarını al
        formats_text = self.image_formats_input.text().strip()
        if not formats_text:
            formats_text = "jpg,jpeg,png,bmp,tiff,webp"
        
        image_extensions = [f".{fmt.strip().lower()}" for fmt in formats_text.split(",")]
        include_subdirs = self.include_subdirs_cb.isChecked()
        
        # Dosyaları tara
        image_files = []
        txt_files = []
        
        if include_subdirs:
            # Alt dizinleri dahil et
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in image_extensions:
                        image_files.append(file_path)
                    elif file_ext == ".txt":
                        txt_files.append(file_path)
        else:
            # Sadece ana dizin
            for file in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, file)):
                    file_ext = os.path.splitext(file)[1].lower()
                    file_path = os.path.join(folder_path, file)
                    
                    if file_ext in image_extensions:
                        image_files.append(file_path)
                    elif file_ext == ".txt":
                        txt_files.append(file_path)
        
        # TXT dosyalarını base name'e göre organize et
        txt_basenames = set()
        for txt_file in txt_files:
            base_name = os.path.splitext(os.path.basename(txt_file))[0]
            txt_basenames.add(base_name)
        
        # Eksik TXT dosyalarını bul
        missing_txt_files = []
        matched_files = []
        
        for image_file in image_files:
            base_name = os.path.splitext(os.path.basename(image_file))[0]
            
            if base_name in txt_basenames:
                matched_files.append(image_file)
            else:
                missing_txt_files.append(image_file)
        
        # Sonuçları kaydet (create_missing_txt_files için)
        self.current_analysis = {
            'folder_path': folder_path,
            'missing_files': missing_txt_files,
            'matched_files': matched_files,
            'total_images': len(image_files),
            'total_txt': len(txt_files),
            'include_subdirs': include_subdirs
        }
        
        # Sonuçları göster
        output_text = f"""Resim-TXT Eşleştirme Analiz Sonuçları
====================================

📁 Klasör: {folder_path}
🔍 Tarama: {"Alt dizinler dahil" if include_subdirs else "Sadece ana dizin"}
📷 Toplam Resim: {len(image_files)}
📄 Toplam TXT: {len(txt_files)}

✅ EŞLEŞEN DOSYALAR: {len(matched_files)}
❌ EKSİK TXT DOSYALARI: {len(missing_txt_files)}

"""
        
        if missing_txt_files:
            output_text += "🔍 EKSİK TXT DOSYALARI LİSTESİ:\n"
            for img_file in missing_txt_files[:20]:  # İlk 20'sini göster
                rel_path = os.path.relpath(img_file, folder_path)
                output_text += f"   • {rel_path}\n"
            
            if len(missing_txt_files) > 20:
                output_text += f"   ... ve {len(missing_txt_files) - 20} dosya daha\n"
        else:
            output_text += "🎉 Tüm resim dosyaları için TXT dosyası mevcut!\n"
        
        if matched_files:
            output_text += f"\n✅ EŞLEŞEN DOSYALAR (ilk 10):\n"
            for img_file in matched_files[:10]:
                rel_path = os.path.relpath(img_file, folder_path)
                output_text += f"   • {rel_path}\n"
            
            if len(matched_files) > 10:
                output_text += f"   ... ve {len(matched_files) - 10} dosya daha\n"
        
        self.matcher_results_text.setText(output_text)
        
        # Oluştur butonunu aktif et
        self.matcher_create_btn.setEnabled(len(missing_txt_files) > 0)
        
        self.statusBar().showMessage(f"Analiz tamamlandı! {len(missing_txt_files)} eksik TXT dosyası bulundu.", 3000)
    
    def create_missing_txt_files(self):
        """Eksik TXT dosyalarını oluştur"""
        if not hasattr(self, 'current_analysis'):
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapmanız gerekiyor!")
            return
        
        analysis = self.current_analysis
        missing_files = analysis['missing_files']
        
        if not missing_files:
            QMessageBox.information(self, "Bilgi", "Oluşturulacak eksik TXT dosyası bulunamadı!")
            return
        
        # Kullanıcıdan onay al
        reply = QMessageBox.question(
            self, 
            "Onay", 
            f"{len(missing_files)} adet boş TXT dosyası oluşturulacak. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            created_count = 0
            error_count = 0
            
            for image_file in missing_files:
                try:
                    # TXT dosya yolunu oluştur
                    image_dir = os.path.dirname(image_file)
                    base_name = os.path.splitext(os.path.basename(image_file))[0]
                    txt_file_path = os.path.join(image_dir, f"{base_name}.txt")
                    
                    # Boş TXT dosyası oluştur
                    with open(txt_file_path, 'w', encoding='utf-8') as f:
                        f.write("")  # Boş dosya
                    
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    app_logger.error(f"TXT dosyası oluşturma hatası {image_file}: {str(e)}")
            
            # Sonuç mesajı
            if error_count == 0:
                QMessageBox.information(
                    self, 
                    "Başarılı", 
                    f"✅ {created_count} adet boş TXT dosyası başarıyla oluşturuldu!"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Kısmi Başarı", 
                    f"✅ {created_count} dosya oluşturuldu\n❌ {error_count} dosyada hata oluştu\n\nDetaylar için log'lara bakın."
                )
            
            # Yeniden analiz et
            self.analyze_image_txt_matching()
            
            self.statusBar().showMessage(f"{created_count} TXT dosyası oluşturuldu!", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"TXT dosyaları oluşturulürken hata oluştu:\n{str(e)}")
            app_logger.error(f"TXT oluşturma genel hatası: {str(e)}")

    def create_yolo_analysis_widget(self):
        """YOLO analiz widget'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Klasör seçimi bölümü
        folder_group = QGroupBox("📁 Klasör Seçimi")
        folder_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        folder_layout = QVBoxLayout(folder_group)
        
        # Klasör seçim alanı
        folder_select_layout = QHBoxLayout()
        
        self.yolo_folder_input = QLineEdit()
        self.yolo_folder_input.setPlaceholderText("YOLO .txt dosyalarının bulunduğu klasörü seçin...")
        self.yolo_folder_input.setStyleSheet(AppStyles.get_input_style())
        
        self.yolo_browse_btn = QPushButton("📁 Gözat")
        self.yolo_browse_btn.setStyleSheet(AppStyles.get_button_style())
        self.yolo_browse_btn.clicked.connect(self.browse_yolo_folder)
        
        folder_select_layout.addWidget(self.yolo_folder_input)
        folder_select_layout.addWidget(self.yolo_browse_btn)
        folder_layout.addLayout(folder_select_layout)
        
        # Analiz butonu
        self.yolo_analyze_btn = QPushButton("🎯 Analiz Et")
        self.yolo_analyze_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.yolo_analyze_btn.clicked.connect(self.start_yolo_analysis)
        self.yolo_analyze_btn.setEnabled(False)
        
        folder_layout.addWidget(self.yolo_analyze_btn)
        layout.addWidget(folder_group)
        
        # Sonuçlar bölümü
        results_group = QGroupBox("📊 Analiz Sonuçları")
        results_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {AppStyles.COLORS['text']};
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        results_layout = QVBoxLayout(results_group)
        
        # Sonuç metni
        self.yolo_results_text = QTextEdit()
        self.yolo_results_text.setPlaceholderText("Analiz sonuçları burada görünecek...")
        self.yolo_results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppStyles.COLORS['gray_100']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 6px;
                padding: 10px;
                font-family: {AppStyles.FONTS['family_mono']};
                font-size: 12px;
                color: {AppStyles.COLORS['text']};
            }}
        """)
        self.yolo_results_text.setMinimumHeight(300)
        
        results_layout.addWidget(self.yolo_results_text)
        
        # Export butonu
        self.yolo_export_btn = QPushButton("📄 CSV Olarak Kaydet")
        self.yolo_export_btn.setStyleSheet(AppStyles.get_button_style())
        self.yolo_export_btn.clicked.connect(self.export_yolo_results)
        self.yolo_export_btn.setEnabled(False)
        
        results_layout.addWidget(self.yolo_export_btn)
        layout.addWidget(results_group)
        
        # Folder input değişikliğini dinle
        self.yolo_folder_input.textChanged.connect(self.on_yolo_folder_changed)
        
        return widget
    
    def browse_yolo_folder(self):
        """YOLO klasörü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "YOLO Dosyalarının Bulunduğu Klasörü Seçin",
            self.yolo_folder_input.text() or os.path.expanduser("~")
        )
        
        if folder:
            self.yolo_folder_input.setText(folder)
    
    def on_yolo_folder_changed(self):
        """Klasör seçimi değiştiğinde"""
        folder_path = self.yolo_folder_input.text().strip()
        has_folder = bool(folder_path and os.path.exists(folder_path))
        self.yolo_analyze_btn.setEnabled(has_folder)
    
    def start_yolo_analysis(self):
        """YOLO analizi başlat"""
        folder_path = self.yolo_folder_input.text().strip()
        
        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir klasör seçin!")
            return
        
        try:
            from ..core.yolo_analyzer import YoloAnalyzer
            
            # Analiz et
            analyzer = YoloAnalyzer()
            results = analyzer.analyze_folder(folder_path)
            
            # Hata kontrolü - eğer hiç dosya yoksa
            if results['total_files'] == 0:
                self.yolo_results_text.setText("Bu klasörde YOLO format (.txt) dosya bulunamadı.")
                self.yolo_export_btn.setEnabled(False)
                return
            
            # Sonuçları göster
            output_text = f"""YOLO Format Analiz Sonuçları
=====================================

📁 Klasör: {folder_path}
📄 Toplam Dosya: {results['total_files']}
🎯 Toplam Nesne: {results['total_objects']}

📊 SINIF İSTATİSTİKLERİ:
"""
            
            # class_counts kullan (class_stats değil)
            if results.get('class_counts'):
                for class_id, count in sorted(results['class_counts'].items()):
                    output_text += f"   Sınıf {class_id}: {count} nesne\n"
            else:
                output_text += "   Hiç nesne bulunamadı.\n"
            
            # Hata dosyaları varsa göster
            if results.get('error_files'):
                output_text += f"\n⚠️  HATA RAPORLARI ({len(results['error_files'])} dosya):\n"
                for error_info in results['error_files']:
                    output_text += f"   • {error_info['file']}: {error_info['error']}\n"
            
            output_text += f"\n📄 DOSYA DETAYLARI:\n"
            
            # file_details dict yapısını kullan
            for filename, object_count in results['file_details'].items():
                output_text += f"\n📄 {filename}:\n"
                output_text += f"   • Nesne sayısı: {object_count}\n"
                
                if object_count == 0:
                    # Hata dosyası mı kontrol et
                    is_error_file = any(err['file'] == filename for err in results.get('error_files', []))
                    if is_error_file:
                        output_text += "   • Durum: Hata (yukarıda detaylar)\n"
                    else:
                        output_text += "   • İçerik: Boş\n"
            
            self.yolo_results_text.setText(output_text)
            self.yolo_export_btn.setEnabled(True)
            self.current_yolo_results = results
            
            self.statusBar().showMessage(f"Analiz tamamlandı! {results['total_files']} dosya analiz edildi.", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz sırasında hata oluştu:\n{str(e)}")
            app_logger.error(f"YOLO analiz hatası: {str(e)}")
    
    def export_yolo_results(self):
        """YOLO sonuçlarını CSV olarak kaydet"""
        if not hasattr(self, 'current_yolo_results'):
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapmanız gerekiyor!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "YOLO Analiz Sonuçlarını Kaydet",
            f"yolo_analysis_{TimeUtils.get_timestamp()}.csv",
            "CSV Dosyaları (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Başlıkları yaz
                    writer.writerow(['Dosya Adı', 'Nesne Sayısı', 'Durum'])
                    
                    # Verileri yaz
                    results = self.current_yolo_results
                    for filename, object_count in results['file_details'].items():
                        # Hata durumu kontrol et
                        is_error_file = any(err['file'] == filename for err in results.get('error_files', []))
                        status = "Hatalı" if is_error_file else ("Boş" if object_count == 0 else "Normal")
                        
                        writer.writerow([
                            filename,
                            object_count,
                            status
                        ])
                    
                    # Hata detayları ekle
                    if results.get('error_files'):
                        writer.writerow([])  # Boş satır
                        writer.writerow(['HATA DETAYLARI'])
                        writer.writerow(['Dosya Adı', 'Hata Açıklaması'])
                        for error_info in results['error_files']:
                            writer.writerow([error_info['file'], error_info['error']])
                
                QMessageBox.information(self, "Başarılı", f"Sonuçlar başarıyla kaydedildi:\n{file_path}")
                self.statusBar().showMessage("CSV dosyası başarıyla kaydedildi!", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")
                app_logger.error(f"CSV kaydetme hatası: {str(e)}")

    def create_header(self, main_layout):
        """Başlık alanını oluştur"""
        header_layout = QHBoxLayout()
        
        # Aktif araç başlığı
        self.tool_title = QLabel("🎬 Video Frame Çıkarma")
        self.tool_title.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['text']};
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        """)
        
        header_layout.addWidget(self.tool_title)
        header_layout.addStretch()
        
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
    
    # =====================================
    # AUGMENTASYON METODLARI
    # =====================================
    
    def browse_augment_source(self):
        """Augmentasyon kaynak klasörünü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Augmentasyon Kaynak Klasörü Seç", 
            self.augment_source_input.text() or os.path.expanduser("~")
        )
        if folder:
            self.augment_source_input.setText(folder)
    
    def browse_augment_target(self):
        """Augmentasyon hedef klasörünü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Augmentasyon Hedef Klasörü Seç", 
            self.augment_target_input.text() or os.path.expanduser("~")
        )
        if folder:
            self.augment_target_input.setText(folder)
    
    def on_augment_folders_changed(self):
        """Augmentasyon klasör inputları değiştiğinde tetiklenir"""
        source_valid = os.path.isdir(self.augment_source_input.text())
        target_valid = self.augment_target_input.text().strip() != ""
        
        can_process = source_valid and target_valid
        self.augment_preview_btn.setEnabled(can_process)
        self.augment_process_btn.setEnabled(can_process)
    
    def select_all_effects(self):
        """Tüm efektleri seç"""
        for checkbox in self.effect_checkboxes.values():
            checkbox.setChecked(True)
    
    def clear_all_effects(self):
        """Tüm efekt seçimlerini temizle"""
        for checkbox in self.effect_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_weather_effects(self):
        """Hava durumu efektlerini seç"""
        weather_effects = ['add_snow', 'add_rain', 'add_fog', 'add_sun_flare']
        self.clear_all_effects()
        for effect in weather_effects:
            if effect in self.effect_checkboxes:
                self.effect_checkboxes[effect].setChecked(True)
    
    def select_road_effects(self):
        """Yol efektlerini seç"""
        road_effects = ['add_gravel', 'add_speed']  # manhole geçici olarak kaldırıldı
        self.clear_all_effects()
        for effect in road_effects:
            if effect in self.effect_checkboxes:
                self.effect_checkboxes[effect].setChecked(True)
    
    def get_selected_effects(self):
        """Seçili efektlerin listesini döndür"""
        selected = []
        for effect_key, checkbox in self.effect_checkboxes.items():
            if checkbox.isChecked():
                selected.append(effect_key)
        return selected
    
    def get_image_files(self, folder_path, formats, include_subdirs=True):
        """Belirtilen klasörden resim dosyalarını al"""
        image_files = []
        format_list = [f.strip().lower() for f in formats.split(',')]
        
        if include_subdirs:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(f'.{fmt}') for fmt in format_list):
                        image_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(f'.{fmt}') for fmt in format_list):
                    image_files.append(file_path)
        
        return image_files
    
    def preview_augmentation(self):
        """Augmentasyon önizlemesi göster"""
        try:
            source_folder = self.augment_source_input.text()
            formats = self.augment_formats_input.text()
            include_subdirs = self.augment_subdirs_cb.isChecked()
            selected_effects = self.get_selected_effects()
            
            if not selected_effects:
                QMessageBox.warning(self, "Uyarı", "Lütfen en az bir efekt seçin!")
                return
            
            # Resim dosyalarını al
            image_files = self.get_image_files(source_folder, formats, include_subdirs)
            
            if not image_files:
                QMessageBox.warning(self, "Uyarı", "Belirtilen klasörde resim dosyası bulunamadı!")
                return
            
            # Önizleme metni oluştur
            preview_text = f"""📊 AUGMENTASYON ÖNİZLEMESİ
            
📁 Kaynak Klasör: {source_folder}
📁 Hedef Klasör: {self.augment_target_input.text()}
🔍 Resim Formatları: {formats}
📂 Alt Dizinler: {'Evet' if include_subdirs else 'Hayır'}
🎨 Seçili Efektler: {len(selected_effects)} adet

🖼️ Bulunan Resimler: {len(image_files)} adet

📋 Uygulanacak Efektler:
"""
            
            for effect in selected_effects:
                effect_names = {
                    'random_brightness': '🔆 Rastgele Parlaklık',
                    'add_shadow': '🌑 Gölge Ekleme',
                    'add_snow': '❄️ Kar Efekti',
                    'add_rain': '🌧️ Yağmur Efekti',
                    'add_fog': '🌫️ Sis Efekti',
                    'add_gravel': '🪨 Çakıl Taşı',
                    'add_sun_flare': '☀️ Güneş Parıltısı',
                    'add_speed': '💨 Hız Bulanıklığı',
                    'add_autumn': '🍂 Sonbahar Renkleri',
                    'random_flip': '🔄 Rastgele Çevirme',
                    'add_manhole': '🕳️ Rögar Kapağı',
                    'correct_exposure': '📸 Pozlama Düzeltme'
                }
                preview_text += f"  • {effect_names.get(effect, effect)}\n"
            
            mode = self.augment_mode_combo.currentText()
            if mode == "Her efekt için ayrı dosya":
                total_files = len(image_files) * len(selected_effects)
                preview_text += f"\n📈 Üretilecek Toplam Dosya: {total_files} adet"
            else:
                preview_text += f"\n📈 Üretilecek Toplam Dosya: {len(image_files)} adet (her resim için rastgele 1 efekt)"
            
            # Önizlemeyi sonuçlar alanında göster
            self.augment_results_text.setPlainText(preview_text)
            
            QMessageBox.information(self, "Önizleme", "Önizleme hazırlandı! Sonuçlar bölümünde detayları görebilirsiniz.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Önizleme oluşturulurken hata oluştu:\n{str(e)}")
            app_logger.error(f"Augmentasyon önizleme hatası: {str(e)}")
    
    def process_augmentation(self):
        """Augmentasyon işlemini başlat"""
        try:
            source_folder = self.augment_source_input.text()
            target_folder = self.augment_target_input.text()
            formats = self.augment_formats_input.text()
            include_subdirs = self.augment_subdirs_cb.isChecked()
            selected_effects = self.get_selected_effects()
            mode = self.augment_mode_combo.currentText()
            prefix = self.augment_prefix_input.text()
            
            if not selected_effects:
                QMessageBox.warning(self, "Uyarı", "Lütfen en az bir efekt seçin!")
                return
            
            # Hedef klasörü oluştur
            os.makedirs(target_folder, exist_ok=True)
            
            # Resim dosyalarını al
            image_files = self.get_image_files(source_folder, formats, include_subdirs)
            
            if not image_files:
                QMessageBox.warning(self, "Uyarı", "Belirtilen klasörde resim dosyası bulunamadı!")
                return
            
            # Onay penceresi
            total_files = len(image_files) * len(selected_effects) if mode == "Her efekt için ayrı dosya" else len(image_files)
            reply = QMessageBox.question(
                self,
                "Onay",
                f"🎨 {len(image_files)} resime augmentasyon uygulanacak.\n"
                f"📈 Toplam {total_files} dosya oluşturulacak.\n\n"
                f"Devam etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # İşlemi başlat
            self.run_augmentation_process(image_files, target_folder, selected_effects, mode, prefix)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Augmentasyon işlemi başlatılırken hata oluştu:\n{str(e)}")
            app_logger.error(f"Augmentasyon işlem başlatma hatası: {str(e)}")
    
    def run_augmentation_process(self, image_files, target_folder, selected_effects, mode, prefix):
        """Augmentasyon işlemini çalıştır"""
        try:
            # Automold'u import et
            from ..core import Automold as am
        except ImportError:
            try:
                # Alternatif import yolu
                sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
                import Automold as am
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Automold modülü yüklenemedi:\n{str(e)}")
                return
        
        total_processed = 0
        total_errors = 0
        error_files = []
        
        # İşlem başlangıcı
        start_time = time.time()
        self.augment_results_text.setPlainText("🎨 Augmentasyon işlemi başlıyor...\n")
        
        try:
            for i, image_path in enumerate(image_files):
                try:
                    # Resmi yükle
                    image = cv2.imread(image_path)
                    if image is None:
                        raise ValueError(f"Resim yüklenemedi: {image_path}")
                    
                    # RGB'ye çevir (OpenCV BGR kullanır)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Dosya adı ve uzantısını al
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    ext = os.path.splitext(image_path)[1]
                    
                    # Efektleri uygula
                    if mode == "Her efekt için ayrı dosya":
                        # Her efekt için ayrı dosya oluştur
                        for effect in selected_effects:
                            try:
                                augmented_image = self.apply_augmentation_effect(image_rgb.copy(), effect, am)
                                
                                # Kaydet
                                output_filename = f"{prefix}{base_name}_{effect}{ext}"
                                output_path = os.path.join(target_folder, output_filename)
                                
                                # BGR'ye çevir ve kaydet
                                augmented_bgr = cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR)
                                cv2.imwrite(output_path, augmented_bgr)
                                total_processed += 1
                                
                            except Exception as e:
                                total_errors += 1
                                error_msg = f"Efekt '{effect}' uygulanırken hata: {str(e)}"
                                error_files.append(f"{image_path} -> {effect}: {error_msg}")
                                app_logger.error(error_msg)
                    else:
                        # Rastgele bir efekt uygula
                        effect = random.choice(selected_effects)
                        try:
                            augmented_image = self.apply_augmentation_effect(image_rgb.copy(), effect, am)
                            
                            # Kaydet
                            output_filename = f"{prefix}{base_name}_{effect}{ext}"
                            output_path = os.path.join(target_folder, output_filename)
                            
                            # BGR'ye çevir ve kaydet
                            augmented_bgr = cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR)
                            cv2.imwrite(output_path, augmented_bgr)
                            total_processed += 1
                            
                        except Exception as e:
                            total_errors += 1
                            error_msg = f"Efekt '{effect}' uygulanırken hata: {str(e)}"
                            error_files.append(f"{image_path} -> {effect}: {error_msg}")
                            app_logger.error(error_msg)
                    
                    # İlerleme göster
                    if (i + 1) % 10 == 0:
                        progress_text = f"İşlenen: {i + 1}/{len(image_files)} resim\n"
                        progress_text += f"Başarılı: {total_processed} dosya\n"
                        if total_errors > 0:
                            progress_text += f"Hata: {total_errors} dosya\n"
                        
                        current_text = self.augment_results_text.toPlainText()
                        self.augment_results_text.setPlainText(current_text + progress_text)
                        QApplication.processEvents()  # UI'yi güncelle
                
                except Exception as e:
                    total_errors += 1
                    error_msg = f"Resim işlenirken hata ({image_path}): {str(e)}"
                    error_files.append(error_msg)
                    app_logger.error(error_msg)
            
            # İşlem sonu raporu
            end_time = time.time()
            duration = end_time - start_time
            
            report = f"""
🎉 AUGMENTASYON İŞLEMİ TAMAMLANDI!

📊 İşlem Özeti:
• İşlenen Resim: {len(image_files)} adet
• Başarılı Dosya: {total_processed} adet
• Hatalı İşlem: {total_errors} adet
• İşlem Süresi: {duration:.2f} saniye
• Hedef Klasör: {target_folder}

"""
            
            if error_files:
                report += "❌ Hatalar:\n"
                for error in error_files[:10]:  # İlk 10 hatayı göster
                    report += f"  • {error}\n"
                if len(error_files) > 10:
                    report += f"  ... ve {len(error_files) - 10} hata daha\n"
            
            self.augment_results_text.setPlainText(report)
            
            if total_errors == 0:
                QMessageBox.information(self, "Başarılı", f"✅ {total_processed} dosya başarıyla oluşturuldu!")
            else:
                QMessageBox.warning(
                    self, 
                    "Kısmi Başarı", 
                    f"✅ {total_processed} dosya oluşturuldu\n❌ {total_errors} işlemde hata oluştu\n\nDetaylar için sonuçlar bölümüne bakın."
                )
            
            self.statusBar().showMessage(f"Augmentasyon tamamlandı: {total_processed} dosya", 5000)
            
        except Exception as e:
            error_msg = f"Augmentasyon işlemi genel hatası: {str(e)}"
            self.augment_results_text.setPlainText(f"❌ {error_msg}")
            QMessageBox.critical(self, "Hata", error_msg)
            app_logger.error(error_msg)
    
    def apply_augmentation_effect(self, image, effect_name, automold_module):
        """Belirtilen efekti resme uygula"""
        try:
            if effect_name == "random_brightness":
                return automold_module.random_brightness(image)
            elif effect_name == "add_shadow":
                return automold_module.add_shadow(image)
            elif effect_name == "add_snow":
                return automold_module.add_snow(image)
            elif effect_name == "add_rain":
                return automold_module.add_rain(image)
            elif effect_name == "add_fog":
                return automold_module.add_fog(image)
            elif effect_name == "add_gravel":
                return automold_module.add_gravel(image)
            elif effect_name == "add_sun_flare":
                return automold_module.add_sun_flare(image)
            elif effect_name == "add_speed":
                return automold_module.add_speed(image)
            elif effect_name == "add_autumn":
                return automold_module.add_autumn(image)
            elif effect_name == "random_flip":
                return automold_module.random_flip(image)
            # elif effect_name == "add_manhole":  # Geçici olarak devre dışı
            #     return automold_module.add_manhole(image)
            elif effect_name == "correct_exposure":
                return automold_module.correct_exposure(image)
            else:
                raise ValueError(f"Bilinmeyen efekt: {effect_name}")
                
        except Exception as e:
            app_logger.error(f"Efekt uygulama hatası ({effect_name}): {str(e)}")
            raise

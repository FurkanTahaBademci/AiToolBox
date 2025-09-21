"""
Modern UI bileşenleri
Gelişmiş kullanıcı deneyimi için özel widget'lar
"""

from PyQt5.QtWidgets import QPushButton, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from .styles import AppStyles

class ModernButton(QPushButton):
    """Modern tasarımlı buton bileşeni"""
    
    def __init__(self, text="", button_type="secondary", icon=None):
        super().__init__(text)
        self.button_type = button_type
        self.setFixedHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
        
    def apply_style(self):
        """Buton tipine göre stil uygula"""
        if self.button_type == "primary":
            self.setStyleSheet(AppStyles.get_primary_button_style())
        elif self.button_type == "danger":
            self.setStyleSheet(AppStyles.get_danger_button_style())
        else:
            self.setStyleSheet(AppStyles.get_secondary_button_style())

class StatusLabel(QLabel):
    """Durum göstergeli gelişmiş label"""
    
    def __init__(self, text="", status="ready"):
        super().__init__(text)
        self.status = status
        self.update_status(status, text)
    
    def update_status(self, status, text=None):
        """Durum ve metni güncelle"""
        self.status = status
        if text:
            self.setText(text)
        
        status_styles = AppStyles.get_status_styles()
        if status in status_styles:
            self.setStyleSheet(status_styles[status])

class InfoCard(QWidget):
    """Bilgi kartı bileşeni"""
    
    def __init__(self, title="", value="", description=""):
        super().__init__()
        self.title = title
        self.value = value
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Başlık
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_600']};
                font-size: {AppStyles.FONTS['size_small']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        
        # Değer
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['dark']};
                font-size: 18px;
                font-weight: {AppStyles.FONTS['weight_bold']};
                margin: 5px 0;
            }}
        """)
        
        # Açıklama
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_600']};
                font-size: {AppStyles.FONTS['size_small']};
            }}
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        # Kart stili
        self.setStyleSheet(f"""
            InfoCard {{
                background-color: {AppStyles.COLORS['white']};
                border: 1px solid {AppStyles.COLORS['gray_300']};
                border-radius: 10px;
            }}
            InfoCard:hover {{
                border-color: {AppStyles.COLORS['primary']};
                box-shadow: 0 2px 8px rgba(0, 122, 204, 0.1);
            }}
        """)
    
    def update_value(self, value):
        """Değeri güncelle"""
        self.value = value
        # Value label'ı bul ve güncelle
        value_label = self.findChild(QLabel)
        if value_label:
            value_label.setText(str(value))

class ProgressCard(QWidget):
    """İlerleme kartı bileşeni"""
    
    def __init__(self, title="İşlem Durumu"):
        super().__init__()
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['dark']};
                font-size: {AppStyles.FONTS['size_heading']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                margin-bottom: 10px;
            }}
        """)
        
        # Durum ve yüzde
        status_layout = QHBoxLayout()
        self.status_label = StatusLabel("Hazır", "ready")
        self.percentage_label = QLabel("")
        self.percentage_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_600']};
                font-size: {AppStyles.FONTS['size_body']};
                font-weight: {AppStyles.FONTS['weight_bold']};
            }}
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.percentage_label)
        
        layout.addWidget(title_label)
        layout.addLayout(status_layout)
        
        # Kart stili
        self.setStyleSheet(f"""
            ProgressCard {{
                background-color: {AppStyles.COLORS['white']};
                border: 2px solid {AppStyles.COLORS['gray_300']};
                border-radius: 12px;
            }}
        """)
    
    def update_progress(self, percentage, status_text, status_type="processing"):
        """İlerlemeyi güncelle"""
        self.status_label.update_status(status_type, status_text)
        if percentage >= 0:
            self.percentage_label.setText(f"%{percentage}")
        else:
            self.percentage_label.setText("")

class LogViewer(QWidget):
    """Gelişmiş log görüntüleyici"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık
        header_layout = QHBoxLayout()
        title_label = QLabel("İşlem Logları")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppStyles.COLORS['gray_700']};
                font-size: {AppStyles.FONTS['size_body']};
                font-weight: {AppStyles.FONTS['weight_bold']};
                margin-bottom: 8px;
            }}
        """)
        
        clear_button = ModernButton("Temizle", "secondary")
        clear_button.setFixedHeight(30)
        clear_button.setFixedWidth(80)
        clear_button.clicked.connect(self.clear_logs)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        
        layout.addLayout(header_layout)
    
    def clear_logs(self):
        """Logları temizle"""
        # Bu fonksiyon main window'dan çağrılacak
        pass

class VideoInfoCard(InfoCard):
    """Video bilgileri için özel kart"""
    
    def __init__(self):
        super().__init__(
            title="VİDEO BİLGİLERİ",
            value="Video seçilmedi",
            description="Lütfen işlemek istediğiniz video dosyasını seçin"
        )
    
    def update_video_info(self, frame_count, fps, width, height, duration):
        """Video bilgilerini güncelle"""
        self.update_value("Video Yüklendi")
        
        # Açıklamayı güncelle
        desc_label = self.findChildren(QLabel)[2]  # Üçüncü label açıklama
        desc_label.setText(
            f"📹 {frame_count:,} frame • "
            f"🎬 {fps} FPS • "
            f"📐 {width}×{height} • "
            f"⏱️ {duration:.1f} saniye"
        )

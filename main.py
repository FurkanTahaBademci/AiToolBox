"""
AI ToolBox
Modern PyQt5 tabanlı çoklu araç platformu

Versiyon: 1.0.0
"""

import sys
import os

# Proje yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Kendi modüllerimizi import et
from src.ui import MainWindow
from src.utils import app_logger

class AIToolBoxApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        
    def setup_application(self):
        """Uygulamayı konfigüre et"""
        # QApplication oluştur
        self.app = QApplication(sys.argv)
        
        # Uygulama bilgileri
        self.app.setApplicationName("AI ToolBox")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("AIToolBox")
        self.app.setOrganizationDomain("aitoolbox.app")
        
        # Yüksek DPI desteği
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Varsayılan font ayarları
        font = QFont("Segoe UI", 9)
        font.setStyleHint(QFont.SansSerif)
        self.app.setFont(font)
        
        app_logger.info("Uygulama başarıyla konfigüre edildi")
    
    def create_main_window(self):
        """Ana pencereyi oluştur"""
        try:
            self.main_window = MainWindow()
            app_logger.info("Ana pencere oluşturuldu")
            return True
        except Exception as e:
            app_logger.error(f"Ana pencere oluşturulurken hata: {e}")
            return False
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            # Uygulamayı kur
            self.setup_application()
            
            # Ana pencereyi oluştur
            if not self.create_main_window():
                app_logger.error("Ana pencere oluşturulamadı, uygulama sonlandırılıyor")
                return 1
            
            # Pencereyi göster
            self.main_window.show()
            
            app_logger.info("AI ToolBox başlatıldı")
            
            # Event loop'u başlat
            return self.app.exec_()
            
        except Exception as e:
            app_logger.error(f"Uygulama çalıştırılırken kritik hata: {e}")
            return 1
        
        finally:
            app_logger.info("Uygulama sonlandırıldı")

def main():
    """Ana uygulama giriş noktası"""
    try:
        app = AIToolBoxApp()
        exit_code = app.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        app_logger.info("Uygulama Ctrl+C ile sonlandırıldı")
        sys.exit(0)
    except Exception as e:
        app_logger.error(f"Kritik uygulama hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

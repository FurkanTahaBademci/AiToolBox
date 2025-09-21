"""
Yardımcı fonksiyonlar ve araçlar
"""

import os
import logging
from datetime import datetime
from PyQt5.QtCore import QStandardPaths

class Logger:
    """Uygulama için gelişmiş logging sistemi"""
    
    def __init__(self, name="AIToolBox"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Log formatı
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Dosya handler
        try:
            log_dir = self.get_log_directory()
            log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Log dosyası oluşturulamadı: {e}")
    
    def get_log_directory(self):
        """Log dizinini al/oluştur"""
        if os.name == 'nt':  # Windows
            log_dir = os.path.join(os.getenv('APPDATA'), 'AIToolBox', 'logs')
        else:  # Linux/Mac
            log_dir = os.path.join(os.path.expanduser('~'), '.aitoolbox', 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)

class FileUtils:
    """Dosya işlemleri için yardımcı sınıf"""
    
    @staticmethod
    def get_safe_filename(filename):
        """Güvenli dosya adı oluştur"""
        # Windows için yasak karakterleri temizle
        forbidden_chars = '<>:"/\\|?*'
        for char in forbidden_chars:
            filename = filename.replace(char, '_')
        
        # Maksimum uzunluk kontrolü
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def get_unique_filename(filepath):
        """Eğer dosya varsa benzersiz ad oluştur"""
        if not os.path.exists(filepath):
            return filepath
        
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_filepath = os.path.join(directory, new_filename)
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1
    
    @staticmethod
    def format_file_size(size_bytes):
        """Dosya boyutunu okunabilir formata çevir"""
        if size_bytes == 0:
            return "0 B"
        
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024.0 and i < len(size_units) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_units[i]}"
    
    @staticmethod
    def validate_video_file(filepath):
        """Video dosyasını doğrula"""
        if not os.path.exists(filepath):
            return False, "Dosya bulunamadı"
        
        if not os.path.isfile(filepath):
            return False, "Bu bir dosya değil"
        
        # Desteklenen formatlar
        supported_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.3gp']
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext not in supported_extensions:
            return False, f"Desteklenmeyen format: {file_ext}"
        
        # Dosya boyutu kontrolü (maksimum 10GB)
        file_size = os.path.getsize(filepath)
        if file_size > 10 * 1024 * 1024 * 1024:  # 10GB
            return False, "Dosya çok büyük (maksimum 10GB)"
        
        if file_size == 0:
            return False, "Dosya boş"
        
        return True, "Geçerli video dosyası"

class TimeUtils:
    """Zaman işlemleri için yardımcı sınıf"""
    
    @staticmethod
    def seconds_to_time_string(seconds):
        """Saniyeyi saat:dakika:saniye formatına çevir"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def estimate_processing_time(total_frames, frames_per_second):
        """Tahmini işlem süresini hesapla"""
        if frames_per_second <= 0:
            return "Bilinmiyor"
        
        estimated_seconds = total_frames / frames_per_second
        return TimeUtils.seconds_to_time_string(estimated_seconds)

class ConfigManager:
    """Uygulama ayarları yöneticisi"""
    
    def __init__(self):
        self.config_dir = self.get_config_directory()
        self.config_file = os.path.join(self.config_dir, 'settings.ini')
        self.default_settings = {
            'last_video_dir': os.path.expanduser('~'),
            'last_output_dir': os.path.expanduser('~'),
            'default_frame_interval': '30',
            'jpeg_quality': '95',
            'auto_open_output': 'true',
            'log_level': 'INFO'
        }
    
    def get_config_directory(self):
        """Konfigürasyon dizinini al/oluştur"""
        if os.name == 'nt':  # Windows
            config_dir = os.path.join(os.getenv('APPDATA'), 'AIToolBox')
        else:  # Linux/Mac
            config_dir = os.path.join(os.path.expanduser('~'), '.aitoolbox')
        
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def load_settings(self):
        """Ayarları yükle"""
        settings = self.default_settings.copy()
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            settings[key.strip()] = value.strip()
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
        
        return settings
    
    def save_settings(self, settings):
        """Ayarları kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# AI ToolBox Settings\n")
                f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for key, value in settings.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")

# Global logger instance
app_logger = Logger()

# Kullanım örneği:
# from src.utils.helpers import app_logger
# app_logger.info("Bu bir bilgi mesajıdır")

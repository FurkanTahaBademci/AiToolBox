"""
YOLO Format Analiz Modülü
YOLO formatındaki .txt dosyalarını analiz eder
"""

import os
import glob
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
from ..utils.helpers import app_logger

class YoloAnalyzer:
    """YOLO format dosyalarını analiz eden sınıf"""
    
    def __init__(self):
        self.class_counts = Counter()
        self.file_counts = defaultdict(int)
        self.total_files = 0
        self.total_objects = 0
        self.error_files = []
        
    def analyze_folder(self, folder_path: str) -> Dict:
        """
        Klasördeki tüm .txt dosyalarını analiz et
        
        Args:
            folder_path: Analiz edilecek klasör yolu
            
        Returns:
            Dict: Analiz sonuçları
        """
        self.reset_statistics()
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Klasör bulunamadı: {folder_path}")
        
        # .txt dosyalarını bul
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        if not txt_files:
            app_logger.warning(f"Klasörde .txt dosyası bulunamadı: {folder_path}")
            return self.get_statistics()
        
        app_logger.info(f"YOLO analizi başlatıldı: {len(txt_files)} dosya bulundu")
        
        # Her dosyayı analiz et
        for txt_file in txt_files:
            try:
                objects = self.parse_yolo_file(txt_file)
                filename = os.path.basename(txt_file)
                self.file_counts[filename] = len(objects)
                
                for class_id, _, _, _, _ in objects:
                    self.class_counts[class_id] += 1
                    self.total_objects += 1
                    
            except Exception as e:
                filename = os.path.basename(txt_file)
                error_msg = str(e)
                self.error_files.append({
                    'file': filename,
                    'error': error_msg
                })
                # Hata dosyasını 0 nesne ile kaydet ki analiz devam etsin
                self.file_counts[filename] = 0
                app_logger.warning(f"Dosya analiz uyarısı {filename}: {error_msg} - Analiz devam ediyor")
        
        self.total_files = len(txt_files)
        app_logger.info(f"YOLO analizi tamamlandı: {self.total_objects} nesne, {len(self.error_files)} hata")
        
        return self.get_statistics()
    
    def parse_yolo_file(self, file_path: str) -> List[Tuple]:
        """
        Tek YOLO dosyasını parse et
        
        Args:
            file_path: YOLO .txt dosya yolu
            
        Returns:
            List[Tuple]: (class_id, x_center, y_center, width, height) listesi
        """
        objects = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Boş satırları atla
                    continue
                
                parts = line.split()
                if len(parts) != 5:
                    raise ValueError(f"Satır {line_num}: Geçersiz format (5 değer bekleniyor, {len(parts)} bulundu)")
                
                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    
                    # Koordinat doğrulaması (0-1 arası olmalı)
                    if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                           0 < width <= 1 and 0 < height <= 1):
                        raise ValueError(f"Satır {line_num}: Koordinatlar 0-1 aralığında olmalı")
                    
                    objects.append((class_id, x_center, y_center, width, height))
                    
                except ValueError as e:
                    raise ValueError(f"Satır {line_num}: {str(e)}")
        
        return objects
    
    def get_statistics(self) -> Dict:
        """Analiz sonuçlarını döndür"""
        if self.total_objects == 0:
            return {
                'total_files': self.total_files,
                'total_objects': 0,
                'class_counts': {},
                'class_percentages': {},
                'avg_objects_per_file': 0,
                'most_common_class': None,
                'least_common_class': None,
                'error_files': self.error_files,
                'files_with_objects': 0,
                'empty_files': self.total_files,
                'file_details': dict(self.file_counts)  # Eksik olan satır eklendi
            }
        
        # Yüzdelik hesapla
        class_percentages = {
            class_id: (count / self.total_objects) * 100 
            for class_id, count in self.class_counts.items()
        }
        
        # En çok ve en az bulunan sınıflar
        most_common = self.class_counts.most_common(1)[0] if self.class_counts else None
        least_common = self.class_counts.most_common()[-1] if self.class_counts else None
        
        # Nesne içeren dosya sayısı
        files_with_objects = sum(1 for count in self.file_counts.values() if count > 0)
        
        return {
            'total_files': self.total_files,
            'total_objects': self.total_objects,
            'class_counts': dict(self.class_counts),
            'class_percentages': class_percentages,
            'avg_objects_per_file': round(self.total_objects / max(self.total_files, 1), 2),
            'most_common_class': most_common,
            'least_common_class': least_common,
            'error_files': self.error_files,
            'files_with_objects': files_with_objects,
            'empty_files': self.total_files - files_with_objects,
            'file_details': dict(self.file_counts)
        }
    
    def reset_statistics(self):
        """İstatistikleri sıfırla"""
        self.class_counts.clear()
        self.file_counts.clear()
        self.total_files = 0
        self.total_objects = 0
        self.error_files.clear()
    
    def export_to_csv(self, output_path: str, stats: Dict = None):
        """Sonuçları CSV olarak dışa aktar"""
        if stats is None:
            stats = self.get_statistics()
        
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Genel istatistikler
            writer.writerow(['Genel İstatistikler'])
            writer.writerow(['Toplam Dosya', stats['total_files']])
            writer.writerow(['Toplam Nesne', stats['total_objects']])
            writer.writerow(['Dosya Başına Ortalama Nesne', stats['avg_objects_per_file']])
            writer.writerow(['Nesne İçeren Dosyalar', stats['files_with_objects']])
            writer.writerow(['Boş Dosyalar', stats['empty_files']])
            writer.writerow([])
            
            # Sınıf istatistikleri
            writer.writerow(['Sınıf İstatistikleri'])
            writer.writerow(['Sınıf ID', 'Nesne Sayısı', 'Yüzde (%)'])
            
            for class_id in sorted(stats['class_counts'].keys()):
                count = stats['class_counts'][class_id]
                percentage = stats['class_percentages'][class_id]
                writer.writerow([class_id, count, f"{percentage:.2f}"])
        
        app_logger.info(f"CSV raporu oluşturuldu: {output_path}")

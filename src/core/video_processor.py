"""
Video işleme ve frame çıkarma modülü
Gelişmiş hata yönetimi ve detaylı loglama ile
"""

import os
import cv2
import time
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class VideoProcessor(QThread):
    """
    Video frame çıkarma işlemini arka planda çalıştıran thread sınıfı
    """
    
    # Sinyaller
    progress_updated = pyqtSignal(int)  # İlerleme yüzdesi
    status_updated = pyqtSignal(str, str)  # Durum mesajı, tip
    log_updated = pyqtSignal(str, str)  # Log mesajı, seviye
    frame_processed = pyqtSignal(int, str)  # İşlenen frame numarası, dosya adı
    finished = pyqtSignal(bool, str)  # Başarı durumu, mesaj
    
    def __init__(self):
        super().__init__()
        self.video_path = ""
        self.output_path = ""
        self.frame_interval = 1
        self.start_frame = 0
        self.end_frame = 0
        self.is_stopped = False
        
        # Çıktı ayarları
        self.output_format = "jpg"  # jpg, png, bmp
        self.output_quality = 95    # 1-100 (sadece JPEG için)
        
        # İstatistikler
        self.total_frames_to_process = 0
        self.processed_frames_count = 0
        self.saved_frames_count = 0
        self.start_time = None
        
    def set_parameters(self, video_path, output_path, frame_interval, start_frame, end_frame, output_format="jpg", output_quality=95):
        """İşlem parametrelerini ayarla"""
        self.video_path = video_path
        self.output_path = output_path
        self.frame_interval = max(1, frame_interval)  # Minimum 1
        self.start_frame = max(0, start_frame)
        self.end_frame = end_frame
        self.output_format = output_format.lower()
        self.output_quality = max(1, min(100, output_quality))  # 1-100 arası
        self.is_stopped = False
        
        self.log_updated.emit(
            f"🔧 İşlem parametreleri ayarlandı: "
            f"Aralık={self.frame_interval}, "
            f"Başlangıç={self.start_frame}, "
            f"Bitiş={self.end_frame if self.end_frame > 0 else 'Video sonu'}, "
            f"Format={self.output_format.upper()}, "
            f"Kalite={self.output_quality}%",
            "info"
        )
        
    def stop_processing(self):
        """İşlemi durdur"""
        self.is_stopped = True
        self.log_updated.emit("⏹️ İşlem durdurma komutu alındı...", "warning")
        
    def run(self):
        """Ana işlem thread'i"""
        try:
            self.start_time = time.time()
            self.processed_frames_count = 0
            self.saved_frames_count = 0
            
            self.status_updated.emit("Video açılıyor...", "processing")
            self.log_updated.emit(f"📁 Video dosyası açılıyor: {self.video_path}", "info")
            
            # Video dosyasını aç
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise Exception("Video dosyası açılamadı. Dosya formatı desteklenmiyor olabilir.")
            
            # Video bilgilerini al
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.log_updated.emit(
                f"📹 Video bilgileri: {total_frames} frame, {fps:.1f} FPS, {width}x{height}",
                "info"
            )
            
            # End frame kontrolü
            if self.end_frame <= 0 or self.end_frame > total_frames:
                self.end_frame = total_frames
                self.log_updated.emit(f"📍 Bitiş frame otomatik ayarlandı: {self.end_frame}", "info")
            
            # Start frame kontrolü
            if self.start_frame >= self.end_frame:
                raise Exception(f"Başlangıç frame ({self.start_frame}) bitiş frame'den ({self.end_frame}) büyük olamaz!")
            
            # İşlenecek frame sayısını hesapla
            self.total_frames_to_process = len(range(self.start_frame, self.end_frame, self.frame_interval))
            
            self.log_updated.emit(
                f"🎯 İşlenecek frame sayısı: {self.total_frames_to_process} "
                f"(Frame {self.start_frame}-{self.end_frame}, aralık: {self.frame_interval})",
                "info"
            )
            
            # Çıktı klasörünü kontrol et
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
                self.log_updated.emit(f"📁 Çıktı klasörü oluşturuldu: {self.output_path}", "info")
            
            # Frame işleme döngüsü
            self.status_updated.emit("Frame'ler işleniyor...", "processing")
            
            frame_numbers = list(range(self.start_frame, self.end_frame, self.frame_interval))
            
            for i, frame_num in enumerate(frame_numbers):
                if self.is_stopped:
                    self.log_updated.emit("⏹️ İşlem kullanıcı tarafından durduruldu", "warning")
                    break
                
                try:
                    # Frame'i al
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                    ret, frame = cap.read()
                    
                    if not ret:
                        self.log_updated.emit(f"⚠️ Frame {frame_num} okunamadı, atlanıyor...", "warning")
                        continue
                    
                    # Dosya adını oluştur
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"frame_{frame_num:06d}_{timestamp}.{self.output_format}"
                    filepath = os.path.join(self.output_path, filename)
                    
                    # Frame'i kaydet - format ve kaliteye göre
                    if self.output_format == "jpg" or self.output_format == "jpeg":
                        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, self.output_quality])
                    elif self.output_format == "png":
                        # PNG için sıkıştırma seviyesi (0-9)
                        compression = 9 - int((self.output_quality / 100) * 9)
                        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, compression])
                    elif self.output_format == "bmp":
                        success = cv2.imwrite(filepath, frame)
                    else:
                        # Varsayılan JPEG
                        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, self.output_quality])
                    
                    if success:
                        self.saved_frames_count += 1
                        self.frame_processed.emit(frame_num, filename)
                        
                        # Her 10 frame'de bir detaylı log
                        if self.saved_frames_count % 10 == 0:
                            elapsed_time = time.time() - self.start_time
                            fps_current = self.saved_frames_count / elapsed_time if elapsed_time > 0 else 0
                            self.log_updated.emit(
                                f"✅ {self.saved_frames_count} frame kaydedildi "
                                f"(Hız: {fps_current:.1f} frame/sn)",
                                "success"
                            )
                    else:
                        self.log_updated.emit(f"❌ Frame {frame_num} kaydedilemedi: {filepath}", "error")
                    
                    self.processed_frames_count += 1
                    
                    # İlerleme hesapla
                    progress = int((i + 1) / len(frame_numbers) * 100)
                    self.progress_updated.emit(progress)
                    
                    # Durum güncelle
                    remaining_frames = len(frame_numbers) - (i + 1)
                    elapsed_time = time.time() - self.start_time
                    
                    if elapsed_time > 0 and i > 0:
                        avg_time_per_frame = elapsed_time / (i + 1)
                        eta_seconds = remaining_frames * avg_time_per_frame
                        eta_minutes = int(eta_seconds / 60)
                        eta_seconds = int(eta_seconds % 60)
                        
                        self.status_updated.emit(
                            f"Frame {frame_num} işlendi • "
                            f"{self.saved_frames_count}/{self.total_frames_to_process} tamamlandı • "
                            f"Kalan süre: {eta_minutes:02d}:{eta_seconds:02d}",
                            "processing"
                        )
                    
                except Exception as e:
                    self.log_updated.emit(f"❌ Frame {frame_num} işlenirken hata: {str(e)}", "error")
                    continue
            
            cap.release()
            
            # İşlem tamamlandı
            if not self.is_stopped:
                total_time = time.time() - self.start_time
                avg_fps = self.saved_frames_count / total_time if total_time > 0 else 0
                
                success_message = (
                    f"✅ İşlem başarıyla tamamlandı!\n"
                    f"📊 İstatistikler:\n"
                    f"• Toplam işlenen frame: {self.processed_frames_count}\n"
                    f"• Başarıyla kaydedilen: {self.saved_frames_count}\n"
                    f"• Toplam süre: {total_time:.1f} saniye\n"
                    f"• Ortalama hız: {avg_fps:.1f} frame/saniye\n"
                    f"• Çıktı klasörü: {self.output_path}"
                )
                
                self.log_updated.emit(success_message, "success")
                self.status_updated.emit(
                    f"Tamamlandı! {self.saved_frames_count} frame kaydedildi",
                    "ready"
                )
                self.finished.emit(True, success_message)
            else:
                self.status_updated.emit(
                    f"Durduruldu! {self.saved_frames_count} frame kaydedildi",
                    "warning"
                )
                self.finished.emit(False, "İşlem kullanıcı tarafından durduruldu")
                
        except Exception as e:
            error_message = f"❌ Video işleme hatası: {str(e)}"
            self.log_updated.emit(error_message, "error")
            self.status_updated.emit("Hata oluştu!", "error")
            self.finished.emit(False, error_message)
            
        finally:
            if 'cap' in locals():
                cap.release()

class VideoAnalyzer:
    """Video dosyası analiz sınıfı"""
    
    @staticmethod
    def analyze_video(video_path):
        """
        Video dosyasını analiz et ve bilgileri döndür
        
        Returns:
            dict: Video bilgileri veya None (hata durumunda)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Dosya boyutu
            file_size = os.path.getsize(video_path)
            file_size_mb = file_size / (1024 * 1024)
            
            cap.release()
            
            return {
                'frame_count': frame_count,
                'fps': fps,
                'width': width,
                'height': height,
                'duration': duration,
                'file_size_mb': file_size_mb,
                'resolution': f"{width}x{height}",
                'codec': 'N/A'  # OpenCV ile codec bilgisi almak zor
            }
            
        except Exception as e:
            print(f"Video analiz hatası: {e}")
            return None
    
    @staticmethod
    def validate_frame_range(start_frame, end_frame, total_frames):
        """
        Frame aralığını doğrula
        
        Returns:
            tuple: (geçerli_mi, düzeltilmiş_start, düzeltilmiş_end, hata_mesajı)
        """
        errors = []
        
        # Başlangıç frame kontrolü
        if start_frame < 0:
            start_frame = 0
            errors.append("Başlangıç frame 0'a ayarlandı")
        
        if start_frame >= total_frames:
            start_frame = total_frames - 1
            errors.append(f"Başlangıç frame {total_frames-1}'e ayarlandı")
        
        # Bitiş frame kontrolü
        if end_frame <= 0 or end_frame > total_frames:
            end_frame = total_frames
            errors.append(f"Bitiş frame {total_frames}'e ayarlandı")
        
        # Aralık kontrolü
        if start_frame >= end_frame:
            end_frame = total_frames
            start_frame = 0
            errors.append("Geçersiz aralık nedeniyle varsayılan değerler kullanıldı")
        
        is_valid = len(errors) == 0
        error_message = "; ".join(errors) if errors else None
        
        return is_valid, start_frame, end_frame, error_message

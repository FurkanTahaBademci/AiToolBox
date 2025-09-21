# AI ToolBox v1.0.0

🤖 **Modern AI Araçları Koleksiyonu**

PyQt5 ile geliştirilmiş, kullanıcı dostu arayüze sahip AI araçları koleksiyonu.

## ✨ Özellikler

### 🎯 **Video İşleme Araçları**
- 📹 Çoklu format desteği (MP4, AVI, MOV, MKV, WMV, FLV, M4V, 3GP)
- 🔍 Otomatik video analizi ve bilgi gösterimi
- ⚙️ Gelişmiş frame aralığı ayarları
- 🎯 Başlangıç ve bitiş frame seçimi
- 📊 Gerçek zamanlı işlem takibi

### 🤖 **YOLO Analiz Araçları**

- 📄 YOLO format dosya analizi (.txt)
- 📊 Sınıf istatistikleri ve sayımları
- 📁 Toplu klasör analizi
- 📈 CSV export özelliği
- 🔍 Detaylı rapor görüntüleme

### 🎨 **Modern Arayüz**

- 🌟 Sade ve profesyonel tasarım
- 📱 Responsive layout (yeniden boyutlandırılabilir)
- 🎨 Modern renk paleti ve tipografi
- 🖱️ Hover efektleri ve animasyonlar
- 📋 Detaylı bilgi kartları

### 🔧 **Gelişmiş Özellikler**

- 🔄 Multi-threading (arayüz donmaması)
- 📈 İlerleme takibi ve durum gösterimi
- 📝 Detaylı log sistemi
- 💾 Ayar kaydetme/yükleme
- ⚠️ Gelişmiş hata yönetimi
- 📊 İstatistik gösterimi

## 📁 Proje Yapısı

```
video/
├── src/                     # Ana kaynak kodlar
│   ├── ui/                  # Kullanıcı arayüzü
│   │   ├── __init__.py
│   │   ├── main_window.py   # Ana pencere
│   │   ├── components.py    # UI bileşenleri
│   │   └── styles.py        # CSS stilleri
│   ├── core/                # Çekirdek işlemler
│   │   ├── __init__.py
│   │   └── video_processor.py # Video işleme
│   └── utils/               # Yardımcı araçlar
│       ├── __init__.py
│       └── helpers.py       # Yardımcı fonksiyonlar
├── assets/                  # Varlıklar (resimler, ikonlar)
├── main.py                  # Ana uygulama dosyası
├── requirements.txt         # Python bağımlılıkları
└── README.md               # Bu dosya
```

## 🚀 Kurulum

### 1. **Python Gereksinimleri**

- Python 3.7 veya üstü
- PyQt5
- OpenCV

### 2. **Bağımlılıkları Yükleyin**

```bash
pip install -r requirements.txt
```

### 3. **Uygulamayı Çalıştırın**

```bash
python main.py
```

## 📖 Kullanım Kılavuzu

### 🎬 **Video Seçimi**

1. "📂 Video Seç" butonuna tıklayın

2. İşlemek istediğiniz video dosyasını seçin

3. Video bilgileri otomatik olarak analiz edilecek

### 💾 **Çıktı Konumu**

1. "📁 Klasör Seç" butonuna tıklayın

2. Frame'lerin kaydedileceği klasörü belirleyin

### ⚙️ **Frame Ayarları**

- **Frame Aralığı**: Her kaç frame'de bir görüntü alınacağını belirler
- **Başlangıç Frame**: İşlemenin başlayacağı frame numarası
- **Bitiş Frame**: İşlemenin biteceği frame (0 = video sonu)

### ▶️ **İşlemi Başlatma**

1. Tüm ayarları kontrol edin

2. "▶️ İşlemi Başlat" butonuna tıklayın

3. İlerlemeyi takip edin

4. İsterseniz "⏹️ Durdur" ile işlemi durdurun

## 🔧 Teknik Detaylar

### **Desteklenen Formatlar**

| Video Formatı | Uzantı | Destek |
|---------------|--------|--------|
| MP4 | .mp4 | ✅ Tam |
| AVI | .avi | ✅ Tam |
| MOV | .mov | ✅ Tam |
| MKV | .mkv | ✅ Tam |
| WMV | .wmv | ✅ Tam |
| FLV | .flv | ✅ Tam |
| M4V | .m4v | ✅ Tam |
| 3GP | .3gp | ✅ Tam |

### **Çıktı Özellikleri**

- **Format**: JPEG (.jpg)
- **Kalite**: %95 (ayarlanabilir)
- **Adlandırma**: `frame_XXXXXX_timestamp.jpg`
- **Maksimum Dosya Boyutu**: 10GB

### **Performans**

- **Multi-threading**: Arayüz responsive kalır
- **Bellek Optimizasyonu**: Büyük videolar için optimize
- **Hız**: ~10-50 frame/saniye (donanıma bağlı)

## 📋 Sürüm Geçmişi

### **v2.0.0** (Mevcut)

- ✅ Tamamen yeniden yazıldı
- ✅ Modüler kod yapısı
- ✅ Modern UI tasarımı
- ✅ Gelişmiş hata yönetimi
- ✅ Detaylı log sistemi
- ✅ Ayar kaydetme/yükleme
- ✅ Frame aralığı düzeltmeleri

### **v1.0.0** (Eski)

- Temel frame çıkarma özelliği
- Basit arayüz
- Sınırlı hata yönetimi

## 🔮 Gelecek Özellikler

- [ ] 🖼️ Video önizleme
- [ ] 🎨 Farklı çıktı formatları (PNG, BMP)
- [ ] 📦 Toplu video işleme
- [ ] ✂️ Video düzenleme araçları
- [ ] 🔍 Gelişmiş filtreleme
- [ ] 🌐 Çoklu dil desteği
- [ ] 🔗 FFmpeg entegrasyonu
- [ ] ☁️ Bulut depolama desteği

## 🐛 Sorun Giderme

### **Yaygın Sorunlar**

**"Video açılamadı" Hatası:**

- Video dosyasının mevcut olduğundan emin olun
- Desteklenen formatta olduğunu kontrol edin
- Dosya izinlerini kontrol edin

**"Çıktı klasörü bulunamadı" Hatası:**

- Klasörün var olduğundan emin olun
- Yazma izniniz olduğunu kontrol edin

**Yavaş İşleme:**

- Daha büyük frame aralığı seçin
- SSD kullanın (HDD yerine)
- Sistem kaynaklarını kontrol edin

### **Log Dosyaları**

Uygulama otomatik olarak log dosyaları oluşturur:

- **Windows**: `%APPDATA%\AIToolBox\logs\`
- **Linux/Mac**: `~/.aitoolbox/logs/`

## 🤝 Katkıda Bulunma

Bu açık kaynak proje katkılara açıktır:

1. Fork yapın

2. Feature branch oluşturun

3. Değişikliklerinizi commit edin

4. Pull request gönderin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

**AcademicSight**

- 🌐 Website: [academicsight.com](https://academicsight.com)
- 📧 Email: info@academicsight.com

---

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

# ⚡ Elektrikli Şarj İstasyonu Lokasyon Analiz Sistemi

Bu proje, elektrikli araç şarj istasyonlarının lokasyon analizini yapan kapsamlı bir web uygulamasıdır. Yatırımcıların ve genel kullanıcıların elektrikli şarj istasyonlarının konumlarını analiz etmesine, yeni istasyonlar için uygun lokasyonları belirlemesine ve yatırım getirisi hesaplamalarını yapmasına olanak tanır.

## 🚀 Özellikler

### 👥 Genel Kullanıcı Özellikleri
- **🗺️ İnteraktif Harita**: Türkiye'deki mevcut şarj istasyonlarını görüntüleme
- **📊 İstatistikler**: Operatör dağılımı, güç dağılımı ve kullanım oranları
- **👥 Demografik Analiz**: Şehir bazında demografik veriler ve potansiyel analizi
- **🔍 Filtreleme**: Şehir, operatör ve güç bazında filtreleme

### 💼 Yatırımcı Özellikleri
- **🎯 Lokasyon Analizi**: Harita üzerinde seçilen konumun potansiyel analizi
- **🏆 Rakip Analizi**: Mevcut operatörlerin performans karşılaştırması
- **💰 ROI Hesaplayıcı**: Detaylı yatırım getirisi hesaplamaları
- **📋 Rapor Oluşturucu**: Kapsamlı analiz raporları

## 📋 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım Adım Kurulum

1. **Projeyi indirin**:
```bash
# GitHub'dan klonlayın (varsa)
git clone https://github.com/kullanici/elektrikli-sarj-istasyonu-analizi.git
cd elektrikli-sarj-istasyonu-analizi

# Veya dosyaları manuel olarak bir klasöre kaydedin
```

2. **Sanal ortam oluşturun (önerilir)**:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Gerekli paketleri yükleyin**:
```bash
pip install -r requirements.txt
```

4. **Uygulamayı çalıştırın**:
```bash
streamlit run app.py
```

5. **Tarayıcınızda açın**:
Uygulama otomatik olarak varsayılan tarayıcınızda açılacaktır. Eğer açılmazsa:
```
http://localhost:8501
```

## 🎯 Kullanım Kılavuzu

### Başlangıç
1. Uygulama açıldığında sol kenar çubuğundan kullanıcı tipinizi seçin:
   - **Genel Kullanıcı**: Mevcut şarj istasyonlarını görüntülemek için
   - **Yatırımcı**: Yatırım analizi yapmak için

### Genel Kullanıcı Modu

#### 🗺️ Şarj İstasyonu Haritası
- Türkiye haritasında mevcut şarj istasyonlarını görüntüleyin
- Şehir, operatör ve güç aralığına göre filtreleme yapın
- İstasyon detaylarını görmek için haritadaki işaretlere tıklayın

#### 📈 İstatistikler
- Operatör dağılımı pasta grafiği
- Güç dağılımı histogramı
- Şehir bazında istasyon sayıları
- Kullanım oranı analizleri

#### 👥 Demografik Analiz
- Şehirlerin demografik verileri tablosu
- Gelir vs EV oranı scatter grafiği
- Şehir potansiyel puanları

### Yatırımcı Modu

#### 🎯 Bölge Analizi
1. Harita üzerinde analiz etmek istediğiniz konuma tıklayın
2. Sistem otomatik olarak lokasyon analizini yapacaktır:
   - Potansiyel puanı (1-10 arası)
   - Yakındaki rakip istasyonlar
   - Demografik veriler
   - Yatırım önerileri

#### 🏆 Rakip Analizi
- Operatör performans tablosu
- Pazar payı analizleri
- Gelir karşılaştırmaları
- SWOT analizi

#### 💰 Yatırım Getirisi
1. **Parametreleri ayarlayın**:
   - İstasyon tipi (AC 22kW - DC 350kW)
   - Soket sayısı
   - Günlük kullanım saati
   - Elektrik fiyatı
   - İşletme maliyetleri

2. **Sonuçları görüntüleyin**:
   - Aylık gelir/gider hesaplamaları
   - 5 yıllık ROI projeksiyonu
   - Geri ödeme süresi
   - Senaryo analizleri

#### 📋 Rapor Oluştur
- Şehir bazında detaylı analiz raporları
- Pazar analizi ve rekabet durumu
- Finansal projeksiyonlar
- SWOT analizi ve öneriler

## 📊 Veri Yapısı

Uygulama şu anda demo amaçlı simüle edilmiş veriler kullanmaktadır:

### Şarj İstasyonları
- İstasyon ID, isim, konum
- Operatör bilgileri
- Güç tipi ve kapasitesi
- Kullanım oranları
- Günlük gelir verileri

### Demografik Veriler
- Şehir nüfusu
- Ortalama gelir seviyesi
- Trafik yoğunluğu
- Elektrikli araç oranı
- Potansiyel puanları

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler
- **Backend**: Python, Streamlit
- **Veri İşleme**: Pandas, NumPy
- **Görselleştirme**: Plotly, Folium, Matplotlib, Seaborn
- **Makine Öğrenmesi**: Scikit-learn
- **Harita**: Folium, Streamlit-Folium

### Analiz Algoritmaları
- **Lokasyon Skoru**: Demografik veriler, rekabet analizi ve trafik yoğunluğu
- **ROI Hesaplama**: Discounted Cash Flow (DCF) modeli
- **Kümeleme**: K-Means algoritması ile bölge segmentasyonu

## 🚀 Gelecek Geliştirmeler

### Kısa Vadeli
- [ ] Gerçek veri kaynaklarının entegrasyonu
- [ ] Daha gelişmiş harita özellikleri
- [ ] PDF rapor export özelliği
- [ ] Kullanıcı hesap sistemi

### Uzun Vadeli
- [ ] Makine öğrenmesi tabanlı tahmin modelleri
- [ ] Mobil uygulama versiyonu
- [ ] API hizmeti
- [ ] Gerçek zamanlı veri güncellemeleri

## 📈 Performans Optimizasyonu

### Veri Önbellekleme
```python
@st.cache_data
def generate_charging_stations():
    # Veri oluşturma fonksiyonu önbelleğe alınır
    pass
```

### Bellek Kullanımı
- Büyük dataframeler için pagination
- Lazy loading teknikleri
- Gereksiz hesaplamaları önleme

## 🔒 Güvenlik

- Veri doğrulama kontrolleri
- SQL injection koruması (veri tabanı entegrasyonu sonrası)
- Kullanıcı girdi sanitizasyonu

## 📞 Destek ve İletişim

### Sorun Bildirme
Herhangi bir hata veya öneriniz için:
1. GitHub Issues bölümünü kullanın
2. Detaylı açıklama ve hata mesajları ekleyin
3. Kullandığınız işletim sistemi ve Python versiyonunu belirtin

### Geliştirme Ortamı
```bash
# Development modunda çalıştırma
streamlit run app.py --server.runOnSave true

# Debug modunda çalıştırma
streamlit run app.py --logger.level debug
```

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

## 🙏 Teşekkürler

Bu proje aşağıdaki açık kaynak projelerden yararlanmıştır:
- Streamlit Framework
- Plotly Grafik Kütüphanesi
- Folium Harita Kütüphanesi
- Pandas Veri Analizi Kütüphanesi

---

**Not**: Bu uygulama eğitim ve demonstrasyon amaçlı geliştirilmiştir. Gerçek yatırım kararları için profesyonel danışmanlık alınması önerilir.

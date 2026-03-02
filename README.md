# Kaynak Kıtlığı ve Ekonomik Eşitsizlik Simülasyonu

Ajan-tabanlı bir ekonomik simülasyon projesi. Sınırlı kaynaklara sahip bir dünyada ajanların hayatta kalma mücadelesini, piyasa dinamiklerini ve ekonomik eşitsizliğin gelişimini modellemektedir.

## Proje Hakkında

Bu simülasyon, 50 ajanın 300 zaman adımı boyunca yiyecek ve para ile yaşadığı bir ekonomik sistem modeller. Ajanlar hayatta kalmak için yiyecek tüketir, kaynak toplar, para kazanır ve birbirleriyle ticaret yapar. Sistem kaynak kıtlığına göre dinamik fiyatlandırma kullanır ve bu da ekonomik eşitsizliğin ortaya çıkmasına neden olur.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py
```

Simülasyon sonunda konsola özet istatistikler yazdırılır ve `simulation_log.csv` dosyası oluşturulur.

## Dosya Yapısı

- `main.py` - Ana simülasyon dosyası
- `world.py` - Dünya ve ekonomik sistem mantığı
- `agent.py` - Ajan sınıfı
- `utils.py` - Yardımcı fonksiyonlar (Gini katsayısı)

## Temel Mekanizmalar

- **Tüketim**: Her ajan her adımda 1 yiyecek tüketir
- **Üretim**: Ajanlar yiyecek toplar veya para kazanır
- **Ticaret**: Ajanlar birbirinden yiyecek alıp satar
- **Fiyatlandırma**: Yiyecek kıtlığına göre otomatik fiyat ayarı
- **Hayatta Kalma**: Yiyeceği bitip satın alamayanlar ölür

## Lisans

Bitirme projesi - 2026

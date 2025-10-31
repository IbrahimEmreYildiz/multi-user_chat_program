# 💬 Network Chat System (Multi-Client TCP Chat Application)

**Network Chat System**, Python kullanılarak geliştirilmiş çok kullanıcılı (multi-client) bir **TCP tabanlı sohbet uygulamasıdır**.  
Her istemci, aynı sunucuya bağlanarak gerçek zamanlı mesajlaşabilir.  
Bu proje, **Çukurova Üniversitesi - CEN322 Network Programming** dersi kapsamında hazırlanmıştır.

---

## 🛰️ Proje Amacı

Bu projenin temel amacı, **istemci-sunucu mimarisi (Client-Server Architecture)** kavramını uygulamalı olarak göstermek ve  
**çoklu bağlantı (multi-threading)**, **özel mesajlaşma**, **rate limit (spam koruması)** gibi gerçek bir sohbet sisteminde karşılaşılabilecek mekanizmaları öğretmektir.

---

## ⚙️ Genel Özellikler

| Özellik | Açıklama |
|----------|-----------|
| 🧩 **Çok kullanıcılı yapı** | Aynı anda birden fazla kullanıcı sunucuya bağlanabilir. |
| 🧠 **Thread’li sunucu** | Her kullanıcı ayrı bir `thread` üzerinden yönetilir. |
| 💬 **Gerçek zamanlı mesajlaşma** | Mesajlar anında tüm istemcilere iletilir. |
| 🔐 **Özel mesaj (Private Message)** | `/msg <kullanıcı> <mesaj>` komutuyla sadece hedef kullanıcıya mesaj gönderilir. |
| 🚫 **Rate limit (spam koruması)** | 5 saniyede 8’den fazla mesaj atan kullanıcı 10 saniye susturulur. |
| 🕓 **Zaman damgası** | Her mesaj `[HH:MM:SS]` formatında zaman etiketiyle görüntülenir. |
| 👥 **Aktif kullanıcı listesi** | Yeni kullanıcı bağlandığında veya çıktığında liste güncellenir. |
| 🧾 **Log sistemi** | Sunucu tarafında tüm olaylar `server_log.txt` dosyasına kaydedilir. |
| ⚠️ **Hata yönetimi** | Bağlantı kesilmeleri, eksik komutlar ve hatalı girişler güvenli biçimde ele alınır. |

---

## 📂 Dosya Yapısı

NetworkChatSystem
├── chat_server.py # Sunucu tarafı (ana merkez)
├── chat_client.py # İstemci tarafı (kullanıcı arabirimi)
├── server_log.txt # Otomatik oluşturulan log dosyası
└── README.md # Proje dökümanı (bu dosya)

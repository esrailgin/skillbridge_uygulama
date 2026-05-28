# skillbridge_uygulama
SkillBridge is a desktop-based career development and skill tracking system built with PyQt6, FastAPI and Microsoft SQL Server.  //   SkillBridge, PyQt6, FastAPI ve Microsoft SQL Server kullanılarak geliştirilen masaüstü tabanlı kariyer gelişim ve beceri takip sistemidir.

# SkillBridge

SkillBridge, kariyer gelişimini daha düzenli takip etmek amacıyla geliştirilen masaüstü tabanlı bir uygulamadır. Uygulamada kullanıcı kayıt/giriş işlemleri, CV analiz geçmişi, beceri takibi, yol haritası, rozet sistemi ve rol bazlı kullanıcı senaryoları bulunmaktadır.

## Kullanılan Teknolojiler

- Python
- PyQt6
- FastAPI
- Microsoft SQL Server
- SQL Server Management Studio
- pyodbc
- httpx

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Öğrenci, yeni mezun, kariyer adayı, mentor ve İK yöneticisi rolleri
- Dashboard ekranı
- CV analiz geçmişi
- Beceri kataloğu
- Yol haritası oluşturma ve ilerleme takibi
- Rozet sistemi
- Demo kullanıcılar

## Çalıştırma

Backend:

```powershell
python -m uvicorn main_api:app

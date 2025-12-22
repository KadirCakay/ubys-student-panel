# 🎓 Bartın Üniversitesi - UBYS Masaüstü Öğrenci Paneli

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

Bu proje, Bartın Üniversitesi öğrencileri için geliştirilmiş, **UBYS (Üniversite Bilgi Yönetim Sistemi)** verilerine daha hızlı ve modern bir arayüz ile erişmeyi sağlayan açık kaynaklı bir masaüstü uygulamasıdır.

Proje, Python ve **CustomTkinter** kullanılarak geliştirilmiştir. Ders notlarına erişimi kolaylaştırır ve sınav sonuçlarını düzenli bir şekilde sunar.

## 🚀 Özellikler

* **Modern Arayüz:** CustomTkinter ile tasarlanmış, göz yormayan "Dark Mode" arayüz.
* **Otomatik Giriş:** "Beni Hatırla" özelliği ile kullanıcı bilgilerini güvenli bir şekilde yerel cihazda tutar.
* **Sınav Sonuçları:** Vize ve Final notlarını karmaşık tablolar yerine şık kartlar halinde gösterir.
* **Akıllı Dosya İndirme:**
    * Derslerin detay sayfalarını otomatik tarar.
    * Gereksiz "Yardım" dosyalarını filtreler.
    * PDF, Word, PPT gibi ders materyallerini tespit eder.
    * OneDrive, Google Forms gibi harici linkleri tarayıcıda açar, dosyaları ise doğrudan indirir.

## 🛠️ Kullanılan Teknolojiler

* **Python 3.10+**
* **CustomTkinter:** Modern GUI tasarımı için.
* **Requests:** HTTP istekleri ve oturum yönetimi için.
* **BeautifulSoup4:** HTML verilerini işlemek (Scraping) için.

## 📦 Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak veya geliştirmek için aşağıdaki adımları izleyin:

1.  **Repoyu klonlayın:**
    ```bash
    git clone https://github.com/KadirCakay/ubys-student-panel.git
    cd ubys-student-panel
    ```

2.  **Gerekli kütüphaneleri yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı başlatın:**
    ```bash
    python main.py
    ```

## 🤝 Katkıda Bulunma (Contributing)

Bu proje geliştirmeye açıktır! Bartın Üniversitesi öğrencisiyseniz veya Python ile ilgileniyorsanız katkılarınızı bekliyoruz.

1.  Bu repoyu **Fork** edin.
2.  Yeni bir özellik için dal (branch) oluşturun (`git checkout -b yeni-ozellik`).
3.  Yaptığınız değişiklikleri **Commit** edin (`git commit -m 'Yeni özellik: Devamsızlık takibi eklendi'`).
4.  Dalı **Push** edin (`git push origin yeni-ozellik`).
5.  Bir **Pull Request (PR)** oluşturun.

## ⚠️ Yasal Uyarı (Disclaimer)

Bu yazılım, öğrencilerin kendi verilerine daha kolay erişmesi amacıyla eğitim ve hobi amaçlı geliştirilmiştir. Bartın Üniversitesi ile resmi bir bağı yoktur.
* Uygulama, kullanıcı adı ve şifrenizi **sadece sizin bilgisayarınızda** (`config.json` dosyasında) saklar. Herhangi bir sunucuya göndermez.
* Kullanım sorumluluğu tamamen kullanıcıya aittir.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Yani kaynak göstererek özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.

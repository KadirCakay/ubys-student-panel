import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlparse, parse_qs, unquote


class UbysClient:
    def __init__(self, ogr_no, sifre, sapid_url):
        self.ogr_no = ogr_no
        self.sifre = sifre
        self.sapid_url = sapid_url
        self.base_url = "https://ubys.bartin.edu.tr"
        self.login_url = "https://ubys.bartin.edu.tr/Account/Login"
        self.session = requests.Session()
        # Varsayılan olarak AJAX taklidi yapıyoruz (Veri çekmek için gerekli)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.giris_basarili = False

    def giris_yap(self):
        """Sisteme giriş yapar ve Session çerezlerini ayarlar."""
        try:
            r_home = self.session.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(r_home.content, "html.parser")
            token_input = soup.find("input", {"name": "__RequestVerificationToken"})

            if not token_input:
                return False, "Token alınamadı."

            payload = {
                "__RequestVerificationToken": token_input["value"],
                "username": self.ogr_no,
                "password": self.sifre,
                "X-Requested-With": "XMLHttpRequest"
            }

            resp = self.session.post(self.login_url, data=payload, headers=self.headers)
            if resp.status_code == 200:
                self.giris_basarili = True
                return True, "Giriş Başarılı"
            else:
                return False, "Giriş başarısız."
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def dersleri_getir(self):
        """Ders listesini ve detay linklerini çeker."""
        if not self.giris_basarili:
            return []

        try:
            r = self.session.get(self.sapid_url, headers=self.headers)
            soup = BeautifulSoup(r.content, "html.parser")
            tablo = soup.find("table")

            if not tablo:
                return []

            ders_listesi = []
            satirlar = tablo.find_all("tr")
            son_eklenen_ders = None

            for satir in satirlar[1:]:
                sutunlar = satir.find_all("td")
                satir_metni = satir.text.replace("\n", " ").strip()

                if len(sutunlar) >= 1:
                    ilk_sutun_text = sutunlar[0].text.strip()

                    # Detay satırı kontrolü (Notlar/Vize/Final)
                    if "Vize" in ilk_sutun_text or "Final" in ilk_sutun_text or ilk_sutun_text == "":
                        if son_eklenen_ders:
                            vize_bul = self.not_ayikla(satir_metni, "Vize")
                            final_bul = self.not_ayikla(satir_metni, "Final")
                            if vize_bul != "-": son_eklenen_ders["vize"] = vize_bul
                            if final_bul != "-": son_eklenen_ders["final"] = final_bul
                        continue

                    # Ders Satırı
                    if len(sutunlar) >= 2:
                        ders_kodu = ilk_sutun_text
                        ders_adi = sutunlar[1].text.strip()

                        # --- Detay Linkini Alma ---
                        raw_link = None
                        all_links = satir.find_all("a", href=True)
                        for l in all_links:
                            if "ClassDetail" in l['href']:
                                # Linki olduğu gibi al, işlemeyi sonra yapacağız
                                raw_link = self.base_url + l['href'] if l['href'].startswith("/") else l['href']
                                break
                        # --------------------------

                        vize_notu = self.not_ayikla(satir_metni, "Vize")
                        final_notu = self.not_ayikla(satir_metni, "Final")

                        yeni_ders = {
                            "kod": ders_kodu,
                            "ad": ders_adi,
                            "vize": vize_notu,
                            "final": final_notu,
                            "link": raw_link
                        }

                        ders_listesi.append(yeni_ders)
                        son_eklenen_ders = yeni_ders

            return ders_listesi
        except Exception as e:
            print(f"Ders çekme hatası: {e}")
            return []

    def ders_detaylarini_getir(self, detay_url):
        if not self.giris_basarili or not detay_url:
            return []

        try:
            parsed_url = urlparse(detay_url)
            params = parse_qs(parsed_url.query)
            class_id = params.get('classId', [None])[0] or params.get('ClassId', [None])[0]

            if not class_id: return []

            target_url = f"https://ubys.bartin.edu.tr/AIS/Student/Class/GetClassDetailPartial?ClassId={class_id}&ClassDetailPartial=2"
            print(f"Hedef: {target_url}")

            # --- DÜZELTME BURADA: REFERER EKLEME ---
            # Sunucuya "Ben bu isteği, Ders Detay sayfasının içindeyken yapıyorum" diyoruz.
            custom_headers = self.headers.copy()
            custom_headers["Referer"] = detay_url  # Referans olarak geldiğimiz sayfayı gösteriyoruz
            custom_headers["X-Requested-With"] = "XMLHttpRequest"  # AJAX olduğunu belirtiyoruz

            # İsteği özel başlıklarla atıyoruz
            r = self.session.get(target_url, headers=custom_headers)
            # ---------------------------------------

            soup = BeautifulSoup(r.content, "html.parser")

            dosyalar = []
            linkler = soup.find_all("a", href=True)
            print(f"Sayfadaki ham link sayısı: {len(linkler)}")

            for link in linkler:
                href = link["href"]
                text = link.text.strip()
                href_lower = href.lower()

                if "javascript" in href_lower or "#" in href: continue
                if "yardım" in text.lower() or "help" in text.lower(): continue

                real_url = None
                icerik_tipi = "belirsiz"

                # 1. Viewer (Önizleme) Linki ise içindeki gerçeği al
                if "viewer.html" in href_lower and "file=" in href:
                    try:
                        ham_url = href.split("file=")[1]
                        real_url = unquote(ham_url)
                        icerik_tipi = "dosya"
                    except:
                        continue

                # 2. Normal Dosya Linki ise
                elif href_lower.endswith(
                        ('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.zip', '.rar', '.txt')):
                    real_url = href
                    icerik_tipi = "dosya"
                elif "getfile" in href_lower or "download" in href_lower or "/file/" in href_lower:
                    real_url = href
                    icerik_tipi = "dosya"

                # 3. Harici Link ise
                elif href_lower.startswith("http"):
                    real_url = href
                    icerik_tipi = "link"

                if real_url:
                    if real_url.startswith("/"):
                        full_link = self.base_url + real_url
                    elif not real_url.startswith("http"):
                        full_link = self.base_url + "/" + real_url
                    else:
                        full_link = real_url

                    if not text: text = "Ders Dosyası"
                    text = " ".join(text.split())

                    if not any(d['url'] == full_link for d in dosyalar):
                        dosyalar.append({"ad": text, "url": full_link, "tip": icerik_tipi})
                        print(f"   [EKLENDİ - {icerik_tipi}]: {text}")

            print(f"Filtre sonrası bulunan: {len(dosyalar)}")
            return dosyalar

        except Exception as e:
            print(f"Detay hatası: {e}")
            return []

    def dosya_indir(self, url, dosya_adi, hedef_klasor=None):
        """Dosyayı belirtilen klasöre indirir. Klasör verilmezse İndirilenler'e kaydeder."""
        try:
            # Eğer özel bir klasör seçildiyse orayı kullan, yoksa İndirilenler'i
            if hedef_klasor:
                download_folder = hedef_klasor
            else:
                download_folder = os.path.expanduser("~/Downloads")

            # Dosya adındaki geçersiz karakterleri temizle
            dosya_adi = "".join([c for c in dosya_adi if c.isalnum() or c in " .-_"]).strip()
            file_path = os.path.join(download_folder, dosya_adi)

            if not os.path.splitext(file_path)[1]:
                file_path += ".pdf"

            # Header Manipülasyonu (Burası aynı kalıyor)
            download_headers = self.headers.copy()
            if "X-Requested-With" in download_headers:
                del download_headers["X-Requested-With"]

            download_headers["Referer"] = "https://ubys.bartin.edu.tr/"
            download_headers[
                "Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            download_headers["Upgrade-Insecure-Requests"] = "1"

            print(f"İndirme Başlıyor: {url} -> {file_path}")

            with self.session.get(url, stream=True, headers=download_headers) as r:
                content_type = r.headers.get("Content-Type", "").lower()
                if "html" in content_type:
                    return False, "Sunucu İzin Vermedi (HTML)"

                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True, file_path
        except Exception as e:
            print(f"İndirme Hatası: {e}")
            return False, str(e)

    def not_ayikla(self, metin, tur):
        match = re.search(fr'{tur}\s*:\s*([\w,]+)', metin)
        if match:
            return match.group(1).strip()
        return "-"
import customtkinter as ctk
import threading
import json
import os
import webbrowser  # Linkleri tarayıcıda açmak için
from ubys_api import UbysClient
from tkinter import filedialog

# --- AYARLAR ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
CONFIG_FILE = "config.json"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bartın Üni - Mobil v5")
        self.geometry("400x700")
        self.bot = None
        self.dersler_cache = []
        self.aktif_kullanici_no = ""

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()
        self.bilgileri_yukle()

    # --- EKRAN GEÇİŞLERİ ---
    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(pady=40, padx=20, fill="both")

        ctk.CTkLabel(frame, text="UBYS Giriş", font=("Roboto", 26, "bold")).pack(pady=20)
        self.entry_user = ctk.CTkEntry(frame, placeholder_text="Öğrenci No", height=45)
        self.entry_user.pack(pady=10, fill="x")
        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="Şifre", show="*", height=45)
        self.entry_pass.pack(pady=10, fill="x")
        self.entry_url = ctk.CTkEntry(frame, placeholder_text="Ders Linki (sapid=...)", height=45)
        self.entry_url.pack(pady=10, fill="x")
        self.check_var = ctk.StringVar(value="off")
        self.checkbox = ctk.CTkCheckBox(frame, text="Beni Hatırla", variable=self.check_var, onvalue="on",
                                        offvalue="off")
        self.checkbox.pack(pady=10)
        self.btn_login = ctk.CTkButton(frame, text="Giriş Yap", height=50, font=("Roboto", 16, "bold"),
                                       command=self.giris_baslat)
        self.btn_login.pack(pady=20, fill="x")
        self.label_status = ctk.CTkLabel(frame, text="", text_color="gray")
        self.label_status.pack(pady=5)

    def show_menu_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"Hoşgeldin\n{self.aktif_kullanici_no}", font=("Roboto", 20)).pack(pady=20)

        ctk.CTkButton(frame, text="📚 DERS NOTLARI", height=80, font=("Roboto", 18, "bold"),
                      fg_color="#F9A825", hover_color="#FBC02D",
                      command=self.show_notlar_listesi).pack(pady=10, fill="x")

        ctk.CTkButton(frame, text="📊 SINAV SONUÇLARI", height=80, font=("Roboto", 18, "bold"),
                      fg_color="#2FA572", hover_color="#1E8E5D",
                      command=self.show_sinav_listesi).pack(pady=10, fill="x")

        ctk.CTkButton(frame, text="Çıkış Yap", fg_color="#D32F2F", hover_color="#B71C1C",
                      command=self.cikis_yap).pack(side="bottom", pady=20)

    # --- MANTIK ---
    def bilgileri_yukle(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.entry_user.insert(0, data.get("user", ""))
                    self.entry_pass.insert(0, data.get("pass", ""))
                    self.entry_url.insert(0, data.get("url", ""))
                    if data.get("remember"): self.checkbox.select()
            except:
                pass

    def bilgileri_kaydet(self):
        if self.check_var.get() == "on":
            data = {"user": self.entry_user.get(), "pass": self.entry_pass.get(), "url": self.entry_url.get(),
                    "remember": True}
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        elif os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def giris_baslat(self):
        no, sifre, url = self.entry_user.get(), self.entry_pass.get(), self.entry_url.get()
        if not no or not sifre or not url: return
        self.aktif_kullanici_no = no
        self.bilgileri_kaydet()
        self.label_status.configure(text="Bağlanılıyor...", text_color="yellow")
        self.btn_login.configure(state="disabled")
        threading.Thread(target=self.giris_islem, args=(no, sifre, url)).start()

    def giris_islem(self, no, sifre, url):
        self.bot = UbysClient(no, sifre, url)
        basarili, mesaj = self.bot.giris_yap()
        if basarili:
            self.label_status.configure(text="Veriler çekiliyor...", text_color="green")
            self.dersleri_goster()
        else:
            self.label_status.configure(text=mesaj, text_color="red")
            self.btn_login.configure(state="normal")

    def dersleri_goster(self):
        self.dersler_cache = self.bot.dersleri_getir()
        self.after(0, self.show_menu_screen)

    # --- EKRANLAR ---
    def show_sinav_listesi(self):
        self.clear_screen()
        top_bar = ctk.CTkFrame(self.container, height=50)
        top_bar.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(top_bar, text="< Geri", width=60, fg_color="gray", command=self.show_menu_screen).pack(
            side="left")
        ctk.CTkLabel(top_bar, text="Sınav Sonuçları", font=("Roboto", 18, "bold")).pack(side="left", padx=20)

        scroll = ctk.CTkScrollableFrame(self.container)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for ders in self.dersler_cache:
            card = ctk.CTkFrame(scroll, fg_color="#2B2B2B")
            card.pack(pady=5, fill="x")
            ctk.CTkLabel(card, text=ders["kod"], text_color="#3B8ED0", font=("Roboto", 12, "bold")).pack(anchor="w",
                                                                                                         padx=10,
                                                                                                         pady=(5, 0))
            ctk.CTkLabel(card, text=ders["ad"], text_color="white", font=("Roboto", 14, "bold"), wraplength=300).pack(
                anchor="w", padx=10)
            grades = ctk.CTkFrame(card, fg_color="#3A3A3A")
            grades.pack(fill="x", padx=10, pady=10)

            v = ctk.CTkFrame(grades, fg_color="transparent")
            v.pack(side="left", expand=True)
            ctk.CTkLabel(v, text="VİZE", font=("Roboto", 10), text_color="gray").pack()
            renk = "#4CAF50" if ders["vize"].replace(",", "").isdigit() and float(
                ders["vize"].replace(",", ".")) >= 50 else "white"
            ctk.CTkLabel(v, text=ders["vize"], font=("Roboto", 14, "bold"), text_color=renk).pack()

            f = ctk.CTkFrame(grades, fg_color="transparent")
            f.pack(side="right", expand=True)
            ctk.CTkLabel(f, text="FİNAL", font=("Roboto", 10), text_color="gray").pack()
            ctk.CTkLabel(f, text=ders["final"], font=("Roboto", 14, "bold")).pack()

    def show_notlar_listesi(self):
        self.clear_screen()
        top_bar = ctk.CTkFrame(self.container, height=50)
        top_bar.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(top_bar, text="< Geri", width=60, fg_color="gray", command=self.show_menu_screen).pack(
            side="left")
        ctk.CTkLabel(top_bar, text="Ders Notları", font=("Roboto", 18, "bold")).pack(side="left", padx=20)

        scroll = ctk.CTkScrollableFrame(self.container)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for ders in self.dersler_cache:
            if ders.get("link"):
                btn = ctk.CTkButton(scroll,
                                    text=f"{ders['kod']} - {ders['ad']}",
                                    font=("Roboto", 14),
                                    fg_color="#333333",
                                    hover_color="#444444",
                                    height=50,
                                    anchor="w",
                                    command=lambda d=ders: self.notlari_ac_popup(d))
                btn.pack(pady=5, fill="x")

    def notlari_ac_popup(self, ders):
        toplevel = ctk.CTkToplevel(self)
        toplevel.title(f"{ders['kod']} Notları")
        toplevel.geometry("400x500")
        toplevel.attributes("-topmost", True)

        label = ctk.CTkLabel(toplevel, text="İçerik Aranıyor...", font=("Roboto", 14))
        label.pack(pady=20)

        scroll_files = ctk.CTkScrollableFrame(toplevel)
        scroll_files.pack(fill="both", expand=True, padx=10, pady=10)

        threading.Thread(target=self.dosyalari_yukle_thread, args=(ders["link"], scroll_files, label)).start()

    def dosyalari_yukle_thread(self, link, parent_frame, status_label):
        icerikler = self.bot.ders_detaylarini_getir(link)

        if not icerikler:
            status_label.configure(text="İçerik bulunamadı.")
            return

        status_label.configure(text=f"{len(icerikler)} Kaynak Bulundu")

        for icerik in icerikler:
            f_frame = ctk.CTkFrame(parent_frame, fg_color="#222222")
            f_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(f_frame, text=icerik["ad"][:30], anchor="w").pack(side="left", padx=10)

            if icerik["tip"] == "link":
                # Link ise Tarayıcıda Aç Butonu
                btn = ctk.CTkButton(f_frame, text="Aç 🔗", width=60, height=30, fg_color="#5bc0de",
                                    hover_color="#46b8da",
                                    command=lambda u=icerik["url"]: self.linki_ac(u))
            else:
                # Dosya ise İndir Butonu
                btn = ctk.CTkButton(f_frame, text="İndir ⬇️", width=60, height=30, fg_color="#3B8ED0",
                                    command=lambda u=icerik["url"], a=icerik["ad"]: self.indir_baslat(u, a))

            btn.pack(side="right", padx=5, pady=5)

    def linki_ac(self, url):
        webbrowser.open(url)

    def indir_baslat(self, url, ad):
        # Kullanıcıya nereye kaydetmek istediğini sor
        hedef_klasor = filedialog.askdirectory(title="Kaydedilecek Klasörü Seçin")

        # Eğer kullanıcı "İptal" derse veya pencereyi kapatırsa işlem yapma
        if not hedef_klasor:
            return

        # Seçilen klasörü thread'e gönder
        threading.Thread(target=self.indir_thread, args=(url, ad, hedef_klasor)).start()

    def indir_thread(self, url, ad, klasor):
        # API'ye klasör bilgisini de gönderiyoruz
        basarili, yol = self.bot.dosya_indir(url, ad, klasor)

        if basarili:
            print(f"İndirme tamamlandı: {yol}")
            # İstersen burada kullanıcıya "Bitti" diye minik bir bildirim gösterebilirsin.
        else:
            print(f"İndirme başarısız: {yol}")

    def cikis_yap(self):
        self.show_login_screen()


if __name__ == "__main__":
    app = App()
    app.mainloop()
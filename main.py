# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

APP = App.get_running_app if False else None
BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
TEMPLATE = ASSETS / "card_template.jpg"
LOGO = ASSETS / "davam_logo_transparent.png"
FONT = ASSETS / "BNazanin.ttf"
OUT_DIR = Path(__file__).resolve().parent / "cards"
OUT_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = Path(__file__).resolve().parent / "card_settings.json"

DEFAULT = {
    "font_size": 70,
    "text_color": [20, 125, 65],
    "texts": {
        "name": {"x": 650, "y": 330},
        "national_id": {"x": 850, "y": 445},
        "activity": {"x": 730, "y": 545},
        "service": {"x": 700, "y": 665},
    },
    "photo": {"x": 1225, "y": 145, "w": 265, "h": 370},
    "qr": {"x": 90, "y": 650, "w": 215, "h": 215},
}


def load_settings():
    s = json.loads(json.dumps(DEFAULT))
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            s["font_size"] = int(saved.get("font_size", s["font_size"]))
            for k in s["texts"]:
                if k in saved.get("texts", {}):
                    s["texts"][k]["x"] = int(saved["texts"][k].get("x", s["texts"][k]["x"]))
                    s["texts"][k]["y"] = int(saved["texts"][k].get("y", s["texts"][k]["y"]))
            for k in ("photo", "qr"):
                for d in ("x", "y", "w", "h"):
                    s[k][d] = int(saved.get(k, {}).get(d, s[k][d]))
        except Exception:
            pass
    return s


SETTINGS = load_settings()


def fa(text):
    return get_display(arabic_reshaper.reshape(str(text))) if text else ""


def font(size=None):
    return ImageFont.truetype(str(FONT), int(size or SETTINGS["font_size"]))


def create_qr(name, national_id, activity, service):
    data = (
        "کارت شناسایی اعضای دوام ثامن\n"
        f"نام و نام خانوادگی: {name}\n"
        f"کد ملی: {national_id}\n"
        f"محل فعالیت: {activity}\n"
        f"رسته خدمتی: {service}\n"
        "جهت استعلام کارت شناسایی با شماره 05136203618 تماس بگیرید"
    )
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def render_card(name, national_id, activity, service, photo_path=""):
    card = Image.open(TEMPLATE).convert("RGB")
    if photo_path and Path(photo_path).exists():
        b = SETTINGS["photo"]
        photo = ImageOps.fit(Image.open(photo_path).convert("RGB"), (b["w"], b["h"]), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", (b["w"], b["h"]), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, b["w"]-1, b["h"]-1), radius=25, fill=255)
        card.paste(photo, (b["x"], b["y"]), mask)

    draw = ImageDraw.Draw(card)
    fnt = font()
    vals = {"name": name, "national_id": national_id, "activity": activity, "service": service}
    for k, value in vals.items():
        if not value:
            continue
        text = fa(value)
        x = SETTINGS["texts"][k]["x"]
        y = SETTINGS["texts"][k]["y"]
        box = draw.textbbox((0, 0), text, font=fnt)
        draw.text((x - (box[2]-box[0]), y), text, font=fnt, fill=tuple(SETTINGS["text_color"]))

    b = SETTINGS["qr"]
    qr = create_qr(name, national_id, activity, service)
    qr = ImageOps.contain(qr, (max(1,b["w"]-18), max(1,b["h"]-18)))
    bg = Image.new("RGB", (b["w"], b["h"]), "white")
    bg.paste(qr, ((b["w"]-qr.width)//2, (b["h"]-qr.height)//2))
    card.paste(bg, (b["x"], b["y"]))
    return card


def save_card(name, national_id, activity, service, photo):
    card = render_card(name, national_id, activity, service, photo)
    safe = "".join(c for c in name if c not in '\\/:*?"<>|').strip() or "card"
    path = OUT_DIR / f"{safe}.jpg"
    card.save(path, "JPEG", quality=98, dpi=(300,300))
    return path


class CardApp(App):
    def build(self):
        self.title = "سامانه صدور کارت شناسایی | دوام ثامن"
        Window.clearcolor = (0.93, 0.96, 0.94, 1)
        self.photo = ""
        self.preview = KivyImage(source=str(LOGO), size_hint=(1, None), height=dp(70), allow_stretch=True, keep_ratio=True)

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(90), padding=dp(8), spacing=dp(8))
        header.add_widget(KivyImage(source=str(LOGO), size_hint_x=None, width=dp(110), allow_stretch=True, keep_ratio=True))
        title_box = BoxLayout(orientation="vertical")
        title_box.add_widget(Label(text="سامانه صدور کارت شناسایی", font_size=dp(22), halign="right", valign="middle"))
        title_box.add_widget(Label(text="دوام ثامن  •  داوطلبین و واکنش اضطراری محلات", font_size=dp(13), halign="right", valign="middle"))
        header.add_widget(title_box)
        root.add_widget(header)

        content = BoxLayout(spacing=dp(10))
        form_scroll = ScrollView(size_hint_x=0.36)
        form = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        form.add_widget(Label(text="اطلاعات عضو", font_size=dp(18), size_hint_y=None, height=dp(35)))
        self.name = self.field(form, "نام و نام خانوادگی")
        self.national = self.field(form, "کد ملی")
        self.activity = self.field(form, "محل فعالیت")
        self.service = self.field(form, "رسته خدمتی")
        btn_photo = Button(text="انتخاب عکس", size_hint_y=None, height=dp(48))
        btn_photo.bind(on_release=self.choose_photo)
        form.add_widget(btn_photo)
        self.photo_label = Label(text="فرمت‌های JPG / PNG / WEBP", size_hint_y=None, height=dp(35))
        form.add_widget(self.photo_label)
        issue = Button(text="صدور کارت", size_hint_y=None, height=dp(55))
        issue.bind(on_release=self.issue_card)
        form.add_widget(issue)
        form.add_widget(Label(text="کارت در پوشه cards ذخیره می‌شود.", size_hint_y=None, height=dp(45)))
        form_scroll.add_widget(form)
        content.add_widget(form_scroll)

        right = BoxLayout(orientation="vertical", spacing=dp(8))
        right.add_widget(Label(text="پیش‌نمایش کارت", size_hint_y=None, height=dp(35), font_size=dp(18)))
        self.card_image = KivyImage(allow_stretch=True, keep_ratio=True)
        right.add_widget(self.card_image)
        content.add_widget(right)
        root.add_widget(content)

        for field in (self.name, self.national, self.activity, self.service):
            field.bind(text=lambda *_: self.update_preview())
        self.update_preview()
        return root

    def field(self, parent, label):
        parent.add_widget(Label(text=label, halign="right", size_hint_y=None, height=dp(28)))
        e = TextInput(multiline=False, halign="right", size_hint_y=None, height=dp(48), padding=[dp(8), dp(10)])
        parent.add_widget(e)
        return e

    def choose_photo(self, *_):
        chooser = FileChooserListView(path="/storage/emulated/0", filters=["*.jpg", "*.jpeg", "*.png", "*.webp"], multiselect=False)
        box = BoxLayout(orientation="vertical")
        box.add_widget(chooser)
        buttons = BoxLayout(size_hint_y=None, height=dp(48))
        ok = Button(text="انتخاب")
        cancel = Button(text="لغو")
        buttons.add_widget(ok); buttons.add_widget(cancel); box.add_widget(buttons)
        popup = Popup(title="انتخاب عکس عضو", content=box, size_hint=(0.95, 0.9))
        cancel.bind(on_release=popup.dismiss)
        def accept(*_):
            if chooser.selection:
                self.photo = chooser.selection[0]
                self.photo_label.text = Path(self.photo).name
                popup.dismiss(); self.update_preview()
        ok.bind(on_release=accept)
        popup.open()

    def values(self):
        return (self.name.text.strip(), self.national.text.strip(), self.activity.text.strip(), self.service.text.strip())

    def update_preview(self):
        try:
            card = render_card(*self.values(), self.photo)
            path = OUT_DIR / "_preview.jpg"
            card.save(path, "JPEG", quality=90)
            self.card_image.source = str(path)
            self.card_image.reload()
        except Exception:
            pass

    def issue_card(self, *_):
        name, national, activity, service = self.values()
        if not name or not national:
            self.show_message("اطلاعات ناقص", "نام و کد ملی را وارد کنید.")
            return
        try:
            path = save_card(name, national, activity, service, self.photo)
            self.show_message("صدور موفق", f"کارت با موفقیت ذخیره شد:\n{path.name}")
        except Exception as e:
            self.show_message("خطا", str(e))

    def show_message(self, title, text):
        Popup(title=title, content=Label(text=text, halign="center"), size_hint=(0.85, 0.35)).open()


if __name__ == "__main__":
    CardApp().run()

import streamlit as st
import re
import datetime
import base64
import io
import qrcode
from weasyprint import HTML

st.set_page_config(page_title="PDF Pro Engine 3.0", page_icon="🚀", layout="wide")

# ستایلی سەرەکی وێبسایتەکە
st.markdown("""
<style>
    .main-title {text-align: center; color: #1e3a8a; font-weight: 900; font-size: 3rem;}
    .sub-title {text-align: center; color: #64748b; margin-bottom: 30px; font-size: 1.2rem;}
</style>
<h1 class='main-title'>🚀 مۆتۆڕی پڕۆفیشناڵی PDF (وەشانی بێ کۆتا)</h1>
<p class='sub-title'>یەکەمین پلاتفۆرمی زیرەک بۆ دروستکردنی کەرەستەی فێرکاری بە بارکۆدی دەنگی</p>
""", unsafe_allow_html=True)

# دابەشکردنی وێبسایتەکە بۆ تاب (Tabs)
tab_manual, tab_ai = st.tabs(["📝 مۆدی دەستی (Manual)", "🤖 مۆدی زیرەکی دەستکرد (AI)"])

with tab_manual:
    col_content, col_settings = st.columns([2, 1])
    
    with col_settings:
        st.markdown("### ⚙️ ڕێکخستنەکان")
        title = st.text_input("📌 ناونیشان:", "وانەی نوێ")
        subtitle = st.text_input("💡 ژێرنووس:", "پوختەی بابەت")
        
        st.markdown("---")
        st.markdown("**📐 قەبارە و دیزاین**")
        page_size = st.selectbox("📄 قەبارەی پەڕە:", ["فەرمی (A4 بۆ پرینت)", "سۆشیال میدیا (بۆ شاشەی مۆبایل)"])
        language_dir = st.selectbox("🌐 زمانی نووسین:", ["ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)", "چەپ بۆ ڕاست (English, Türkçe)"])
        theme = st.selectbox("🎨 دیزاینی پەڕەکان:", [
            "دەفتەری تێبینی (هێڵکار)", 
            "تۆڕی زانستی (گرافیک)",
            "پزیشکی و کلینیکی (شین)", 
            "گفتوگۆ و زمان (مۆر)", 
            "کلاسیک و ئەدەبی (قاوەیی)"
        ])
        
        st.markdown("---")
        st.markdown("**🎙️ بارکۆدی دەنگی (QR Code)**")
        st.info("دەتوانیت لێرە دەنگەکە تۆمار بکەیت و دایبەزێنیت، پاشان لە تێلیگرام یان درایڤ بڵاوی بکەیتەوە و لینکەکەی لێرە دابنێیت.")
        audio_bytes = st.audio_input("🔴 تۆمارکردنی دەنگ ڕاستەوخۆ:")
        qr_link = st.text_input("🔗 لینکی دەنگ/ڤیدیۆ بۆ بارکۆد:", placeholder="https://t.me/yourchannel/123")
        
        st.markdown("---")
        cover_page = st.checkbox("📄 پەڕەی بەرگ (Cover)", value=True)
        show_flag = st.checkbox("☀️ ئاڵای کوردستان (لۆگۆ)", value=True)
        watermark = st.text_input("🔏 هێمای ئاو:", "")

    with col_content:
        st.markdown("### 📝 ناوەڕۆکی بابەت")
        st.success("💡 **تایبەتمەندییەکان:** سەردێڕ `#` | تۆخکردن `**وشە**` | هایلایت `==وشە==` | خشتە `| وشە | وشە |`")
        raw_text = st.text_area("دەقەکەت لێرە دابنێ (کۆپی و پەیست بکە):", height=450)
        
        if st.button("🚀 دروستکردنی PDF بە کوالێتی بەرز", type="primary", use_container_width=True):
            if not raw_text.strip():
                st.error("⚠️ تکایە ناوەڕۆکەکە پڕ بکەرەوە.")
            else:
                with st.spinner("مۆتۆڕەکە خەریکی داڕشتن و نەخشاندنی کۆدەکانە... ⏳"):
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                    
                    themes_dict = {
                        "دەفتەری تێبینی (هێڵکار)": {"primary": "#334155", "bg": "repeating-linear-gradient( #f8fafc, #f8fafc 38px, #cbd5e1 38px, #cbd5e1 39px )", "card": "rgba(255,255,255,0.9)", "border": "#64748b", "accent": "#f1f5f9"},
                        "تۆڕی زانستی (گرافیک)": {"primary": "#0f766e", "bg": "linear-gradient(#ccfbf1 1px, transparent 1px), linear-gradient(90deg, #ccfbf1 1px, transparent 1px)", "bg_size": "25px 25px", "card": "rgba(255,255,255,0.95)", "border": "#14b8a6", "accent": "#ccfbf1"},
                        "پزیشکی و کلینیکی (شین)": {"primary": "#0369a1", "bg": "#f0f9ff", "card": "#ffffff", "border": "#0ea5e9", "accent": "#bae6fd"},
                        "گفتوگۆ و زمان (مۆر)": {"primary": "#6d28d9", "bg": "#f5f3ff", "card": "#ffffff", "border": "#8b5cf6", "accent": "#ddd6fe"},
                        "کلاسیک و ئەدەبی (قاوەیی)": {"primary": "#92400e", "bg": "#fefce8", "card": "#ffffff", "border": "#d97706", "accent": "#fde68a"}
                    }
                    t_style = themes_dict.get(theme, themes_dict["پزیشکی و کلینیکی (شین)"])
                    bg_css = f'background: {t_style["bg"]};' if "gradient" in t_style["bg"] else f'background-color: {t_style["bg"]};'
                    if "bg_size" in t_style: bg_css += f' background-size: {t_style["bg_size"]};'
                    
                    is_rtl = "ڕاست" in language_dir
                    dir_attr = "rtl" if is_rtl else "ltr"
                    align_attr = "right" if is_rtl else "left"
                    alt_align = "left" if is_rtl else "right"
                    lang_code = "ckb" if is_rtl else "en"
                    
                    # دیاریکردنی قەبارەی پەڕە
                    if "سۆشیال میدیا" in page_size:
                        page_css = "size: 108mm 192mm; margin: 15mm 10mm;" # قەبارەی ستۆری/مۆبایل
                        content_font = "14pt"
                    else:
                        page_css = "size: A4; margin: 25mm 20mm;" # قەبارەی ئاسایی
                        content_font = "16pt"

                    content_blocks = ""
                    in_table = False
                    table_content = ""
                    speakers = []
                    
                    for line in lines:
                        # فۆرماتەکان
                        line = re.sub(r'\*\*(.*?)\*\*', f'<strong style="color: {t_style["primary"]}; font-weight: 900;">\\1</strong>', line)
                        line = re.sub(r'==(.*?)==', f'<span style="background-color: {t_style["accent"]}; padding: 2px 8px; border-radius: 4px; border: 1px solid {t_style["border"]};">\\1</span>', line)

                        if line.startswith("#"):
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]}; box-shadow: 0 4px 10px rgba(0,0,0,0.08); font-size: {content_font};">{table_content}</table>'
                                in_table = False; table_content = ""
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'<div style="background: {t_style["accent"]}; padding: 15px; border-radius: 8px; margin: 25px 0 15px 0; border-{align_attr}: 6px solid {t_style["primary"]}; page-break-after: avoid;"><h2 style="margin: 0; color: {t_style["primary"]}; font-size: 130%; font-weight: 900;">{header_text}</h2></div>'
                            
                        elif "|" in line:
                            if not in_table: in_table = True
                            cells = [c.strip() for c in line.split("|") if c.strip()]
                            row_html = "".join([f'<td style="border: 1px solid {t_style["border"]}; padding: 10px; text-align: center;">{c}</td>' for c in cells])
                            table_content += f'<tr style="border-bottom: 2px solid {t_style["accent"]};">{row_html}</tr>'

                        elif (":" in line or "：" in line) and theme == "گفتوگۆ و زمان (مۆر)":
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            parts = re.split(r'[:：]', line, maxsplit=1)
                            sp, msg = parts[0].strip(), parts[1].strip()
                            if sp not in speakers: speakers.append(sp)
                            is_alt = (speakers.index(sp) % 2 == 1)
                            bubble_css = f"float: {alt_align}; background: #ffffff; border-{align_attr}: 5px solid {t_style['border']};" if is_alt else f"float: {align_attr}; background: {t_style['accent']}; border-{align_attr}: 5px solid {t_style['primary']};"
                            content_blocks += f'<div style="width: 100%; clear: both; margin-bottom: 15px; overflow: hidden; page-break-inside: avoid;"><div style="width: 80%; {bubble_css} padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><span style="display: block; font-weight: 900; color: {t_style["primary"]}; margin-bottom: 5px; font-size: 85%;">{sp}</span><p style="margin: 0; font-size: {content_font}; line-height: 1.8;">{msg}</p></div></div>'
                            
                        else:
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]}; font-size: {content_font};">{table_content}</table>'
                                in_table = False; table_content = ""
                            content_blocks += f'<div style="background:{t_style["card"]}; padding:18px; border-radius:10px; margin-bottom:15px; border-{align_attr}:4px solid {t_style["border"]}; box-shadow: 0 2px 8px rgba(0,0,0,0.04); page-break-inside:avoid;"><p style="margin:0; font-size:{content_font}; line-height:2.0; text-align: {align_attr};">{line}</p></div>'
                    
                    if in_table:
                        content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]}; font-size: {content_font};">{table_content}</table>'

                    # دروستکردنی بارکۆد QR ئەگەر لینک هەبێت
                    qr_html = ""
                    if qr_link:
                        qr = qrcode.QRCode(box_size=10, border=1)
                        qr.add_data(qr_link)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color=t_style["primary"], back_color="white")
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        qr_html = f'<div style="position: absolute; top: 0px; {alt_align}: 0px; text-align: center;"><img src="data:image/png;base64,{img_str}" width="90" style="border: 2px solid {t_style["border"]}; border-radius: 8px; padding: 5px; background: white;"><div style="font-size: 9pt; color: {t_style["primary"]}; font-weight: bold; margin-top: 5px;">سکانی دەنگ</div></div>'

                    flag_html = ""
                    if show_flag:
                        flag_svg = """<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="width: 50px; height: auto; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);"><rect width="300" height="66.6" fill="#ED2024"/><rect y="66.6" width="300" height="66.6" fill="#FFFFFF"/><rect y="133.2" width="300" height="66.8" fill="#278E43"/><g transform="translate(150, 100)"><circle r="22" fill="#FEBD11"/><path d="M 0 -35 L 4 -22 L 15 -32 L 9 -19 L 26 -20 L 15 -11 L 33 -5 L 20 0 L 33 5 L 15 11 L 26 20 L 9 19 L 15 32 L 4 22 L 0 35 L -4 22 L -15 32 L -9 19 L -26 20 L -15 11 L -33 5 L -20 0 L -33 -5 L -15 -11 L -26 -20 L -9 -19 L -15 -32 L -4 -22 Z" fill="#FEBD11"/></g></svg>"""
                        flag_html = f'<div style="position: fixed; top: -20px; {align_attr}: 0px; z-index: 1000;">{flag_svg}</div>'

                    cover_html = f'''
                    <div style="text-align: center; margin-top: 40%; page-break-after: always;">
                        <div style="display: inline-block; padding: 40px; border: 3px solid {t_style["border"]}; border-radius: 20px; background: {t_style["card"]}; box-shadow: 0 15px 35px rgba(0,0,0,0.08);">
                            <h1 style="font-size: 250%; color: {t_style["primary"]}; border-bottom: 4px solid {t_style["accent"]}; padding-bottom: 20px; margin-bottom: 20px; font-weight: 900;">{title}</h1>
                            <p style="font-size: 150%; color: #475569; margin-bottom: 30px;">{subtitle}</p>
                            <div style="display: inline-block; padding: 10px 25px; background: {t_style["accent"]}; border-radius: 30px; font-size: 120%; color: {t_style["primary"]}; font-weight:bold;">{datetime.datetime.now().strftime("%Y-%m-%d")}</div>
                        </div>
                    </div>
                    ''' if cover_page else ""
                    
                    header_html = f'''
                    <div style="position: relative; border-{align_attr}: 8px solid {t_style["primary"]}; padding: 20px; margin-bottom: 40px; background: {t_style["card"]}; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <h1 style="margin: 0; color: {t_style["primary"]}; font-size: 180%; font-weight: 900; width: 70%;">{title}</h1>
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 110%;">{subtitle}</p>
                        {qr_html}
                    </div>
                    ''' if not cover_page else (f'<div style="position: relative; margin-bottom: 30px; height: 100px;">{qr_html}</div>' if qr_link else "")
                    
                    watermark_html = f'<div style="position: fixed; top: 40%; left: 10%; transform: rotate(-45deg); font-size: 500%; font-weight: 900; color: {t_style["primary"]}; opacity: 0.05; z-index: -1; white-space: nowrap;">{watermark}</div>' if watermark else ""

                    final_html = f"""
                    <!DOCTYPE html>
                    <html dir="{dir_attr}" lang="{lang_code}">
                    <head>
                    <meta charset="utf-8">
                    <style>
                    @page {{
                        {page_css}
                        {bg_css}
                    }}
                    body {{ font-family: 'Amiri', Tahoma, sans-serif; direction: {dir_attr}; text-align: {align_attr}; color: #0f172a; margin: 0; padding: 0; line-height: 1.6; }}
                    </style>
                    </head>
                    <body>
                    {flag_html}
                    {watermark_html}
                    {cover_html}
                    {header_html}
                    <div>{content_blocks}</div>
                    </body>
                    </html>
                    """

                    output_file = "Pro_Engine_Document.pdf"
                    HTML(string=final_html).write_pdf(output_file)
                    
                    with open(output_file, "rb") as f:
                        pdf_data = f.read()
                        
                    st.success("✅ ئامادەیە! فایلە پڕۆفیشناڵەکەت ئامادە کرا.")
                    st.download_button(label="📥 داگرتنی بەڵگەنامەکە", data=pdf_data, file_name=output_file, mime="application/pdf", use_container_width=True)

with tab_ai:
    st.markdown("### 🤖 مۆدی زیرەکی دەستکرد (هەڵبژاردەی داهاتوو)")
    st.info("لەم بەشەدا لە داهاتوودا سیستەمەکە ڕاستەوخۆ دەبەسترێتەوە بە ژیری دەستکردەوە (وەک ChatGPT یان Gemini).")
    ai_prompt = st.text_area("بە کوردی پێی بڵێ چیت دەوێت دروستی بکات؟ (بۆ نموونە: ٥ پرسیارم بۆ بنووسە لەسەر نەخۆشی شەکرە)", height=200)
    if st.button("✨ دروستکردن بە AI"):
        st.warning("⚠️ بۆ کارپێکردنی ئەم بەشە پێویستیمان بە کڕینی API Key دەبێت. بۆ ئێستا دەتوانیت تابـی (مۆدی دەستی) بەکاربهێنیت.")

st.markdown("<hr><p style='text-align: center; color: #94a3b8;'>بەرهەمهێنراو بە شانازییەوە لەلایەن Nimat Ahmed © 2026</p>", unsafe_allow_html=True)

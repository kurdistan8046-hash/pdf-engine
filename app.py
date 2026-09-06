import streamlit as st
import re
import datetime
import base64
import io
import qrcode
from weasyprint import HTML

st.set_page_config(page_title="PDF Pro Engine", page_icon="📄", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1e3a8a; font-weight: 900;'>PDF Pro Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 30px;'>سیستەمی پێشکەوتووی دروستکردنی PDF بە پشتگیری زیرەکی دەستکرد و دیزاینی خۆکار</p>", unsafe_allow_html=True)

tab_manual, tab_ai = st.tabs(["📝 مۆدی دەستی و خۆکار", "🤖 مۆدی زیرەکی دەستکرد (AI)"])

with tab_manual:
    col_content, col_settings = st.columns([2, 1])
    
    with col_settings:
        st.markdown("### ⚙️ ڕێکخستنەکان")
        title = st.text_input("📌 ناونیشان:", "بابەتی نوێ")
        subtitle = st.text_input("💡 ژێرنووس:", "پوختە")
        
        st.markdown("---")
        mode_type = st.radio("شێوازی دیزاین:", ["خۆکار (Auto-Detect)", "دەستی و ئارەزوومەندانە (Manual)"])
        
        active_theme = "دەفتەری تێبینی (هێڵکار)"
        language_dir = "ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)"
        
        if mode_type == "دەستی و ئارەزوومەندانە (Manual)":
            language_dir = st.selectbox("🌐 زمانی نووسین:", ["ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)", "چەپ بۆ ڕاست (English, Türkçe)"])
            active_theme = st.selectbox("🎨 دیزاینی پەڕەکان:", [
                "دەفتەری تێبینی (هێڵکار)", 
                "تۆڕی زانستی (گرافیک)",
                "پزیشکی و کلینیکی (شین)", 
                "گفتوگۆ و زمان (مۆر)", 
                "کلاسیک و ئەدەبی (قاوەیی)"
            ])
        
        st.markdown("---")
        qr_link = st.text_input("🔗 لینکی دەنگ/ڤیدیۆ بۆ بارکۆد:", placeholder="https://...")
        cover_page = st.checkbox("📄 پەڕەی بەرگ (Cover)", value=True)
        show_flag = st.checkbox("☀️ ئاڵای کوردستان (لۆگۆ)", value=True)
        watermark = st.text_input("🔏 هێمای ئاو:", "")

    with col_content:
        st.markdown("### 📝 ناوەڕۆکی بابەت")
        
        with st.expander("📖 شێوازی بەکارهێنان"):
            st.markdown("""
            * **سەردێڕ:** `#` لە پێش دەقەکە.
            * **تۆخکردن:** `**وشە**`
            * **هایلایت:** `==وشە==`
            * **خشتە:** `| وشە | وشە |`
            """)
            
        raw_text = st.text_area("دەقەکەت لێرە دابنێ:", height=450)
        
        if st.button("🚀 دروستکردنی PDF", type="primary", use_container_width=True):
            if not raw_text.strip():
                st.error("⚠️ تکایە ناوەڕۆکەکە پڕ بکەرەوە.")
            else:
                with st.spinner("چاوەڕێ بە... ⏳ خەریکی ئامادەکردنین"):
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                    
                    if mode_type == "خۆکار (Auto-Detect)":
                        is_dialogue = sum(1 for line in lines if ":" in line or "：" in line) > len(lines) * 0.3
                        is_medical = any(w in raw_text.lower() for w in ['نەخۆش', 'پزیشک', 'چارەسەر', 'دەرمان', 'patient', 'medical', 'treatment'])
                        is_english = any(ord(c) < 128 for c in raw_text[:50] if c.isalpha())
                        
                        if is_medical: active_theme = "پزیشکی و کلینیکی (شین)"
                        elif is_dialogue: active_theme = "گفتوگۆ و زمان (مۆر)"
                        else: active_theme = "دەفتەری تێبینی (هێڵکار)"
                        
                        dir_attr = "ltr" if is_english else "rtl"
                        align_attr = "left" if is_english else "right"
                        alt_align = "right" if is_english else "left"
                        lang_code = "en" if is_english else "ckb"
                    else:
                        is_rtl = "ڕاست" in language_dir
                        dir_attr = "rtl" if is_rtl else "ltr"
                        align_attr = "right" if is_rtl else "left"
                        alt_align = "left" if is_rtl else "right"
                        lang_code = "ckb" if is_rtl else "en"

                    themes_dict = {
                        "دەفتەری تێبینی (هێڵکار)": {"primary": "#334155", "bg": "repeating-linear-gradient( #f8fafc, #f8fafc 38px, #cbd5e1 38px, #cbd5e1 39px )", "card": "rgba(255,255,255,0.9)", "border": "#64748b", "accent": "#f1f5f9"},
                        "تۆڕی زانستی (گرافیک)": {"primary": "#0f766e", "bg": "linear-gradient(#ccfbf1 1px, transparent 1px), linear-gradient(90deg, #ccfbf1 1px, transparent 1px)", "bg_size": "25px 25px", "card": "rgba(255,255,255,0.95)", "border": "#14b8a6", "accent": "#ccfbf1"},
                        "پزیشکی و کلینیکی (شین)": {"primary": "#0369a1", "bg": "#f0f9ff", "card": "#ffffff", "border": "#0ea5e9", "accent": "#bae6fd"},
                        "گفتوگۆ و زمان (مۆر)": {"primary": "#6d28d9", "bg": "#f5f3ff", "card": "#ffffff", "border": "#8b5cf6", "accent": "#ddd6fe"},
                        "کلاسیک و ئەدەبی (قاوەیی)": {"primary": "#92400e", "bg": "#fefce8", "card": "#ffffff", "border": "#d97706", "accent": "#fde68a"}
                    }
                    t_style = themes_dict.get(active_theme, themes_dict["دەفتەری تێبینی (هێڵکار)"])
                    bg_css = f'background: {t_style["bg"]};' if "gradient" in t_style["bg"] else f'background-color: {t_style["bg"]};'
                    if "bg_size" in t_style: bg_css += f' background-size: {t_style["bg_size"]};'
                    
                    content_blocks = ""
                    in_table = False
                    table_content = ""
                    speakers = []
                    
                    for line in lines:
                        line = re.sub(r'\*\*(.*?)\*\*', f'<strong style="color: {t_style["primary"]}; font-weight: 900;">\\1</strong>', line)
                        line = re.sub(r'==(.*?)==', f'<span style="background-color: {t_style["accent"]}; padding: 2px 8px; border-radius: 4px; border: 1px solid {t_style["border"]};">\\1</span>', line)

                        if line.startswith("#"):
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'
                                in_table = False; table_content = ""
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'<div style="background: {t_style["accent"]}; padding: 15px; border-radius: 8px; margin: 25px 0 15px 0; border-{align_attr}: 6px solid {t_style["primary"]}; page-break-after: avoid;"><h2 style="margin: 0; color: {t_style["primary"]}; font-size: 130%; font-weight: 900;">{header_text}</h2></div>'
                            
                        elif "|" in line:
                            if not in_table: in_table = True
                            cells = [c.strip() for c in line.split("|") if c.strip()]
                            row_html = "".join([f'<td style="border: 1px solid {t_style["border"]}; padding: 10px; text-align: center;">{c}</td>' for c in cells])
                            table_content += f'<tr style="border-bottom: 2px solid {t_style["accent"]};">{row_html}</tr>'

                        elif (":" in line or "：" in line) and active_theme == "گفتوگۆ و زمان (مۆر)":
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            parts = re.split(r'[:：]', line, maxsplit=1)
                            sp, msg = parts[0].strip(), parts[1].strip()
                            if sp not in speakers: speakers.append(sp)
                            is_alt = (speakers.index(sp) % 2 == 1)
                            bubble_css = f"float: {alt_align}; background: #ffffff; border-{align_attr}: 5px solid {t_style['border']};" if is_alt else f"float: {align_attr}; background: {t_style['accent']}; border-{align_attr}: 5px solid {t_style['primary']};"
                            content_blocks += f'<div style="width: 100%; clear: both; margin-bottom: 15px; overflow: hidden; page-break-inside: avoid;"><div style="width: 80%; {bubble_css} padding: 15px; border-radius: 12px;"><span style="display: block; font-weight: 900; color: {t_style["primary"]}; margin-bottom: 5px; font-size: 85%;">{sp}</span><p style="margin: 0; font-size: 16pt; line-height: 1.8;">{msg}</p></div></div>'
                            
                        else:
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'
                                in_table = False; table_content = ""
                            content_blocks += f'<div style="background:{t_style["card"]}; padding:18px; border-radius:10px; margin-bottom:15px; border-{align_attr}:4px solid {t_style["border"]}; page-break-inside:avoid;"><p style="margin:0; font-size:16pt; line-height:2.0; text-align: {align_attr};">{line}</p></div>'
                    
                    if in_table:
                        content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'

                    qr_html = ""
                    if qr_link:
                        qr = qrcode.QRCode(box_size=10, border=1)
                        qr.add_data(qr_link)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color=t_style["primary"], back_color="white")
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        qr_html = f'<div style="position: absolute; top: 0px; {alt_align}: 0px; text-align: center;"><img src="data:image/png;base64,{img_str}" width="90" style="border: 2px solid {t_style["border"]}; border-radius: 8px; padding: 5px; background: white;"><div style="font-size: 9pt; color: {t_style["primary"]}; font-weight: bold; margin-top: 5px;">QR Code</div></div>'

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
                        size: A4; margin: 25mm 20mm;
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

                    # PRO FIX: Using In-Memory Buffer instead of saving to disk directly
                    try:
                        pdf_buffer = io.BytesIO()
                        HTML(string=final_html).write_pdf(target=pdf_buffer)
                        pdf_data = pdf_buffer.getvalue()
                        
                        st.success("✅ فایلەکە بە سەرکەوتوویی ئامادە کرا.")
                        st.download_button(
                            label="📥 داگرتنی فایلی PDF", 
                            data=pdf_data, 
                            file_name=f"{title.replace(' ', '_')}.pdf", 
                            mime="application/pdf", 
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"⚠️ هەڵەیەک ڕوویدا لە کاتی دروستکردنی PDF: تێبینی: دڵنیابە لەوەی کتێبخانەکانی GTK3 لەسەر ئامێرەکەت دابەزێنراون. جۆری هەڵە: {e}")

with tab_ai:
    st.markdown("### 🤖 مۆدی زیرەکی دەستکرد (AI)")
    st.info("لەم بەشەدا دەتوانیت داواکارییەکەت بنووسیت تا AI ناوەڕۆکت بۆ دروست بکات و ڕێکی بخات.")
    ai_input_text = st.text_area("نموونە: ٥ پرسیار لەسەر نەخۆشی شەکرە بنووسە", height=200)
    if st.button("✨ دروستکردن بە یارمەتی AI", type="primary"):
        if not ai_input_text.strip():
            st.error("تکایە داواکارییەک بنووسە.")
        else:
            st.success("✅ سیستەمەکە ئامادەیە بۆ وەرگرتنی داواکارییەکە و بەستنەوەی بە API.")
            st.info("بۆ چالاککردنی تاقیکاری، دەتوانیت دەقەکە ببەیتە مۆدی دەستی و ڕاستەوخۆ دیزاینی بکەیت.")

st.markdown("<hr><p style='text-align: center; color: #94a3b8;'>PDF Pro Engine - Optimized Version</p>", unsafe_allow_html=True)

import streamlit as st
import re
import datetime
import base64
import io
import qrcode
from weasyprint import HTML
import google.generativeai as genai

# ڕێکخستنی پەڕەی ستریملیت
st.set_page_config(page_title="PDF Pro Engine", page_icon="📄", layout="wide")

# بیرگەی کاتی بۆ گواستنەوەی دەق لە AI بۆ دەستی
if 'doc_content' not in st.session_state:
    st.session_state.doc_content = ""

st.markdown("<h1 style='text-align: center; color: #1e3a8a; font-weight: 900;'>PDF Pro Engine (Ultimate Edition)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 30px;'>سیستەمی پێشکەوتووی دروستکردنی PDF لەگەڵ زیرەکی دەستکرد و کۆنترۆڵی تەواوی دیزاین</p>", unsafe_allow_html=True)

tab_manual, tab_ai = st.tabs(["📝 مۆدی دەستی و دیزاینکردن", "🤖 مۆدی زیرەکی دەستکرد (AI)"])

with tab_manual:
    col_content, col_settings = st.columns([2, 1])
    
    with col_settings:
        st.markdown("### ⚙️ ڕێکخستنەکان")
        title = st.text_input("📌 ناونیشان:", "بابەتی نوێ")
        subtitle = st.text_input("💡 ژێرنووس:", "پوختە")
        
        st.markdown("---")
        # تایبەتمەندییە نوێیەکانی دیزاین
        st.markdown("#### 📏 پێوانە و فۆنت")
        page_size = st.selectbox("پەڕە:", ["A4", "A5", "Letter"])
        margin_size = st.selectbox("لێوارەکان (Margins):", ["ئاسایی (Normal)", "تەسک (Narrow)", "فراوان (Wide)"])
        font_family = st.selectbox("جۆری فۆنت:", ["Amiri", "Arial", "Tahoma", "Times New Roman"])
        font_size = st.slider("قەبارەی فۆنت:", min_value=10, max_value=24, value=16)
        line_spacing = st.slider("بۆشایی دێڕەکان:", min_value=1.0, max_value=3.0, value=1.8, step=0.1)
        
        st.markdown("---")
        mode_type = st.radio("شێوازی دیزاین:", ["خۆکار (Auto-Detect)", "دەستی (Manual)"])
        active_theme = "دەفتەری تێبینی (هێڵکار)"
        language_dir = "ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)"
        
        if mode_type == "دەستی (Manual)":
            language_dir = st.selectbox("🌐 زمانی نووسین:", ["ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)", "چەپ بۆ ڕاست (English, Türkçe)"])
            active_theme = st.selectbox("🎨 دیزاینی پەڕەکان:", [
                "دەفتەری تێبینی (هێڵکار)", "تۆڕی زانستی (گرافیک)", "پزیشکی و کلینیکی (شین)", "گفتوگۆ و زمان (مۆر)", "کلاسیک و ئەدەبی (قاوەیی)"
            ])
        
        st.markdown("---")
        st.markdown("#### 🖼️ زیادکراوەکان")
        qr_link = st.text_input("🔗 لینکی دەنگ/ڤیدیۆ بۆ بارکۆد:", placeholder="https://...")
        custom_logo = st.file_uploader("لەبری ئاڵا لۆگۆی خۆت دابنێ (ئارەزوومەندانە):", type=["png", "jpg", "jpeg"])
        cover_page = st.checkbox("📄 پەڕەی بەرگ (Cover)", value=True)
        show_flag = st.checkbox("☀️ ئاڵای کوردستان", value=True)
        footer_text = st.text_input("🔽 دەقی خوارەوەی پەڕە (Footer):", "ئامادەکراوە بە PDF Pro Engine")
        watermark = st.text_input("🔏 هێمای ئاو (Watermark):", "")

    with col_content:
        st.markdown("### 📝 ناوەڕۆکی بابەت")
        raw_text = st.text_area("دەقەکەت لێرە دابنێ یان لە مۆدی AI دروستی بکە:", value=st.session_state.doc_content, height=500, key="manual_text_input")
        
        if st.button("🚀 دروستکردنی PDF", type="primary", use_container_width=True):
            if not st.session_state.manual_text_input.strip():
                st.error("⚠️ تکایە ناوەڕۆکەکە پڕ بکەرەوە.")
            else:
                with st.spinner("چاوەڕێ بە... ⏳ خەریکی ئامادەکردنین"):
                    lines = [line.strip() for line in st.session_state.manual_text_input.split('\n') if line.strip()]
                    
                    # دیاریکردنی ئاراستە
                    if mode_type == "خۆکار (Auto-Detect)":
                        is_english = any(ord(c) < 128 for c in st.session_state.manual_text_input[:50] if c.isalpha())
                        dir_attr = "ltr" if is_english else "rtl"
                    else:
                        is_rtl = "ڕاست" in language_dir
                        dir_attr = "rtl" if is_rtl else "ltr"
                        
                    align_attr = "right" if dir_attr == "rtl" else "left"
                    alt_align = "left" if dir_attr == "rtl" else "right"
                    lang_code = "ckb" if dir_attr == "rtl" else "en"

                    # ڕێکخستنی لێوارەکان
                    margin_dict = {"ئاسایی (Normal)": "25mm 20mm", "تەسک (Narrow)": "15mm 15mm", "فراوان (Wide)": "35mm 30mm"}
                    margin_css = margin_dict.get(margin_size, "25mm 20mm")

                    # دیزاینەکان
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
                    
                    # دروستکردنی ناوەڕۆک
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

                        else:
                            if in_table:
                                content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'
                                in_table = False; table_content = ""
                            content_blocks += f'<div style="background:{t_style["card"]}; padding:18px; border-radius:10px; margin-bottom:15px; border-{align_attr}:4px solid {t_style["border"]}; page-break-inside:avoid;"><p style="margin:0; text-align: {align_attr};">{line}</p></div>'
                    
                    if in_table: content_blocks += f'<table style="width:100%; border-collapse: collapse; margin: 20px 0; background: {t_style["card"]};">{table_content}</table>'

                    # ئامادەکردنی وێنە و لۆگۆ
                    logo_html = ""
                    if custom_logo:
                        img_str = base64.b64encode(custom_logo.read()).decode()
                        img_format = custom_logo.name.split('.')[-1]
                        logo_html = f'<div style="position: absolute; top: 0; {align_attr}: 0; z-index: 1000;"><img src="data:image/{img_format};base64,{img_str}" style="height: 60px; max-width: 150px;"></div>'
                    elif show_flag:
                        flag_svg = """<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="width: 50px; height: auto; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);"><rect width="300" height="66.6" fill="#ED2024"/><rect y="66.6" width="300" height="66.6" fill="#FFFFFF"/><rect y="133.2" width="300" height="66.8" fill="#278E43"/><g transform="translate(150, 100)"><circle r="22" fill="#FEBD11"/><path d="M 0 -35 L 4 -22 L 15 -32 L 9 -19 L 26 -20 L 15 -11 L 33 -5 L 20 0 L 33 5 L 15 11 L 26 20 L 9 19 L 15 32 L 4 22 L 0 35 L -4 22 L -15 32 L -9 19 L -26 20 L -15 11 L -33 5 L -20 0 L -33 -5 L -15 -11 L -26 -20 L -9 -19 L -15 -32 L -4 -22 Z" fill="#FEBD11"/></g></svg>"""
                        logo_html = f'<div style="position: absolute; top: -10px; {align_attr}: 0; z-index: 1000;">{flag_svg}</div>'

                    qr_html = ""
                    if qr_link:
                        qr = qrcode.QRCode(box_size=10, border=1)
                        qr.add_data(qr_link)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color=t_style["primary"], back_color="white")
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        qr_html = f'<div style="position: absolute; top: 0px; {alt_align}: 0px; text-align: center;"><img src="data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}" width="80" style="border: 2px solid {t_style["border"]}; border-radius: 8px; padding: 5px; background: white;"></div>'

                    cover_html = f'''
                    <div style="text-align: center; margin-top: 40%; page-break-after: always; position: relative;">
                        {logo_html}
                        <div style="display: inline-block; padding: 40px; border: 3px solid {t_style["border"]}; border-radius: 20px; background: {t_style["card"]}; box-shadow: 0 15px 35px rgba(0,0,0,0.08); margin-top: 50px;">
                            <h1 style="font-size: 250%; color: {t_style["primary"]}; border-bottom: 4px solid {t_style["accent"]}; padding-bottom: 20px; margin-bottom: 20px; font-weight: 900;">{title}</h1>
                            <p style="font-size: 150%; color: #475569; margin-bottom: 30px;">{subtitle}</p>
                            <div style="display: inline-block; padding: 10px 25px; background: {t_style["accent"]}; border-radius: 30px; font-size: 120%; color: {t_style["primary"]}; font-weight:bold;">{datetime.datetime.now().strftime("%Y-%m-%d")}</div>
                        </div>
                    </div>
                    ''' if cover_page else ""
                    
                    header_html = f'''
                    <div style="position: relative; border-{align_attr}: 8px solid {t_style["primary"]}; padding: 20px; margin-bottom: 40px; margin-top: 20px; background: {t_style["card"]}; border-radius: 12px;">
                        {logo_html if not cover_page else ""}
                        <h1 style="margin: 0; color: {t_style["primary"]}; font-size: 180%; font-weight: 900; width: 70%;">{title}</h1>
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 110%;">{subtitle}</p>
                        {qr_html}
                    </div>
                    '''
                    
                    watermark_html = f'<div style="position: fixed; top: 40%; left: 10%; transform: rotate(-45deg); font-size: 600%; font-weight: 900; color: {t_style["primary"]}; opacity: 0.04; z-index: -1; white-space: nowrap;">{watermark}</div>' if watermark else ""

                    final_html = f"""
                    <!DOCTYPE html>
                    <html dir="{dir_attr}" lang="{lang_code}">
                    <head>
                    <meta charset="utf-8">
                    <style>
                    @page {{
                        size: {page_size}; 
                        margin: {margin_css};
                        @bottom-center {{
                            content: "{footer_text} - " counter(page);
                            font-family: '{font_family}', sans-serif;
                            font-size: 10pt;
                            color: #64748b;
                        }}
                        {bg_css}
                    }}
                    body {{ 
                        font-family: '{font_family}', sans-serif; 
                        direction: {dir_attr}; 
                        text-align: {align_attr}; 
                        color: #0f172a; 
                        margin: 0; 
                        padding: 0; 
                        font-size: {font_size}pt;
                        line-height: {line_spacing}; 
                    }}
                    </style>
                    </head>
                    <body>
                    {watermark_html}
                    {cover_html}
                    {header_html if not cover_page else ('<div style="position: relative; height: 80px; margin-bottom: 20px;">' + logo_html + qr_html + '</div>' if (logo_html or qr_html) else '')}
                    <div>{content_blocks}</div>
                    </body>
                    </html>
                    """

                    try:
                        pdf_buffer = io.BytesIO()
                        HTML(string=final_html).write_pdf(target=pdf_buffer)
                        
                        st.success("✅ فایلەکە بە سەرکەوتوویی ئامادە کرا.")
                        st.download_button(
                            label="📥 داگرتنی فایلی PDF", 
                            data=pdf_buffer.getvalue(), 
                            file_name=f"{title.replace(' ', '_')}.pdf", 
                            mime="application/pdf", 
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"⚠️ هەڵەیەک ڕوویدا: {e}")

with tab_ai:
    st.markdown("### 🤖 دروستکردنی ناوەڕۆک بە زیرەکی دەستکرد")
    
    with st.expander("ℹ️ چۆن کلیل (API Key) وەربگرم؟", expanded=True):
        st.markdown("""
        بۆ بەکارهێنانی ئەم بەشە بە خۆڕایی، پێویستت بە کلیلی تایبەتی خۆتە:
        1. بڕۆ بۆ ماڵپەڕی **[Google AI Studio](https://aistudio.google.com/app/apikey)** بە ئیمەیڵەکەت (Gmail).
        2. دوگمەی **Create API key** دابگرە و کلیلەکە کۆپی بکە.
        3. کلیلەکە لەم خانەیەی خوارەوە دابنێ. *(تێبینی: کلیلەکەت پارێزراوە و لەلای ئێمە پاشەکەوت ناکرێت).*
        """)
        
    user_api_key = st.text_input("🔑 کلیلی تایبەتت (Gemini API Key):", type="password", placeholder="AIzaSy...")
    
    ai_input_text = st.text_area("✍️ چی بنووسم بۆت؟", placeholder="نموونە: پوختەیەک لەسەر نەخۆشی شەکرە بنووسە لەگەڵ ٥ ڕێنمایی خۆپاراستن، با بە خشتە و سەردێڕ بێت.", height=150)
    
    if st.button("✨ داواکردن لە AI", type="primary", use_container_width=True):
        if not user_api_key:
            st.error("⚠️ تکایە سەرەتا کلیلی API دابنێ لە خانەی سەرەوە.")
        elif not ai_input_text.strip():
            st.error("⚠️ تکایە داواکارییەک بنووسە.")
        else:
            with st.spinner("🤖 زیرەکی دەستکرد خەریکی نووسینە..."):
                try:
                    # بەستنەوە بە گۆگڵ جێمینای
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # داواکردن لە مۆدێلەکە کە فۆرماتی تایبەت بەکاربهێنێت بۆ ئەپەکەمان
                    system_prompt = f"تۆ یاریدەدەرێکی زیرەکی. وەڵامەکانت بە جوانی ڕێکبخە. بۆ سەردێڕەکان # بەکاربهێنە، بۆ وشەی گرنگ **وشە** بەکاربهێنە، وە ئەگەر پێویست بوو خشتە بەکاربهێنە بە نیشانەی |. بە زمانی پێویست وەڵام بدەرەوە.\n\nداواکاری بەکارهێنەر: {ai_input_text}"
                    
                    response = model.generate_content(system_prompt)
                    
                    # خستنە ناو بیرگەی کاتی
                    st.session_state.doc_content = response.text
                    st.success("✅ دەقەکە ئامادەیە! ناوەڕۆکەکە خرایە ناو خانەی نووسین لە 'مۆدی دەستی'. ئێستا بڕۆ ئەوێ بۆ بینین و دیزاینکردنی بۆ PDF.")
                    
                except Exception as e:
                    st.error(f"❌ هەڵەیەک لە پەیوەندیکردن بە AI ڕوویدا. دڵنیابە کلیلەکەت ڕاستە. (هۆکار: {e})")

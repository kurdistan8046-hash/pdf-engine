import streamlit as st
import re
import datetime
import io
from weasyprint import HTML, CSS
import google.generativeai as genai

# ڕێکخستنی سەرەکی وێبسایت
st.set_page_config(page_title="PDF Pro Engine", page_icon="👑", layout="wide")

if 'doc_content' not in st.session_state:
    st.session_state.doc_content = ""

# دانانی ئاڵای کوردستان و ناونیشان لەسەر وێبسایتەکە بە دیزاینی شاهانە
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="width: 120px; height: auto; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); border: 2px solid #e2e8f0;">
        <rect width="300" height="66.6" fill="#ED2024"/>
        <rect y="66.6" width="300" height="66.6" fill="#FFFFFF"/>
        <rect y="133.2" width="300" height="66.8" fill="#278E43"/>
        <g transform="translate(150, 100)">
            <circle r="22" fill="#FEBD11"/>
            <path d="M 0 -35 L 4 -22 L 15 -32 L 9 -19 L 26 -20 L 15 -11 L 33 -5 L 20 0 L 33 5 L 15 11 L 26 20 L 9 19 L 15 32 L 4 22 L 0 35 L -4 22 L -15 32 L -9 19 L -26 20 L -15 11 L -33 5 L -20 0 L -33 -5 L -15 -11 L -26 -20 L -9 -19 L -15 -32 L -4 -22 Z" fill="#FEBD11"/>
        </g>
    </svg>
    <h1 style='color: #1e3a8a; font-weight: 900; margin-top: 15px; font-size: 3rem;'>PDF Pro Engine</h1>
    <p style='color: #64748b; font-size: 1.2rem; font-weight: bold;'>مۆتۆڕی دروستکردنی کەرەستەی فێرکاری ئاست بەرز</p>
</div>
<hr style="border: 2px solid #e2e8f0; border-radius: 5px;">
""", unsafe_allow_html=True)

tab_pdf, tab_ai = st.tabs(["📄 دروستکردنی PDF (پڕۆفیشناڵ)", "🤖 مۆدی زیرەکی دەستکرد (AI)"])

with tab_pdf:
    col_content, col_settings = st.columns([2, 1])
    
    with col_settings:
        st.markdown("<h3 style='color:#0f172a;'>⚙️ ڕێکخستنی پەڕە</h3>", unsafe_allow_html=True)
        title = st.text_input("📌 ناونیشانی سەرەکی:", "نەخۆشی شەکرە")
        subtitle = st.text_input("💡 ژێرنووس (وانە یان بەش):", "نیشانەکان و خۆپاراستن")
        
        st.markdown("---")
        st.markdown("### 🎨 دیزاینی پێشکەوتوو")
        active_theme = st.selectbox("قاڵب هەڵبژێرە:", [
            "پزیشکی و ئەکادیمی (فەرمی 🩺)", 
            "زمان و دیالۆگ (شێوەی چات 💬)", 
            "کتێبی کلاسیک (قاوەیی کراوە 📖)",
            "مۆدێرن و تاریک (Dark Mode 🌙)"
        ])
        
        language_dir = st.selectbox("🌐 ئاڕاستەی دەق:", ["ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)", "چەپ بۆ ڕاست (English)"])
        
        cover_page = st.checkbox("📄 دروستکردنی پەڕەی بەرگ (Cover)", value=True)
        watermark = st.text_input("🔏 هێمای ئاو (ناوێک بنووسە بۆ ناوەڕاستی پەڕەکان):", "")

    with col_content:
        st.info("💡 **تایبەتمەندییەکان:** `#` بۆ سەردێڕ | `**وشە**` بۆ تۆخکردن | `==وشە==` بۆ هایلایت | `|وشە|وشە|` بۆ خشتە. ئەگەر دیالۆگ بنووسیت وەکو (پزیشک: فەرموو دابنیشە)، ئەوا خۆی دەیکاتە بڵقی چات!")
        raw_text = st.text_area("دەقەکەت لێرە دابنێ (یان لە بەشی AI بیهێنە):", value=st.session_state.doc_content, height=450)
        
        if st.button("🚀 بەرهەمهێنانی PDF بە کوالێتی بەرز", type="primary", use_container_width=True):
            if not raw_text.strip():
                st.error("⚠️ تکایە دەقێک بنووسە.")
            else:
                with st.spinner("⏳ مۆتۆڕەکە خەریکی داڕشتنی دیزاینەکانە..."):
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                    is_rtl = "ڕاست" in language_dir
                    dir_attr = "rtl" if is_rtl else "ltr"
                    align_attr = "right" if is_rtl else "left"
                    alt_align = "left" if is_rtl else "right"
                    
                    # دیزاینە زەخمەکان
                    themes = {
                        "زمان و دیالۆگ (شێوەی چات 💬)": {
                            "bg": "#f0fdf4", "primary": "#166534", "text": "#0f172a", 
                            "chat1": "#dcf8c6", "chat2": "#ffffff", "border": "#22c55e",
                            "font": "Amiri"
                        },
                        "پزیشکی و ئەکادیمی (فەرمی 🩺)": {
                            "bg": "#ffffff", "primary": "#0369a1", "text": "#1e293b", 
                            "chat1": "#f1f5f9", "chat2": "#e2e8f0", "border": "#0284c7",
                            "font": "Amiri"
                        },
                        "کتێبی کلاسیک (قاوەیی کراوە 📖)": {
                            "bg": "#fdf8f5", "primary": "#78350f", "text": "#451a03", 
                            "chat1": "#fef3c7", "chat2": "#ffedd5", "border": "#d97706",
                            "font": "Amiri"
                        },
                        "مۆدێرن و تاریک (Dark Mode 🌙)": {
                            "bg": "#0f172a", "primary": "#38bdf8", "text": "#f8fafc", 
                            "chat1": "#1e293b", "chat2": "#334155", "border": "#0ea5e9",
                            "font": "Amiri"
                        }
                    }
                    t = themes[active_theme]
                    
                    content_blocks = ""
                    in_table = False
                    table_content = ""
                    speakers = []

                    for line in lines:
                        # فۆرماتکردنی دەق
                        line = re.sub(r'\*\*(.*?)\*\*', f'<strong style="color:{t["primary"]}; font-weight:900;">\\1</strong>', line)
                        line = re.sub(r'==(.*?)==', f'<span style="background-color:#fef08a; color:#1f2937; padding:2px 6px; border-radius:4px;">\\1</span>', line)

                        # سەردێڕ
                        if line.startswith("#"):
                            if in_table:
                                content_blocks += f'<table class="premium-table">{table_content}</table>'
                                in_table = False; table_content = ""
                            
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'<div class="premium-header"><h2 style="margin:0;">{header_text}</h2></div>'

                        # خشتە ئەکادیمییەکان
                        elif "|" in line:
                            if not in_table: in_table = True
                            cells = [c.strip() for c in line.split("|") if c.strip()]
                            row_html = "".join([f'<td>{c}</td>' for c in cells])
                            table_content += f'<tr>{row_html}</tr>'

                        # پارسەری دیالۆگ (شێوەی چاتی مۆدێرن)
                        elif (":" in line or "：" in line) and "زمان" in active_theme:
                            if in_table:
                                content_blocks += f'<table class="premium-table">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            parts = re.split(r'[:：]', line, maxsplit=1)
                            sp, msg = parts[0].strip(), parts[1].strip()
                            if sp not in speakers: speakers.append(sp)
                            
                            is_alt = (speakers.index(sp) % 2 == 1)
                            bubble_class = "chat-bubble-alt" if is_alt else "chat-bubble"
                            
                            content_blocks += f'''
                            <div class="chat-container">
                                <div class="{bubble_class}">
                                    <div class="chat-name">{sp}</div>
                                    <div class="chat-msg">{msg}</div>
                                </div>
                            </div>
                            '''
                            
                        # دەقی ئاسایی
                        else:
                            if in_table:
                                content_blocks += f'<table class="premium-table">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            content_blocks += f'<div class="normal-text">{line}</div>'
                            
                    if in_table:
                        content_blocks += f'<table class="premium-table">{table_content}</table>'

                    # CSS ـی زەبەلاح و پڕۆفیشناڵ
                    css_string = f"""
                    @page {{
                        size: A4;
                        margin: 20mm;
                        background-color: {t["bg"]};
                        @bottom-center {{
                            content: counter(page);
                            font-family: '{t["font"]}', sans-serif;
                            font-size: 14pt;
                            color: {t["primary"]};
                            font-weight: bold;
                        }}
                    }}
                    body {{
                        font-family: '{t["font"]}', sans-serif;
                        direction: {dir_attr};
                        text-align: {align_attr};
                        color: {t["text"]};
                        font-size: 18pt;
                        line-height: 2.2;
                    }}
                    .cover-page {{
                        text-align: center;
                        margin-top: 30%;
                        page-break-after: always;
                    }}
                    .cover-box {{
                        display: inline-block;
                        padding: 50px 80px;
                        border: 4px solid {t["primary"]};
                        border-radius: 20px;
                        background-color: {t["bg"]};
                        box-shadow: 10px 10px 0px {t["border"]}40;
                    }}
                    .cover-title {{
                        font-size: 45pt;
                        color: {t["primary"]};
                        border-bottom: 5px solid {t["border"]};
                        padding-bottom: 20px;
                        margin-bottom: 20px;
                        font-weight: 900;
                    }}
                    .cover-subtitle {{
                        font-size: 24pt;
                        color: {t["text"]};
                        opacity: 0.8;
                    }}
                    .premium-header {{
                        background-color: {t["primary"]}15;
                        padding: 20px;
                        border-radius: 12px;
                        border-{align_attr}: 8px solid {t["primary"]};
                        margin: 40px 0 20px 0;
                        color: {t["primary"]};
                        page-break-after: avoid;
                    }}
                    .chat-container {{
                        width: 100%;
                        clear: both;
                        margin-bottom: 20px;
                        overflow: hidden;
                        page-break-inside: avoid;
                    }}
                    .chat-bubble {{
                        float: {align_attr};
                        background-color: {t["chat1"]};
                        padding: 15px 25px;
                        border-radius: 25px 25px 25px 5px;
                        border: 2px solid {t["border"]}50;
                        max-width: 80%;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    }}
                    .chat-bubble-alt {{
                        float: {alt_align};
                        background-color: {t["chat2"]};
                        padding: 15px 25px;
                        border-radius: 25px 25px 5px 25px;
                        border: 2px solid {t["border"]}50;
                        max-width: 80%;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    }}
                    .chat-name {{
                        font-weight: 900;
                        color: {t["primary"]};
                        font-size: 14pt;
                        margin-bottom: 5px;
                    }}
                    .chat-msg {{
                        font-size: 18pt;
                        color: {t["text"]};
                    }}
                    .normal-text {{
                        margin-bottom: 15px;
                        text-align: justify;
                        padding: 10px;
                    }}
                    .premium-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 30px 0;
                        background-color: {t["chat2"]};
                        border-radius: 10px;
                        overflow: hidden;
                        border: 2px solid {t["primary"]};
                    }}
                    .premium-table td {{
                        border: 1px solid {t["border"]}50;
                        padding: 15px;
                        text-align: center;
                    }}
                    .premium-table tr:nth-child(even) {{
                        background-color: {t["chat1"]};
                    }}
                    .watermark {{
                        position: fixed;
                        top: 45%;
                        left: 20%;
                        transform: rotate(-45deg);
                        font-size: 80pt;
                        font-weight: 900;
                        color: {t["primary"]};
                        opacity: 0.05;
                        z-index: -1;
                    }}
                    """

                    cover_html = f'''
                    <div class="cover-page">
                        <div class="cover-box">
                            <div class="cover-title">{title}</div>
                            <div class="cover-subtitle">{subtitle}</div>
                            <div style="margin-top: 40px; font-size: 14pt; color: {t["primary"]}; font-weight: bold;">
                                {datetime.datetime.now().strftime("%Y-%m-%d")}
                            </div>
                        </div>
                    </div>
                    ''' if cover_page else f'<h1 style="color:{t["primary"]}; text-align:center; font-size:35pt; border-bottom:3px solid {t["border"]}; padding-bottom:15px;">{title}</h1><h3 style="text-align:center; opacity:0.7;">{subtitle}</h3>'

                    watermark_html = f'<div class="watermark">{watermark}</div>' if watermark else ""

                    final_html = f"""
                    <!DOCTYPE html>
                    <html dir="{dir_attr}">
                    <head>
                        <meta charset="utf-8">
                        <style>{css_string}</style>
                    </head>
                    <body>
                        {watermark_html}
                        {cover_html}
                        <div>{content_blocks}</div>
                    </body>
                    </html>
                    """
                    
                    pdf_buf = io.BytesIO()
                    HTML(string=final_html).write_pdf(target=pdf_buf)
                    
                    st.success("✅ ئامادەیە! فایلە شاهانەکەت دروستکرا.")
                    st.download_button("📥 داگرتنی فایلی PDF", data=pdf_buf.getvalue(), file_name=f"{title}.pdf", mime="application/pdf", use_container_width=True)

with tab_ai:
    st.markdown("### 🤖 دروستکردنی ناوەڕۆک بە ژیری دەستکرد")
    
    with st.expander("ℹ️ چۆنیەتی هێنانی کلیلی API (تایبەت بە خۆت)", expanded=True):
        st.markdown("""
        ئەم کلیلە **تایبەتە بە خۆت (Individualized)** و بە تەواوی پارێزراوە، لە هیچ سێرڤەرێک پاشەکەوت ناکرێت. بۆ وەرگرتنی:
        1. بڕۆ بۆ ماڵپەڕی فەرمی [Google AI Studio](https://aistudio.google.com/app/apikey).
        2. بە ئیمەیڵەکەت (Gmail) بچۆ ژوورەوە.
        3. لەوێ کلیک لە دوگمەی شین بکە کە نووسراوە **Create API key** و کلیلەکە کۆپی بکە.
        4. کلیلەکە بهێنە و لەم خانەیەی خوارەوە دایبنێ.
        """)
        
    user_api_key = st.text_input("🔑 کلیلی تایبەتت (Gemini API Key):", type="password", placeholder="کلیلەکەت لێرە دابنێ (AIzaSy...)")
    
    ai_input_text = st.text_area("✍️ داواکارییەکەت بنووسە:", placeholder="نموونە: ٥ خاڵی گرنگ بنووسە لەسەر نیشانەکانی نەخۆشی شەکرە و چۆنیەتی خۆپاراستن لێی بە شێوەی خشتە...", height=150)
    
    if st.button("✨ داواکردن لە AI و هێنانە ناوەوە", type="primary", use_container_width=True):
        if not user_api_key:
            st.error("⚠️ تکایە سەرەتا کلیلی تایبەتی خۆت دابنێ.")
        elif not ai_input_text.strip():
            st.error("⚠️ تکایە داواکارییەک بنووسە.")
        else:
            with st.spinner("🤖 خەریکی بیرکردنەوە و نووسینە..."):
                try:
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"وەڵامەکەت با زۆر ڕێکخراو بێت. ئەگەر دیالۆگە با شێوازی ناوی کەسەکە و دوو خاڵ بێت وەکو (پزیشک: فەرموو). ئەگەر زانیارییە سەردێڕەکان بە # بنووسە و زانیارییە گرنگەکان بکە بە خشتە. \n\nداواکاری: {ai_input_text}")
                    st.session_state.doc_content = response.text
                    st.success("✅ دەقەکە ئامادەیە! ناوەڕۆکەکە خرایە ناو خانەی نووسین لە تابـی 'دروستکردنی PDF'. بڕۆ ئەوێ بۆ دیزاینکردنی.")
                except Exception as e:
                    st.error(f"❌ کێشەیەک ڕوویدا لە بەستنەوە بە AI. دڵنیابە کلیلەکەت ڕاستە. (وردەکاری: {e})")

st.markdown("<br><hr><p style='text-align: center; color: #94a3b8; font-weight: bold;'>دروستکراوە بە تەکنەلۆژیای پێشکەوتوو © 2026</p>", unsafe_allow_html=True)

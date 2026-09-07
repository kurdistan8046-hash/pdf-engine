import streamlit as st
import re
import datetime
import io
from weasyprint import HTML
import google.generativeai as genai

# ڕێکخستنی سەرەکی وێبسایت
st.set_page_config(page_title="PDF Pro Engine", page_icon="👑", layout="wide")

if 'doc_content' not in st.session_state:
    st.session_state.doc_content = ""

# دانانی ئاڵای کوردستان و ناونیشان
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
        title = st.text_input("📌 ناونیشانی سەرەکی:", value="", placeholder="بۆ نموونە: وانەی یەکەم...")
        subtitle = st.text_input("💡 ژێرنووس (پوختە):", value="", placeholder="بۆ نموونە: پێشەکی بابەت...")
        
        st.markdown("---")
        st.markdown("### 🎨 دیزاینی پێشکەوتوو")
        active_theme = st.selectbox("قاڵب هەڵبژێرە:", [
            "پزیشکی و ئەکادیمی (فەرمی 🩺)", 
            "زمان و دیالۆگ (شێوەی چات 💬)", 
            "کتێبی کلاسیک (قاوەیی کراوە 📖)",
            "مۆدێرن و تاریک (Dark Mode 🌙)"
        ])
        
        language_dir = st.selectbox("🌐 ئاڕاستەی دەق:", [
            "ڕاست بۆ چەپ (کوردی، عەرەبی، فارسی)", 
            "چەپ بۆ ڕاست (English, Türkçe)",
            "تێکەڵ (Mix - Auto)"
        ])
        
        cover_page = st.checkbox("📄 دروستکردنی پەڕەی بەرگ (Cover)", value=True)
        watermark = st.text_input("🔏 هێمای ئاو (Watermark):", placeholder="ناو یان لۆگۆی خۆت لێرە بنووسە...")

    with col_content:
        with st.expander("💡 ڕێنمایی: چۆن دەقەکانم ڕێکبخەم؟ (نموونەکان لێرە ببینە)", expanded=True):
            st.markdown("""
            <div dir="rtl" style="text-align: right;">
            بۆ ئەوەی دیزاینێکی زۆر جوان بەدەست بهێنیت، ئەم نیشانانە <b>لەناو خانەی نووسینەکەی خوارەوە</b> بەکاربهێنە:
            <br><br>
            <b>١. سەردێڕەکان:</b> نیشانەی <code>#</code> بخەرە پێش دێڕەکە.<br>
            <i>دەقەکە بەم شێوەیە بنووسە:</i> <code># ئەمە سەردێڕێکی گەورەیە</code><br><br>
            <b>٢. تۆخکردن:</b> وشەکە بخەرە نێوان دوو ئەستێرە.<br>
            <i>دەقەکە بەم شێوەیە بنووسە:</i> <code>**ئەم وشەیە تۆخە**</code><br><br>
            <b>٣. هایلایت (ڕەنگکردن):</b> وشەکە بخەرە نێوان دوو یەکسان.<br>
            <i>دەقەکە بەم شێوەیە بنووسە:</i> <code>==ئەمە زۆر گرنگە==</code><br><br>
            <b>٤. بڵقی چات (دیالۆگ):</b> ناوی کەسەکە بنووسە و دوو خاڵ دابنێ.<br>
            <i>دەقەکە بەم شێوەیە بنووسە:</i> <code>سیاوش: سلام داداش</code><br><br>
            <b>٥. خشتە:</b> نیشانەی <code>|</code> لە نێوان وشەکان دابنێ.<br>
            <i>دەقەکە بەم شێوەیە بنووسە:</i> <code>| وشە | مانا | پێچەوانە |</code>
            </div>
            """, unsafe_allow_html=True)
            
        raw_text = st.text_area("دەقەکەت لێرە دابنێ (یان لە مۆدی AI بیهێنە):", value=st.session_state.doc_content, height=450, placeholder="دەقەکانت لێرە بنووسە یان پەیستی بکە...\n\nبۆ نموونە:\n# پێشەکی\nئەمە دەقێکی ئاساییە بۆ تاقیکردنەوە...\n\n| ناو | تەمەن |\n| عەلی | ٢٢ |")
        
        if st.button("🚀 بەرهەمهێنانی PDF بە کوالێتی بەرز", type="primary", use_container_width=True):
            if not raw_text.strip():
                st.error("⚠️ تکایە دەقێک بنووسە پێش ئەوەی دروستی بکەیت.")
            else:
                with st.spinner("⏳ مۆتۆڕەکە خەریکی داڕشتنی دیزاینەکانە..."):
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                    
                    if "Mix" in language_dir:
                        dir_attr = "auto"
                        align_attr = "start"
                        alt_align = "end"
                    elif "ڕاست" in language_dir:
                        dir_attr = "rtl"
                        align_attr = "right"
                        alt_align = "left"
                    else:
                        dir_attr = "ltr"
                        align_attr = "left"
                        alt_align = "right"
                    
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
                        line = re.sub(r'\*\*(.*?)\*\*', f'<strong style="color:{t["primary"]}; font-weight:900;">\\1</strong>', line)
                        line = re.sub(r'==(.*?)==', f'<span style="background-color:#fef08a; color:#1f2937; padding:2px 6px; border-radius:4px;">\\1</span>', line)

                        if line.startswith("#"):
                            if in_table:
                                content_blocks += f'<table class="premium-table" dir="{dir_attr}">{table_content}</table>'
                                in_table = False; table_content = ""
                            
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'<div class="premium-header" dir="{dir_attr}"><h2 style="margin:0;">{header_text}</h2></div>'

                        elif "|" in line:
                            if not in_table: in_table = True
                            cells = [c.strip() for c in line.split("|") if c.strip()]
                            row_html = "".join([f'<td>{c}</td>' for c in cells])
                            table_content += f'<tr>{row_html}</tr>'

                        elif (":" in line or "：" in line) and "زمان" in active_theme:
                            if in_table:
                                content_blocks += f'<table class="premium-table" dir="{dir_attr}">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            parts = re.split(r'[:：]', line, maxsplit=1)
                            sp, msg = parts[0].strip(), parts[1].strip()
                            if sp not in speakers: speakers.append(sp)
                            
                            is_alt = (speakers.index(sp) % 2 == 1)
                            
                            # ئەم بەشە نوێیە کێشەی بڕانی پەڕەکانی چارەسەر کرد
                            wrapper_class = "chat-wrapper-alt" if is_alt else "chat-wrapper-normal"
                            bubble_class = "chat-bubble-alt" if is_alt else "chat-bubble"
                            
                            content_blocks += f'''
                            <div class="{wrapper_class}" dir="{dir_attr}">
                                <div class="{bubble_class}">
                                    <div class="chat-name">{sp}</div>
                                    <div class="chat-msg">{msg}</div>
                                </div>
                            </div>
                            '''
                            
                        else:
                            if in_table:
                                content_blocks += f'<table class="premium-table" dir="{dir_attr}">{table_content}</table>'
                                in_table = False; table_content = ""
                                
                            content_blocks += f'<div class="normal-text" dir="{dir_attr}">{line}</div>'
                            
                    if in_table:
                        content_blocks += f'<table class="premium-table" dir="{dir_attr}">{table_content}</table>'

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
                    .chat-wrapper-normal {{
                        text-align: {align_attr};
                        margin-bottom: 20px;
                        page-break-inside: avoid;
                        width: 100%;
                    }}
                    .chat-wrapper-alt {{
                        text-align: {alt_align};
                        margin-bottom: 20px;
                        page-break-inside: avoid;
                        width: 100%;
                    }}
                    .chat-bubble {{
                        display: inline-block;
                        text-align: {align_attr};
                        background-color: {t["chat1"]};
                        padding: 15px 25px;
                        border-radius: 20px;
                        border: 2px solid {t["border"]}50;
                        max-width: 80%;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    }}
                    .chat-bubble-alt {{
                        display: inline-block;
                        text-align: {align_attr};
                        background-color: {t["chat2"]};
                        padding: 15px 25px;
                        border-radius: 20px;
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

                    doc_title = title if title.strip() else "Document"
                    doc_subtitle = subtitle if subtitle.strip() else ""

                    cover_html = f'''
                    <div class="cover-page" dir="{dir_attr}">
                        <div class="cover-box">
                            <div class="cover-title">{doc_title}</div>
                            <div class="cover-subtitle">{doc_subtitle}</div>
                            <div style="margin-top: 40px; font-size: 14pt; color: {t["primary"]}; font-weight: bold;">
                                {datetime.datetime.now().strftime("%Y-%m-%d")}
                            </div>
                        </div>
                    </div>
                    ''' if cover_page else f'<h1 dir="{dir_attr}" style="color:{t["primary"]}; text-align:center; font-size:35pt; border-bottom:3px solid {t["border"]}; padding-bottom:15px;">{doc_title}</h1><h3 dir="{dir_attr}" style="text-align:center; opacity:0.7;">{doc_subtitle}</h3>'

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
                    st.download_button("📥 داگرتنی فایلی PDF", data=pdf_buf.getvalue(), file_name=f"{doc_title.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

with tab_ai:
    st.markdown("### 🤖 دروستکردنی ناوەڕۆک بە ژیری دەستکرد")
    
    with st.expander("ℹ️ چۆنیەتی وەرگرتنی کلیلی تایبەت بە خۆت", expanded=True):
        st.markdown("""
        <div dir="rtl" style="text-align: right; line-height: 1.8;">
        ئەم مۆتۆڕە پێویستی بە کلیلێکی ژیری دەستکرد هەیە بۆ ئەوەی کارەکانت بۆ بکات. ئەم کلیلە بە تەواوی تایبەتە بە خۆت و لە هیچ سێرڤەرێک پاشەکەوت ناکرێت. بۆ وەرگرتنی:
        <br><br>
        ١. بڕۆ بۆ ماڵپەڕی فەرمی (Google AI Studio).<br>
        ٢. بە ئیمەیڵەکەت (Gmail) بچۆ ژوورەوە.<br>
        ٣. کلیک لە دوگمەی دروستکردنی کلیل (Create API key) بکە.<br>
        ٤. کلیلەکە کۆپی بکە و لێرە لە خوارەوە دایبنێ.
        </div>
        """, unsafe_allow_html=True)
        
    user_api_key = st.text_input("🔑 کلیلی تایبەتت (Gemini API Key):", type="password", placeholder="کلیلەکەت لێرە دابنێ...")
    
    ai_input_text = st.text_area("✍️ داواکارییەکەت بنووسە:", placeholder="بۆ نموونە: کورتەیەکم بۆ بنووسە لەسەر سوودەکانی وەرزشکردن، با خشتە و سەردێڕی تێدا بێت...", height=150)
    
    if st.button("✨ داواکردن لە AI و هێنانە ناوەوە", type="primary", use_container_width=True):
        if not user_api_key:
            st.error("⚠️ تکایە سەرەتا کلیلی تایبەتی خۆت دابنێ لە خانەی سەرەوە.")
        elif not ai_input_text.strip():
            st.error("⚠️ تکایە داواکارییەک بنووسە بۆ ئەوەی AI بۆت ئامادە بکات.")
        else:
            with st.spinner("🤖 خەریکی بیرکردنەوە و نووسینە..."):
                try:
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"وەڵامەکەت با زۆر ڕێکخراو بێت. ئەگەر دیالۆگە با شێوازی ناوی کەسەکە و دوو خاڵ بێت وەکو (ناوی کەس: قسەکە). ئەگەر زانیارییە سەردێڕەکان بە # بنووسە و زانیارییە گرنگەکان بکە بە خشتە. \n\nداواکاری: {ai_input_text}")
                    st.session_state.doc_content = response.text
                    st.success("✅ دەقەکە ئامادەیە! ناوەڕۆکەکە خرایە ناو خانەی نووسین لە تابـی 'دروستکردنی PDF'. بڕۆ ئەوێ بۆ دیزاینکردنی.")
                except Exception as e:
                    st.error(f"❌ کێشەیەک ڕوویدا لە بەستنەوە بە AI. دڵنیابە کلیلەکەت ڕاستە. (وردەکاری: {e})")

st.markdown("<br><hr><p style='text-align: center; color: #94a3b8; font-weight: bold;'>بە هیوای سوود © 2026</p>", unsafe_allow_html=True)

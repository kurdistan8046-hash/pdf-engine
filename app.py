import streamlit as st
import streamlit.components.v1 as components
import re
import datetime
import io
import base64
from weasyprint import HTML

st.set_page_config(page_title="PDF Pro Engine", page_icon="📄", layout="wide")

# ناونیشانی سەرەکی
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <h1 style='color: #1e3a8a; font-weight: 900; font-size: 2.5rem;'>PDF Pro Engine</h1>
    <p style='color: #64748b; font-size: 1.1rem; font-weight: bold;'>مۆتۆڕی دروستکردنی فایلی فێرکاری</p>
</div>
<hr style="border: 2px solid #e2e8f0;">
""", unsafe_allow_html=True)

tab_edit, tab_custom, tab_preview = st.tabs(["📝 ١. نووسین و ڕێکخستن", "🎨 ٢. ڕەنگەکان (تایبەت)", "👁️ ٣. پێشبینین و داگرتن"])

# گۆڕاوەکان بۆ دیزاینی تایبەت
with tab_custom:
    st.markdown("### 🎨 ڕەنگەکان بە دڵی خۆت ڕێکبخە")
    st.info("💡 تێبینی: بۆ ئەوەی ئەم ڕەنگانە کار بکەن، دەبێت لە بەشی 'نووسین' قاڵبی **(تایبەت بە خۆم 🎨)** هەڵبژێریت.")
    
    col1, col2, col3 = st.columns(3)
    custom_primary = col1.color_picker("ڕەنگی سەرەکی (هێڵ و سەردێڕ):", "#e11d48")
    custom_bg = col2.color_picker("ڕەنگی پاشخان (Background):", "#fff1f2")
    custom_text = col3.color_picker("ڕەنگی دەق (Text):", "#1e293b")
    
    col4, col5, col6 = st.columns(3)
    custom_chat1 = col4.color_picker("ڕەنگی چاتی کەسی یەکەم:", "#ffe4e6")
    custom_chat2 = col5.color_picker("ڕەنگی چاتی کەسی دووەم:", "#ffffff")
    custom_border = col6.color_picker("ڕەنگی چوارچێوەکان:", "#f43f5e")

with tab_edit:
    col_content, col_settings = st.columns([2, 1])
    
    with col_settings:
        st.markdown("### ⚙️ ڕێکخستنەکان")
        title = st.text_input("📌 ناونیشانی سەرەکی:", value="بابەتی نوێ")
        subtitle = st.text_input("💡 ژێرنووس (پوختە):", value="")
        
        active_theme = st.selectbox("🎨 قاڵب هەڵبژێرە:", [
            "پزیشکی (شین 🩺)", 
            "زمان و چات (سەوز 💬)", 
            "کلاسیک (قاوەیی 📖)",
            "تاریک (Dark Mode 🌙)",
            "سروشتی (سەوز 🌿)",
            "فەرمی (ڕەساسی 🏢)",
            "کچانە (پەمەیی 🌸)",
            "شاهانە (ڕەش و زێڕین 👑)",
            "تایبەت بە خۆم (Custom 🎨)"
        ])
        
        language_dir = st.selectbox("🌐 ئاڕاستەی دەق:", [
            "ڕاست بۆ چەپ (کوردی، عەرەبی...)", 
            "چەپ بۆ ڕاست (English...)",
            "تێکەڵ (Mix - Auto)"
        ])
        
        cover_page = st.checkbox("📄 پەڕەی بەرگ (Cover)", value=True)
        uploaded_logo = st.file_uploader("🖼️ وێنە یان لۆگۆ دابنێ (بۆ سەر پەڕەی بەرگ):", type=['png', 'jpg', 'jpeg'])

    with col_content:
        st.info("💡 **چۆن بنووسم؟** `#` بۆ سەردێڕ | `**تۆخ**` | `==هایلایت==` | `ناوی کەس: قسەکە` بۆ چات | `|یەک|دوو|` بۆ خشتە.")
        raw_text = st.text_area("دەقەکەت لێرە بنووسە یان پەیست بکە:", height=350, placeholder="# پێشەکی\nسڵاو، ئەمە تاقیکردنەوەیە...\n\nمامۆستا: سڵاو قوتابیان\nقوتابی: سڵاو مامۆستا")

# فەنکشنی دروستکردنی HTML (بۆ ئەوەی لە پێشبینین و PDF بەکاربێت)
def generate_html_content():
    if not raw_text.strip():
        return ""
        
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # دیاریکردنی ئاڕاستە
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
    
    # ڕێکخستنی قاڵبەکان
    themes = {
        "پزیشکی (شین 🩺)": {"bg": "#ffffff", "primary": "#0369a1", "text": "#1e293b", "chat1": "#f1f5f9", "chat2": "#e2e8f0", "border": "#0284c7"},
        "زمان و چات (سەوز 💬)": {"bg": "#f0fdf4", "primary": "#166534", "text": "#0f172a", "chat1": "#dcf8c6", "chat2": "#ffffff", "border": "#22c55e"},
        "کلاسیک (قاوەیی 📖)": {"bg": "#fdf8f5", "primary": "#78350f", "text": "#451a03", "chat1": "#fef3c7", "chat2": "#ffedd5", "border": "#d97706"},
        "تاریک (Dark Mode 🌙)": {"bg": "#0f172a", "primary": "#38bdf8", "text": "#f8fafc", "chat1": "#1e293b", "chat2": "#334155", "border": "#0ea5e9"},
        "سروشتی (سەوز 🌿)": {"bg": "#f8fafc", "primary": "#15803d", "text": "#1e293b", "chat1": "#dcfce3", "chat2": "#f1f5f9", "border": "#16a34a"},
        "فەرمی (ڕەساسی 🏢)": {"bg": "#ffffff", "primary": "#334155", "text": "#0f172a", "chat1": "#f8fafc", "chat2": "#e2e8f0", "border": "#64748b"},
        "کچانە (پەمەیی 🌸)": {"bg": "#fdf2f8", "primary": "#be185d", "text": "#4c1d95", "chat1": "#fce7f3", "chat2": "#ffffff", "border": "#db2777"},
        "شاهانە (ڕەش و زێڕین 👑)": {"bg": "#171717", "primary": "#fbbf24", "text": "#fef3c7", "chat1": "#262626", "chat2": "#404040", "border": "#d97706"},
        "تایبەت بە خۆم (Custom 🎨)": {"bg": custom_bg, "primary": custom_primary, "text": custom_text, "chat1": custom_chat1, "chat2": custom_chat2, "border": custom_border}
    }
    
    t = themes[active_theme]
    
    # ئامادەکردنی وێنەکە ئەگەر هەبێت
    logo_html = ""
    if uploaded_logo:
        encoded_image = base64.b64encode(uploaded_logo.read()).decode()
        img_type = uploaded_logo.name.split('.')[-1]
        logo_html = f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/{img_type};base64,{encoded_image}" style="max-height: 150px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></div>'
        uploaded_logo.seek(0) # گەڕاندنەوە بۆ ئەوەی دواتر بخوێندرێتەوە
    
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

        elif ":" in line or "：" in line:
            if in_table:
                content_blocks += f'<table class="premium-table" dir="{dir_attr}">{table_content}</table>'
                in_table = False; table_content = ""
                
            parts = re.split(r'[:：]', line, maxsplit=1)
            sp, msg = parts[0].strip(), parts[1].strip()
            if sp not in speakers: speakers.append(sp)
            
            is_alt = (speakers.index(sp) % 2 == 1)
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
            font-family: 'Amiri', Tahoma, sans-serif;
            font-size: 12pt;
            color: {t["primary"]};
        }}
    }}
    body {{
        font-family: 'Amiri', Tahoma, sans-serif;
        direction: {dir_attr};
        text-align: {align_attr};
        color: {t["text"]};
        font-size: 16pt;
        line-height: 2.0;
        background-color: {t["bg"]};
        margin: 0; padding: 20px;
    }}
    .cover-page {{
        text-align: center;
        margin-top: 20%;
        page-break-after: always;
    }}
    .cover-box {{
        display: inline-block;
        padding: 50px 80px;
        border: 4px solid {t["primary"]};
        border-radius: 20px;
        background-color: {t["bg"]};
        box-shadow: 8px 8px 0px {t["border"]}50;
    }}
    .cover-title {{
        font-size: 40pt;
        color: {t["primary"]};
        border-bottom: 4px solid {t["border"]};
        padding-bottom: 20px;
        margin-bottom: 20px;
        font-weight: 900;
    }}
    .cover-subtitle {{
        font-size: 20pt;
        color: {t["text"]};
        opacity: 0.9;
    }}
    .premium-header {{
        background-color: {t["primary"]}15;
        padding: 15px;
        border-radius: 10px;
        border-{align_attr}: 6px solid {t["primary"]};
        margin: 30px 0 15px 0;
        color: {t["primary"]};
        page-break-after: avoid;
    }}
    .chat-wrapper-normal {{ text-align: {align_attr}; margin-bottom: 15px; width: 100%; }}
    .chat-wrapper-alt {{ text-align: {alt_align}; margin-bottom: 15px; width: 100%; }}
    .chat-bubble {{
        display: inline-block; text-align: {align_attr}; background-color: {t["chat1"]};
        padding: 12px 20px; border-radius: 20px; border: 1px solid {t["border"]}50; max-width: 80%;
    }}
    .chat-bubble-alt {{
        display: inline-block; text-align: {align_attr}; background-color: {t["chat2"]};
        padding: 12px 20px; border-radius: 20px; border: 1px solid {t["border"]}50; max-width: 80%;
    }}
    .chat-name {{ font-weight: 900; color: {t["primary"]}; font-size: 12pt; margin-bottom: 5px; }}
    .chat-msg {{ font-size: 16pt; color: {t["text"]}; }}
    .normal-text {{ margin-bottom: 15px; }}
    .premium-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: {t["chat2"]}; border-radius: 8px; overflow: hidden; border: 2px solid {t["primary"]}; }}
    .premium-table td {{ border: 1px solid {t["border"]}50; padding: 12px; text-align: center; }}
    .premium-table tr:nth-child(even) {{ background-color: {t["chat1"]}; }}
    """

    cover_html = f'''
    <div class="cover-page" dir="{dir_attr}">
        {logo_html}
        <div class="cover-box">
            <div class="cover-title">{title}</div>
            <div class="cover-subtitle">{subtitle}</div>
            <div style="margin-top: 30px; font-size: 12pt; color: {t["primary"]}; font-weight: bold;">
                {datetime.datetime.now().strftime("%Y-%m-%d")}
            </div>
        </div>
    </div>
    ''' if cover_page else f'{logo_html}<h1 dir="{dir_attr}" style="color:{t["primary"]}; text-align:center; font-size:30pt; border-bottom:3px solid {t["border"]}; padding-bottom:15px;">{title}</h1><h3 dir="{dir_attr}" style="text-align:center; opacity:0.8;">{subtitle}</h3>'

    final_html = f"""
    <!DOCTYPE html>
    <html dir="{dir_attr}">
    <head>
        <meta charset="utf-8">
        <style>{css_string}</style>
    </head>
    <body>
        {cover_html}
        <div>{content_blocks}</div>
    </body>
    </html>
    """
    return final_html

# تابـی سێیەم بۆ پێشبینین و داگرتن
with tab_preview:
    if raw_text.strip():
        generated_html = generate_html_content()
        
        col_down, col_info = st.columns([1, 2])
        with col_down:
            st.markdown("### 📥 داگرتنی فایلەکە")
            if st.button("🚀 دروستکردنی PDF", type="primary", use_container_width=True):
                with st.spinner("⏳ مۆتۆڕەکە خەریکی دروستکردنی فایلەکەیە..."):
                    pdf_buf = io.BytesIO()
                    HTML(string=generated_html).write_pdf(target=pdf_buf)
                    st.success("✅ فایلەکەت ئامادەیە!")
                    st.download_button("⬇️ لێرە کلیک بکە بۆ داگرتن", data=pdf_buf.getvalue(), file_name=f"{title.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
                    
        with col_info:
            st.markdown("### 👁️ پێشبینینی شاشە (Preview)")
            st.info("ئەمەی خوارەوە شێوەی ڕاستەقینەی دیزاینەکەتە. ئەگەر بە دڵت نییە بڕۆوە تابـی یەکەم دەستکاری بکە.")
        
        # پیشاندانی ناوەڕۆک بە شێوەی لایڤ
        components.html(generated_html, height=700, scrolling=True)
    else:
        st.warning("⚠️ تکایە لە تابـی 'نووسین' دەقێک بنووسە بۆ ئەوەی لێرە پێشبینینەکەی ببینیت.")

st.markdown("<br><hr><p style='text-align: center; color: #94a3b8; font-weight: bold;'>بە هیوای سوود © 2026</p>", unsafe_allow_html=True)

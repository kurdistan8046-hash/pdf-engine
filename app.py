import streamlit as st
import re
import datetime
from weasyprint import HTML

st.set_page_config(page_title="PDF Pro Engine", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>✨ مۆتۆڕی زیرەکی دروستکردنی PDF</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 30px;'>سیستەمی پێشکەوتوو بۆ گۆڕینی دەق بۆ PDF لە هەموو بوارەکاندا</p>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### ⚙️ ڕێکخستنەکان")
    title = st.text_input("📌 ناونیشان:", "بەڵگەنامەی فەرمی")
    subtitle = st.text_input("💡 ژێرنووس:", "")
    
    language_dir = st.selectbox("🌐 زمانی نووسین:", ["ڕاست بۆ چەپ (کوردی، عەرەبی)", "چەپ بۆ ڕاست (English)"])
    theme = st.selectbox("🎨 دیزاین:", ["زیرەک (AI)", "گشتی و فەرمی (ڕەساسی)", "پزیشکی و زانستی (شین)", "گفتوگۆ و زمان (مۆر)", "کلاسیک و ئەدەبی (قاوەیی)"])
    
    cover_page = st.checkbox("📄 دروستکردنی پەڕەی بەرگ", value=True)
    show_flag = st.checkbox("☀️ دانانی ئاڵای کوردستان (لۆگۆ)", value=True)
    
    watermark = st.text_input("🔏 هێمای ئاو:", "")
    footer = st.text_input("🔻 فۆتەر:", "بەرهەمهێنراو بە مۆتۆڕی زیرەک")

with col1:
    st.markdown("### 📝 ناوەڕۆک")
    st.info("تێبینی: ئەگەر دەتەوێت سەردێڕی گەورە دروست بکەیت، نیشانەی # بخەرە پێش نووسینەکە.")
    raw_text = st.text_area("دەقەکەت لێرە دابنێ:", height=400)
    
    if st.button("🚀 دروستکردن و داگرتنی PDF", use_container_width=True):
        if not raw_text.strip():
            st.error("⚠️ تکایە دەقێک لە خانەی ناوەڕۆکدا بنووسە.")
        else:
            with st.spinner("مۆتۆڕەکە خەریکی داڕشتنی دیزاینە... ⏳"):
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                
                is_dialogue = sum(1 for line in lines if ":" in line or "：" in line) > len(lines) * 0.3
                is_medical = any(w in raw_text.lower() for w in ['نەخۆش', 'پزیشک', 'چارەسەر', 'دەرمان', 'patient', 'medical', 'treatment', 'disease', 'surgery', 'clinic'])
                is_poetry = all(len(line.split()) < 8 for line in lines) and len(lines) > 4
                
                active_theme = theme
                if theme == "زیرەک (AI)":
                    if is_medical: active_theme = "پزیشکی و زانستی (شین)"
                    elif is_dialogue: active_theme = "گفتوگۆ و زمان (مۆر)"
                    elif is_poetry: active_theme = "کلاسیک و ئەدەبی (قاوەیی)"
                    else: active_theme = "گشتی و فەرمی (ڕەساسی)"

                themes_dict = {
                    "گشتی و فەرمی (ڕەساسی)": {"primary": "#334155", "bg": "#f8fafc", "card": "#ffffff", "border": "#64748b", "accent": "#e2e8f0"},
                    "پزیشکی و زانستی (شین)": {"primary": "#0369a1", "bg": "#f0f9ff", "card": "#ffffff", "border": "#0ea5e9", "accent": "#bae6fd"},
                    "گفتوگۆ و زمان (مۆر)": {"primary": "#6d28d9", "bg": "#f5f3ff", "card": "#ffffff", "border": "#8b5cf6", "accent": "#ddd6fe"},
                    "کلاسیک و ئەدەبی (قاوەیی)": {"primary": "#92400e", "bg": "#fefce8", "card": "#ffffff", "border": "#d97706", "accent": "#fde68a"}
                }
                t_style = themes_dict.get(active_theme, themes_dict["گشتی و فەرمی (ڕەساسی)"])
                
                is_rtl = "ڕاست" in language_dir
                dir_attr = "rtl" if is_rtl else "ltr"
                align_attr = "right" if is_rtl else "left"
                alt_align = "left" if is_rtl else "right"
                lang_code = "ckb" if is_rtl else "en"
                
                content_blocks = ""
                speakers = []
                
                if active_theme == "گفتوگۆ و زمان (مۆر)":
                    for line in lines:
                        if ":" in line or "：" in line:
                            sp = re.split(r'[:：]', line, maxsplit=1)[0].strip()
                            if sp not in speakers: speakers.append(sp)
                            
                    for line in lines:
                        if line.startswith("#"):
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'<h2 style="color: {t_style["primary"]}; border-bottom: 2px solid {t_style["accent"]}; padding-bottom: 10px; margin-top: 20px;">{header_text}</h2>'
                        elif ":" in line or "：" in line:
                            parts = re.split(r'[:：]', line, maxsplit=1)
                            sp, msg = parts[0].strip(), parts[1].strip()
                            is_alt = (speakers.index(sp) % 2 == 1)
                            
                            if is_alt:
                                bubble_css = f"float: {alt_align}; background: #f8fafc; border-{align_attr}: 5px solid {t_style['border']};"
                            else:
                                bubble_css = f"float: {align_attr}; background: {t_style['bg']}; border-{align_attr}: 5px solid {t_style['primary']};"
                                
                            content_blocks += f'''
                            <div style="width: 100%; clear: both; margin-bottom: 20px; overflow: hidden; page-break-inside: avoid;">
                                <div style="width: 75%; {bubble_css} padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                    <span style="display: block; font-weight: bold; color: {t_style['primary']}; margin-bottom: 8px; font-size: 12pt;">{sp}</span>
                                    <p style="margin: 0; font-size: 15pt; line-height: 1.8; color: #1e293b;">{msg}</p>
                                </div>
                            </div>
                            '''
                        else:
                            content_blocks += f'<div style="width: 100%; clear: both; margin-bottom: 15px;"><div style="background:{t_style["card"]}; padding:15px; border-radius:10px; border-{align_attr}:4px solid {t_style["border"]};"><p style="margin:0; font-size:15pt; line-height:1.8;">{line}</p></div></div>'
                else:
                    for line in lines:
                        if line.startswith("#"):
                            header_text = line.replace("#", "").strip()
                            content_blocks += f'''
                            <div style="background: {t_style["accent"]}; padding: 15px 20px; border-radius: 8px; margin: 30px 0 15px 0; border-{align_attr}: 6px solid {t_style["primary"]}; page-break-after: avoid;">
                                <h2 style="margin: 0; color: {t_style["primary"]}; font-size: 20pt;">{header_text}</h2>
                            </div>
                            '''
                        else:
                            content_blocks += f'''
                            <div style="background:{t_style["card"]}; padding:20px; border-radius:10px; margin-bottom:15px; border-{align_attr}:4px solid {t_style["accent"]}; box-shadow: 0 2px 5px rgba(0,0,0,0.03); page-break-inside:avoid;">
                                <p style="margin:0; font-size:15pt; line-height:2.0; color: #334155; text-align: {align_attr};">{line}</p>
                            </div>
                            '''

                # دروستکردنی لۆگۆی ئاڵای کوردستان (SVG)
                flag_html = ""
                if show_flag:
                    flag_svg = """
                    <svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="width: 55px; height: auto; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.15); border: 1px solid rgba(0,0,0,0.05);">
                        <rect width="300" height="66.6" fill="#ED2024"/>
                        <rect y="66.6" width="300" height="66.6" fill="#FFFFFF"/>
                        <rect y="133.2" width="300" height="66.8" fill="#278E43"/>
                        <g transform="translate(150, 100)">
                            <circle r="22" fill="#FEBD11"/>
                            <path d="M 0 -35 L 4 -22 L 15 -32 L 9 -19 L 26 -20 L 15 -11 L 33 -5 L 20 0 L 33 5 L 15 11 L 26 20 L 9 19 L 15 32 L 4 22 L 0 35 L -4 22 L -15 32 L -9 19 L -26 20 L -15 11 L -33 5 L -20 0 L -33 -5 L -15 -11 L -26 -20 L -9 -19 L -15 -32 L -4 -22 Z" fill="#FEBD11"/>
                        </g>
                    </svg>
                    """
                    flag_html = f'<div style="position: fixed; top: -50px; {alt_align}: -10px; z-index: 1000;">{flag_svg}</div>'

                cover_html = f'''
                <div style="text-align: center; margin-top: 30%; page-break-after: always;">
                    <div style="display: inline-block; padding: 40px; border: 2px solid {t_style["accent"]}; border-radius: 20px; background: {t_style["card"]}; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                        <h1 style="font-size: 42pt; color: {t_style["primary"]}; border-bottom: 4px solid {t_style["border"]}; padding-bottom: 20px; margin-bottom: 25px;">{title}</h1>
                        <p style="font-size: 22pt; color: #475569; margin-bottom: 40px;">{subtitle}</p>
                        <div style="display: inline-block; padding: 10px 25px; background: {t_style["bg"]}; border-radius: 30px; font-size: 14pt; color: {t_style["primary"]}; font-weight:bold;">{datetime.datetime.now().strftime("%Y-%m-%d")}</div>
                    </div>
                </div>
                ''' if cover_page else ""
                
                header_html = f'''
                <div style="border-{align_attr}: 8px solid {t_style["primary"]}; padding: 20px 25px; margin-bottom: 40px; background: {t_style["bg"]}; border-radius: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 style="margin: 0; color: {t_style["primary"]}; font-size: 26pt;">{title}</h1>
                        <p style="margin: 10px 0 0 0; color: #475569; font-size: 16pt;">{subtitle}</p>
                    </div>
                </div>
                ''' if not cover_page else ""
                
                watermark_html = f'<div style="position: fixed; top: 45%; left: 20%; transform: rotate(-45deg); font-size: 70pt; color: {t_style["primary"]}; opacity: 0.05; z-index: -1; white-space: nowrap;">{watermark}</div>' if watermark else ""

                final_html = f"""
                <!DOCTYPE html>
                <html dir="{dir_attr}" lang="{lang_code}">
                <head>
                <meta charset="utf-8">
                <style>
                @page {{
                    size: A4; margin: 25mm 20mm; background-color: {t_style["bg"]};
                    @bottom-{align_attr} {{ content: counter(page) " / " counter(pages); font-family: 'Amiri', sans-serif; font-size: 11pt; color: #94a3b8; font-weight: bold; }}
                    @bottom-{alt_align} {{ content: "{footer}"; font-family: 'Amiri', sans-serif; font-size: 11pt; color: #94a3b8; font-weight: bold; }}
                }}
                body {{ font-family: 'Amiri', Tahoma, sans-serif; direction: {dir_attr}; text-align: {align_attr}; color: #1e293b; margin: 0; padding: 0; line-height: 1.6; }}
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
                    
                st.success("✅ ئامادەیە! فایلەکەت بە کوالێتی بەرز دروستکرا.")
                st.download_button(label="📥 داگرتنی بەڵگەنامەکە", data=pdf_data, file_name=output_file, mime="application/pdf", use_container_width=True)

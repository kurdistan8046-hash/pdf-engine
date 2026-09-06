import streamlit as st
import re
import datetime
from weasyprint import HTML

st.set_page_config(page_title="PDF Pro Engine", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>✨ مۆتۆڕی زیرەکی دروستکردنی PDF</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 30px;'>سیستەمی پێشکەوتوو بۆ گۆڕینی دەق بۆ PDF</p>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### ⚙️ ڕێکخستنەکان")
    title = st.text_input("📌 ناونیشان:", "بەڵگەنامەی فەرمی")
    subtitle = st.text_input("💡 ژێرنووس:", "")
    theme = st.selectbox("🎨 دیزاین:", ["زیرەک (AI)", "پزیشکی و زانستی (شین)", "گفتوگۆ و زمان (مۆر)", "کلاسیک و ئەدەبی (قاوەیی)"])
    cover_page = st.checkbox("📄 دروستکردنی پەڕەی بەرگ")
    watermark = st.text_input("🔏 هێمای ئاو:", "")
    footer = st.text_input("🔻 فۆتەر:", "بەرهەمهێنراو بە سیستەمی زیرەک")

with col1:
    st.markdown("### 📝 ناوەڕۆک")
    raw_text = st.text_area("دەقەکەت لێرە دابنێ:", height=350)

if st.button("🚀 دروستکردن و داگرتنی PDF", use_container_width=True):
    if not raw_text.strip():
        st.error("⚠️ تکایە دەقێک لە خانەی ناوەڕۆکدا بنووسە.")
    else:
        with st.spinner("مۆتۆڕەکە خەریکی داڕشتنی دیزاینە... ⏳"):
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            is_dialogue = sum(1 for line in lines if ":" in line or "：" in line) > len(lines) * 0.3
            is_medical = any(w in raw_text.lower() for w in ['نەخۆش', 'پزیشک', 'چارەسەر', 'دەرمان', 'patient'])
            is_poetry = all(len(line.split()) < 8 for line in lines) and len(lines) > 4

            active_theme = theme
            if theme == "زیرەک (AI)":
                if is_medical: active_theme = "پزیشکی و زانستی (شین)"
                elif is_dialogue: active_theme = "گفتوگۆ و زمان (مۆر)"
                elif is_poetry: active_theme = "کلاسیک و ئەدەبی (قاوەیی)"
                else: active_theme = "پزیشکی و زانستی (شین)"

            themes_dict = {
                "پزیشکی و زانستی (شین)": {"primary": "#0369a1", "bg": "#f8fafc", "card": "#ffffff", "border": "#0284c7"},
                "گفتوگۆ و زمان (مۆر)": {"primary": "#5b21b6", "bg": "#fdf8ff", "card": "#ffffff", "border": "#8b5cf6"},
                "کلاسیک و ئەدەبی (قاوەیی)": {"primary": "#78350f", "bg": "#fefce8", "card": "#fffbeb", "border": "#d97706"}
            }
            t_style = themes_dict.get(active_theme, themes_dict["پزیشکی و زانستی (شین)"])

            content_blocks = ""
            speakers = []
            
            if is_dialogue or active_theme == "گفتوگۆ و زمان (مۆر)":
                for line in lines:
                    if ":" in line or "：" in line:
                        sp = re.split(r'[:：]', line, maxsplit=1)[0].strip()
                        if sp not in speakers: speakers.append(sp)
                
                for line in lines:
                    if ":" in line or "：" in line:
                        parts = re.split(r'[:：]', line, maxsplit=1)
                        sp, msg = parts[0].strip(), parts[1].strip()
                        is_alt = (speakers.index(sp) % 2 == 1)
                        alt_css = f"border-right: 5px solid {t_style['primary']}; margin-right: 15%; background: rgba(0,0,0,0.02);" if is_alt else f"border-right: 5px solid {t_style['border']}; margin-left: 15%;"
                        content_blocks += f'<div style="background:{t_style["card"]}; padding:15px; border-radius:12px; margin-bottom:12px; {alt_css} page-break-inside:avoid;"><span style="display:block; font-weight:bold; color:{t_style["primary"]}; margin-bottom:5px; font-size:13pt;">{sp}</span><p style="margin:0; font-size:15pt; line-height:1.8;">{msg}</p></div>'
                    else:
                        content_blocks += f'<div style="background:{t_style["card"]}; padding:15px; border-radius:10px; margin-bottom:12px; border-right:4px solid {t_style["border"]}; page-break-inside:avoid;"><p style="margin:0; font-size:15pt; line-height:1.8;">{line}</p></div>'
            else:
                for line in lines:
                    content_blocks += f'<div style="background:{t_style["card"]}; padding:20px; border-radius:10px; margin-bottom:15px; border-right:5px solid {t_style["border"]}; page-break-inside:avoid;"><p style="margin:0; font-size:15pt; line-height:2.0;">{line}</p></div>'

            cover_html = f'<div style="height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; page-break-after: always;"><h1 style="font-size: 45pt; color: {t_style["primary"]}; border-bottom: 5px solid {t_style["border"]}; padding-bottom: 15px; margin-bottom:20px;">{title}</h1><p style="font-size: 20pt; color: #475569;">{subtitle}</p><div style="margin-top: 60px; font-size: 14pt; color: #94a3b8; font-weight:bold;">{datetime.datetime.now().strftime("%Y-%m-%d")}</div></div>' if cover_page else ""
            header_html = f'<div style="border-right: 8px solid {t_style["border"]}; padding: 20px; margin-bottom: 35px; background: {t_style["card"]}; border-radius: 10px;"><h1 style="margin: 0; color: {t_style["primary"]}; font-size: 26pt;">{title}</h1><p style="margin: 10px 0 0 0; color: #475569; font-size: 16pt;">{subtitle}</p></div>' if not cover_page else ""
            watermark_html = f'<div style="position: fixed; top: 40%; left: 25%; transform: rotate(-45deg); font-size: 80pt; color: {t_style["primary"]}; opacity: 0.04; z-index: -1;">{watermark}</div>' if watermark else ""

            final_html = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
            <meta charset="utf-8">
            <style>
              @page {{
                size: A4; margin: 20mm; background-color: {t_style["bg"]};
                @bottom-left {{ content: counter(page) " / " counter(pages); font-family: 'Amiri', sans-serif; font-size: 11pt; color: #64748b; font-weight: bold; }}
                @bottom-right {{ content: "{footer}"; font-family: 'Amiri', sans-serif; font-size: 11pt; color: #64748b; font-weight: bold; }}
              }}
              body {{ font-family: 'Amiri', sans-serif; direction: rtl; color: #1e293b; margin: 0; padding: 0; }}
            </style>
            </head>
            <body>
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

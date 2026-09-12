import base64
from pathlib import Path

import streamlit as st

from services.ai import (
    generate_personalized_quiz,
    get_available_models,
)
from services.worksheet_pdf import generate_worksheet_pdf
from utils.ui import apply_global_css

st.set_page_config(
    page_title="پنل معلم",
    page_icon=None,
    layout="wide",
)

apply_global_css()


def load_font(filename: str) -> str:
    font_path = Path("fonts") / filename
    return base64.b64encode(font_path.read_bytes()).decode()


regular_font = load_font("YekanBakh-Regular.woff")
bold_font = load_font("YekanBakh-Bold.woff")
semibold_font = load_font("YekanBakh-SemiBold.woff")

st.markdown(
    """
        <style>
            input,
            textarea {
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl !important;
                text-align: right !important;
            }

            input::placeholder,
            textarea::placeholder {
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl !important;
                text-align: right !important;
            }
 </style>""",
    unsafe_allow_html=True,
)

st.title("پنل معلم")
st.write("برای هر دانش‌آموز یک کاربرگ تمرینی شخصی‌سازی‌شده بسازید.")


# -------------------------
# Student information
# -------------------------

st.title("مشخصات دانش‌آموز")

student_name = st.text_input(
    "نام دانش‌آموز",
    placeholder="مثلاً سارا",
)

education_level = st.selectbox(
    "پایه تحصیلی",
    ["اول", "دوم", "سوم", "چهارم", "پنجم", "ششم"],
)

subject = st.selectbox(
    "درس",
    ["ریاضی", "فارسی", "علوم"],
)


# -------------------------
# Weaknesses
# -------------------------

st.title("ضعف‌های دانش‌آموز")

weaknesses = st.text_area(
    "ضعف‌ها و مهارت‌هایی که نیاز به تمرین دارند",
    placeholder=(
        "مثلاً:\n"
        "مفهوم تقسیم مساوی را خوب متوجه نشده است.\n"
        "در حل مسئله‌های تقسیم دچار مشکل می‌شود.\n"
        "در تشخیص اینکه چه زمانی باید از تقسیم استفاده کند مشکل دارد."
    ),
    height=160,
)

teacher_notes = st.text_area(
    "توضیحات معلم",
    placeholder=(
        "مثلاً دانش‌آموز محاسبه‌های ساده را انجام می‌دهد "
        "اما در مسئله‌های کلامی نیاز به تمرین بیشتری دارد."
    ),
    height=120,
)


# -------------------------
# Worksheet settings
# -------------------------

st.title("تنظیمات کاربرگ")

question_count = st.slider(
    "تعداد سؤال",
    min_value=5,
    max_value=10,
    value=6,
)


# -------------------------
# Model
# -------------------------

available_models = get_available_models()

if not available_models:
    st.error("هیچ مدل Ollama پیدا نشد.")
    st.stop()

model_name = st.selectbox(
    "مدل",
    available_models,
)


# -------------------------
# Generate
# -------------------------

if st.button(
    "ساخت کاربرگ شخصی‌سازی‌شده",
    type="primary",
):

    if not weaknesses.strip():
        st.warning("ابتدا ضعف‌های دانش‌آموز را وارد کنید.")
        st.stop()

    with st.spinner("در حال طراحی کاربرگ..."):

        try:
            quiz_data = generate_personalized_quiz(
                model_name=model_name,
                education_level=education_level,
                subject=subject,
                weaknesses=weaknesses,
                teacher_notes=teacher_notes,
                question_count=question_count,
            )

            pdf_bytes = generate_worksheet_pdf(quiz_data)

            st.session_state.teacher_quiz = quiz_data
            st.session_state.teacher_pdf = pdf_bytes

            st.success("کاربرگ با موفقیت ساخته شد.")

        except Exception as e:
            st.error(f"ساخت کاربرگ با خطا مواجه شد: {e}")


# -------------------------
# Preview
# -------------------------

if "teacher_quiz" in st.session_state:

    st.divider()

    st.header("پیش‌نمایش سؤال‌ها")

    quiz_data = st.session_state.teacher_quiz

    for question in quiz_data.get("questions", []):

        st.markdown(f"**{question['id']}. {question['question']}**")

        st.caption(
            f"مهارت: {question.get('target_weakness', '')} | "
            f"سطح: {question.get('difficulty', '')}"
        )

        if "options" in question:
            for option in question["options"]:
                st.write(f"- {option}")

        st.write("")


# -------------------------
# Download
# -------------------------

if "teacher_pdf" in st.session_state:

    st.download_button(
        label="دانلود کاربرگ",
        data=st.session_state.teacher_pdf,
        file_name="کاربرگ-شخصی‌سازی‌شده.pdf",
        mime="application/pdf",
    )

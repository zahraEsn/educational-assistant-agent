import base64
from pathlib import Path

import streamlit as st

from services.ai import (
    generate_personalized_quiz,
    get_available_models,
)
from services.worksheet_pdf import generate_worksheet_pdf


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
    placeholder="مثلاً علی شعبانی",
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

            # اطمینان از وجود فیلد راهنمایی برای هر سؤال
            for question in quiz_data.get("questions", []):
                question.setdefault("hint", "")

            st.session_state.teacher_quiz = quiz_data

            # PDF قبلی را حذف کن تا فقط نسخه ویرایش‌شده ساخته شود
            st.session_state.pop("teacher_pdf", None)

            st.success(
                "کاربرگ اولیه با موفقیت ساخته شد. اکنون می‌توانید سؤال‌ها را ویرایش کنید."
            )

        except Exception as e:
            st.error(f"ساخت کاربرگ با خطا مواجه شد: {e}")


# -------------------------
# Edit / Preview
# -------------------------

if "teacher_quiz" in st.session_state:

    st.divider()

    st.header("ویرایش و پیش‌نمایش سؤال‌ها")

    quiz_data = st.session_state.teacher_quiz

    edited_questions = []

    with st.form("edit_worksheet_form"):

        for index, question in enumerate(quiz_data.get("questions", [])):

            st.subheader(f"سؤال {index + 1}")

            st.caption(
                f"مهارت: {question.get('target_weakness', '')} | "
                f"سطح: {question.get('difficulty', '')}"
            )

            edited_question = st.text_area(
                "متن سؤال",
                value=question.get("question", ""),
                height=100,
                key=f"question_{index}",
            )

            edited_hint = st.text_area(
                "راهنمایی سؤال",
                value=question.get("hint", ""),
                height=80,
                key=f"hint_{index}",
            )

            if "options" in question:

                st.markdown("گزینه‌ها")

                edited_options = []

                for option_index, option in enumerate(question["options"]):

                    edited_option = st.text_input(
                        f"گزینه {option_index + 1}",
                        value=str(option),
                        key=f"option_{index}_{option_index}",
                    )

                    edited_options.append(edited_option)

            else:
                edited_options = None

            edited_question_data = {
                **question,
                "question": edited_question,
                "hint": edited_hint,
            }

            if edited_options is not None:
                edited_question_data["options"] = edited_options

            edited_questions.append(edited_question_data)

            st.divider()

        submitted = st.form_submit_button(
            "ذخیره تغییرات و ساخت کاربرگ",
            type="primary",
        )

    if submitted:

        updated_quiz = {
            **quiz_data,
            "questions": edited_questions,
        }

        pdf_bytes = generate_worksheet_pdf(updated_quiz)

        st.session_state.teacher_quiz = updated_quiz
        st.session_state.teacher_pdf = pdf_bytes

        st.success("تغییرات ذخیره شد و نسخه نهایی کاربرگ ساخته شد.")

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

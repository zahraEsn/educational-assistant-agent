import streamlit as st

from utils.ui import apply_global_css

st.set_page_config(
    page_title="داشبورد",
    page_icon=None,
    layout="wide",
)

apply_global_css()


# =========================
# Dashboard
# =========================


def show_dashboard():
    st.title("داشبورد")

    st.write("به سامانه آموزشی خوش آمدید.")

    st.write("لطفاً بخش موردنظر خود را انتخاب کنید.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("پنل دانش‌آموز")

        st.write(
            "در این بخش می‌توانید با دستیار آموزشی "
            "تمرین کنید، سؤال بپرسید و آزمون بگیرید."
        )

        if st.button(
            "ورود به پنل دانش‌آموز",
            use_container_width=True,
        ):
            st.switch_page(student_page)

    with col2:
        st.subheader("پنل معلم")

        st.write(
            "در این بخش می‌توانید برای هر دانش‌آموز "
            "کاربرگ تمرینی شخصی‌سازی‌شده بسازید."
        )

        if st.button(
            "ورود به پنل معلم",
            use_container_width=True,
        ):
            st.switch_page(teacher_page)


# =========================
# Pages
# =========================

dashboard_page = st.Page(
    show_dashboard,
    title="داشبورد",
    url_path="dashboard",
    default=True,
)

student_page = st.Page(
    "pages/پنل_دانش‌آموز.py",
    title="پنل دانش‌آموز",
    url_path="student",
)

teacher_page = st.Page(
    "pages/پنل_معلم.py",
    title="پنل معلم",
    url_path="teacher",
)


# =========================
# Navigation
# =========================

page = st.navigation(
    [
        dashboard_page,
        student_page,
        teacher_page,
    ]
)

page.run()

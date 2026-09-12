import base64
from pathlib import Path

import streamlit as st


def load_font(filename: str) -> str:
    font_path = Path("fonts") / filename
    return base64.b64encode(font_path.read_bytes()).decode()


def apply_global_css() -> None:
    regular_font = load_font("YekanBakh-Regular.woff")
    bold_font = load_font("YekanBakh-Bold.woff")
    semibold_font = load_font("YekanBakh-SemiBold.woff")

    st.markdown(
        f"""
        <style>

            /* =========================
               Fonts
            ========================= */

            @font-face {{
                font-family: 'Yekan Bakh';
                src: url(data:font/woff;base64,{regular_font}) format('woff');
                font-weight: 400;
            }}

            @font-face {{
                font-family: 'Yekan Bakh';
                src: url(data:font/woff;base64,{semibold_font}) format('woff');
                font-weight: 600;
            }}

            @font-face {{
                font-family: 'Yekan Bakh';
                src: url(data:font/woff;base64,{bold_font}) format('woff');
                font-weight: 700;
            }}


            /* =========================
               Main app
            ========================= */

            .stApp {{
                direction: rtl;
            }}

            .stApp,
            .stApp * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               RTL
            ========================= */

            .stApp {{
                text-align: right;
            }}

            .stApp p,
            .stApp span,
            .stApp div,
            .stApp label,
            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp h5,
            .stApp h6 {{
                direction: rtl;
                text-align: right;
            }}


            /* =========================
               Title / Header
            ========================= */

            [data-testid="stTitle"],
            [data-testid="stHeader"],
            [data-testid="stHeadingWithActionElements"],
            div.stHeading,
            div.stHeading * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               Markdown
            ========================= */

            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl;
                text-align: right;
            }}


            /* =========================
               Widget labels
            ========================= */

            [data-testid="stWidgetLabel"],
            [data-testid="stWidgetLabel"] *,
            [data-testid="stWidgetLabelHelp"],
            [data-testid="stWidgetLabelHelp"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl;
                text-align: right;
            }}


            /* =========================
               Input
            ========================= */

            input,
            textarea {{
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl !important;
                text-align: right !important;
            }}

            input::placeholder,
            textarea::placeholder {{
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl !important;
                text-align: right !important;
            }}


            /* =========================
               Selectbox
            ========================= */

            div[data-baseweb="select"],
            div[data-baseweb="select"] *,
            div[role="option"] {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}

            div[data-baseweb="select"] {{
                direction: rtl;
            }}


            /* =========================
               Slider
            ========================= */

            [data-testid="stSlider"],
            [data-testid="stSlider"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               Buttons
            ========================= */

            button,
            button * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               Caption
            ========================= */

            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               Sidebar
            ========================= */

            section[data-testid="stSidebar"] {{
                direction: rtl;
            }}

            section[data-testid="stSidebar"],
            section[data-testid="stSidebar"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
            }}


            /* =========================
               Chat
            ========================= */

            [data-testid="stChatMessageContent"],
            [data-testid="stChatMessageContent"] * {{
                font-family: 'Yekan Bakh', sans-serif !important;
                direction: rtl;
                text-align: right;
            }}


            /* =========================
               Material icons
               ========================= */

            .material-symbols-rounded,
            .material-symbols-outlined,
            .material-icons,
            [data-testid="stSidebarCollapseButton"] span {{
                font-family:
                    'Material Symbols Rounded',
                    'Material Symbols Outlined',
                    'Material Icons'
                    !important;
            }}


            /* =========================
               Hide sidebar collapse
            ========================= */

            [data-testid="stSidebarCollapseButton"] {{
                display: none !important;
            }}

        </style>
        """,
        unsafe_allow_html=True,
    )

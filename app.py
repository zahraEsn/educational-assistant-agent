"""
AI Tutor - Local AI Study Buddy

A privacy-focused AI tutoring application that runs entirely on your local machine.
Provides personalized explanations and generates custom quizzes across multiple subjects.

Author: Hariom Kumar
License: MIT
Repository: https://github.com/hari7261/AI-Tutor
"""

import base64
import html
import json
import logging
from pathlib import Path

import ollama
import streamlit as st
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


def load_font(filename):
    font_path = Path("fonts") / filename
    return base64.b64encode(font_path.read_bytes()).decode()


regular_font = load_font("YekanBakh-Regular.woff")
bold_font = load_font("YekanBakh-Bold.woff")
semibold_font = load_font("YekanBakh-SemiBold.woff")


# =========================
# Global CSS
# =========================

st.markdown(
    f"""
    <style>
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

				.material-symbols-rounded,
				.material-symbols-outlined,
				.material-icons,
				[data-testid="stSidebarCollapseButton"] span {{
						font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
				}}

        /* حذف دکمه بستن Sidebar */
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}


        /* کل برنامه */
        .stApp {{
            direction: rtl;
            font-family: 'Yekan Bakh', sans-serif;
        }}

        /* عنوان st.title */
        div.stHeading h1 {{
            font-family: 'Yekan Bakh', sans-serif !important;
            direction: rtl;
            text-align: right;
        }}

        /* متن‌ها */
        .stMarkdown,
        .stText,
        .stCaption,
        .stHeading,
        label,
        p,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {{
            font-family: 'Yekan Bakh', sans-serif;
            direction: rtl;
            text-align: right;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            direction: rtl;
        }}

        section[data-testid="stSidebar"] * {{
            font-family: 'Yekan Bakh', sans-serif;
        }}

        /* Chat messages */

        [data-testid="stChatMessageContent"] * {{
            font-family: 'Yekan Bakh', sans-serif;
            direction: rtl;
            text-align: right;
        }}

        /* Chat input */
        [data-testid="stChatInput"] textarea {{
            direction: rtl;
            text-align: right;
            font-family: 'Yekan Bakh', sans-serif;
        }}

        /* Selectbox / Radio */
        div[data-baseweb="select"] *,
        div[role="option"],
        div[role="radiogroup"] * {{
            font-family: 'Yekan Bakh', sans-serif !important;
        }}

        div[data-baseweb="select"] {{
            direction: rtl;
        }}

        div[role="radiogroup"] {{
            direction: rtl;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def quiz_to_html(quiz_data: dict) -> str:
    questions_html = ""

    for question in quiz_data.get("questions", []):
        question_id = html.escape(str(question.get("id", "")))
        question_text = html.escape(str(question.get("question", "")))
        question_type = question.get("question_type", "")
        difficulty = question.get("difficulty", "")
        hint = html.escape(str(question.get("hint", "")))
        options = question.get("options", [])

        difficulty_labels = {
            "آسان": "آسان",
            "متوسط": "متوسط",
            "سخت": "سخت",
        }

        difficulty_class = {
            "آسان": "easy",
            "متوسط": "medium",
            "سخت": "hard",
        }.get(difficulty, "unknown")

        difficulty_label = difficulty_labels.get(difficulty, "")

        options_html = ""

        if options:
            options_html = """
            <div class="options">
            """

            for option in options:
                option_text = html.escape(str(option))

                options_html += f"""
                    <div class="option">
                        <span class="checkbox"></span>
                        <span>{option_text}</span>
                    </div>
                """

            options_html += "</div>"

        answer_area = ""

        if question_type in {"short_answer", "problem_solving"}:
            answer_area = """
            <div class="answer-area">
                <div class="answer-line"></div>
                <div class="answer-line"></div>
                <div class="answer-line"></div>
                <div class="answer-line"></div>
            </div>
            """

        elif question_type == "fill_blank":
            answer_area = """
            <div class="fill-answer">
                پاسخ:
                <span class="blank-line"></span>
            </div>
            """

        elif not options:
            answer_area = """
            <div class="answer-area">
                <div class="answer-line"></div>
                <div class="answer-line"></div>
            </div>
            """

        questions_html += f"""
        <section class="question">
            <div class="question-header">
                <span class="question-number">{question_id}</span>
                <div class="question-content">

                    <div class="question-meta">
                        <span class="difficulty {difficulty_class}">
                            {difficulty_label}
                        </span>
                    </div>

                    <div class="question-text">
                        {question_text}
                    </div>

                </div>
            </div>

            {options_html}

            {answer_area}

            <div class="hint">
                <strong>راهنمایی:</strong>
                {hint}
            </div>
        </section>
        """

    return f"""
		<!DOCTYPE html>
		<html lang="fa" dir="rtl">
			<head>
					<meta charset="UTF-8">

					<style>

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

							@page {{
									size: A4;
									margin: 18mm 16mm 20mm 16mm;

									@bottom-center {{
											content: "صفحه " counter(page);
											font-family: 'Yekan Bakh', sans-serif;
											font-size: 9px;
											color: #888;
									}}
							}}

							* {{
									box-sizing: border-box;
							}}

							body {{
									direction: rtl;
									font-family: 'Yekan Bakh', sans-serif;
									color: #202124;
									background: white;
									font-size: 13px;
									line-height: 1.9;
									margin: 0;
							}}

							.worksheet {{
									width: 100%;
							}}

							.header {{
									border-bottom: 2px solid #222;
									padding-bottom: 12px;
									margin-bottom: 22px;
							}}

							.title {{
									font-size: 22px;
									font-weight: 700;
									margin-bottom: 10px;
							}}

							.student-info {{
									display: flex;
									gap: 25px;
									font-size: 12px;
							}}

							.info-line {{
									flex: 1;
									border-bottom: 1px solid #999;
									padding-bottom: 4px;
							}}

							.question {{
									margin-bottom: 22px;
									break-inside: avoid;
									page-break-inside: avoid;
							}}

							.question-header {{
									display: flex;
									align-items: flex-start;
									gap: 10px;
									font-size: 15px;
									font-weight: 600;
							}}

							.question-number {{
									width: 30px;
									height: 30px;
									border: 1.5px solid #333;
									border-radius: 50%;
									display: flex;
									align-items: center;
									justify-content: center;
									font-size: 12px;
									font-weight: 700;
									flex-shrink: 0;
							}}

							.question-content {{
									flex: 1;
							}}

							.question-meta {{
									margin-bottom: 2px;
							}}

							.difficulty {{
									display: inline-block;
									font-size: 9px;
									font-weight: 600;
									padding: 1px 7px;
									border: 1px solid #999;
									border-radius: 10px;
							}}

							.question-text {{
									line-height: 1.9;
							}}

							.question-text {{
									flex: 1;
							}}

							.difficulty.easy {{
									border-style: solid;
							}}

							.difficulty.medium {{
									border-style: dashed;
							}}

							.difficulty.hard {{
									border-style: double;
							}}

							.options {{
									margin-top: 12px;
									margin-right: 37px;
							}}

							.option {{
									display: flex;
									align-items: center;
									gap: 9px;
									margin: 7px 0;
							}}

							.checkbox {{
									width: 14px;
									height: 14px;
									border: 1.5px solid #444;
									display: inline-block;
									flex-shrink: 0;
							}}

							.answer-area {{
									margin-top: 12px;
									margin-right: 37px;
							}}

							.answer-line {{
									border-bottom: 1px solid #bbb;
									height: 25px;
							}}

							.fill-answer {{
									margin-top: 15px;
									margin-right: 37px;
							}}

							.blank-line {{
									display: inline-block;
									width: 150px;
									border-bottom: 1px solid #333;
									margin-right: 8px;
							}}

							.hint {{
									margin-top: 12px;
									margin-right: 37px;
									padding: 8px 12px;
									border-right: 3px solid #555;
									background: #f7f7f7;
									font-size: 11px;
									color: #555;
							}}

							.footer {{
									margin-top: 30px;
									padding-top: 10px;
									border-top: 1px solid #ddd;
									text-align: center;
									font-size: 10px;
									color: #888;
							}}

					</style>
			</head>

			<body>

				<div class="worksheet">

						<header class="header">
								<div class="title">کاربرگ تمرین</div>

								<div class="student-info">
										<div class="info-line">
												نام دانش‌آموز:
										</div>

										<div class="info-line">
												تاریخ:
										</div>
								</div>
						</header>

						{questions_html}

				</div>

			</body>
		</html>
		"""


def generate_worksheet_pdf(quiz_data: dict) -> bytes:
    html_content = quiz_to_html(quiz_data)

    font_config = FontConfiguration()

    pdf_bytes = HTML(string=html_content).write_pdf(font_config=font_config)

    return pdf_bytes


# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to get available models
@st.cache_data
def get_available_models():
    try:
        models_response = ollama.list()
        model_names = []

        # Handle the ListResponse object from ollama
        if hasattr(models_response, "models"):
            for model in models_response.models:
                # Each model has a 'model' attribute with the name
                if hasattr(model, "model"):
                    model_names.append(model.model)
                elif isinstance(model, dict):
                    # Fallback for dict format
                    name = model.get("name") or model.get("model") or model.get("id")
                    if name:
                        model_names.append(name)
                elif isinstance(model, str):
                    model_names.append(model)
        elif isinstance(models_response, dict) and "models" in models_response:
            # Fallback for older API format
            for model in models_response["models"]:
                if isinstance(model, dict):
                    name = model.get("name") or model.get("model") or model.get("id")
                    if name:
                        model_names.append(name)
                elif isinstance(model, str):
                    model_names.append(model)

        # Prioritize models - check for exact matches and partial matches
        preferred_order = [
            "gemma3:latest",
            "gemma3",
            "gemma2:2b",
            "gemma2",
            "llama3",
            "mistral",
            "deepseek-coder",
        ]
        ordered_models = []

        # First, add exact matches from preferred list
        for preferred in preferred_order:
            if preferred in model_names:
                ordered_models.append(preferred)

        # Then add any other models not in preferred list
        for model in model_names:
            if model not in ordered_models:
                ordered_models.append(model)

        return ordered_models
    except Exception as e:
        # Show more detailed error for debugging
        st.error(f"Error connecting to Ollama: {e!s}")
        st.info("Make sure Ollama is running: `ollama serve`")
        return []


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_file" not in st.session_state:
    st.session_state.quiz_file = None

if "worksheet_pdf" not in st.session_state:
    st.session_state.worksheet_pdf = None

# App title
st.title("🎓 دوست مطالعه و تمرین")

# Sidebar for settings
with st.sidebar:
    st.header("🎯 مشخصات دانش‌آموز")

    # Education level dropdown
    education_level = st.selectbox(
        "کلاس چندمی؟",
        ["اول", "دوم", "سوم", "چهارم", "پنجم", "ششم"],
        index=1,
    )

    # Subject dropdown
    subject = st.selectbox(
        "از کدوم درس سوال داری؟",
        ["ریاضی", "فارسی", "علوم"],
        index=2,
    )

    # # Subject dropdown
    # season = st.selectbox(
    #     "کدوم فصل؟",
    #     ["1", "	2", "3"],
    #     index=2,
    # )

    # Mode selection (Explanation vs. Quiz)
    mode = st.radio(
        "چطور باهم تمرین کنیم؟", ["برام توضیح بده", "ازم امتحان بگیر"], index=0
    )

    # Model selection - only show available models
    available_models = get_available_models()
    if available_models:
        model_name = st.selectbox(
            "AI Model",
            available_models,
            index=0,
            help="Gemma3 is recommended for better performance",
        )
        # Show model info
        if "gemma3" in model_name.lower():
            st.success("✅ Using Gemma3 - Excellent choice!")
        elif "deepseek-coder" in model_name.lower():
            st.success("✅ Using DeepSeek Coder - Great for coding tasks!")
        elif available_models and not any(
            "gemma3" in m.lower() for m in available_models
        ):
            st.info("💡 Install Gemma3 for better performance: `ollama pull gemma3`")
    else:
        st.error("⚠️ No Ollama models found.")
        st.markdown("**Install Gemma3 (recommended):**")
        st.code("ollama pull gemma3", language="bash")
        st.markdown("**Or other models:**")
        st.code("ollama pull llama3\nollama pull deepseek-coder", language="bash")
        model_name = None

    st.markdown("---")
    st.markdown("💡 همه تلاشم رو برای یادگیریت می‌کنم")

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input(f"درباره‌ی درس {subject} سوالت رو بپرس..."):
    if not model_name:
        st.error("Please install an Ollama model first!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Customize system prompt based on mode
        if mode == "برام توضیح بده":
            system_prompt = f"""
						تو یک دستیار آموزشی خصوصی، مهربان و صبور برای دانش‌آموزان دوره ابتدایی ایران هستی.

						اطلاعات دانش‌آموز:
						- پایه تحصیلی: {education_level} ابتدایی
						- درس: {subject}

						هدف اصلی:
						به دانش‌آموز کمک کن که موضوع را واقعاً بفهمد و خودش فکر کند.
						تو فقط یک پاسخ‌دهنده نیستی؛ نقش یک معلم خصوصی خوب را داری.

						قوانین بسیار مهم:

						1. سطح تمام پاسخ‌ها باید دقیقاً متناسب با پایه {education_level} ابتدایی باشد.
							فرض کن دانش‌آموز کم‌سن است و ممکن است بسیاری از مفاهیم پایه را هنوز نداند.

						2. مطالب را بسیار ساده، کوتاه و مرحله‌به‌مرحله توضیح بده.
							از جمله‌های کوتاه و واژه‌های ساده فارسی استفاده کن.

						3. ساده‌سازی نباید باعث اشتباه علمی شود.
							همیشه اولویت با درست بودن مطلب است، حتی اگر لازم باشد توضیح کمی ساده‌تر یا کوتاه‌تر شود.

						4. هرگز برای پر کردن پاسخ، اطلاعاتی که از صحت آن مطمئن نیستی اختراع نکن.
							اگر جواب را دقیق نمی‌دانی یا مطمئن نیستی، صادقانه بگو:
							«مطمئن نیستم و بهتر است این موضوع را دقیق بررسی کنیم.»
							هرگز حدس را به‌عنوان واقعیت بیان نکن.

						5. اگر درباره یک موضوع علمی توضیح می‌دهی:
							- از علت و معلول واقعی و درست استفاده کن.
							- اطلاعات علمی را تغییر نده.
							- توضیح ساده باشد، اما نادرست نباشد.
							- از توضیح‌های خیالی یا ساختگی استفاده نکن.

						6. از تشبیه و مثال فقط زمانی استفاده کن که واقعاً به فهم مفهوم کمک کند.
							تشبیه نباید جای توضیح اصلی را بگیرد.
							اگر تشبیه ممکن است باعث برداشت اشتباه شود، از آن استفاده نکن.

						7. برای موضوعات علمی، ریاضی و درسی:
							- اگر اصطلاح علمی را نمی‌دانی، اصطلاح جعلی نساز.
							- از واژه‌های بی‌معنی یا شبیه‌به‌واژه‌های علمی استفاده نکن.
							- ابتدا مفهوم واقعی را خیلی ساده توضیح بده،
							- سپس در صورت نیاز یک مثال ساده ارائه کن.

						8. اگر دانش‌آموز سؤال ساده‌ای پرسید، پاسخ را بی‌دلیل پیچیده نکن.
							فقط به اندازه‌ای توضیح بده که سؤال او پاسخ داده شود.

						9. اگر دانش‌آموز سؤال یا مسئله‌ای دارد که می‌تواند خودش حل کند:
							مستقیماً جواب نهایی را نده.
							ابتدا یک راهنمایی کوچک بده و از او بخواه خودش فکر کند.

						10. راهنمایی باید واقعاً به سمت پاسخ هدایت کند،
								اما نباید پاسخ را لو بدهد.

						11. اگر دانش‌آموز جواب اشتباه داد:
								- او را سرزنش نکن.
								- بگو اشتباه کردن طبیعی است.
								- یک نکته کوچک برای پیدا کردن اشتباه بده.
								- اجازه بده خودش دوباره تلاش کند.
								- فقط در صورت نیاز پاسخ کامل را توضیح بده.

						12. اگر دانش‌آموز جواب را نمی‌داند:
								مفهوم موردنیاز را در ساده‌ترین شکل توضیح بده
								و سپس دوباره از او یک سؤال کوچک بپرس.

						13. اگر دانش‌آموز از تو مثال خواست:
								مثال باید مستقیماً با مفهوم مرتبط باشد.
								از مثال‌های بی‌ربط، عجیب یا غیرواقعی استفاده نکن.

						14. هر بار فقط یک مرحله از آموزش را انجام بده.
								از انباشتن چند توضیح مختلف در یک پاسخ خودداری کن.

						15. در پایان هر پاسخ لازم نیست سؤال جدید بپرسی.

								فقط زمانی سؤال آموزشی بپرس که:
								- برای ادامه یادگیری همان موضوع واقعاً لازم باشد،
								- دانش‌آموز هنوز در حال یادگیری فعال باشد،
								- و از سؤال پرسیدن خسته یا ناراضی به نظر نرسد.

								در هر پاسخ حداکثر یک سؤال آموزشی بپرس.

								اگر دانش‌آموز به سؤال پاسخ درست داد و مفهوم را فهمید، لازم نیست حتماً سؤال دیگری مطرح کنی.
								گاهی فقط پاسخ را تأیید کن و مکالمه را متوقف کن.

						16. لحن تو باید:
								- دوستانه
								- مهربان
								- صبور
								- تشویق‌کننده
								- مناسب یک کودک
								باشد.

						17. دانش‌آموز را بیش از حد با عبارت‌های تشویقی خطاب نکن.
								تشویق باید طبیعی باشد و بعد از تلاش یا پاسخ او استفاده شود.

						18. هیچ‌وقت برای ادامه دادن مکالمه، سؤال یا موضوع بی‌ربط مطرح نکن.
								سؤال بعدی باید مستقیماً به موضوع فعلی مربوط باشد.

						19. اگر دانش‌آموز نام خود را گفت، آن را در همین مکالمه به خاطر داشته باش
								و در صورت طبیعی بودن از نام او استفاده کن.
								اگر نامی قبلاً در مکالمه گفته نشده، ادعا نکن که آن را می‌دانی.

						20. اگر موضوع دانش‌آموز خارج از درس «{subject}» یا خارج از سطح پایه {education_level} بود،
								خیلی کوتاه توضیح بده و او را به محتوای مناسب برگردان.

						21. پاسخ‌ها را به زبان فارسی بنویس.

						22. از اطلاعات ساختگی، مثال‌های بی‌معنی، تشبیه‌های نامرتبط،
								و پاسخ‌هایی که فقط برای پر کردن مکالمه تولید شده‌اند خودداری کن.

						23. قوانین کنترل مکالمه و پایان آموزش:

							- اگر دانش‌آموز عباراتی مانند:
								«بسه»
								«کافیه»
								«دیگه سوال نپرس»
								«خیلی سوال می‌پرسی»
								«خسته شدم»
								«حوصله ندارم»
								«دیگه نمی‌خوام»
								«تموم»
								«فعلاً»
								یا هر عبارت مشابهی گفت، فوراً آموزش و پرسش را متوقف کن.

							- وقتی دانش‌آموز خسته، بی‌حوصله یا ناراضی به نظر می‌رسد:
								سؤال جدید نپرس.
								تمرین جدید پیشنهاد نده.
								بازی یا فعالیت دیگری پیشنهاد نده.

							- در پایان چنین مکالمه‌ای یک جمله کوتاه و دوستانه بگو، مانند:
								«خسته نباشی، امروز خیلی خوب تلاش کردی.»

						اصل مهم:
						«ساده، درست، مرتبط و مرحله‌به‌مرحله آموزش بده.»

						هر زمان بین «ساده بودن» و «درست بودن» مجبور به انتخاب شدی،
						درست بودن را حفظ کن و آن را با زبان ساده توضیح بده.
						"""
        else:  # Quiz mode
            system_prompt = f"""
						تو یک طراح تمرین و معلم باتجربه برای دانش‌آموزان دوره ابتدایی ایران هستی.

						اطلاعات ثابت دانش‌آموز:
						- پایه تحصیلی: {education_level} ابتدایی
						- درس: {subject}

						هدف:
						برای موضوعی که دانش‌آموز در پیام خود مشخص کرده است، یک مجموعه ۵ تا ۷ سؤالی طراحی کن.
						این مجموعه باید طوری باشد که دانش‌آموز با حل کردن آن‌ها، موضوع را بهتر بفهمد، مفاهیم اصلی را تمرین کند و بتواند کاربرد آن‌ها را در موقعیت‌های مختلف تشخیص دهد.

						موضوع فقط از داخل پیام دانش‌آموز مشخص می‌شود.
						آن را از خودت حدس نزن و موضوع جدیدی به آن اضافه نکن.

						========================
						قوانین اصلی طراحی سؤال
						========================

						1. تعداد سؤال‌ها باید دقیقاً بین ۵ تا ۷ باشد.

						2. همه سؤال‌ها باید دقیقاً مناسب پایه {education_level} ابتدایی و درس {subject} باشند.

						3. محتوای سؤال‌ها باید با سطح واقعی دانش‌آموزان همان پایه در ایران هماهنگ باشد.
							از مفاهیمی که معمولاً در پایه‌های بالاتر آموزش داده می‌شوند استفاده نکن.

						4. هدف مجموعه فقط تولید چند سؤال تصادفی نیست.
							سؤال‌ها باید چند جنبه مختلف از همان موضوع را پوشش دهند.

						5. هر سؤال باید یک هدف آموزشی مشخص داشته باشد.
							مشخص باشد که سؤال دقیقاً چه مفهوم یا مهارتی را تمرین می‌کند.

						6. سؤال‌ها نباید تکراری باشند.
							دو سؤال نباید فقط با عوض کردن چند عدد یا چند کلمه، عملاً یک سؤال یکسان باشند.

						7. اگر یک مفهوم مهم نیاز به تمرین بیشتر دارد، می‌توان آن را با دو سؤال متفاوت و در دو موقعیت متفاوت تمرین کرد.

						========================
						تنوع و سطح دشواری
						========================

						8. سؤال‌ها باید از آسان به سخت مرتب شوند.

						9. مجموعه باید شامل هر سه سطح دشواری باشد:
							- آسان
							- متوسط
							- سخت

						10. مثلا اگر ۷ سؤال تولید می‌کنی:
							- ۲ سؤال آسان
							- ۳ سؤال متوسط
							- ۲ سؤال سخت

						11. سخت بودن سؤال نباید فقط به معنی طولانی بودن متن باشد.
								سؤال سخت باید به دلیل نیاز به فکر کردن، مقایسه، ترکیب مفاهیم یا کاربرد مفهوم در موقعیتی جدید سخت باشد.

						12. سؤال‌های آسان باید برای تثبیت مفهوم پایه باشند.
								سؤال‌های متوسط باید کاربرد مفهوم را تمرین کنند.
								سؤال‌های سخت باید دانش‌آموز را به فکر کردن و ترکیب مطالب وادار کنند.

						========================
						نوع سؤال
						========================

						13. تا حد امکان از انواع مختلف سؤال استفاده کن:
								- multiple_choice
								- true_false
								- fill_blank
								- short_answer
								- problem_solving

						14. نوع سؤال باید با موضوع هماهنگ باشد.
								به زور برای همه موضوع‌ها از همه انواع سؤال استفاده نکن.

						15. برای ریاضی، در صورت مناسب بودن موضوع، از ترکیبی از:
								- محاسبه
								- مقایسه
								- کامل کردن
								- مسئله کاربردی
								- استدلال ساده
								استفاده کن.

						========================
						قوانین بسیار مهم برای دنیای واقعی
						========================

						16. هر سؤال داستانی یا کاربردی باید از نظر دنیای واقعی منطقی و قابل تصور باشد.

						17. از موقعیت‌های غیرواقعی، عجیب یا خنده‌دار استفاده نکن.

						18. قبل از قرار دادن یک موقعیت واقعی در سؤال، بررسی کن که آن اتفاق در زندگی واقعی ممکن باشد.

						مثلاً این سؤال نامناسب است:
						«یک مشتری با ۵۰ هزار تومان، ۳ لپ‌تاپ خرید.»

						چنین موقعیتی از نظر اقتصادی و دنیای واقعی منطقی نیست.

						به جای آن از موقعیت‌های طبیعی مانند:
						- خرید چند مداد
						- خرید چند دفتر
						- خرید چند پاک‌کن
						- تقسیم خوراکی بین چند نفر
						- شمارش کتاب‌ها
						- تعداد دانش‌آموزان
						- تعداد صندلی‌ها
						- ساعت و زمان
						- اندازه‌گیری طول و وزن
						- تعداد میوه‌ها
						استفاده کن؛ به شرطی که اعداد و موقعیت واقعی و معقول باشند.

						19. اشیاء، تعدادها، واحدها، قیمت‌ها و موقعیت‌های سؤال باید با یکدیگر سازگار باشند.

						20. از ترکیب تصادفی اسم‌ها و اشیاء که معنای واقعی ندارند خودداری کن.

						مثلاً چنین عبارتی ممنوع است:
						«۱۲ عدد گلاب را بین ۶ گل تقسیم کن.»

						21. قبل از خروجی نهایی، هر سؤال را از نظر «منطقی بودن داستان» بررسی کن.
								اگر یک کودک بتواند بپرسد «این اصلاً چرا باید اتفاق بیفتد؟»، سؤال را اصلاح کن.

						========================
						قوانین ویژه مسائل ریاضی
						========================

						22. اگر موضوع مربوط به جمع، تفریق، ضرب یا تقسیم است، مسئله باید با مفهوم همان عمل سازگار باشد.

						23. در مسائل تقسیم برای دانش‌آموز ابتدایی:
								اگر موضوع مربوط به تقسیم مساوی و مفهوم تقسیم دقیق است، بهتر است تعدادها طوری انتخاب شوند که تقسیم مفهوم واضح و متناسب با سطح دانش‌آموز باشد که در نهایت به جواب روند برسد.

						24. سؤال نباید عملیاتی را طلب کند که دانش‌آموز هنوز در سطح پایه خود نیاموخته است.

						25. واحدها باید درست استفاده شوند.
								مثلاً:
								- پول با تومان یا هزار تومان
								- مایع با لیتر یا میلی‌لیتر
								- وزن با گرم یا کیلوگرم
								- طول با سانتی‌متر یا متر

						26. در مسائل کاربردی از اعداد غیرمنطقی یا غیرطبیعی خودداری کن.

						========================
						قوانین صورت سؤال
						========================

						27. صورت سؤال باید کوتاه، روشن و بدون ابهام باشد.

						28. جمله‌بندی باید طبیعی و درست فارسی باشد.

						29. از متن‌های طولانی و داستان‌های غیرضروری خودداری کن.

						30. سؤال باید دقیقاً مشخص کند دانش‌آموز چه چیزی را باید پیدا کند.

						31. هیچ سؤال نباید دارای اطلاعات اضافی و بی‌فایده باشد.

						32. سؤال نباید پاسخ را در خود پنهان کرده باشد.

						33. اگر سؤال چندگزینه‌ای است، فقط یک گزینه باید به‌طور واضح درست باشد.
								گزینه‌های غلط باید واقعی و قابل‌قبول باشند و نباید آن‌قدر عجیب باشند که پاسخ درست فوراً مشخص شود.

						========================
						قوانین بسیار سخت‌گیرانه برای Hint
						========================

						34. برای هر سؤال دقیقاً یک hint تولید کن.

						35. hint فقط باید یک «سرنخ کوچک» برای شروع فکر کردن باشد.

						36. hint نباید پاسخ را بگوید.

						37. hint نباید مقدار عددی پاسخ را بیان کند.

						38. hint نباید گزینه صحیح را مشخص کند.

						39. hint نباید مراحل کامل حل را توضیح دهد.

						40. hint نباید صورت سؤال را با کلمات دیگر تکرار کند و نباید فقط همان دستور سؤال باشد.

						مثال نامناسب:

						سؤال:
						«حاصل ۳۶ تقسیم بر ۹ چند است؟»

						راهنمایی نامناسب:
						«۳۶ را بر ۹ تقسیم کن.»

						این راهنمایی فقط صورت سؤال را به شکل دیگری تکرار کرده است.

						راهنمایی بهتر:
						«به این فکر کن که ۳۶ را می‌توان به چند گروه مساوی تقسیم کرد.»

						مثال دیگر:

						سؤال:
						«۵ مداد داری و ۳ مداد دیگر می‌خری. حالا چند مداد داری؟»

						راهنمایی نامناسب:
						«۵ را با ۳ جمع کن.»

						راهنمایی بهتر:
						«تعداد مدادهای جدید را به چیزی که از قبل داشتی اضافه کن.»

						41. اگر می‌توانی یک hint بدهی که دانش‌آموز را یک قدم به جواب نزدیک کند، اما هنوز مجبور باشد خودش فکر کند، همان را انتخاب کن.

						42. hint نباید آن‌قدر کلی باشد که هیچ کمکی نکند.

						========================
						قوانین آموزشی
						========================

						43. سؤال‌ها باید باعث یادگیری شوند، نه فقط سنجش حفظیات.

						44. اگر موضوع یک مفهوم اصلی دارد، چند سؤال باید همان مفهوم را از زاویه‌های مختلف تمرین کنند.

						45. در مجموعه، حداقل یک سؤال باید به کاربرد مفهوم در یک موقعیت طبیعی و روزمره بپردازد، در صورتی که چنین کاری برای آن موضوع مناسب باشد.

						46. اگر موضوع فقط با سؤال مستقیم بهتر آموزش داده می‌شود، مسئله مصنوعی و اجباری نساز.

						47. از موقعیت‌های روزمره آشنا برای دانش‌آموز ایرانی استفاده کن.

						48. مثال‌ها می‌توانند شامل مدرسه، خانه، کتاب، دفتر، مداد، خوراکی، ساعت، خریدهای کوچک، بازی، حیاط مدرسه و موارد مشابه باشند.

						49. از موقعیت‌های غیرطبیعی فقط برای سخت‌تر کردن سؤال استفاده نکن.

						========================
						ممنوعیت پاسخ
						========================

						50. پاسخ صحیح را هرگز در خروجی قرار نده.

						51. هیچ‌کدام از این فیلدها را تولید نکن:
								- answer
								- correct_answer
								- solution
								- explanation
								- پاسخ صحیح
								- جواب
								- حل

						52. در سؤال چندگزینه‌ای، گزینه درست را مشخص نکن.

						========================
						قوانین JSON
						========================

						53. خروجی باید فقط JSON معتبر باشد.

						54. هیچ متن، توضیح، Markdown، ```json یا متن اضافه قبل یا بعد از JSON ننویس.

						55. ریشه JSON فقط باید یک کلید به نام "questions" داشته باشد.

						56. مقدار "questions" باید آرایه‌ای شامل ۵ تا ۷ سؤال باشد.

						57. هر سؤال باید دقیقاً این ساختار را داشته باشد:

						{{
							"id": 1,
							"question": "صورت سؤال",
							"question_type": "multiple_choice",
							"difficulty": "آسان",
							"concept": "مفهوم مورد تمرین",
							"hint": "راهنمایی کوتاه"
						}}

						58. مقدار "id" باید برای هر سؤال یکتا باشد.

						58. مقدار "difficulty" فقط یکی از این موارد باشد:
								"آسان"
								"متوسط"
								"سخت"

						59. مقدار "question_type" فقط یکی از این موارد باشد:
								"multiple_choice"
								"true_false"
								"fill_blank"
								"short_answer"
								"problem_solving"

						60. فقط اگر question_type برابر با "multiple_choice" بود، فیلد "options" را اضافه کن.

						61. برای multiple_choice، فیلد "options" باید دقیقاً شامل ۴ گزینه باشد.

						62. برای سؤال‌هایی که multiple_choice نیستند، فیلد "options" را اصلاً تولید نکن.

						63. برای هر مقدار رشته‌ای، از JSON syntax معتبر استفاده کن.

						64. هیچ comma اضافی در آخر آرایه یا object قرار نده.

						========================
						کنترل نهایی قبل از خروجی
						========================

						قبل از تولید JSON، تک‌تک سؤال‌ها را در ذهن بررسی کن.

						برای هر سؤال بررسی کن:

						1. آیا برای پایه {education_level} مناسب است؟
						2. آیا به موضوع فعلی مربوط است؟
						3. آیا از نظر علمی و آموزشی درست است؟
						4. آیا از نظر دنیای واقعی منطقی است؟
						5. آیا اتفاق یا خرید یا موقعیت مطرح‌شده واقعاً ممکن است؟
						6. آیا عددها و واحدها منطقی هستند؟
						7. آیا سؤال با مفهوم موردنظر هماهنگ است؟
						8. آیا صورت سؤال واضح است؟
						9. آیا سؤال تکراری نیست؟
						10. آیا سطح دشواری آن درست انتخاب شده؟
						11. آیا hint پاسخ را لو نمی‌دهد؟
						12. آیا hint فقط صورت سؤال را تکرار نمی‌کند؟
						13. آیا در سؤال چندگزینه‌ای فقط یک پاسخ قابل قبول وجود دارد؟
						14. آیا هیچ پاسخ صحیحی در هیچ فیلدی قرار نگرفته است؟
						15. آیا JSON معتبر است؟

						اگر هر کدام از این بررسی‌ها شکست خورد، سؤال را اصلاح کن و سپس خروجی نهایی را تولید کن.

						اصل نهایی:
						سؤال خوب برای یک کودک باید «درست، واقعی، قابل فهم، مرتبط، آموزنده و قابل حل» باشد.

						فقط JSON نهایی را خروجی بده.
						"""

        chat_messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            *st.session_state.messages,
        ]

        chat_messages.extend(st.session_state.messages)

        try:
            # Stream response from Ollama
            response = ollama.chat(
                model=model_name, messages=chat_messages, stream=True
            )

            for chunk in response:
                content = chunk["message"]["content"]
                full_response += content

            if mode == "برام توضیح بده":
                message_placeholder.markdown(full_response + "▌")
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            else:
                message_placeholder.markdown("در حال آماده‌سازی نمونه سؤال‌ها...")

            # ذخیره خروجی آزمون برای دانلود
            if mode == "ازم امتحان بگیر":
                try:
                    clean_response = full_response.strip()

                    clean_response = clean_response.removeprefix("```json")
                    clean_response = clean_response.removeprefix("```")
                    clean_response = clean_response.removesuffix("```")

                    clean_response = clean_response.strip()

                    quiz_data = json.loads(clean_response)

                    st.session_state.worksheet_pdf = generate_worksheet_pdf(quiz_data)

                    message_placeholder.markdown(
                        "نمونه سؤال‌ها آماده شد، می‌تونی کاربرگت رو دانلود کنی. موفق باشی :)"
                    )

                except json.JSONDecodeError:
                    st.error("خروجی تولیدشده JSON معتبر نیست.")

                except Exception as e:
                    logger.exception("Failed to generate worksheet PDF")
                    st.error(f"ساخت PDF کاربرگ با خطا مواجه شد: {e}")

        except ollama.ResponseError:
            error_msg = f"❌ Model '{model_name}' not found. Please install it using: `ollama pull {model_name}`"
            message_placeholder.markdown(error_msg)
            full_response = error_msg
        except Exception as e:
            error_msg = f"❌ Error: {e!s}"
            message_placeholder.markdown(error_msg)
            full_response = error_msg


# =========================
# Download Quiz
# =========================

if st.session_state.worksheet_pdf:
    st.download_button(
        label="دانلود کاربرگ دانش‌آموز",
        data=st.session_state.worksheet_pdf,
        file_name="کاربرگ-دانش‌آموز.pdf",
        mime="application/pdf",
        key="download_worksheet_pdf",
    )

import base64
import html
from pathlib import Path

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


def load_font(filename):
    font_path = Path("fonts") / filename
    return base64.b64encode(font_path.read_bytes()).decode()


regular_font = load_font("YekanBakh-Regular.woff")
bold_font = load_font("YekanBakh-Bold.woff")
semibold_font = load_font("YekanBakh-SemiBold.woff")


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
    print("QUIZ DATA:")
    print(quiz_data)

    html_content = quiz_to_html(quiz_data)

    font_config = FontConfiguration()

    pdf_bytes = HTML(string=html_content).write_pdf(font_config=font_config)

    return pdf_bytes

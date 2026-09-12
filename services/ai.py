import json

import ollama
import streamlit as st

from prompts.quiz_prompts import build_personalized_quiz_prompt


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


def generate_personalized_quiz(
    model_name: str,
    education_level: str,
    subject: str,
    weaknesses: str,
    teacher_notes: str,
    question_count: int,
) -> dict:

    system_prompt = build_personalized_quiz_prompt(
        education_level=education_level,
        subject=subject,
        weaknesses=weaknesses,
        teacher_notes=teacher_notes,
        question_count=question_count,
    )

    user_prompt = f"""
    برای این دانش‌آموز یک کاربرگ شخصی‌سازی‌شده تولید کن.

    پایه: {education_level}
    درس: {subject}

    ضعف‌های اصلی:
    {weaknesses}

    توضیحات معلم:
    {teacher_notes}

    تعداد سؤال:
    {question_count}
    """

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    content = response["message"]["content"].strip()

    content = content.removeprefix("```json")
    content = content.removeprefix("```")
    content = content.removesuffix("```")
    content = content.strip()

    return json.loads(content)


def validate_quiz(quiz_data: dict, expected_count: int) -> None:
    if set(quiz_data.keys()) != {"questions"}:
        raise ValueError("ساختار JSON باید فقط شامل questions باشد.")

    questions = quiz_data["questions"]

    if len(questions) != expected_count:
        raise ValueError(f"تعداد سؤال‌ها باید {expected_count} باشد.")

    allowed_types = {
        "multiple_choice",
        "true_false",
        "fill_blank",
        "short_answer",
        "problem_solving",
    }

    allowed_difficulties = {
        "آسان",
        "متوسط",
        "سخت",
    }

    for question in questions:

        required_fields = {
            "id",
            "question",
            "question_type",
            "difficulty",
            "concept",
            "hint",
        }

        missing = required_fields - question.keys()

        if missing:
            raise ValueError(f"فیلدهای الزامی وجود ندارند: {missing}")

        if question["question_type"] not in allowed_types:
            raise ValueError("question_type نامعتبر است.")

        if question["difficulty"] not in allowed_difficulties:
            raise ValueError("difficulty نامعتبر است.")

        if question["question_type"] == "multiple_choice":

            if "options" not in question:
                raise ValueError("سؤال چندگزینه‌ای باید options داشته باشد.")

            if len(question["options"]) != 4:
                raise ValueError("سؤال چندگزینه‌ای باید دقیقاً ۴ گزینه داشته باشد.")

        elif "options" in question:
            raise ValueError("سؤال غیر چندگزینه‌ای نباید options داشته باشد.")

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from ai_helper import ask_ai

# 페이지 설정
st.set_page_config(page_title="우리 반 MBTI수집소", layout="wide")

# JSON 파일 경로
MBTI_FILE = Path("mbti.json")

# MBTI 질문 정의
MBTI_QUESTIONS = [
    {
        "question": "1. 새로운 상황에서 당신은?",
        "options": ["A. 신중하게 준비하고 시작한다", "B. 즉흥적으로 도전한다"],
        "dimension": "JP"  # Judging vs Perceiving
    },
    {
        "question": "2. 문제를 해결할 때 당신은?",
        "options": ["A. 논리와 원칙을 따른다", "B. 상대방의 감정을 먼저 생각한다"],
        "dimension": "TF"  # Thinking vs Feeling
    },
    {
        "question": "3. 새로운 정보를 접할 때 당신은?",
        "options": ["A. 현실적이고 구체적으로 본다", "B. 패턴과 가능성을 본다"],
        "dimension": "SN"  # Sensing vs Intuition
    },
    {
        "question": "4. 에너지를 얻는 방식은?",
        "options": ["A. 혼자 있거나 소수 친구들과 있을 때", "B. 많은 사람들과 함께 있을 때"],
        "dimension": "EI"  # Extraversion vs Introversion
    }
]

def load_mbti_data():
    """mbti.json 파일을 로드합니다."""
    if MBTI_FILE.exists():
        with open(MBTI_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"title": "우리 반 MBTI수집소", "records": []}

def save_mbti_data(data):
    """mbti.json 파일에 데이터를 저장합니다."""
    with open(MBTI_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def analyze_mbti_with_ai(answers, question_text):
    """AI를 사용하여 MBTI 유형, 별명, 설명, 해설을 생성합니다."""
    prompt = f"""사용자가 다음과 같이 답변했습니다:
- 질문 1 (준비형 vs 즉흥형): {answers[0]}
- 질문 2 (논리형 vs 감정형): {answers[1]}
- 질문 3 (현실형 vs 직관형): {answers[2]}
- 질문 4 (외향형 vs 내향형): {answers[3]}

위의 답변을 바탕으로 다음 형식의 JSON을 반환해주세요:
{{
    "mbti": "4글자 MBTI 유형 (예: INFP)",
    "nickname": "이 유형을 설명하는 재미있는 별명",
    "description": "이 유형에 대한 한 문장 설명",
    "explanation": "이 유형의 장점과 특징을 2-3줄로 설명"
}}

반드시 유효한 JSON 형식으로만 응답하세요."""

    response = ask_ai(prompt)

    # JSON 응답 파싱
    try:
        # 응답에서 JSON만 추출
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        # 파싱 실패 시 기본값 반환
        return {
            "mbti": "UNKN",
            "nickname": "분석 중...",
            "description": "AI 분석 중 오류가 발생했습니다.",
            "explanation": "다시 시도해주세요."
        }

def analyze_class_atmosphere():
    """반 친구들의 MBTI 정보를 바탕으로 반 분위기를 분석합니다."""
    data = load_mbti_data()

    if not data["records"]:
        return None

    mbti_types = [record["mbti"] for record in data["records"]]
    mbti_text = ", ".join(mbti_types)

    prompt = f"""우리 반 친구들의 MBTI 유형이 다음과 같습니다:
{mbti_text}

이 데이터를 바탕으로 우리 반의 분위기와 특징을 분석해주세요.
다음 항목들을 포함하여 3-4줄로 분석해주세요:
1. 반의 전체적인 성향
2. 반의 강점
3. 반이 주의해야 할 점
4. 반의 화합을 위한 조언"""

    return ask_ai(prompt)

# 메인 UI
st.title("🎭 우리 반 MBTI수집소")

# 탭 분할
tab1, tab2 = st.tabs(["✅ MBTI 검사하기", "📊 결과 보기"])

with tab1:
    st.subheader("MBTI 검사")

    # 사용자 입력
    user_name = st.text_input("당신의 이름을 입력하세요", placeholder="예: 김철수")

    st.write("---")

    # 질문과 답변 수집
    answers = []
    answer_texts = []

    for i, q in enumerate(MBTI_QUESTIONS):
        st.write(f"**{q['question']}**")
        selected = st.radio(
            label=f"question_{i}",
            options=q['options'],
            key=f"radio_{i}",
            label_visibility="collapsed"
        )
        answers.append(selected)
        # 선택지 A/B 추출
        answer_texts.append(selected.split(". ")[1] if ". " in selected else selected)

    st.write("---")

    # 제출 버튼
    if st.button("🚀 MBTI 분석하기", use_container_width=True):
        if not user_name.strip():
            st.error("이름을 입력해주세요!")
        else:
            with st.spinner("AI가 당신의 MBTI를 분석 중입니다..."):
                # AI로 MBTI 분석
                analysis = analyze_mbti_with_ai(answer_texts, answers)

                # 데이터 저장
                data = load_mbti_data()
                record = {
                    "nick": user_name.strip(),
                    "mbti": analysis.get("mbti", "UNKN"),
                    "answer": answer_texts,
                    "day": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "nickname": analysis.get("nickname", ""),
                    "description": analysis.get("description", ""),
                    "explanation": analysis.get("explanation", "")
                }
                data["records"].append(record)
                save_mbti_data(data)

                # 결과 표시
                st.success("✨ 분석 완료!")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("당신의 MBTI", analysis.get("mbti", "UNKN"))
                with col2:
                    st.metric("별명", analysis.get("nickname", ""))

                st.info(f"**{analysis.get('description', '')}**")
                st.write(f"**상세 설명**\n{analysis.get('explanation', '')}")

with tab2:
    st.subheader("반 친구들의 MBTI")

    data = load_mbti_data()

    if data["records"]:
        # 참여 인원 표시
        st.metric("참여한 친구 수", len(data["records"]))

        st.write("---")

        # MBTI 정보 표 표시
        st.write("**반 친구들의 MBTI 정보**")

        table_data = []
        for record in data["records"]:
            table_data.append({
                "이름": record["nick"],
                "MBTI": record["mbti"],
                "별명": record["nickname"],
                "설명": record["description"],
                "저장일": record["day"]
            })

        st.dataframe(table_data, use_container_width=True)

        st.write("---")

        # 반 분위기 분석
        st.write("**우리 반의 분위기 분석**")
        with st.spinner("반 분위기를 분석 중입니다..."):
            atmosphere = analyze_class_atmosphere()
            if atmosphere:
                st.info(atmosphere)
    else:
        st.warning("아직 참여한 친구가 없습니다. 먼저 MBTI 검사를 해주세요!")

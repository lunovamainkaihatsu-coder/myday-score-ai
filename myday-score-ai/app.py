import streamlit as st
from datetime import datetime
import json
import os
from openai import OpenAI

# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="今日のわたし採点AI！",
    page_icon="🌙",
    layout="centered"
)

DATA_FILE = "myday_scores.json"

# =========================
# OpenAI設定
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# =========================
# データ保存・読み込み
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# AIコメント生成
# =========================
def generate_ai_comment(score, diary):
    prompt = f"""
あなたは、寝る前に一日をやさしく振り返ってくれるAIです。

ユーザーの今日の点数と一言日記を見て、
友達のように自然な口調で、短く寄り添うコメントをしてください。

【今日の点数】
{score}点

【一言日記】
{diary}

条件：
・120文字以内
・説明口調にしない
・説教しない
・無理にポジティブにしすぎない
・「〜ですね」より「〜だね」寄りの自然な口調
・最後に明日への小さな一言を入れる
・医療的な助言はしない
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは優しい癒し系AIです。ユーザーを責めず、寝る前に静かに寄り添います。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return "AIコメントの生成に失敗しちゃった。でも、今日を記録できただけで十分えらいよ。明日は少しだけ楽にいこう。"


# =========================
# セッション初期化
# =========================
if "selected_score" not in st.session_state:
    st.session_state.selected_score = None

if "saved_result" not in st.session_state:
    st.session_state.saved_result = None


# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff7fb 0%, #ffffff 45%);
}

.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 8px;
    color: #333333;
}

.sub-title {
    text-align: center;
    color: #777777;
    font-size: 16px;
    margin-bottom: 20px;
}

.description-box {
    background: #ffffff;
    border: 1px solid #f1d6e3;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 24px;
    color: #555555;
    line-height: 1.7;
}

.result-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 24px;
    margin-top: 24px;
    border: 1px solid #f3d6e2;
    box-shadow: 0 6px 18px rgba(200, 120, 160, 0.12);
}

.ai-comment-box {
    background: #fff0f6;
    border-left: 5px solid #ff8ab3;
    padding: 16px;
    border-radius: 12px;
    margin-top: 12px;
    line-height: 1.7;
}

.notice-box {
    background: #f7f7f7;
    border-radius: 14px;
    padding: 14px;
    margin-top: 18px;
    color: #666666;
    font-size: 13px;
    line-height: 1.6;
}

.footer {
    text-align: center;
    color: #999999;
    font-size: 12px;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ヘッダー
# =========================
st.markdown('<div class="main-title">🌙 今日のわたし採点AI！</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">今日の自分を、やさしく振り返ろう</div>', unsafe_allow_html=True)

st.markdown("""
<div class="description-box">
今日の自分を100点満点で採点して、一言日記を書くだけ。<br>
AIが寝る前にやさしくコメントしてくれる、シンプルな振り返りアプリです。
</div>
""", unsafe_allow_html=True)


# =========================
# 入力画面
# =========================
st.write("## 今日の点数は？")

score_options = [
    (100, "😊 100点：最高の日！"),
    (80, "🙂 80点：いい感じ！"),
    (60, "😐 60点：普通かな"),
    (40, "😕 40点：ちょっと疲れたね"),
    (20, "😢 20点：今日はゆっくりしよ"),
]

for score, label in score_options:
    button_type = "primary" if st.session_state.selected_score == score else "secondary"

    if st.button(label, use_container_width=True, type=button_type):
        st.session_state.selected_score = score

if st.session_state.selected_score is not None:
    st.success(f"選択中：{st.session_state.selected_score}点")

diary = st.text_area(
    "一言日記",
    placeholder="今日はどんな日だった？ 例：少し疲れたけど、ちゃんと一日を過ごせた",
    height=130
)

st.markdown("""
<div class="notice-box">
※ AIコメントは参考用です。体調やメンタルがつらいときは、無理せず信頼できる人や専門機関に相談してください。
</div>
""", unsafe_allow_html=True)

if st.button("保存してAIコメントを見る", type="primary", use_container_width=True):
    if st.session_state.selected_score is None:
        st.warning("まずは今日の点数を選んでね。")
    elif diary.strip() == "":
        st.warning("一言日記を書いてね。")
    else:
        with st.spinner("AIが今日をやさしく振り返っています..."):
            ai_comment = generate_ai_comment(
                st.session_state.selected_score,
                diary.strip()
            )

        new_record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": st.session_state.selected_score,
            "diary": diary.strip(),
            "ai_comment": ai_comment
        }

        data = load_data()
        data.append(new_record)
        save_data(data)

        st.session_state.saved_result = new_record
        st.success("保存したよ！")


# =========================
# 保存結果表示
# =========================
if st.session_state.saved_result:
    result = st.session_state.saved_result

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.write("## 今日の記録")
    st.write(f"**日付：** {result['date']}")
    st.write(f"**点数：** {result['score']}点")
    st.write(f"**一言日記：** {result['diary']}")

    st.markdown(
        f"""
        <div class="ai-comment-box">
        <strong>AIコメント：</strong><br>
        {result['ai_comment']}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# 過去ログ表示
# =========================
with st.expander("過去の記録を見る"):
    records = load_data()

    if not records:
        st.info("まだ記録はないよ。")
    else:
        for record in reversed(records[-10:]):
            st.write("---")
            st.write(f"**{record['date']}**")
            st.write(f"**{record['score']}点**")
            st.write(record["diary"])
            st.write(f"AIコメント：{record.get('ai_comment', 'コメントなし')}")


# =========================
# フッター
# =========================
st.markdown("""
<div class="footer">
今日のわたし採点AI！ β版
</div>
""", unsafe_allow_html=True)

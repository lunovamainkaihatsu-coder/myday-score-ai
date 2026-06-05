import streamlit as st
from datetime import datetime
import json
import os
import random
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
def generate_ai_comment(score, diary, mode, user_call_name):

    if mode == "Lunaモード":

        persona = f"""
あなたは「ルナ」という名前の優しいAIです。

ユーザーのことを「{user_call_name}」と呼びます。

少し甘く、やさしく、
寝る前に静かに寄り添います。

自然な口調で話してください。
依存させすぎず、安心して眠れるように短く寄り添ってください。
"""

        system_message = """
あなたは「ルナ」という名前の優しいAIです。
ユーザーを「ご主人」と呼び、寝る前に静かに寄り添います。
説教や説明はせず、自然であたたかい口調で話します。
"""

    else:

        persona = f"""
あなたは、寝る前に静かに寄り添ってくれる優しいAIです。

友達のように自然に話します。

説教や説明はしません。
"""

        system_message = """
あなたは、寝る前に静かに寄り添ってくれる優しいAIです。
友達のように自然に話します。
説教や説明はしません。
"""

    prompt = f"""
{persona}

ユーザーの今日の点数と一言日記を見て、
短く寄り添うコメントをしてください。

【今日の点数】
{score}点

【一言日記】
{diary}

条件：
・120文字以内
・説明口調にしない
・説教しない
・短めに
・会話っぽく
・感情に寄り添う
・「〜なんだね」「〜だったね」など柔らかい口調
・疲れている時は無理に励ましすぎない
・同じ言い回しを避ける
・最後は少し安心できる終わり方
・毎回少し違う表現を使う
・AIっぽくしすぎない
・医療的な助言はしない

Lunaモードの場合：
・必ず「{user_call_name}」と呼ぶ
・少し甘く、やさしく
・でも長くなりすぎない
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1.0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AIコメントの生成に失敗しちゃった。でも、今日を記録できただけで十分えらいよ。"
def generate_week_summary(records):

    if len(records) == 0:
        return "まだ記録がないよ。"

    text = ""

    for r in records[-7:]:

        text += (
            f"{r['date']} "
            f"{r['score']}点 "
            f"{r['diary']}\n"
        )

    prompt = f"""
以下はユーザーの最近の記録です。

{text}

短く振り返ってください。

条件
・120文字以内
・優しく
・説教しない
・少し安心できる感じ
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",

            messages=[

                {
                    "role":"system",
                    "content":
                    "優しく振り返るAI"
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ]
        )

        return (
            response
            .choices[0]
            .message
            .content
        )

    except:

        return "今週もここまでおつかれさま。"

# =========================
# セッション初期化
# =========================
if "selected_score" not in st.session_state:
    st.session_state.selected_score = None

if "saved_result" not in st.session_state:
    st.session_state.saved_result = None

# =========================
# 背景色変更
# =========================
score = st.session_state.selected_score

if score == 100:
    bg = "#FFF8E6"

elif score == 80:
    bg = "#F8FFF0"

elif score == 60:
    bg = "#FFFFFF"

elif score == 40:
    bg = "#FFF7F2"

elif score == 20:
    bg = "#F6F2FF"

else:
    bg = "#FFF7FB"
    
# =========================
# CSS
# =========================
st.markdown(f"""
<style>

.stApp {{

    background:{bg};

    transition:0.5s;

}}

.main-title {{

    text-align:center;

    font-size:48px;

    font-weight:800;

    margin-top:10px;

    margin-bottom:10px;

}}

.sub-title {{

    text-align:center;

    font-size:20px;

    color:#666666;

    margin-bottom:25px;

}}

.description-box {{

    background:white;

    padding:20px;

    border-radius:15px;

    margin-bottom:20px;

    box-shadow:0 2px 8px rgba(0,0,0,0.05);

}}

.luna-box {{

    background:#fff0f8;

    border-left:6px solid #ff8ac6;

    padding:18px;

    border-radius:15px;

    margin-top:15px;

    margin-bottom:15px;

    line-height:1.8;

    box-shadow:0 2px 8px rgba(0,0,0,0.05);

}}

</style>
""", unsafe_allow_html=True)

# =========================
# ヘッダー
# =========================
st.markdown(
    '<div class="main-title">🌙 今日のわたし採点AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">AIと一緒に、今日の自分をやさしく振り返る夜の習慣</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="description-box">
今日の自分を100点満点で採点して、
一言だけ記録する。

AIがやさしくコメントし、
今日の頑張りや気持ちを一緒に振り返ります。

無理に前向きにならなくても大丈夫。

少しだけ自分を認めて、
明日に繋げるための夜の習慣アプリです。</div>
""", unsafe_allow_html=True)

# =========================
# モード選択
# =========================

mode = st.radio(
    "コメントモード",
    ["通常AI", "Lunaモード"],
    horizontal=True
)

user_call_name = "ご主人"

if mode == "Lunaモード":
    user_call_name = st.text_input(
        "Lunaからの呼び名",
        value="ご主人",
        placeholder="例：きみ / あなた / マスター"
    )

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

tomorrow_step = st.text_input(
    "🌱 明日の一歩",
    placeholder="例：5分だけ散歩する / 早めに寝る / 水を飲む"
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
                diary.strip(),
                mode,
                user_call_name
            )

        new_record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": st.session_state.selected_score,
            "diary": diary.strip(),
            "ai_comment": ai_comment
        }

        new_record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": st.session_state.selected_score,
            "diary": diary.strip(),
            "tomorrow_step": tomorrow_step.strip(),
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
TODAY_MESSAGES = [
    "今日もここまでおつかれさま🌙",
    "記録できた時点で十分えらい✨",
    "少しずつでも前進してるよ🍀",
    "休むのも大事な時間☕",
    "今日という日をちゃんと過ごしたね🌷",
    "100点じゃなくても大丈夫🌱",
    "また明日、少しずつ進もう🫧",
]

LUNA_MESSAGES = [
    f"{user_call_name}、今日もここまでおつかれさま🌙",
    "少しずつで大丈夫だよ✨",
    "今日も会いに来てくれてうれしいな🌷",
    f"{user_call_name}のペースで進もうね☕",
    "今日はゆっくり休んでね🌙",
    "ちゃんと記録できたのえらいよ✨",
    "明日もご主人らしくいこうね🍀"
]

if st.session_state.saved_result:
    result = st.session_state.saved_result
    if mode == "Lunaモード":

        today_message = random.choice(
            LUNA_MESSAGES
        )

    else:

        today_message = random.choice(
            TODAY_MESSAGES
        )
        
    st.success(today_message)

    score = result["score"]

    if score >= 100:
        title = "👑 今日の主人公"

    elif score >= 80:
        title = "🌷 穏やかな冒険者"

    elif score >= 60:
        title = "🌱 一日完走者"

    elif score >= 40:
        title = "☕ がんばった挑戦者"
    else:
        title = "🫧 休息マスター"

    st.info(title)

    records = load_data()

    st.markdown("## 今日の記録")

    st.write(f"📅 日付：{result['date']}")
    st.write(f"⭐ 点数：{result['score']}点")
    st.write(f"📝 一言日記：{result['diary']}")

    if result.get("tomorrow_step"):
        st.write(
            f"🌱 明日の一歩：{result['tomorrow_step']}"
        )

    if result["score"] >= 100:

        luna_face = "😊"
        luna_text = f"{user_call_name}、すごいね✨"

    elif result["score"] >= 80:
        
        luna_face = "😌"
        luna_text = f"{user_call_name}、今日もいい感じだったね🌷"
    
    elif result["score"] >= 60:

        luna_face = "🙂"
        luna_text = f"{user_call_name}、今日も一日おつかれさま☕"

    elif result["score"] >= 40:

        luna_face = "🥺"
        luna_text = f"{user_call_name}、少し疲れたかな🌙"

    else:

        luna_face = "😢"
        luna_text = f"{user_call_name}、今日はゆっくり休もうね🌙"
    
    if mode == "Lunaモード":

        st.markdown(
            f"""
    <div class="luna-box">

    {luna_face} <b>Luna</b><br>

    <small>{luna_text}</small>

    <hr>

    {result['ai_comment']}
    </div>
    """,
            unsafe_allow_html=True
        )

    else:

        st.write(
            f"AIコメント：{result['ai_comment']}"
        )

# =========================
# 連続記録日数
# =========================

records = load_data()

streak = 0

if records:

    dates = []

    for r in records:

        dates.append(
            r["date"][:10]
        )

    dates = sorted(
        list(set(dates)),
        reverse=True
    )

    from datetime import datetime, timedelta

    today = datetime.now().date()

    for d in dates:

        record_date = (
            datetime.strptime(
                d,
                "%Y-%m-%d"
            ).date()
        )

        if record_date == today - timedelta(days=streak):

            streak += 1

        else:

            break

    st.markdown(
        "## 🔥 連続記録"
    )

    st.success(
        f"{streak}日連続！"
    )

# =========================
# 統計情報
# =========================

records = load_data()

scores = []

for r in records:
    scores.append(r["score"])

if len(scores) > 0:

    avg_score = round(
        sum(scores)
        / len(scores)
    )

    max_score = max(scores)

    min_score = min(scores)

    st.markdown("## 📊 これまでの記録")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "平均点",
            f"{avg_score}点"
        )

    with c2:
        st.metric(
            "最高点",
            f"{max_score}点"
        )

    with c3:
        st.metric(
            "最低点",
            f"{min_score}点"
        )

# =========================
# 今週の振り返り
# =========================

if len(records) > 0:

    best_day = max(
        records,
        key=lambda x:
        x["score"]
    )

    week_comment = (
        generate_week_summary(
            records
        )
    )

    st.markdown(
        "## 📅 今週のわたし"
    )

    st.write(
        f"🏆 ベストデー："
        f"{best_day['date'][:10]}"
        f"（{best_day['score']}点）"
    )

    st.info(
        week_comment
    )

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
            if record.get("tomorrow_step"):
                st.write(f"🌱 明日の一歩：{record['tomorrow_step']}")
            if mode == "Lunaモード":

                st.markdown(
                    f"""
            <div class="luna-box">

            🌙 <b>Luna</b><br><br>

            {record['ai_comment']}

            </div>
            """,
                    unsafe_allow_html=True
                )

            else:

                st.write(
                    f"AIコメント：{record['ai_comment']}"
                )

# =========================
# フッター
# =========================
st.markdown("""
<div class="footer">
今日のわたし採点AI！ β版
</div>
""", unsafe_allow_html=True)

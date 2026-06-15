import streamlit as st
import random
import json
from datetime import datetime
from pathlib import Path
import os
from openai import OpenAI

st.set_page_config(
    page_title="今日の開発室 β",
    page_icon="🛠️",
    layout="wide"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

HISTORY = DATA_DIR / "history.json"

if not HISTORY.exists():
    HISTORY.write_text("[]", encoding="utf-8")


def load_history():
    try:
        with open(HISTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(data):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


themes = [
    "UI改善",
    "バグ修正",
    "新機能追加",
    "ブログを書く",
    "Noteを書く",
    "AI実験",
    "コード整理",
    "公開準備",
]

moods = ["😊", "🙂", "😐", "😵", "😴"]


def create_step(theme):
    ideas = {
        "UI改善": ["余白を10pxだけ調整", "タイトルを見やすくする", "色を1か所変更する"],
        "バグ修正": ["エラーを1個だけ直す", "例外処理を追加する", "不要コードを削除"],
        "新機能追加": ["ボタンだけ作る", "画面だけ作る", "保存処理だけ追加"],
        "ブログを書く": ["タイトルだけ考える", "導入100文字だけ書く", "見出しを作る"],
        "Noteを書く": ["冒頭だけ書く", "画像案だけ考える", "公開ボタン手前まで"],
        "AI実験": ["プロンプト1個試す", "モデル比較する", "出力だけ観察する"],
        "コード整理": ["関数1個整理", "変数名だけ改善", "コメント追加"],
        "公開準備": ["README更新", "スクショ撮影", "説明文を書く"],
    }

    return random.choice(ideas.get(theme, ["5分だけ進める"]))


def get_api_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def create_ai_step(theme, project, mood):
    api_key = get_api_key()

    if not api_key:
        return create_step(theme)

    client = OpenAI(api_key=api_key)

    history = load_history()

    recent_history = history[-3:]

    recent_text = ""

    for h in recent_history:

        recent_text += (
            f"- {h.get('project', '')} / "
            f"{h.get('theme', '')} / "
            f"{h.get('mood', '')}\n"
        )

    prompt = f"""
あなたは個人開発をやさしく支える相棒です。
以下の状況に合わせて、今日やる小さな一歩を1つだけ提案してください。

テーマ：{theme}
プロジェクト：{project}
気分：{mood}
最近の履歴：
{recent_text}

条件：
- 5〜15分でできる
- 具体的
- やさしい言葉
- 1文だけ
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは個人開発を支える優しい相棒です。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return create_step(theme)
    
def get_streak_days(history):

    streak = 0

    for h in reversed(history):

        if h.get("done", False):
            streak += 1
        else:
            break

    return streak

st.title("🛠️ 今日の開発室 β")
st.caption("今日、何を作る？")

history = load_history()

streak = get_streak_days(history)

st.info(f"🔥 連続達成回数：{streak}")

st.divider()

st.subheader("🤖 今日の開発を決める")

plan_project = st.text_input("作りたいもの", key="plan_project")
plan_mood = st.selectbox("今の気分", moods, key="plan_mood")

if st.button("🤖 AIに今日の開発を決めてもらう"):
    st.session_state.theme = random.choice(themes)
    st.session_state.step = create_ai_step(
        st.session_state.theme,
        plan_project,
        plan_mood
    )

if "theme" in st.session_state:
    st.success(f"今日のテーマ：{st.session_state.theme}")
    st.info(f"今日の一歩：{st.session_state.step}")

st.divider()

st.subheader("今日の記録")

record_project = st.text_input("作ったもの", key="record_project")

time = st.number_input(
    "作業時間（分）",
    0,
    600,
    15
)

record_mood = st.selectbox("今の気分", moods, key="record_mood")

if st.button("保存する"):
    history = load_history()

    history.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "project": record_project,
            "time": time,
            "mood": record_mood,
            "theme": st.session_state.get("theme", ""),
            "step": st.session_state.get("step", ""),
        }
    )

    save_history(history)

    st.success("保存した！")

st.divider()

st.subheader("履歴")

history = load_history()

if history:

    changed = False

    for i, h in enumerate(reversed(history[-10:])):

        real_index = len(history) - 1 - i

        with st.container(border=True):

            st.write(f"📅 {h.get('date', '')}")
            st.write(f"📝 {h.get('project', '')}")
            st.write(f"⏱️ {h.get('time', '')}分")
            st.write(f"💭 {h.get('mood', '')}")

            if h.get("theme"):
                st.write(f"🎯 {h.get('theme')}")

            if h.get("step"):
                st.write(f"👣 {h.get('step')}")

            completed = st.checkbox(
                "達成！",
                value=h.get("done", False),
                key=f"done_{real_index}"
            )

            if completed != h.get("done", False):
                history[real_index]["done"] = completed
                changed = True

            if completed:
                st.success("🎉 今日の一歩達成！")

    if changed:
        save_history(history)

else:
    st.caption("まだ履歴なし")

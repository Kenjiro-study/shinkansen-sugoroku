import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="新幹線すごろく", layout="wide")

# CSS調整（優勝者表示用のスタイルを追加）
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight:bold; }
    .stButton>button { width: 100%; height: 50px; font-size: 18px; border-radius: 8px; }
    [data-testid="stSidebar"] button { 
        background-color: #ff4b4b; 
        color: white; 
        font-weight: bold;
    }
    .winner-text {
        font-size: 50px;
        font-weight: bold;
        color: #ff4b4b;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# データ・定数定義
# ==========================================
EVENT_DECK_DATA = [
    {"name": "追加乗車＋", "weight": 15, "desc": "今日はもう少し進もう！\n**サイコロを振って出た目の数だけ進む。**"},
    {"name": "追加乗車ー", "weight": 15, "desc": "今日は少し戻ってみよう...\n**1〜3の好きな数だけ戻る。**"},
    {"name": "お土産の誘惑", "weight": 15, "desc": "お土産を見てたら乗り遅れた！\n**【1回休み】になる。**"},
    {"name": "旅の思い出",   "weight": 15, "desc": "窓から見える景色も思い出。\n**まだ誰も持っていないスタンプを1つゲットできる！**"},
    {"name": "思い出の共有", "weight": 15, "desc": "他の人の思い出を聞こう。\n**他の人を一人選んで、スタンプを1つもらう。**"},
    {"name": "博識（はくしき）", "weight": 10, "desc": "日本のことなら何でも知ってるぞ！\n**クイズの正解・不正解に関わらず、スタンプをゲット！**"},
    {"name": "新幹線乗り換え", "weight": 10, "desc": "速い新幹線に乗り換えだ！\n**もう一度サイコロを振って、出た目 × 2マス進む。**"},
    {"name": "幻のスタンプ帳", "weight": 5,  "desc": "すごいアイテムだ！\n**このターンに通ったマスのスタンプを全部ゲットできる！**"}
]

# ==========================================
# 関数
# ==========================================
@st.cache_data
def load_data():
    try:
        return pd.read_csv("quiz_data.csv")
    except FileNotFoundError:
        return None

df = load_data()

# ==========================================
# セッション状態の初期化
# ==========================================
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'game_ended' not in st.session_state: # ゲーム終了フラグを追加
    st.session_state.game_ended = False

if 'players' not in st.session_state:
    st.session_state.players = [] 
if 'current_player_idx' not in st.session_state:
    st.session_state.current_player_idx = 0 
if 'player_cards' not in st.session_state:
    st.session_state.player_cards = {} 

if 'stamp_owners' not in st.session_state:
    if df is not None:
        all_stations = df['駅名'].unique()
        st.session_state.stamp_owners = {station: None for station in all_stations}
    else:
        st.session_state.stamp_owners = {}

if 'dice_count' not in st.session_state:
    st.session_state.dice_count = 0
if 'dice_result' not in st.session_state:
    st.session_state.dice_result = None
if 'current_station_data' not in st.session_state:
    st.session_state.current_station_data = None


# ==========================================
# フェーズ1: ゲーム開始前の設定画面
# ==========================================
if not st.session_state.game_started:
    st.title("🚄 新幹線すごろく セットアップ")
    
    if df is None:
        st.error("エラー：'quiz_data.csv' が見つかりません。フォルダに配置してください。")
    else:
        st.write("まずはプレイヤーを登録してね！")
        num_players = st.number_input("プレイする人数", min_value=1, max_value=6, value=2)
        
        with st.form("setup_form"):
            player_names = []
            for i in range(num_players):
                name = st.text_input(f"プレイヤー {i+1} の名前", value=f"プレイヤー{i+1}")
                player_names.append(name)
            
            submitted = st.form_submit_button("ゲームスタート！")
            
            if submitted:
                st.session_state.players = player_names
                st.session_state.player_cards = {name: [] for name in player_names}
                all_stations = df['駅名'].unique()
                st.session_state.stamp_owners = {station: None for station in all_stations}
                st.session_state.game_started = True
                st.session_state.game_ended = False
                st.rerun()

# ==========================================
# フェーズ3: ゲーム終了画面（優勝発表）
# ==========================================
elif st.session_state.game_ended:
    st.balloons() # 紙吹雪エフェクト！
    
    st.title("🎉 結果発表 🎉")
    
    # スタンプ集計
    counts = {p: 0 for p in st.session_state.players}
    for owner in st.session_state.stamp_owners.values():
        if owner in counts:
            counts[owner] += 1
    
    # ランキング作成
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    winner_name = sorted_counts[0][0]
    winner_score = sorted_counts[0][1]
    
    # 優勝者表示
    st.markdown(f"<div class='winner-text'>🏆 優勝 🏆<br>{winner_name} さん！</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;'>獲得スタンプ：{winner_score}枚</h3>", unsafe_allow_html=True)
    
    st.divider()
    
    # 全員のランキング表示
    st.subheader("📊 最終ランキング")
    for rank, (p, count) in enumerate(sorted_counts, 1):
        if rank == 1:
            st.markdown(f"### 🥇 {rank}位: {p} ({count}枚)")
        elif rank == 2:
            st.markdown(f"#### 🥈 {rank}位: {p} ({count}枚)")
        elif rank == 3:
            st.markdown(f"#### 🥉 {rank}位: {p} ({count}枚)")
        else:
            st.write(f"{rank}位: {p} ({count}枚)")
            
    st.divider()
    
    if st.button("もう一度遊ぶ"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# フェーズ2: メインゲーム画面
# ==========================================
else:
    current_player = st.session_state.players[st.session_state.current_player_idx]
    
    # --- サイドバー ---
    with st.sidebar:
        st.title("🎮 進行状況")
        st.info(f"今は\n\n**{current_player}**\n\nさんの番です")
        
        st.write("---")
        if st.button("次のプレイヤーへ交代 ⏭️"):
            st.session_state.current_player_idx = (st.session_state.current_player_idx + 1) % len(st.session_state.players)
            st.session_state.dice_result = None
            st.session_state.current_station_data = None
            st.rerun()
            
        st.write("---")
        # ゲーム終了ボタン
        if st.button("🏁 ゲーム終了して結果を見る"):
            st.session_state.game_ended = True
            st.rerun()
            
        st.write("---")
        st.write("📊 **スタンプ獲得数**")
        counts = {p: 0 for p in st.session_state.players}
        for owner in st.session_state.stamp_owners.values():
            if owner in counts:
                counts[owner] += 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for p, count in sorted_counts:
            marker = "👉" if p == current_player else "　"
            st.write(f"{marker} **{p}**: {count}枚")
        
        st.write("---")
        if st.button("ゲームをリセット", type="secondary"):
             st.session_state.clear()
             st.rerun()

    # --- メインエリア ---
    st.title(f"🚄 新幹線すごろく ({current_player}のターン)")

    tab1, tab2, tab3, tab4 = st.tabs(["🎲 サイコロ", "❓ クイズ", "🎒 アイテム", "💮 スタンプ"])

    # タブ1: サイコロ
    with tab1:
        st.header(f"{current_player} さん、サイコロを振ってね")
        col1, col2 = st.columns([1, 2])
        with col1:
             if st.button("サイコロを振る！", key="dice_btn"):
                st.session_state.dice_count += 1
                st.session_state.dice_result = random.randint(1, 6)
        with col2:
            if st.session_state.dice_result is not None:
                st.markdown(f"<div style='font-size:80px; font-weight:bold; color:#0066cc;'>🎲 {st.session_state.dice_result}</div>", unsafe_allow_html=True)
                num = st.session_state.dice_result
                if num >= 5:
                    st.success("たくさん進めるね！🚀")

    # タブ2: クイズ
    with tab2:
        st.header("駅のクイズ")
        st.write("ランダムに問題が出るよ！")
        if df is not None:
            if st.button("問題を出題する！", key="quiz_btn"):
                st.session_state.current_station_data = df.sample(1).iloc[0]
            
            if st.session_state.current_station_data is not None:
                station_data = st.session_state.current_station_data
                st.divider()
                st.markdown(f"### 📍 {station_data['駅名']}駅")
                st.markdown(f"<div class='big-font'>{station_data['問題文']}</div>", unsafe_allow_html=True)
                st.write("") 
                if pd.notna(station_data['選択肢A']):
                    st.markdown(f"**A.** {station_data['選択肢A']}")
                    st.markdown(f"**B.** {station_data['選択肢B']}")
                    st.markdown(f"**C.** {station_data['選択肢C']}")
                st.write("---")
                with st.expander("答えを見る"):
                    st.markdown(f"### 正解は... **{station_data['正解']}**")
                    if '解説' in df.columns and pd.notna(station_data['解説']):
                        st.info(f"💡 解説：{station_data['解説']}")

    # タブ3: イベントカード
    with tab3:
        st.header(f"🎒 {current_player} のアイテム")
        st.write("##### ▼ カードを引く")
        
        if st.button("イベントカードを引く！", key="draw_card"):
            weights = [card['weight'] for card in EVENT_DECK_DATA]
            drawn_card = random.choices(EVENT_DECK_DATA, weights=weights, k=1)[0].copy()
            st.session_state.player_cards[current_player].append(drawn_card)
            st.success(f"「{drawn_card['name']}」を手に入れた！")
            st.rerun()

        st.divider()
        st.write(f"##### ▼ {current_player} が持っているカード")
        my_cards = st.session_state.player_cards[current_player]
        
        if len(my_cards) == 0:
            st.info("まだカードを持っていません")
        else:
            for i, card in enumerate(my_cards):
                with st.expander(f"🎫 {card['name']}"):
                    st.write(card['desc']) 
                    if st.button("このカードを使う", key=f"use_{i}"):
                        my_cards.pop(i)
                        st.session_state.player_cards[current_player] = my_cards
                        st.success(f"「{card['name']}」を使った！")
                        st.rerun()

    # タブ4: スタンプ管理
    with tab4:
        st.header("💮 スタンプ帳")
        
        st.subheader("📍 新しいスタンプをゲット！")
        st.write("まだ誰も持っていないスタンプから検索してゲットできます。")
        available_stations = [s for s, owner in st.session_state.stamp_owners.items() if owner is None]
        
        if available_stations:
            col_get1, col_get2 = st.columns([3, 1])
            with col_get1:
                target_station = st.selectbox("駅を選択（文字入力で検索できます）", available_stations)
            with col_get2:
                if st.button("ゲットする！", key="get_stamp"):
                    st.session_state.stamp_owners[target_station] = current_player
                    st.success(f"やった！ {current_player} が「{target_station}」のスタンプをゲットした！")
                    st.rerun()
        else:
            st.info("すべてのスタンプが誰かに取られました！ここからは奪い合いです！")

        st.divider()

        st.subheader("🎁 スタンプの移動（イベント用）")
        st.write("イベントでスタンプを渡したり、奪ったりする時はここを使ってね。")
        col_move1, col_move2, col_move3 = st.columns(3)
        with col_move1:
            from_player = st.selectbox("誰から？", st.session_state.players, index=st.session_state.current_player_idx)
        from_player_stamps = [s for s, owner in st.session_state.stamp_owners.items() if owner == from_player]
        with col_move2:
            if from_player_stamps:
                move_station = st.selectbox("どのスタンプを？", from_player_stamps)
            else:
                move_station = None
                st.warning("スタンプを持っていません")
        with col_move3:
            to_player = st.selectbox("誰へ？", st.session_state.players)
        if st.button("スタンプを移動させる"):
            if move_station and from_player != to_player:
                st.session_state.stamp_owners[move_station] = to_player
                st.success(f"「{move_station}」のスタンプが {from_player} から {to_player} に移動しました！")
                st.rerun()
            elif from_player == to_player:
                st.error("自分には移動できません")
            else:
                st.error("移動できるスタンプがありません")

        st.divider()
        st.subheader("📊 みんなのスタンプ状況")
        for p in st.session_state.players:
            p_stamps = [s for s, owner in st.session_state.stamp_owners.items() if owner == p]
            with st.expander(f"{p} のスタンプ ({len(p_stamps)}枚)"):
                if p_stamps:
                    st.write(" / ".join(p_stamps))
                else:
                    st.write("なし")
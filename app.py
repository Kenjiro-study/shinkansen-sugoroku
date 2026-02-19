import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="新幹線すごろく", layout="wide")

# CSS調整
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
    .score-detail {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ボーナスルールの定義
# ==========================================
BONUS_RULES = [
    {
        "name": "🐮 北海道新幹線好き",
        "stations": ["札幌", "新小樽", "倶知安", "長万部", "新八雲", "新函館北斗", "木古内", "奥津軽いまべつ", "新青森"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "👹 秋田新幹線好き",
        "stations": ["秋田", "大曲", "角館", "田沢湖", "雫石", "盛岡"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🍒 山形新幹線好き",
        "stations": ["新庄", "大石田", "村山", "さくらんぼ東根", "天童", "山形", "かみのやま温泉", "赤湯", "高畠", "米沢", "福島"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🚄 東北新幹線好き",
        "stations": ["新青森", "七戸十和田", "八戸", "二戸", "いわて沼宮内", "盛岡", "新花巻", "北上", "水沢江刺", "一ノ関", "くりこま高原", "古川", "仙台", "白石蔵王", "福島", "郡山", "新白河", "那須塩原", "宇都宮", "小山"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🌾 上越新幹線好き",
        "stations": ["大宮", "高崎", "上毛高原", "越後湯沢", "浦佐", "長岡", "燕三条", "新潟"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🦀 北陸新幹線好き",
        "stations": ["安中榛名", "軽井沢", "佐久平", "上田", "長野", "飯山", "上越妙高", "糸魚川", "黒部宇奈月温泉", "富山", "新高岡", "金沢", "小松", "加賀温泉", "福井", "芦原温泉", "越前たけふ", "敦賀"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🗻 東海道新幹線好き",
        "stations": ["新大阪", "京都", "米原", "岐阜羽島", "名古屋", "三河安城", "豊橋", "浜松", "掛川", "静岡", "新富士", "三島", "熱海", "小田原", "新横浜", "品川", "東京"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🍑 山陽新幹線好き",
        "stations": ["新神戸", "西明石", "姫路", "相生", "岡山", "新倉敷", "福山", "新尾道", "三原", "東広島", "広島", "新岩国", "徳山", "新山口", "厚狭", "新下関", "小倉"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🕊️ 西九州新幹線好き",
        "stations": ["新鳥栖", "武雄温泉", "嬉野温泉", "新大村", "諫早", "長崎"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🐻 九州新幹線好き",
        "stations": ["博多", "新鳥栖", "久留米", "筑後船小屋", "新大牟田", "新玉名", "熊本", "新八代", "新水俣", "出水", "川内", "鹿児島中央"],
        "type": "any", "threshold": 5, "points": 5
    },
    {
        "name": "🍊 四国制覇",
        "stations": ["松山", "高知", "高松", "徳島"],
        "type": "all", "points": 3
    },
    {
        "name": "♨️ 温泉制覇",
        "stations": ["かみのやま温泉", "黒部宇奈月温泉", "加賀温泉", "芦原温泉", "嬉野温泉", "武雄温泉"],
        "type": "all", "points": 7
    },
    {
        "name": "⛰️ 「山」がつく駅制覇",
        "stations": ["村山", "山形", "郡山", "小山", "飯山", "富山", "岡山", "福山", "徳山", "新山口", "松山"],
        "type": "all", "points": 10
    },
    {
        "name": "🏙️ 大都市制覇",
        "stations": ["東京", "新大阪", "名古屋"],
        "type": "all", "points": 3
    },
    {
        "name": "🏁 スタートとゴール",
        "stations": ["札幌", "東京"],
        "type": "all", "points": 5
    }
]

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

def calculate_score(player_name, stamp_owners):
    """
    プレイヤーの得点と内訳（マッチした駅名含む）を計算する関数
    """
    my_stamps = [s for s, owner in stamp_owners.items() if owner == player_name]
    
    base_score = len(my_stamps)
    total_score = base_score
    # スタンプ数の内訳にも、何のスタンプを持っているかを記録
    details = [{"name": "🎫 スタンプ数", "points": base_score, "matched_stations": my_stamps}]
    
    my_stamps_set = set(my_stamps)
    
    for rule in BONUS_RULES:
        target_stations = set(rule["stations"])
        match_stations = list(my_stamps_set & target_stations)
        match_count = len(match_stations)
        
        bonus_points = 0
        if rule["type"] == "any":
            if match_count >= rule["threshold"]:
                bonus_points = rule["points"]
        elif rule["type"] == "all":
            if match_count == len(target_stations):
                bonus_points = rule["points"]
        
        if bonus_points > 0:
            total_score += bonus_points
            details.append({
                "name": rule["name"], 
                "points": bonus_points, 
                "matched_stations": match_stations # 影響した駅を記録
            })
            
    return total_score, details

def go_to_next_player():
    """
    ゴールしていない次のプレイヤーへ順番を回す関数。
    全員ゴールしていたらゲーム終了フラグを立てる。
    """
    if len(st.session_state.finished_players) >= len(st.session_state.players):
        st.session_state.game_ended = True
        return
        
    current = st.session_state.current_player_idx
    for _ in range(len(st.session_state.players)):
        current = (current + 1) % len(st.session_state.players)
        if st.session_state.players[current] not in st.session_state.finished_players:
            st.session_state.current_player_idx = current
            break
            
    st.session_state.dice_result = None
    st.session_state.current_station_data = None

df = load_data()

# ==========================================
# セッション状態の初期化
# ==========================================
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'game_ended' not in st.session_state:
    st.session_state.game_ended = False

if 'players' not in st.session_state:
    st.session_state.players = [] 
if 'current_player_idx' not in st.session_state:
    st.session_state.current_player_idx = 0 
if 'player_cards' not in st.session_state:
    st.session_state.player_cards = {} 
if 'finished_players' not in st.session_state:
    st.session_state.finished_players = [] # ゴールした人のリスト

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
if 'used_quiz_indices' not in st.session_state:
    st.session_state.used_quiz_indices = []


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
                st.session_state.used_quiz_indices = []
                st.session_state.finished_players = []
                st.session_state.game_started = True
                st.session_state.game_ended = False
                st.rerun()

# ==========================================
# フェーズ3: ゲーム終了画面（優勝発表）
# ==========================================
elif st.session_state.game_ended:
    st.balloons()
    
    st.title("🎉 結果発表 🎉")
    st.write("最終得点（スタンプ数 ＋ ボーナス点）で順位が決まります！")
    
    results = []
    for p in st.session_state.players:
        score, details = calculate_score(p, st.session_state.stamp_owners)
        results.append({"player": p, "score": score, "details": details})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    winner = results[0]
    
    st.markdown(f"<div class='winner-text'>🏆 優勝 🏆<br>{winner['player']} さん！</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;'>獲得スコア：{winner['score']}点</h3>", unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("📊 最終ランキングと内訳")
    for rank, res in enumerate(results, 1):
        player_name = res["player"]
        score = res["score"]
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}位"
        
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"### {medal} {player_name}")
                st.markdown(f"**合計: {score}点**")
            with col2:
                with st.expander("得点の内訳を見る"):
                    for d in res["details"]:
                        # 影響した駅のリストを文字列にする
                        if d['matched_stations']:
                            matched_str = "、".join(d['matched_stations'])
                        else:
                            matched_str = "なし"
                        
                        st.write(f"・{d['name']}： **+{d['points']}点**")
                        # その下に小さく影響した駅名を表示
                        st.markdown(f"<span style='color:#666; font-size:14px;'>　({matched_str})</span>", unsafe_allow_html=True)
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
        
        st.write("▼ 参加プレイヤー")
        for p in st.session_state.players:
            if p in st.session_state.finished_players:
                st.write(f"🎉 **{p}** <span style='color:#888;'>(ゴール済み)</span>", unsafe_allow_html=True)
            elif p == current_player:
                st.write(f"👉 **{p}**")
            else:
                st.write(f"　 {p}")
                
        st.write("---")
        
        if st.button("次のプレイヤーへ交代 ⏭️"):
            go_to_next_player()
            st.rerun()
            
        # ★追加：ゴールボタン
        if st.button("🏁 ゴール！（上がり）"):
            st.session_state.finished_players.append(current_player)
            st.success(f"🎉 {current_player} さんがゴールしました！")
            go_to_next_player() # ゴールしたら自動で次の人へ
            st.rerun()
            
        st.write("---")
        st.write("📊 **現在のスタンプ数**")
        counts = {p: 0 for p in st.session_state.players}
        for owner in st.session_state.stamp_owners.values():
            if owner in counts:
                counts[owner] += 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for p, count in sorted_counts:
            marker = "👉" if p == current_player else "　"
            st.write(f"{marker} **{p}**: {count}枚")
            
        st.write("---")
        with st.expander("開発者メニュー"):
            if st.button("強制終了して結果を見る"):
                st.session_state.game_ended = True
                st.rerun()
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
        st.write("ランダムに問題が出るよ！（同じ問題は出ないようになってるよ）")
        if df is not None:
            if st.button("問題を出題する！", key="quiz_btn"):
                all_indices = df.index.tolist()
                available_indices = [i for i in all_indices if i not in st.session_state.used_quiz_indices]
                
                if not available_indices:
                    st.session_state.used_quiz_indices = [] 
                    available_indices = all_indices 
                    st.toast("全問制覇おめでとう！問題がリセットされました♻️") 
                
                chosen_index = random.choice(available_indices)
                st.session_state.used_quiz_indices.append(chosen_index)
                st.session_state.current_station_data = df.loc[chosen_index]
            
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
# 遊戲後端主程式 (app.py) - UC劇本衛教強化版 (邏輯修正)

from flask import Flask, jsonify, request, session
from flask_session import Session
import secrets
from flask_cors import CORS
from flask import render_template

# --- 初始化 Flask 應用 ---
app = Flask(__name__)
CORS(app, supports_credentials=True) 
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = secrets.token_hex(16)
Session(app)

@app.route('/')
def index():
    """首頁路由，返回遊戲說明頁面"""
    return render_template('index.html')


# --- 【全新優化】遊戲核心數據 (UC劇本衛教與劇情強化版) ---
game_data = {
    "scene_1_home": {
        "start_node": "HOME_1",
        "nodes": {
            "HOME_1": {"type": "dialogue", "speaker": "旁白", "text": "清晨的陽光透過窗簾的縫隙灑入房間，你蜷縮在床上，腹部一陣陣的刺痛讓你不得不醒來。", "next": "HOME_2"},
            "HOME_2": {"type": "dialogue", "speaker": "小信", "text": "嗚…又開始了…不只是肚子痛，還一直拉肚子，糞便裡好像混著血跟黏液…整個人都快虛脫了。", "next": "HOME_3"},
            "HOME_3": {"type": "dialogue", "speaker": "媽媽", "text": "小信，你臉色怎麼這麼蒼白？這樣反反覆覆也不是辦法，體重都掉了不少。我們去看醫生好不好？", "next": "HOME_4"},
            "HOME_4": {"type": "dialogue", "speaker": "小信", "text": "可是…我好累，完全沒力氣…", "next": "HOME_5"},
            "HOME_5": { "type": "choice", "speaker": "媽媽", "text": "我知道你很難受。隔壁王阿姨說她有個偏方很有效，說不定…", "choices": [ {"text": "（既然是王阿姨的好意…試試看吧。）", "action": "TRY_REMEDY"}, {"text": "（媽，我怕亂吃會更嚴重，我們還是去看醫生。）", "action": "SEE_DOCTOR"} ] },
            "REMEDY_1": { "type": "dialogue", "speaker": "旁白", "text": "你喝下了王阿姨給的草藥湯，味道很苦澀。當晚，你的腹痛不但沒有減輕，反而更加劇烈，甚至開始發燒。", "next": "REMEDY_2", "image": "assets/herb_soup.png" },
            "REMEDY_2": {"type": "dialogue", "speaker": "媽媽", "text": "（驚慌）怎麼會這樣！都是媽不好，不該讓你亂試偏方！我們現在馬上去掛急診！", "action": "GO_TO_CLINIC_URGENT"}
        }
    },
    "scene_2_clinic": {
        "start_node": "CLINIC_1",
        "nodes": {
            "CLINIC_1": {"type": "dialogue", "speaker": "周醫師", "text": "小信，別緊張。根據你反覆腹痛、血便、體重減輕和疲倦的症狀，我懷疑是『發炎性腸道疾病』(Inflammatory Bowel Disease, IBD)。", "next": "CLINIC_2"},
            "CLINIC_2": {"type": "dialogue", "speaker": "小信", "text": "IBD？那到底是什麼？", "next": "CLINIC_3"},
            "CLINIC_3": {"type": "dialogue", "speaker": "周醫師", "text": "IBD主要分成兩大類：『潰瘍性結腸炎(UC)』和『克隆氏症(CD)』。它們都是慢性、反覆發作的自體免疫疾病，簡單說，就是免疫系統失調，轉而攻擊自己的腸道。", "next": "CLINIC_4"},
            "CLINIC_4": {"type": "dialogue", "speaker": "周醫師", "text": "這兩種病的好發年齡有點不同，潰瘍性結腸炎常見於 20-35 歲的年輕人；克隆氏症則有兩個高峰，一個是年輕人，另一個是 40-60 歲的中年族群。", "next": "CLINIC_5"},
            "CLINIC_5": {"type": "dialogue", "speaker": "周醫師", "text": "為了確定你是哪一種類型，我們會需要做一系列檢查。首先是抽血和糞便檢測，評估發炎指數和排除感染。最重要的，是安排『結腸鏡』檢查。", "next": "CLINIC_6"},
            "CLINIC_6": {"type": "dialogue", "speaker": "周醫師", "text": "透過結腸鏡，我們可以看見你腸道黏膜的實際狀況，並取一點組織做病理化驗。這是確診最關鍵的一步。", "next": "CLINIC_7"},
            "CLINIC_7": {"type": "dialogue", "speaker": "小信", "text": "聽起來好複雜…我的人生是不是完蛋了…", "next": "CLINIC_8"},
            "CLINIC_8": {"type": "dialogue", "speaker": "伶娜護理師", "text": "小信，請不要這麼想！我是你的個管護理師伶娜。對抗IBD需要一個團隊，而你就是團隊的核心！我們醫師、護理師，大家都會一起協助你。", "next": "CLINIC_9"},
            "CLINIC_9": { "type": "event", "action": "FINISH_DIAGNOSIS", "text": "經過一系列檢查，你的報告顯示發炎範圍集中在大腸的表層黏膜。周醫師診斷你為IBD中的『潰瘍性結腸炎(UC)』。你看著報告，心情沈重，但護理師溫暖的話語給了你一絲力量。", "next_scene": "scene_3_treatment_plan" }
        }
    },
    "scene_3_treatment_plan": {
        "start_node": "PLAN_1",
        "nodes": {
            "PLAN_1": {"type": "dialogue", "speaker": "周醫師", "text": "小信，你的診斷是潰瘍性結腸炎。首先你要理解，IBD雖然目前無法『根治』，但我們的治療目標非常明確：透過藥物控制發炎，讓腸道黏膜癒合，進入沒有症狀的『緩解期』。", "next": "PLAN_2"},
            "PLAN_2": {"type": "dialogue", "speaker": "周醫師", "text": "治療分為兩階段：『誘導緩解』，也就是用藥快速壓下急性發炎；再來是『維持緩解』，用藥物讓你好不容易穩定的腸道，不再輕易復發。所以，即使不痛了，也要規律用藥，這非常重要。", "next": "PLAN_3"},
            "PLAN_3": {"type": "dialogue", "speaker": "周醫師", "text": "為了確保你了解自己的『武器』，我們來做個小測驗吧。了解藥物是治療成功的第一步！", "next": "MINIGAME_MEDS_1"},
            
            "MINIGAME_MEDS_1": { "type": "minigame", "game_type": "medication_quiz", "data": { "question": "問題一：我最先拿到的基礎藥物 5-ASA (氨基水楊酸)，它的主要作用是什麼？", "options": ["A. 強力止痛，痛的時候才吃", "B. 抑制腸道黏膜發炎，是維持緩解的基礎藥物", "C. 殺死腸道壞菌的抗生素", "D. 補充維他命，增強體力", "E. 讓自己快速進入睡眠"], "correct_answer": "B. 抑制腸道黏膜發炎，是維持緩解的基礎藥物" }, "success_node": "MEDS_SUCCESS_1", "failure_node": "MEDS_FAIL_1" },
            "MEDS_SUCCESS_1": {"type": "dialogue", "speaker": "周醫師", "text": "完全正確！5-ASA是透過抗發炎作用來幫助腸道黏膜癒合的。下一題！", "next": "MINIGAME_MEDS_2"},
            "MEDS_FAIL_1": {"type": "dialogue", "speaker": "伶娜護理師", "text": "不對喔。5-ASA是『抗發炎』藥物，不是止痛藥，必須規律服用才能穩定控制發炎。沒關係，我們看下一題。", "next": "MINIGAME_MEDS_2"},

            "MINIGAME_MEDS_2": { "type": "minigame", "game_type": "medication_quiz", "data": { "question": "問題二：當急性發作較嚴重時，醫師可能會開立『皮質類固醇』(俗稱美國仙丹)，關於它的敘述何者正確？", "options": ["A. 它是保養品，可以長期每天使用", "B. 因為沒副作用，可以自行增加劑量", "C. 主要用於『誘導緩解』，快速降低發炎，但不適合長期維持治療", "D. 它可以治癒IBD", "E. 它是一種益生菌"], "correct_answer": "C. 主要用於『誘導緩解』，快速降低發炎，但不適合長期維持治療" }, "success_node": "MEDS_SUCCESS_2", "failure_node": "MEDS_FAIL_2" },
            "MEDS_SUCCESS_2": {"type": "dialogue", "speaker": "周醫師", "text": "很好！類固醇是快速壓制發炎的利器，但因長期使用的副作用，我們的目標都是盡快讓你能『脫離』類固醇治療。最後一題！", "next": "MINIGAME_MEDS_3"},
            "MEDS_FAIL_2": {"type": "dialogue", "speaker": "伶娜護理師", "text": "這個觀念很重要喔！類固醇主要是快速『誘導緩解』，但不適合長期用來『維持』病情。我們的目標是穩定後就減量停用。記住了嗎？來看最後一題。", "next": "MINIGAME_MEDS_3"},

            "MINIGAME_MEDS_3": { "type": "minigame", "game_type": "medication_quiz", "data": { "question": "問題三：如果傳統藥物效果不佳，醫師可能會建議使用『生物製劑』，它的主要特色是？", "options": ["A. 它是從植物萃取的草藥", "B. 它是一種價格便宜的成藥", "C. 它可以讓體重快速增加", "D. 它是標靶治療，能精準抑制體內特定的發炎因子，副作用相對較小", "E. 它是一種灌腸劑，從肛門給藥"], "correct_answer": "D. 它是標靶治療，能精準抑制體內特定的發炎因子，副作用相對較小" }, "success_node": "MEDS_SUCCESS_3", "failure_node": "MEDS_FAIL_3" },
            "MEDS_SUCCESS_3": {"type": "dialogue", "speaker": "周醫師", "text": "太棒了！你對藥物的理解非常到位！生物製劑是我們治療IBD很重要的武器，能幫助許多病友達成『黏膜癒合』的目標。", "next": "PLAN_4"},
            "MEDS_FAIL_3": {"type": "dialogue", "speaker": "伶娜護理師", "text": "生物製劑是比較新的『標靶藥物』，能精準地抑制發炎反應。它不是草藥或成藥，是需要醫師處方並定期注射的。記住，有任何藥物問題，一定要跟我們團隊討論！", "next": "PLAN_4"},
            
            "PLAN_4": {"type": "dialogue", "speaker": "伶娜護理師", "text": "小信，藥物之外，『營養』是我們另一個重要的武器。很多病友會問，是不是什麼都不能吃了？其實不是的。", "next": "PLAN_5"},
            "PLAN_5": {"type": "dialogue", "speaker": "伶娜護理師", "text": "在疾病『緩解期』，你應該盡量維持均衡飲食，跟健康的人一樣。但在現在這種『發作期』，飲食就需要特別調整，目標是讓腸道休息。", "next": "PLAN_6"},
            "PLAN_6": {"type": "dialogue", "speaker": "伶娜護理師", "text": "所以我們要選擇『低渣、易消化』的食物。例如白飯、麵條、去皮的雞肉和魚肉、蒸蛋、過濾的果汁、去皮去籽的瓜類水果等。 要避免油炸、辛辣、纖維粗的蔬菜(如芹菜、牛蒡)和含糖飲料。", "next": "PLAN_7"},
            "PLAN_7": { "type": "event", "action": "FINISH_TREATMENT_PLAN", "text": "你從醫師和護理師那裡得到了完整的治療計畫，感覺對於未來要如何面對這個疾病，有了一個更清晰的方向。", "next_scene": "scene_4_daily_life" }
        }
    },
    "scene_4_daily_life": {
        "start_node": "DAILY_1",
        "nodes": {
            "DAILY_1": {"type": "dialogue", "speaker": "旁白", "text": "出院回家後，你開始了與IBD共存的新生活。你每天按時服藥，並試著遵循護理師的建議。", "next": "DAILY_2"},
            "DAILY_2": {"type": "dialogue", "speaker": "阿誠", "text": "（訊息聲）小信！好點沒？晚上出來吃個麻辣鍋跟炸雞，慶祝你出院啊！", "next": "DAILY_3"},
            "DAILY_3": {"type": "dialogue", "speaker": "小信內心", "text": "（好想吃…但我記得伶娜護理師說過，發作期飲食要特別注意…現在的我，應該吃什麼才對呢？）", "next": "MINIGAME_DIET"},
            "MINIGAME_DIET": { "type": "minigame", "game_type": "diet_selection", "data": { "prompt": "現在是[b]發炎急性期[/b]，我該選擇哪些「低渣、易消化」的食物呢？ (最多選5樣)", "safe_foods": [ {"name": "白飯", "image": "assets/food_rice.png"}, {"name": "麵條", "image": "assets/food_noodles.png"}, {"name": "魚肉", "image": "assets/food_fish.png"}, {"name": "蒸蛋", "image": "assets/food_steamed_egg.png"} ], "trigger_foods": [ {"name": "炸雞", "image": "assets/food_fried_chicken.png"}, {"name": "麻辣鍋", "image": "assets/food_hot_pot.png"}, {"name": "生菜沙拉", "image": "assets/food_salad.png"}, {"name": "含糖飲料", "image": "assets/food_soda.png"} ] }, "success_node": "DIET_GOOD", "failure_node": "DIET_FAIL" },
            "DIET_PERFECT": {"type": "dialogue", "speaker": "小信", "text": "（回訊息）「謝啦！但我現在只能吃清淡點的，改天等我狀況更好再約！」你為自己做出正確的選擇感到自豪。", "next": "DAILY_4"},
            "DIET_GOOD": {"type": "dialogue", "speaker": "小信", "text": "（回訊息）「謝啦！但我現在只能吃清淡點的，改天再約！」雖然有點遺憾，但你知道這是正確的決定。", "next": "DAILY_4"},
            "DIET_FAIL": {"type": "dialogue", "speaker": "旁白", "text": "你終究沒能抵擋誘惑，或選錯了食物。當晚，熟悉的腹痛再次來襲…「唉…早知道就該聽護理師的話…」", "next": "DAILY_4"},
            "DAILY_4": { "type": "event", "action": "FINISH_DAILY_LIFE", "text": "你開始學習如何在日常生活中做出選擇，這不僅關乎食物，也關乎如何與疾病共處。", "next_scene": "scene_5_long_term" }
        }
    },
    "scene_5_long_term": {
        "start_node": "LONGTERM_1",
        "nodes": {
            "LONGTERM_1": {"type": "dialogue", "speaker": "旁白", "text": "幾個月過去了，在藥物和飲食的控制下，你的症狀逐漸穩定下來，進入了『緩解期』。", "next": "LONGTERM_2"},
            "LONGTERM_2": {"type": "dialogue", "speaker": "周醫師", "text": "小信，回診狀況看起來不錯。最近都沒什麼症狀了吧？記得，即使感覺良好，維持用藥也非常重要。", "next": "LONGTERM_3"},
            "LONGTERM_3": {"type": "dialogue", "speaker": "周醫師", "text": "研究顯示，在緩解期擅自停藥的病人，復發的風險遠高於持續服藥的病人。我們的目標是『長期、穩定』的控制，這需要你和我們一起努力。", "next": "LONGTERM_4"},
            "LONGTERM_4": {"type": "dialogue", "speaker": "小信", "text": "醫師，我知道了。不過有時候面對朋友或課業壓力，還是會覺得很焦慮…", "next": "LONGTERM_5"},
            "LONGTERM_5": {"type": "dialogue", "speaker": "伶娜護理師", "text": "小信，這是很正常的。壓力雖然不會『直接引起』IBD，但確實可能使症狀惡化。除了和家人朋友聊聊，也可以尋求心理健康專業人士的幫助，或者參加病友支持團體，你會發現你不是一個人在戰鬥。", "next": "LONGTERM_6"},
             "LONGTERM_6": {"type": "dialogue", "speaker": "伶娜護理師", "text": "我們醫療團隊就是你最好的後盾。有任何問題，不管是身體上的不適，還是心理上的困擾，隨時都可以跟我們聯絡！", "next": "LONGTERM_7"},
            "LONGTERM_7": { "type": "event", "action": "FINISH_LONG_TERM", "text": "你理解到，與IBD共存是一場漫長的旅程，不只需要藥物，更需要知識、耐心和強大的心理支持。", "next_scene": "scene_6_finale" }
        }
    },
    "scene_6_finale": {
        "start_node": "FINALE_1",
        "nodes": {
            "FINALE_1": {"type": "dialogue", "speaker": "旁白", "text": "又過了幾個月，你的生活因為你的每一個選擇，而走向了不同的樣貌。", "next": "FINALE_CHECK"},
            "FINALE_CHECK": { "type": "event", "action": "FINALE_CHECK" },
            "GOOD_ENDING": { "type": "dialogue", "speaker": "旁白", "text": "你與病友們一同參加 519 世界IBD日活動，臉上帶著自信的微笑。「雖然這條路很長，但我學會了和它共存。感謝我的家人和醫療團隊，我的人生依然可以很精彩。」", "background": "assets/IBD.png", "is_ending": True },
            "BAD_ENDING": { "type": "dialogue", "speaker": "旁白", "text": "因為不遵醫囑、聽信偏方或飲食混亂，導致病情反覆發作，你再次躺在冰冷的病床上。「為什麼…為什麼總是好不了…我到底該怎麼辦…」", "background": "assets/SAD.png", "is_ending": True }
        }
    }
}


# --- 遊戲狀態初始化 ---
def initialize_player_state():
    """初始化一個新的玩家狀態"""
    return {
        "health": 50,
        "stress": 30,
        "adherence": 10,
        "current_scene": "scene_1_home",
        "current_node": "HOME_1",
        "med_quiz_passed": 0, # 修改為計數器，記錄答對幾題
        "diet_game_passed": False
    }

# --- API 路由定義 ---

@app.route("/start", methods=['POST'])
def start_game():
    """開始或重新開始一個新遊戲"""
    session.clear() # 確保清除舊的 session
    session['player_state'] = initialize_player_state()
    state = session['player_state']
    scene = state['current_scene']
    node_key = state['current_node']
    return jsonify({
        'node': game_data[scene]['nodes'][node_key],
        'scene': scene,
        'state': state
    })

# --- 【關鍵修正】重構後的動作處理函式 ---
@app.route("/action", methods=['POST'])
def perform_action():
    """統一處理所有玩家動作"""
    if 'player_state' not in session:
        return jsonify({"error": "遊戲尚未開始，請先訪問 /start"}), 400

    data = request.json
    player_action = data.get('action')
    state = session.get('player_state')
    
    current_scene_key = state['current_scene']
    current_node_key = state['current_node']
    current_node_data = game_data[current_scene_key]['nodes'][current_node_key]

    # A. 處理來自前端按鈕的特定動作 (選擇題)
    if player_action == "TRY_REMEDY":
        state['adherence'] -= 15; state['stress'] += 15; state['health'] -= 25
        state['current_node'] = "REMEDY_1"
    elif player_action == "SEE_DOCTOR":
        state['adherence'] += 35; state['stress'] -= 25
        state['current_scene'] = "scene_2_clinic"; state['current_node'] = "CLINIC_1"
    
    # B. 處理小遊戲提交的結果
    elif player_action == "submit_minigame_result":
        game_type = current_node_data.get('game_type')
        payload = data.get('payload')

        if game_type == "medication_quiz":
            is_success = payload == current_node_data['data']['correct_answer']
            if is_success:
                state['adherence'] += 35
                state['med_quiz_passed'] += 1
            else:
                state['adherence'] -= 5
            state['current_node'] = current_node_data['success_node'] if is_success else current_node_data['failure_node']

        elif game_type == "diet_selection":
            player_selection = set(payload if isinstance(payload, list) else [])
            safe_foods_names = {food['name'] for food in current_node_data['data']['safe_foods']}
            num_safe_selected = len(player_selection.intersection(safe_foods_names))
            num_trigger_selected = len(player_selection) - num_safe_selected

            if num_trigger_selected == 0 and num_safe_selected >= 3:
                state['health'] += 40; state['stress'] -= 15; state['adherence'] += 5
                state['diet_game_passed'] = True
                state['current_node'] = "DIET_PERFECT"
            elif num_trigger_selected <= 1 and num_safe_selected >= 2:
                state['health'] += 25;state['stress'] -= 15; state['adherence'] += 5
                state['diet_game_passed'] = True
                state['current_node'] = "DIET_GOOD"
            else:
                state['health'] -= 20; state['stress'] += 10
                state['current_node'] = "DIET_FAIL"

    # C. 處理點擊「下一步」按鈕的推進邏輯
    elif player_action == "advance":
        # 如果當前節點有 'next'，直接跳到下一個對話
        if 'next' in current_node_data:
            state['current_node'] = current_node_data['next']
        # 如果當前節點有 'action'，則執行對應的事件
        elif 'action' in current_node_data:
            event_action = current_node_data['action']
            if event_action == "GO_TO_CLINIC_URGENT":
                 state['adherence'] -= 15; state['stress'] += 20; state['health'] -= 20
                 state['current_scene'] = "scene_2_clinic"; state['current_node'] = "CLINIC_1"
            elif event_action in ["FINISH_DIAGNOSIS", "FINISH_TREATMENT_PLAN", "FINISH_DAILY_LIFE", "FINISH_LONG_TERM"]:
                state['current_scene'] = current_node_data['next_scene']
                state['current_node'] = game_data[state['current_scene']]['start_node']
            elif event_action == "FINALE_CHECK":
                stats_ok = state['health'] > 80 and state['adherence'] > 80 and state['stress'] < 20
                choices_ok = state['med_quiz_passed'] >= 2 and state['diet_game_passed']
                if stats_ok and choices_ok:
                    state['current_node'] = "GOOD_ENDING"
                else:
                    state['current_node'] = "BAD_ENDING"
    
    # 確保數值在 0-100 的範圍內
    state['health'] = max(0, min(100, state['health']))
    state['stress'] = max(0, min(100, state['stress']))
    state['adherence'] = max(0, min(100, state['adherence']))

    session['player_state'] = state

    scene = state['current_scene']
    node_key = state['current_node']
    return jsonify({
        'node': game_data[scene]['nodes'][node_key],
        'scene': scene,
        'state': state
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


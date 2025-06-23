// --- CONFIGURATION & 資源對應表 ---
const BACKEND_URL = '';
const STATIC_ASSETS = '/static/assets/';

const characterImages = {
  '小信': STATIC_ASSETS + 'char_xiaoxin.png',
  '媽媽': STATIC_ASSETS + 'char_mom.png',
  '周醫師': STATIC_ASSETS + 'char_doctor.png',
  '伶娜護理師': STATIC_ASSETS + 'char_nurse.png',
  '阿誠': STATIC_ASSETS + 'char_friend.png',
  '旁白': '',
  '小信內心': STATIC_ASSETS + 'char_think.png'
};

// --- 【關鍵修正】更新場景與背景圖的對應關係 ---
const sceneBackgrounds = {
  'scene_1_home': STATIC_ASSETS + 'bg_home.png',
  'scene_2_clinic': STATIC_ASSETS + 'bg_clinic.png',
  'scene_3_treatment_plan': STATIC_ASSETS + 'bg_clinic.png', // 指定場景3繼續使用診所背景
  'scene_4_daily_life': STATIC_ASSETS + 'bg_food.png',       // 指定場景4使用食物背景
  'scene_5_long_term': STATIC_ASSETS + 'bg_clinic.png'        // 指定場景5回到診所背景
  // 場景6的結局背景由後端動態提供，此處不需設定
};

// --- HTML ELEMENT REFERENCES (先宣告變數) ---
let statusContainer, dialogueContainer, speakerName, dialogueText, nextButton,
    backgroundLayer, characterSprite, choiceButtonsContainer,
    minigameContainer, dietGameTemplate, eventImage, endingActionsContainer;

let dietGameTimer = null;

// --- 核心函式 ---

async function postToAction(action, data = {}) {
  console.log(`%c[Request -> /action] Action: ${action}`, 'color: #0077cc;', data);
  try {
    const response = await fetch(`${BACKEND_URL}/action`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ action, ...data }),
      credentials: 'include'
    });
    if (!response.ok) { throw new Error(`HTTP error! Status: ${response.status}`); }
    const responseData = await response.json();
    console.log('%c[Response] Received Data:', 'color: #009933;', responseData);
    return responseData;
  } catch (error) {
    console.error("Error calling /action endpoint:", error);
    dialogueContainer.classList.remove('hidden');
    speakerName.textContent = "錯誤";
    dialogueText.textContent = "無法連接到遊戲伺服器。請確認後端程式 (app.py) 正在運行。";
  }
}

function parseTextToHTML(text) {
  if (!text) return '';
  return text
    .replace(/\[b\](.*?)\[\/b\]/g, '<strong>$1</strong>')
    .replace(/\[color=(.*?)\](.*?)\[\/color\]/g, '<span style="color:$1;">$2</span>');
}

function renderStatus(state) {
  if (!state) return;
  statusContainer.innerHTML = `
    <div class="status-item"><span class="status-label">健康</span><div class="status-bar"><div class="status-bar-inner" id="health-bar-inner" style="width: ${state.health}%"></div></div></div>
    <div class="status-item"><span class="status-label">壓力</span><div class="status-bar"><div class="status-bar-inner" id="stress-bar-inner" style="width: ${state.stress}%"></div></div></div>
    <div class="status-item"><span class="status-label">依從性</span><div class="status-bar"><div class="status-bar-inner" id="adherence-bar-inner" style="width: ${state.adherence}%"></div></div></div>
  `;
  document.getElementById('health-bar-inner').style.background = 'linear-gradient(90deg, #4CAF50, #8BC34A)';
  document.getElementById('stress-bar-inner').style.background = 'linear-gradient(90deg, #FF9800, #FFC107)';
  document.getElementById('adherence-bar-inner').style.background = 'linear-gradient(90deg, #2196F3, #03A9F4)';
}

function renderDietMinigame(nodeData) {
    if (!dietGameTemplate) {
        console.error("CRITICAL: dietGameTemplate not found! Cannot render minigame.");
        return;
    }
    const gameData = nodeData.data;
    minigameContainer.innerHTML = dietGameTemplate.innerHTML;
    const promptEl = minigameContainer.querySelector('#diet-game-prompt');
    const timerDisplay = minigameContainer.querySelector('#timer-display');
    const buffetArea = minigameContainer.querySelector('#buffet-area');
    const plateArea = minigameContainer.querySelector('#plate-area');
    const submitButton = minigameContainer.querySelector('#submit-diet-button');
    promptEl.innerHTML = parseTextToHTML(gameData.prompt);
    const safeFoodNames = new Set(gameData.safe_foods.map(f => f.name));
    const allFoods = [...gameData.safe_foods, ...gameData.trigger_foods];
    allFoods.forEach(foodObject => {
        const foodEl = createFoodElement(foodObject, safeFoodNames.has(foodObject.name));
        buffetArea.appendChild(foodEl);
    });
    setupDropArea(buffetArea);
    setupDropArea(plateArea);
    function createFoodElement(foodObject, isSafe) {
        const foodEl = document.createElement('div');
        foodEl.className = 'food-item';
        foodEl.draggable = true;
        foodEl.dataset.name = foodObject.name;
        foodEl.dataset.isSafe = isSafe;
        const imgEl = document.createElement('img');
        imgEl.src = STATIC_ASSETS + foodObject.image.split('/').pop();
        imgEl.alt = foodObject.name;
        imgEl.onerror = () => { imgEl.style.display = 'none'; foodEl.querySelector('span').textContent += ' (圖片遺失)'; console.error(`Failed to load image: ${foodObject.image}`); };
        foodEl.appendChild(imgEl);
        const nameEl = document.createElement('span');
        nameEl.textContent = foodObject.name;
        foodEl.appendChild(nameEl);
        foodEl.addEventListener('dragstart', (event) => { event.dataTransfer.setData('text/plain', event.target.dataset.name); setTimeout(() => foodEl.classList.add('dragging'), 0); });
        foodEl.addEventListener('dragend', () => foodEl.classList.remove('dragging'));
        return foodEl;
    }
    function setupDropArea(area) {
        area.addEventListener('dragover', event => { event.preventDefault(); area.classList.add('drag-over'); });
        area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
        area.addEventListener('drop', event => {
            event.preventDefault();
            area.classList.remove('drag-over');
            const foodName = event.dataTransfer.getData('text/plain');
            const draggedEl = document.querySelector(`.food-item[data-name="${foodName}"]`);
            if (area.id === 'plate-area' && plateArea.children.length >= 5) return;
            if (area.id === 'plate-area') {
                draggedEl.classList.remove('incorrect');
                draggedEl.classList.add(draggedEl.dataset.isSafe === 'true' ? 'correct' : 'incorrect');
            } else {
                 draggedEl.classList.remove('correct', 'incorrect');
            }
            area.appendChild(draggedEl);
        });
    }
    const submitSelection = () => {
        clearInterval(dietGameTimer);
        const selectedFoods = Array.from(plateArea.querySelectorAll('.food-item')).map(el => el.dataset.name);
        postToAction('submit_minigame_result', { payload: selectedFoods }).then(renderNode);
    };
    submitButton.onclick = submitSelection;
    let timeLeft = 30;
    timerDisplay.textContent = timeLeft;
    dietGameTimer = setInterval(() => {
        timeLeft--;
        timerDisplay.textContent = timeLeft;
        if (timeLeft <= 0) { clearInterval(dietGameTimer); submitSelection(); }
    }, 1000);
}

function renderNode(responseData) {
    if (!responseData || !responseData.node) {
        console.error("Render failed: Invalid response data", responseData);
        return;
    }
    const nodeData = responseData.node;
    
    // 清理畫面
    choiceButtonsContainer.innerHTML = '';
    endingActionsContainer.innerHTML = '';
    minigameContainer.innerHTML = '';
    minigameContainer.classList.add('hidden');
    dialogueContainer.classList.add('hidden');
    nextButton.style.display = 'none';

    // 更新狀態與背景
    renderStatus(responseData.state);
    if (nodeData.background) {
        backgroundLayer.style.backgroundImage = `url('${nodeData.background}')`;
    } else {
        backgroundLayer.style.backgroundImage = `url('${sceneBackgrounds[responseData.scene] || ''}')`;
    }

    const speakerImage = characterImages[nodeData.speaker];
    characterSprite.style.display = speakerImage ? 'block' : 'none';
    characterSprite.style.opacity = speakerImage ? 1 : 0;
    if(speakerImage) characterSprite.src = speakerImage;
    
    // 根據節點類型，決定渲染什麼內容
    if (nodeData.type === 'minigame') {
        minigameContainer.classList.remove('hidden');
        if (nodeData.game_type === 'medication_quiz') {
            const questionEl = document.createElement('h2');
            questionEl.className = 'minigame-question';
            questionEl.innerHTML = parseTextToHTML(nodeData.data.question);
            minigameContainer.appendChild(questionEl);
            nodeData.data.options.forEach(optionText => {
                const button = document.createElement('button');
                button.innerHTML = parseTextToHTML(optionText);
                button.className = 'minigame-option-button';
                button.onclick = () => {
                    postToAction('submit_minigame_result', { payload: optionText }).then(renderNode);
                };
                minigameContainer.appendChild(button);
            });
        } else if (nodeData.game_type === 'diet_selection') {
            renderDietMinigame(nodeData);
        }
    } else {
        dialogueContainer.classList.remove('hidden');
        speakerName.textContent = nodeData.speaker;
        dialogueText.innerHTML = parseTextToHTML(nodeData.text || '');

        if (nodeData.is_ending) {
            const replayButton = document.createElement('button');
            replayButton.textContent = '重新遊玩';
            replayButton.className = 'replay-button';
            replayButton.onclick = startGame;
            endingActionsContainer.appendChild(replayButton);
        } else if (nodeData.type === 'choice') {
            nodeData.choices.forEach(choice => {
                const button = document.createElement('button');
                button.innerHTML = parseTextToHTML(choice.text);
                button.classList.add('choice-button');
                button.onclick = () => {
                    // 修正：選擇題的 action 也應該發送到 /action
                    postToAction('action', { action: choice.action }).then(renderNode);
                };
                choiceButtonsContainer.appendChild(button);
            });
        } else {
            nextButton.style.display = 'block';
            nextButton.onclick = () => {
                postToAction('action', { action: 'advance' }).then(renderNode);
            };
        }
    }
}

async function startGame() {
  console.log("Starting game...");
  try {
    const response = await fetch(`${BACKEND_URL}/start`, {
        method: 'POST',
        credentials: 'include'
    });
    if (!response.ok) { throw new Error(`HTTP error! Status: ${response.status}`); }
    const responseData = await response.json();
    if (responseData) {
      renderNode(responseData);
    }
  } catch (error) {
    console.error("Could not start game:", error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM fully loaded and parsed. Initializing game elements.");
  
  statusContainer = document.getElementById('status-container');
  dialogueContainer = document.getElementById('dialogue-container');
  speakerName = document.getElementById('speaker-name');
  dialogueText = document.getElementById('dialogue-text');
  nextButton = document.getElementById('dialogue-next');
  backgroundLayer = document.getElementById('background-layer');
  characterSprite = document.getElementById('character-sprite');
  choiceButtonsContainer = document.getElementById('choice-buttons-container');
  minigameContainer = document.getElementById('minigame-container');
  dietGameTemplate = document.getElementById('diet-game-template');
  eventImage = document.getElementById('event-image');
  endingActionsContainer = document.getElementById('ending-actions-container');

  startGame();
});

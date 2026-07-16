/**
 * AI DM — D&D 5E 跑团前端
 * 安全重构版：修复 XSS，增强错误处理，添加 Toast 通知
 */

const API = location.origin;
let campId = null;
let charId = null;
let socket = null;       // Socket.IO 客户端实例
let myName = '';

/* ========== DOM 快捷方法 ========== */
const $ = id => document.getElementById(id);

/* ========== 安全工具 ========== */

/** 将文本中的 HTML 特殊字符转义 */
function esc(str) {
  if (typeof str !== 'string') return str;
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/** 安全地设置包含换行符的文本（将 \\n 转为 <br>） */
function setHtmlWithBr(el, text) {
  el.innerHTML = esc(text).replace(/\n/g, '<br>');
}

/** 安全创建元素并设置文本内容 */
function createEl(tag, opts = {}) {
  const el = document.createElement(tag);
  if (opts.className) el.className = opts.className;
  if (opts.text) el.textContent = opts.text;
  if (opts.html) el.innerHTML = opts.html;
  if (opts.title) el.title = opts.title;
  return el;
}

/* ========== Toast 通知系统 ========== */

let toastContainer = null;

function initToast() {
  if (toastContainer) return;
  toastContainer = createEl('div', { className: 'toast-container' });
  document.body.appendChild(toastContainer);
}

function toast(msg, type = 'info', duration = 3000) {
  initToast();
  const t = createEl('div', {
    className: `toast ${type}`,
    text: msg,
  });
  toastContainer.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = 'opacity .3s';
    setTimeout(() => t.remove(), 300);
  }, duration);
}

/* ========== 视图切换 ========== */

const SCREENS = ['mainMenu', 'newGameForm', 'continueForm', 'joinForm'];

function show(screenId) {
  SCREENS.forEach(id => {
    $(id).style.display = id === screenId ? 'block' : 'none';
  });
}

function showNewGame() { show('newGameForm'); }
function showJoin()    { show('joinForm'); }

async function showContinue() {
  show('continueForm');
  const ul = $('campList');
  ul.innerHTML = '';
  try {
    const res = await fetch(`${API}/campaigns`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.campaigns || data.campaigns.length === 0) {
      const li = createEl('li', { text: '暂无保存的战役' });
      li.style.color = '#555';
      ul.appendChild(li);
      return;
    }

    data.campaigns.forEach(c => {
      const li = createEl('li');
      li.className = 'camp-list';
      const cn = createEl('div', { className: 'cn', text: `#${c.id} ${c.name}` });
      const cs = createEl('div', {
        className: 'cs',
        text: c.setting || c.summary || '(无摘要)',
      });
      li.appendChild(cn);
      li.appendChild(cs);
      li.onclick = () => resumeCampaign(c.id);
      ul.appendChild(li);
    });
  } catch (e) {
    toast(`加载战役失败: ${e.message}`, 'error');
  }
}

function backToMenu() { show('mainMenu'); }

/* ========== 日志系统（XSS 修复） ========== */

/** 向日志添加纯文本条目（安全） */
function addText(cls, text) {
  const d = createEl('div', { className: cls, text });
  $('log').appendChild(d);
  d.scrollIntoView();
  return d;
}

/** 向日志添加支持 <br> 的内容（先转义再替换） */
function addHtml(cls, rawText) {
  const d = document.createElement('div');
  d.className = cls;
  setHtmlWithBr(d, rawText);
  $('log').appendChild(d);
  d.scrollIntoView();
  return d;
}

/* ========== 角色面板 ========== */

function hpColor(pct) {
  return pct > 50 ? '#2a2' : pct > 25 ? '#aa2' : '#a22';
}

async function refreshChar() {
  try {
    const res = await fetch(`${API}/character/${charId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const c = await res.json();

    $('charName').textContent = `${c.name} Lv${c.level}`;
    $('hpText').textContent = `HP ${c.hp}/${c.hp_max}`;

    const pct = c.hp_max ? Math.max(0, (c.hp / c.hp_max) * 100) : 0;
    const fill = $('hpFill');
    fill.style.width = pct + '%';
    fill.style.background = hpColor(pct);

    $('charAC').textContent = c.ac;
    $('charSpeed').textContent = c.speed + '尺';
    $('charProf').textContent = '+' + c.proficiency;

    // 条件标签 — 安全构建
    const condEl = $('charCond');
    condEl.innerHTML = '';
    (c.conditions || []).forEach(x => {
      const tag = createEl('span', { className: 'cond-tag', text: x });
      condEl.appendChild(tag);
    });

    // 属性网格 — 安全构建
    const sg = $('statGrid');
    sg.innerHTML = '';
    const abbr = { str: '力', dex: '敏', con: '体', int: '智', wis: '感', cha: '魅' };
    for (const [k, v] of Object.entries(c.abilities)) {
      const d = createEl('div', { className: 'stat' });
      const modStr = `${v.mod >= 0 ? '+' : ''}${v.mod}`;
      d.innerHTML = `<div class="n">${abbr[k] || k}</div><div class="v">${v.score}</div><div class="m">${modStr}</div>`;
      sg.appendChild(d);
    }
  } catch (e) {
    toast(`刷新角色失败: ${e.message}`, 'error');
  }
}

/* ========== 场景与战斗 ========== */

function showChoices(opts) {
  const c = $('choices');
  c.innerHTML = '';
  (opts || []).forEach((o, i) => {
    const b = createEl('div', { className: 'choice' });
    const num = createEl('b', { text: `${i + 1}.` });
    b.appendChild(num);
    b.appendChild(document.createTextNode(' ' + o));
    b.onclick = () => {
      $('inp').value = o;
    };
    c.appendChild(b);
  });
}

function updatePlayers(players) {
  const el = $('playerList');
  el.textContent = '玩家: ';
  players.forEach(p => {
    const span = createEl('span', { className: 'p', text: p.name });
    el.appendChild(span);
  });
}

function updateTurn(turn) {
  const t = $('turnInd');
  if (turn) {
    t.style.display = 'block';
    t.textContent = turn === myName ? '轮到你行动!' : `等待 ${turn} 行动...`;
  } else {
    t.style.display = 'none';
  }
}

function updateScene(s) {
  if (!s || !s.location) return;
  $('scLoc').textContent = s.location;
  $('scAtm').textContent = s.atmosphere || '—';
  $('scNpc').textContent = (s.npcs || []).map(n => n.name).join(', ') || '—';
  $('scExit').textContent = (s.exits || []).join(' / ') || '—';
  $('scSit').textContent = (s.situation || '').slice(0, 250);
  $('sceneBox').style.display = 'block';
}

function updateCombat(c) {
  if (!c || !c.active) {
    $('combatBox').style.display = 'none';
    return;
  }
  $('combatBox').style.display = 'block';
  $('cmbRound').textContent = c.round;
  const o = $('cmbOrder');
  o.innerHTML = '';
  (c.initiative_order || []).forEach(p => {
    const d = createEl('div', {
      className: 'init-row' + (p.name === c.current_turn ? ' current' : ''),
    });
    d.innerHTML = `<span class="iv">${p.initiative}</span><span class="nm">${esc(p.name)}(${esc(p.side)})</span>`;
    o.appendChild(d);
  });
  $('rightPanel').style.display = 'block';
  updateTurn(c.current_turn);
}

function enterGame() {
  $('mainMenu').style.display = 'none';
  $('gameLayout').style.display = 'grid';
  refreshChar();
  fetch(`${API}/scene/${campId}`).then(r => r.json()).then(updateScene).catch(() => {});
  fetch(`${API}/combat/${campId}`).then(r => r.json()).then(updateCombat).catch(() => {});
}

/* ========== Socket.IO 实时通信 ========== */

function connectWS() {
  // 使用 Socket.IO 客户端，支持自动重连、房间管理、消息缓冲
  socket = io(API, {
    transports: ['websocket'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: Infinity,
    query: {
      campaign_id: campId,
      character_id: charId,
      name: myName,
    },
  });

  socket.on('connect', () => {
    addText('meta', '(已连接)');
  });

  socket.on('disconnect', () => {
    addText('meta', '(连接断开，尝试重连...)');
  });

  socket.on('connect_error', (err) => {
    toast(`连接错误: ${err.message}`, 'error');
  });

  // 注册所有事件处理器
  socket.on('join', (d) => {
    addText('meta', `${d.name} 加入了`);
    updatePlayers(d.players);
  });

  socket.on('leave', (d) => {
    addText('meta', `${d.name} 离开了`);
    updatePlayers(d.players);
  });

  socket.on('result', (d) => {
    if (d.player !== myName) addText('other', `【${d.player}】 ${d.narration}`);
    else addHtml('dm', d.narration);
    const dd = d.dice || {};
    if (dd.d20) {
      const dmg = dd.damage ? ` 伤${dd.damage}` : '';
      const hitStr = dd.hit ? '命中' : '未中';
      const critStr = dd.crit ? ' 重击' : '';
      addText('dice', `[${d.player}] d20=${dd.d20} ${hitStr}${critStr}${dmg}`);
    }
    showChoices(d.action_options);
    refreshChar();
  });

  socket.on('processing', (d) => {
    addText('meta', `⏳ ${d.player} 正在判定...`);
  });

  socket.on('player_acting', (d) => {
    if (d.player !== myName) addText('meta', `⟳ ${d.player} 正在: ${d.action}`);
  });

  socket.on('scene_update', (d) => updateScene(d.scene));
  socket.on('combat_update', (d) => updateCombat(d));
  socket.on('turn_advanced', (d) => updateTurn(d.next));
  socket.on('round_end', (d) => addText('meta', `第 ${d.round} 轮结束`));
  socket.on('monster_turn', (d) => addText('meta', `👾 ${d.monster} 的回合`));
  socket.on('monster_action', (d) => addText('other', `【${d.monster}】 ${JSON.stringify(d.result)}`));
  socket.on('combat_end', (d) => {
    addText('meta', `⚔️ 战斗结束: ${d.outcome}`);
    $('combatBox').style.display = 'none';
  });
  socket.on('player_ready', (d) => addText('meta', `${d.player} 已准备`));
  socket.on('character_update', (d) => {
    const hpMax = d.hp_max || 1;
    const hp = d.hp || 0;
    const pct = hpMax ? (hp / hpMax) * 100 : 0;
    $('hpText').textContent = `HP ${hp}/${hpMax}`;
    $('hpFill').style.width = pct + '%';
    $('hpFill').style.background = hpColor(pct);
  });
  socket.on('error', (d) => addText('meta', '⚠ ' + d.message));
}

/* ========== 游戏流程 ========== */

/** 统一 fetch 包装，自动处理错误 */
async function apiPost(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiGet(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/** 设置按钮加载状态 */
function setLoading(id, text, loading = true) {
  const btn = $(id);
  if (loading) {
    btn.disabled = true;
    btn.dataset.origText = btn.textContent;
    btn.innerHTML = `<span class="spinner"></span>${text}`;
  } else {
    btn.disabled = false;
    btn.textContent = btn.dataset.origText || text;
  }
}

function resetLoading(id, fallbackText) {
  const btn = $(id);
  btn.disabled = false;
  btn.textContent = btn.dataset.origText || fallbackText;
}

// AI 生成世界设定
async function generateWorld() {
  const btnId = 'genWorldBtn';
  setLoading(btnId, '生成中...');
  try {
    const r = await apiPost('/generate_setting', {});
    if (r.setting) {
      $('ngSetting').value = r.setting;
      toast('世界设定生成成功', 'success');
    } else {
      toast('生成失败: ' + (r.error || '未知错误'), 'error');
    }
  } catch (e) {
    toast('请求失败: ' + e.message, 'error');
  } finally {
    resetLoading(btnId, '✨ AI 生成世界设定');
  }
}

// 开始新游戏
async function startNewGame() {
  myName = $('ngName').value.trim() || '冒险者';
  const setting = $('ngSetting').value.trim();
  if (!setting) {
    toast('请输入世界设定', 'warn');
    return;
  }

  const startBtn = 'startGameBtn';
  setLoading(startBtn, '创建角色中...');
  addText('meta', '(建角色...)');

  try {
    const c = await apiPost('/campaign', { name: myName + '的冒险' });
    campId = c.id;

    const ch = await apiPost('/character', {
      name: myName,
      char_class: '战士',
      level: 5,
      abilities: { str: 16, dex: 10, con: 15, int: 10, wis: 12, cha: 10 },
      hp_max: 38,
      ac: 18,
      campaign_id: campId,
    });
    charId = ch.id;

    setLoading(startBtn, 'DM 生成开场中...(约10秒)');
    addText('meta', '(DM 生成开场...)');

    const r = await apiPost('/open', {
      setting,
      tone: '',
      campaign_id: campId,
      character_id: charId,
    });

    $('log').innerHTML = '';
    addHtml('dm', r.narration);
    showChoices(r.action_options);

    resetLoading(startBtn, '🗺️ 开始冒险');
    enterGame();
    connectWS();
  } catch (e) {
    toast('创建游戏失败: ' + e.message, 'error');
    resetLoading(startBtn, '🗺️ 开始冒险');
  }
}

// 继续游戏
async function resumeCampaign(cid) {
  campId = cid;
  try {
    const st = await apiGet(`/campaign/${cid}/state`);
    if (st.error) {
      toast(st.error, 'error');
      return;
    }

    if (st.characters && st.characters.length > 0) {
      charId = st.characters[0].id;
      myName = st.characters[0].name;
    } else {
      toast('该战役没有角色', 'warn');
      return;
    }

    $('log').innerHTML = '';
    if (st.summary) addText('meta', '📖 剧情回顾: ' + st.summary.slice(0, 200) + '...');
    if (st.scene) updateScene(st.scene);
    if (st.combat) updateCombat(st.combat);

    enterGame();
    connectWS();
    addText('meta', `继续战役 #${cid} (${st.campaign.name})`);
  } catch (e) {
    toast('继续游戏失败: ' + e.message, 'error');
  }
}

// 加入房间
async function joinGame() {
  campId = parseInt($('joinCampId').value);
  myName = $('joinName').value.trim() || '冒险者';
  if (!campId) {
    toast('请填写房间号', 'warn');
    return;
  }
  try {
    const ch = await apiPost('/join', { name: myName, campaign_id: campId });
    if (ch.error) {
      toast(ch.error, 'error');
      return;
    }
    charId = ch.character_id;
    $('log').innerHTML = '';
    addText('meta', `加入房间 #${campId}`);
    enterGame();
    connectWS();
  } catch (e) {
    toast('加入房间失败: ' + e.message, 'error');
  }
}

// 发送行动
function send() {
  const t = $('inp').value.trim();
  if (!t || !socket) return;
  $('inp').value = '';
  addText('you', '> ' + t);
  socket.emit('action', { player_input: t });
}

// 绑定回车发送
$('inp').addEventListener('keydown', e => {
  if (e.key === 'Enter') send();
});

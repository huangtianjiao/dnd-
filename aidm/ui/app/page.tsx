"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { API, apiGet, apiPost, errMsg } from "./lib/api";
import type { CharacterSheet, SceneData, CombatData, LogEntry, OpeningData, RoomJoinResult } from "./lib/types";
import { useSocket } from "./hooks/useSocket";
import { RoomPanel, HostControls } from "./components/RoomPanel";
import { OpeningConfirm } from "./components/OpeningConfirm";
import { LootPanel } from "./components/LootPanel";
import { FeatDialog } from "./components/FeatDialog";
import { CharacterPanel } from "./components/CharacterPanel";
import { SceneBox } from "./components/SceneBox";
import { NarrativeArea } from "./components/NarrativeArea";
import { CombatBox } from "./components/CombatBox";
import { RestDialog } from "./components/RestDialog";
import { InventoryPanel } from "./components/InventoryPanel";
import { WeaponEquip } from "./components/WeaponEquip";
import { StrongholdPanel } from "./components/StrongholdPanel";
import { RulesReference } from "./components/RulesReference";
import { DeathSaveTracker } from "./components/DeathSaveTracker";
import { SpellbookModal } from "./components/SpellbookModal";

// 购点法花费表（与后端 char_create.POINT_BUY_COST 一致，13 以上非线性）
const POINT_BUY_COST: Record<number, number> = { 8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9 };
const METHOD_LABEL: Record<string, string> = { standard_array: "标准阵列", point_buy: "购点法", roll: "掷骰", free: "自由" };

// 阵营九宫格（与后端 char_create.ALIGNMENTS 一致）
const ALIGNMENTS = [
  "守序善良", "中立善良", "混乱善良",
  "守序中立", "绝对中立", "混乱中立",
  "守序邪恶", "中立邪恶", "混乱邪恶",
];

// 属性调整值: floor((score - 10) / 2)
const abilityMod = (score: number) => Math.floor((score - 10) / 2);

// 世界设定留空时的默认值（避免"开始冒险"静默卡住）
const DEFAULT_SETTING = "经典剑与魔法奇幻世界：边境小镇近日频频有商队失踪，镇长悬赏招募冒险者调查郊外的废弃矿坑。";

// 生命值上限: 1级取满骰面 + 每级体质调整值 + 2级起每级取骰面均值(向下取整+1)
const suggestHP = (hitDie: number, conMod: number, level: number) =>
  hitDie + level * conMod + (level - 1) * (Math.floor(hitDie / 2) + 1);

// 起始 AC：按职业护甲受训给基准护甲 + 盾牌+2；无护甲取 10+敏捷
const suggestAC = (armor: string, dexMod: number) => {
  let base = 10 + dexMod;
  if (armor.includes("重甲")) base = 16;
  else if (armor.includes("中甲")) base = 14 + Math.min(dexMod, 2);
  else if (armor.includes("轻甲")) base = 11 + dexMod;
  if (armor.includes("盾牌")) base += 2;
  return base;
};

// ──────────────────────────────────────────────────────────────────────────
// 主页面
// ──────────────────────────────────────────────────────────────────────────

export default function Page() {
  const [screen, setScreen] = useState<"menu" | "newGame" | "continue" | "join" | "createRoom" | "roomList" | "openingReview" | "game">("menu");
  const [log, setLog] = useState<LogEntry[]>([]);
  const [campId, setCampId] = useState<number | null>(null);
  const [charId, setCharId] = useState<number | null>(null);
  const [character, setCharacter] = useState<CharacterSheet | null>(null);
  const [scene, setScene] = useState<SceneData | null>(null);
  const [combat, setCombat] = useState<CombatData | null>(null);
  const [choices, setChoices] = useState<string[]>([]);
  const [inp, setInp] = useState("");
  const [rolling, setRolling] = useState(false);
  const [diceResult, setDiceResult] = useState<{ d20?: number; hit?: boolean; crit?: boolean; dmg?: number } | null>(null);
  const [campaigns, setCampaigns] = useState<{ id: number; name: string; setting?: string }[]>([]);
  const [myName, setMyName] = useState("");
  const [toastMsg, setToastMsg] = useState<{ msg: string; type: string } | null>(null);

  // ── 房间（多人）/ 开场预览 ──
  const [roomId, setRoomId] = useState<string | null>(null);
  const [isHost, setIsHost] = useState(false);
  const [opening, setOpening] = useState<OpeningData | null>(null);
  const [openingLoading, setOpeningLoading] = useState(false);
  const [worldSetting, setWorldSetting] = useState("");
  const [starting, setStarting] = useState(false);

  // ── 角色创建 ──
  const [charRace, setCharRace] = useState("人类");
  const [charClass, setCharClass] = useState("战士");
  const [charSubclass, setCharSubclass] = useState("");
  const [charBackground, setCharBackground] = useState("");
  const [charAlignment, setCharAlignment] = useState("绝对中立");
  const [charLevel, setCharLevel] = useState(5);
  const [charAbilities, setCharAbilities] = useState<Record<string, number>>({ str: 16, dex: 10, con: 15, int: 10, wis: 12, cha: 10 });
  // 属性生成方式：standard_array/point_buy/roll/free（后端 /character 按 method 校验）
  const [abilityMethod, setAbilityMethod] = useState<"standard_array" | "point_buy" | "roll" | "free">("free");

  // ── 种族/职业/背景（从后端拉取，避免前端硬编码漂移）──
  const [races, setRaces] = useState<{ name: string; speed: number }[]>([]);
  const [classes, setClasses] = useState<{ name: string; hit_die: number; armor_training: string; spellcasting?: string | null; subclasses?: string[]; subclass_level?: number }[]>([]);
  const [backgrounds, setBackgrounds] = useState<{ name: string; ability_scores: string[]; feat: string; skill_prof: string[]; tool_prof: string; equipment: string }[]>([]);

  // ── 法术列表（从后端 /spells 拉取，供法术书展示）──
  const [spells, setSpells] = useState<{ name: string; level: number; school: string; casting_time: string; range: string; duration: string; components: string[]; description: string }[]>([]);

  // ── DM 模式 ──
  const [isDm, setIsDm] = useState(false);

  const diceBoxRef = useRef<any>(null);

  // ── Toast ──
  const toast = useCallback((msg: string, type = "info") => {
    setToastMsg({ msg, type });
    setTimeout(() => setToastMsg(null), 3000);
  }, []);

  // ── 动态加载 3D 骰子 ──
  useEffect(() => {
    import("@3d-dice/dice-box")
      .then(({ default: DiceBox }) => {
        const db = new DiceBox("#dice-box", { assetPath: "/assets/dice-box" });
        db.init();
        diceBoxRef.current = db;
      })
      .catch(() => {
        console.log("DiceBox 未加载（降级）");
        toast("3D 骰子不可用，使用文本结果", "warn");
      });
  }, [toast]);

  // ── 拉取种族/职业/背景列表（去硬编码，与后端 data 表对齐）──
  useEffect(() => {
    apiGet("/races").then((r: any) => setRaces(r.races || [])).catch(() => {});
    apiGet("/classes").then((r: any) => setClasses(r.classes || [])).catch(() => {});
    apiGet("/backgrounds").then((r: any) => setBackgrounds(r.backgrounds || [])).catch(() => {});
    apiGet("/spells").then((r: any) => setSpells(r.spells || [])).catch(() => {});
  }, []);

  // ── 刷新角色卡 ──
  const refreshChar = useCallback(async () => {
    if (!charId) return;
    try {
      const c = await apiGet(`/character/${charId}`);
      setCharacter(c);
    } catch (e) {
      /* 忽略 */
    }
  }, [charId]);

  // ── Socket.IO（由 hooks/useSocket 统一管理事件订阅与重连；
  // dice 按 kind 分派、combat_end 清空、end_turn 推进先攻均在 hook 内处理，
  // 避免本文件内联逻辑与 hook 漂移）──
  const { connectWS, send: socketSend, endTurn, ready, dmMonsterTurn, dmMonsterAction, dmCombatEnd } = useSocket({
    onLog: (entry: LogEntry) => setLog((l) => [...l, entry]),
    onScene: setScene,
    onCombat: setCombat,
    onChoices: setChoices,
    onCharacterUpdate: refreshChar,
    onToast: toast,
    onServerDisconnect: () => setScreen("menu"),
    onCombatEnd: () => setCombat(null),
  });

  // ── 开始新游戏 ──
  const startNewGame = useCallback(async () => {
    if (starting) return;
    const name = myName.trim() || "冒险者";
    // 世界设定允许留空：给默认值而非静默 return（E2E B1）
    let setting = inp.trim();
    if (!setting) {
      setting = DEFAULT_SETTING;
      toast("未填写世界设定，已使用默认设定", "info");
    }

    setStarting(true);
    try {
      const c = await apiPost("/campaign", { name: `${name}的冒险` });
      const camp = c;

      const cls = classes.find((x) => x.name === charClass);
      const raceData = races.find((x) => x.name === charRace);
      if (!cls || !raceData) {
        toast("种族/职业数据未就绪，请稍候", "error");
        return;
      }
      // 前端按生成方式校验（后端 /character 也会校验兜底）
      const vals = Object.values(charAbilities);
      if (abilityMethod === "point_buy" && vals.reduce((s, v) => s + (POINT_BUY_COST[v] ?? 0), 0) > 27) {
        toast("购点法超支（>27），无法开始", "error");
        return;
      }
      if (abilityMethod === "standard_array" && [...vals].sort((a, b) => a - b).join() !== "8,10,12,13,14,15") {
        toast("标准阵列须为 [15,14,13,12,10,8] 的排列", "error");
        return;
      }
      const conMod = abilityMod(charAbilities.con);
      const dexMod = abilityMod(charAbilities.dex);
      const ch = await apiPost("/character", {
        name,
        race: charRace,
        char_class: charClass,
        subclass: charSubclass,
        background: charBackground,
        alignment: charAlignment,
        level: charLevel,
        abilities: charAbilities,
        ability_method: abilityMethod,
        hp_max: suggestHP(cls.hit_die, conMod, charLevel),
        ac: suggestAC(cls.armor_training, dexMod),
        speed: raceData.speed,
        campaign_id: camp.id,
      });

      setCampId(camp.id);
      setCharId(ch.id);
      setMyName(name);
      setWorldSetting(setting);

      toast("DM 生成开场中...(约10秒)", "info");
      const r = await apiPost("/open", {
        setting,
        tone: "",
        campaign_id: camp.id,
        character_id: ch.id,
      });

      // 先进入开场预览，确认后才正式进入游戏
      setOpening({ narration: r.narration || "", action_options: r.action_options || [], scene: r.scene });
      setScreen("openingReview");
      setInp("");
    } catch (e: any) {
      // /open 依赖 LLM，可能失败：必须 toast 错误而非卡死
      toast("创建游戏失败: " + errMsg(e), "error");
    } finally {
      setStarting(false);
    }
  }, [starting, myName, inp, charRace, charClass, charLevel, charAbilities, abilityMethod, classes, races, toast]);

  // ── 开场预览：确认进入游戏 ──
  const confirmOpening = useCallback(() => {
    if (!campId || !charId) return;
    const name = myName.trim() || "冒险者";
    setLog([]);
    if (opening?.narration) setLog((l) => [...l, { c: "dm", t: opening.narration }]);
    if (opening?.action_options) setChoices(opening.action_options);
    setScreen("game");
    connectWS(campId, charId, name, isDm ? "dm" : undefined);
    // /open 已返回 scene，直接用；refreshChar 立即拉角色卡（character 已落库）。
    // 不再 setTimeout 重拉 /scene /combat；战斗态留 null，由 socket combat_update 推送。
    if (opening?.scene) setScene(opening.scene);
    refreshChar();
  }, [campId, charId, myName, opening, connectWS, refreshChar]);

  // ── 开场预览：重新生成 ──
  const regenerateOpening = useCallback(async () => {
    if (!campId || !charId) return;
    setOpeningLoading(true);
    try {
      const r = await apiPost("/open", {
        setting: worldSetting,
        tone: "",
        campaign_id: campId,
        character_id: charId,
      });
      setOpening({ narration: r.narration || "", action_options: r.action_options || [], scene: r.scene });
    } catch (e) {
      toast("重新生成失败: " + errMsg(e), "error");
    } finally {
      setOpeningLoading(false);
    }
  }, [campId, charId, worldSetting, toast]);

  // ── 按当前角色创建配置生成角色字段（供房间创建/加入） ──
  const buildCharacter = useCallback(
    (name: string) => {
      const cls = classes.find((x) => x.name === charClass);
      const raceData = races.find((x) => x.name === charRace);
      // 数据未就绪时用保守默认值，避免 RoomPanel 调用崩
      const hitDie = cls?.hit_die ?? 8;
      const armor = cls?.armor_training ?? "轻甲";
      const speed = raceData?.speed ?? 30;
      return {
        race: charRace,
        char_class: charClass,
        level: charLevel,
        abilities: charAbilities,
        hp_max: suggestHP(hitDie, abilityMod(charAbilities.con), charLevel),
        ac: suggestAC(armor, abilityMod(charAbilities.dex)),
        speed,
      };
    },
    [charRace, charClass, charLevel, charAbilities, classes, races]
  );

  // ── 属性生成方式切换（标准阵列/购点法/掷骰/自由）──
  const switchAbilityMethod = useCallback((m: "standard_array" | "point_buy" | "roll" | "free") => {
    setAbilityMethod(m);
    if (m === "standard_array") setCharAbilities({ str: 15, dex: 14, con: 13, int: 12, wis: 10, cha: 8 });
    else if (m === "point_buy") setCharAbilities({ str: 8, dex: 8, con: 8, int: 8, wis: 8, cha: 8 });
    // roll 由 rollAbilities 异步触发；free 不改值
  }, []);

  // ── 掷骰生成六维（调后端 /roll-abilities）──
  const rollAbilities = useCallback(async () => {
    try {
      const r = await apiGet<{ values: number[] }>("/roll-abilities");
      const vals = r.values || [];
      if (vals.length === 6) {
        setCharAbilities({ str: vals[0], dex: vals[1], con: vals[2], int: vals[3], wis: vals[4], cha: vals[5] });
        setAbilityMethod("roll");
      }
    } catch (e) {
      toast("掷骰失败: " + errMsg(e), "error");
    }
  }, [apiGet, toast]);

  // ── 房间创建/加入成功后进入游戏 ──
  const enterRoomGame = useCallback(
    (r: RoomJoinResult, host: boolean, name: string) => {
      setCampId(r.campaign_id);
      setCharId(r.character_id);
      setMyName(name);
      setRoomId(r.room_id);
      setIsHost(host);
      setScreen("game");
      connectWS(r.campaign_id, r.character_id, name, isDm ? "dm" : undefined);
      setLog([{ c: "meta", t: `加入房间 ${r.room_id}${host ? "（房主）" : ""}` }]);

      setTimeout(() => {
        apiGet(`/character/${r.character_id}`).then(setCharacter).catch(() => {});
        apiGet(`/scene/${r.campaign_id}`).then(setScene).catch(() => {});
        apiGet(`/combat/${r.campaign_id}`).then(setCombat).catch(() => {});
      }, 100);
    },
    [connectWS]
  );

  // ── 保存进度 ──
  const saveSession = useCallback(async () => {
    if (!campId) return;
    try {
      toast("保存进度中...", "info");
      const r = await apiPost("/session/end", { campaign_id: campId });
      const recap = String(r?.recap ?? "").trim();
      toast(recap ? `已保存: ${recap.slice(0, 50)}` : "进度已保存", "success");
    } catch (e) {
      toast("保存失败: " + errMsg(e), "error");
    }
  }, [campId, toast]);

  // ── 继续游戏 ──
  const showContinue = useCallback(async () => {
    setScreen("continue");
    try {
      const data = await apiGet("/campaigns");
      setCampaigns(data.campaigns || []);
    } catch (e) {
      toast("加载战役失败", "error");
    }
  }, [toast]);

  const resumeCampaign = useCallback(
    async (cid: number) => {
      try {
        const st = await apiGet(`/campaign/${cid}/state`);
        if (st.characters && st.characters.length > 0) {
          const ch = st.characters[0];
          setCharId(ch.id);
          setMyName(ch.name);
          setCampId(cid);
          setScreen("game");
          connectWS(cid, ch.id, ch.name, isDm ? "dm" : undefined);
          setLog([]);
          if (st.summary) setLog((l) => [...l, { c: "meta", t: `📖 剧情回顾: ${st.summary.slice(0, 200)}...` }]);
          // /campaign/{id}/state 已返回 scene+combat，直接用，不再 setTimeout 重拉
          setScene(st.scene ?? null);
          setCombat(st.combat ?? null);
          refreshChar();
        } else {
          toast("该战役没有角色", "warn");
        }
      } catch (e: any) {
        toast("继续游戏失败: " + errMsg(e), "error");
      }
    },
    [connectWS, refreshChar, toast]
  );

  // ── 加入房间 ──
  const joinGame = useCallback(async () => {
    const cid = parseInt(inp);
    if (!cid) {
      toast("请填写房间号", "warn");
      return;
    }
    const name = myName.trim() || "冒险者";
    try {
      // 透传种族/职业/等级/属性/HP/AC（JoinIn 支持），否则施法职业经 /join 进入法术位为空
      const ch = await apiPost("/join", { name, campaign_id: cid, ...buildCharacter(name) });
      setCharId(ch.character_id || ch.id);
      setCampId(cid);
      setMyName(name);
      setScreen("game");
      connectWS(cid, ch.character_id || ch.id, name, isDm ? "dm" : undefined);
      setLog([]);
      setLog((l) => [...l, { c: "meta", t: `加入房间 #${cid}` }]);
      setInp("");
    } catch (e: any) {
      toast("加入房间失败: " + errMsg(e), "error");
    }
  }, [inp, myName, connectWS, toast, buildCharacter]);

  // ── 发送行动（先写 you-log 再经 hook emit action）──
  const send = useCallback(() => {
    const t = inp.trim();
    if (!t) return;
    setLog((l) => [...l, { c: "you", t: `> ${t}` }]);
    socketSend(t);
    setInp("");
  }, [inp, socketSend]);

  // ── AI 生成世界设定 ──
  const generateWorld = useCallback(async () => {
    try {
      const r = await apiPost("/generate_setting", {});
      if (r.setting) {
        setInp(r.setting);
        toast("世界设定生成成功", "success");
      }
    } catch (e: any) {
      toast("生成失败: " + errMsg(e), "error");
    }
  }, [toast]);

  // ── 全局 Toast（所有屏幕都渲染；之前仅 game 屏渲染，导致菜单/建角等屏的提示完全不可见）──
  const toastEl = toastMsg ? (
    <div style={{ position: "fixed", top: 12, right: 12, zIndex: 80 }}
      className={`px-4 py-2 rounded shadow-lg ${toastMsg.type === "error" ? "bg-red-800" : toastMsg.type === "warn" ? "bg-yellow-800" : toastMsg.type === "success" ? "bg-green-800" : "bg-blue-800"}`}>
      {toastMsg.msg}
    </div>
  ) : null;

  // ── 渲染 ──
  if (screen === "menu") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100">
        {toastEl}
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-bold text-amber-400">🐉 AI DM</h1>
          <p className="text-neutral-500">D&D 5E 硬性判定链跑团系统</p>
          <div className="space-y-3">
            <button onClick={() => setScreen("newGame")} className="block w-64 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300">
              🆕 开始新游戏
            </button>
            <button onClick={showContinue} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              📖 继续游戏
            </button>
            <button onClick={() => setScreen("join")} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              🚪 加入游戏
            </button>
            <button onClick={() => setScreen("createRoom")} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              🏰 创建房间
            </button>
            <button onClick={() => setScreen("roomList")} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              📋 房间列表
            </button>
            <button onClick={() => { setIsDm(true); setScreen("join"); }} className="block w-64 px-6 py-3 bg-purple-800 border border-purple-600 rounded hover:border-purple-400">
              🎭 以 DM 身份加入
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (screen === "newGame") {
    if (!races.length || !classes.length) {
      return (
        <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100">
          {toastEl}
          <div className="text-neutral-500">加载种族/职业数据...</div>
        </main>
      );
    }
    const cls = classes.find((x) => x.name === charClass) || classes[0];
    const raceData = races.find((r) => r.name === charRace) || races[0];
    const hpPreview = suggestHP(cls.hit_die, abilityMod(charAbilities.con), charLevel);
    const acPreview = suggestAC(cls.armor_training, abilityMod(charAbilities.dex));
    const ABILITY_KEYS: [string, string][] = [["str", "力量"], ["dex", "敏捷"], ["con", "体质"], ["int", "智力"], ["wis", "感知"], ["cha", "魅力"]];
    const pbTotal = abilityMethod === "point_buy" ? Object.values(charAbilities).reduce((s, v) => s + (POINT_BUY_COST[v] ?? 0), 0) : 0;
    const pbRemaining = 27 - pbTotal;

    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        {toastEl}
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">开始新冒险</h2>

          <input value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />

          <div className="grid grid-cols-3 gap-2">
            <label className="text-xs text-neutral-500 space-y-1">
              <span>种族</span>
              <select value={charRace} onChange={(e) => setCharRace(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                {races.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
              </select>
            </label>
            <label className="text-xs text-neutral-500 space-y-1">
              <span>职业</span>
              <select value={charClass} onChange={(e) => setCharClass(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                {classes.map((c) => <option key={c.name} value={c.name}>{c.name}</option>)}
              </select>
            </label>
            <label className="text-xs text-neutral-500 space-y-1">
              <span>等级</span>
              <input type="number" min={1} max={20} value={charLevel} onChange={(e) => setCharLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded" />
            </label>
          </div>

          {/* 子职（subclass_level <= charLevel 时可选） */}
          {(() => {
            const cls = classes.find((x) => x.name === charClass);
            const subs = cls?.subclasses || [];
            const subLv = cls?.subclass_level || 3;
            if (subs.length === 0 || charLevel < subLv) return null;
            return (
              <label className="text-xs text-neutral-500 space-y-1">
                <span>子职（{subLv}级解锁）</span>
                <select value={charSubclass} onChange={(e) => setCharSubclass(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                  <option value="">(不选)</option>
                  {subs.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
            );
          })()}

          {/* 背景 + 阵营 */}
          <div className="grid grid-cols-2 gap-2">
            <label className="text-xs text-neutral-500 space-y-1">
              <span>背景</span>
              <select value={charBackground} onChange={(e) => setCharBackground(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                <option value="">(无)</option>
                {backgrounds.map((b) => <option key={b.name} value={b.name}>{b.name}</option>)}
              </select>
            </label>
            <label className="text-xs text-neutral-500 space-y-1">
              <span>阵营</span>
              <select value={charAlignment} onChange={(e) => setCharAlignment(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                {ALIGNMENTS.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </label>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500">六维属性</span>
              <div className="flex gap-1 text-[10px]">
                {(["standard_array", "point_buy", "roll", "free"] as const).map((m) => (
                  <button key={m} onClick={m === "roll" ? rollAbilities : () => switchAbilityMethod(m)} className={`px-2 py-1 rounded border ${abilityMethod === m ? "bg-amber-400 text-neutral-900 border-amber-400" : "bg-neutral-800 border-neutral-700 hover:border-amber-400"}`}>
                    {METHOD_LABEL[m]}
                  </button>
                ))}
              </div>
            </div>
            {abilityMethod === "point_buy" && (
              <div className={`text-[10px] ${pbRemaining < 0 ? "text-red-400" : pbRemaining > 0 ? "text-neutral-400" : "text-green-400"}`}>
                购点 {pbTotal}/27 剩余 {pbRemaining}{pbRemaining < 0 ? " 超支!" : ""}
              </div>
            )}
            <div className="grid grid-cols-6 gap-1">
              {ABILITY_KEYS.map(([k, label]) => {
                const v = charAbilities[k] || 10;
                const m = abilityMod(v);
                const lo = abilityMethod === "point_buy" ? 8 : 1;
                const hi = abilityMethod === "point_buy" ? 15 : 20;
                return (
                  <div key={k} className="bg-neutral-800 rounded p-1 text-center">
                    <div className="text-[10px] text-neutral-500">{label}</div>
                    <input type="number" min={lo} max={hi} value={v} onChange={(e) => setCharAbilities({ ...charAbilities, [k]: Math.max(lo, Math.min(hi, parseInt(e.target.value) || lo)) })} className="w-full text-center bg-neutral-900 border border-neutral-700 rounded text-sm py-0.5" />
                    <div className="text-[10px] text-amber-400">{m >= 0 ? `+${m}` : m}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="text-xs text-neutral-400 flex gap-4">
            <span>生命值上限 <b className="text-amber-400">{hpPreview}</b></span>
            <span>护甲 <b className="text-amber-400">{acPreview}</b></span>
            <span>速度 <b className="text-amber-400">{raceData.speed}</b></span>
          </div>

          <textarea value={inp} onChange={(e) => setInp(e.target.value)} placeholder="输入世界设定..." rows={4} className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded resize-none" />
          <div className="flex gap-2">
            <button onClick={generateWorld} className="px-4 py-2 bg-neutral-700 border border-neutral-600 rounded text-sm hover:bg-neutral-600">
              ✨ AI 生成世界设定
            </button>
            <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
              ← 返回
            </button>
          </div>
          <button onClick={startNewGame} disabled={starting} className="w-full px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40">
            {starting ? "⏳ 创建中...（DM 生成开场约 10 秒）" : "🗺️ 开始冒险"}
          </button>
        </div>
      </main>
    );
  }

  if (screen === "continue") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        {toastEl}
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">继续冒险</h2>
          {campaigns.length === 0 ? (
            <p className="text-neutral-500">暂无保存的战役</p>
          ) : (
            <ul className="space-y-2">
              {campaigns.map((c) => (
                <li key={c.id}>
                  <button onClick={() => resumeCampaign(c.id)} className="w-full text-left px-4 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
                    <div className="font-bold text-amber-400">#{c.id} {c.name}</div>
                    <div className="text-xs text-neutral-500">{c.setting || "(无摘要)"}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
            ← 返回
          </button>
        </div>
      </main>
    );
  }

  if (screen === "join") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        {toastEl}
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">加入房间</h2>
          <input value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <div className="grid grid-cols-3 gap-2">
            <label className="text-xs text-neutral-500 space-y-1">
              <span>种族</span>
              <select value={charRace} onChange={(e) => setCharRace(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                {races.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
              </select>
            </label>
            <label className="text-xs text-neutral-500 space-y-1">
              <span>职业</span>
              <select value={charClass} onChange={(e) => setCharClass(e.target.value)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded">
                {classes.map((c) => <option key={c.name} value={c.name}>{c.name}</option>)}
              </select>
            </label>
            <label className="text-xs text-neutral-500 space-y-1">
              <span>等级</span>
              <input type="number" min={1} max={20} value={charLevel} onChange={(e) => setCharLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded" />
            </label>
          </div>
          <input value={inp} onChange={(e) => setInp(e.target.value)} placeholder="房间号（campaign_id）..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <div className="flex gap-2">
            <button onClick={joinGame} className="flex-1 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300">
              🚪 加入
            </button>
            <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
              ← 返回
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (screen === "createRoom" || screen === "roomList") {
    return (
      <>
        {toastEl}
        <RoomPanel
          view={screen === "createRoom" ? "create" : "list"}
          defaultName={myName}
          buildCharacter={buildCharacter}
          onEntered={enterRoomGame}
          onBack={() => setScreen("menu")}
          toast={toast}
        />
      </>
    );
  }

  if (screen === "openingReview") {
    return (
      <>
        {toastEl}
        <OpeningConfirm
          narration={opening?.narration || ""}
          actionOptions={opening?.action_options || []}
          loading={openingLoading}
          onConfirm={confirmOpening}
          onRegenerate={regenerateOpening}
          onBack={() => setScreen("newGame")}
        />
      </>
    );
  }

  // ── 游戏主界面 ──
  return (
    <main className="min-h-screen bg-neutral-900 text-neutral-100">
      {/* 3D 骰子容器 */}
      <div id="dice-box" style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 50 }} />

      {/* 骰子结果覆盖层 */}
      {diceResult && (
        <div style={{ position: "fixed", top: "30%", left: 0, width: "100%", textAlign: "center", zIndex: 60 }}>
          <div style={{ fontSize: "3em", fontWeight: "bold", color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44", textShadow: "0 0 20px currentColor" }}>
            {diceResult.d20}
          </div>
          <div style={{ fontSize: "1.2em", color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44" }}>
            {diceResult.crit ? "⚡ 重击!" : diceResult.hit ? "✓ 命中" : "✗ 未中"}
            {diceResult.dmg != null ? ` 💥${diceResult.dmg}` : ""}
          </div>
        </div>
      )}

      {/* Toast */}
      {toastEl}

      {/* 三栏布局 */}
      <div className="flex h-screen overflow-hidden">
        {/* 左栏 — 角色卡 */}
        <aside className="w-56 shrink-0 border-r border-neutral-800 overflow-y-auto p-3 space-y-3">
          <CharacterPanel character={character} />
          {charId && <FeatDialog charId={charId} onSelected={refreshChar} toast={toast} />}
          {charId && (
            <InventoryPanel characterId={charId} toast={toast} onUpdated={refreshChar} />
          )}
          {charId && character && (
            <WeaponEquip
              characterId={charId}
              currentWeapon={character.equipped_weapon}
              toast={toast}
              onEquipped={refreshChar}
            />
          )}
          {character && character.hp <= 0 && !character.dead && (
            <DeathSaveTracker
              successes={character.death_successes || 0}
              failures={character.death_failures || 0}
              onRoll={() => socketSend("掷死亡豁免")}
            />
          )}
          {character && (character.spell_slots || character.known_spells) && (
            <SpellbookModal
              spells={spells
                .filter((s) => {
                  const known = character.known_spells || [];
                  return known.length === 0 || known.includes(s.name);
                })
                .map((s) => ({
                  name: s.name, level: s.level, school: s.school,
                  time: s.casting_time, range: s.range,
                  duration: s.duration, components: (s.components || []).join(", "),
                  desc: s.description || "",
                }))}
              spellSlots={character.spell_slots || {}}
              onCast={(spellName) => socketSend(`施放 ${spellName}`)}
            />
          )}
        </aside>

        {/* 中栏 — 主舞台 */}
        <section className="flex-1 flex flex-col overflow-hidden">
          {/* 场景盒 */}
          <SceneBox scene={scene} />

          {/* 叙事区（NarrativeArea 自带滚动） */}
          <NarrativeArea log={log} />

          {/* 行动选项 */}
          {choices.length > 0 && (
            <div className="px-4 py-2 flex gap-2 flex-wrap border-t border-neutral-800">
              {choices.map((c, i) => (
                <button key={i} onClick={() => setInp(c)}
                  className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400 hover:bg-neutral-700">
                  {i + 1}. {c}
                </button>
              ))}
            </div>
          )}

          {/* 输入框 */}
          <div className="px-4 py-3 flex gap-2 border-t border-neutral-800">
            <input
              value={inp}
              onChange={(e) => setInp(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              placeholder="输入你的行动..."
              className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded focus:border-amber-400 focus:outline-none"
            />
            <button
              onClick={send}
              disabled={rolling}
              className="px-5 py-2 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40"
            >
              {rolling ? "🎲 掷骰中..." : "🎲 掷骰"}
            </button>
          </div>
        </section>

        {/* 右栏 — 战斗面板 */}
        <aside className="w-56 shrink-0 border-l border-neutral-800 overflow-y-auto p-3 space-y-3">
          {/* 战斗状态 */}
          <CombatBox combat={combat} />
          {combat?.active && (
            <button
              onClick={() => endTurn()}
              className="w-full px-2 py-1.5 bg-amber-400 text-neutral-900 font-bold rounded text-xs hover:bg-amber-300"
            >
              ⏭️ 结束回合
            </button>
          )}

          {/* 战利品 / 保存进度 */}
          <div className="border-t border-neutral-800 pt-2 space-y-1.5">
            {campId && <LootPanel campaignId={campId} partyNames={[myName || "冒险者"]} toast={toast} />}
            {charId && (
              <RestDialog onRest={async (type) => {
                try {
                  await apiPost(`/character/${charId}/rest`, { type });
                  refreshChar();
                  toast(type === "short" ? "短休完成" : "长休完成", "success");
                } catch (e) { toast("休息失败: " + errMsg(e), "error"); }
              }} />
            )}
            <button onClick={saveSession} className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400">
              💾 保存进度
            </button>
            {campId && charId && (
              <StrongholdPanel campaignId={campId} characterId={charId} toast={toast} />
            )}
          </div>

          {/* DM 控制面板 */}
          {isDm && (
            <div className="border-t border-neutral-800 pt-2 space-y-1.5">
              <div className="text-xs font-bold text-purple-400">DM 控制</div>
              <button onClick={() => ready()} className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400">
                ✓ 准备就绪
              </button>
              <button onClick={() => dmMonsterTurn("怪物")} className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400">
                👾 怪物回合
              </button>
              <button onClick={() => dmCombatEnd("victory")} className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400">
                ⚔️ 结束战斗
              </button>
            </div>
          )}

          {/* 房主管理 */}
          {isHost && roomId && <HostControls roomId={roomId} myName={myName} toast={toast} onTransferred={() => setIsHost(false)} />}

          {/* 玩家信息 */}
          <div className="border-t border-neutral-800 pt-2">
            <div className="text-xs text-neutral-500">玩家: {myName}</div>
            {campId && <div className="text-xs text-neutral-500">战役 #{campId}</div>}
            {roomId && <div className="text-xs text-neutral-500">房间 {roomId}{isHost ? " 👑" : ""}</div>}
          </div>

          {/* 规则速查 */}
          <RulesReference />
        </aside>
      </div>
    </main>
  );
}

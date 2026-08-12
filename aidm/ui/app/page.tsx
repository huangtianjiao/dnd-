"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { apiGet, apiPost, errMsg } from "./lib/api";
import type { OpeningData, RoomJoinResult, GameMode } from "./lib/types";
import { useSocket, setSessionToken } from "./hooks/useSocket";
import { useCharacter, useCombat, useGameState } from "./hooks/useGameState";
import { RoomPanel, HostControls } from "./components/RoomPanel";
import { OpeningConfirm } from "./components/OpeningConfirm";
import { LootPanel } from "./components/LootPanel";
import { FeatDialog } from "./components/FeatDialog";
import { StrongholdPanel } from "./components/StrongholdPanel";
import { SummaryModal } from "./components/SummaryModal";
import { MonsterInfoModal } from "./components/MonsterInfoModal";
import { RoomInfoModal } from "./components/RoomInfoModal";
import { FeatsBrowser } from "./components/FeatsBrowser";
import { MagicItemsBrowser } from "./components/MagicItemsBrowser";
import { HITLDialog } from "./components/HITLDialog";
import DiceLayer, { DiceLayerHandle } from "./components/v2/DiceLayer";
import { TopBar, PartyBar, SidePanel, PanelTab } from "./components/v2/chrome";
import { CombatBar, NarrativeStream, QuickChips, ActionInput } from "./components/v2/stage";
import { CharacterSheetTab, SpellbookTab, InventoryTab, RuleLookupTab } from "./components/v2/tabs";

// 购点法花费表（与后端 char_create.POINT_BUY_COST 一致，13 以上非线性）
const POINT_BUY_COST: Record<number, number> = { 8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9 };
const METHOD_LABEL: Record<string, string> = { standard_array: "标准阵列", point_buy: "购点法", roll: "掷骰", free: "自由" };

const ALIGNMENTS = [
  "守序善良", "中立善良", "混乱善良",
  "守序中立", "绝对中立", "混乱中立",
  "守序邪恶", "中立邪恶", "混乱邪恶",
];

const abilityMod = (score: number) => Math.floor((score - 10) / 2);

const DEFAULT_SETTING = "经典剑与魔法奇幻世界：边境小镇近日频频有商队失踪，镇长悬赏招募冒险者调查郊外的废弃矿坑。";

const suggestHP = (hitDie: number, conMod: number, level: number) =>
  hitDie + level * conMod + (level - 1) * (Math.floor(hitDie / 2) + 1);

const suggestAC = (armor: string, dexMod: number) => {
  let base = 10 + dexMod;
  if (armor.includes("重甲")) base = 16;
  else if (armor.includes("中甲")) base = 14 + Math.min(dexMod, 2);
  else if (armor.includes("轻甲")) base = 11 + dexMod;
  if (armor.includes("盾牌")) base += 2;
  return base;
};

export default function Page() {
  const [screen, setScreen] = useState<"menu" | "newGame" | "continue" | "join" | "createRoom" | "roomList" | "openingReview" | "game">("menu");
  const [campId, setCampId] = useState<number | null>(null);
  const [charId, setCharId] = useState<number | null>(null);
  const [inp, setInp] = useState("");
  const [campaigns, setCampaigns] = useState<{ id: number; name: string; setting?: string; summary?: string }[]>([]);
  const [myName, setMyName] = useState("");
  const [toastMsg, setToastMsg] = useState<{ msg: string; type: string } | null>(null);
  // 多角色战役恢复：先拉完整状态，再弹窗选“我是谁”
  const [pendingResume, setPendingResume] = useState<{ cid: number; st: any } | null>(null);

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
  const [abilityMethod, setAbilityMethod] = useState<"standard_array" | "point_buy" | "roll" | "free">("free");

  // ── 种族/职业/背景/法术 ──
  const [races, setRaces] = useState<{ name: string; speed: number }[]>([]);
  const [classes, setClasses] = useState<{ name: string; hit_die: number; armor_training: string; spellcasting?: string | null; subclasses?: string[]; subclass_level?: number }[]>([]);
  const [backgrounds, setBackgrounds] = useState<{ name: string; ability_scores: string[]; feat: string; skill_prof: string[]; tool_prof: string; equipment: string }[]>([]);
  const [spells, setSpells] = useState<{ name: string; level: number; school: string; casting_time: string; range: string; duration: string; components: string[]; description: string }[]>([]);

  // ── DM 模式 ──
  const [isDm, setIsDm] = useState(false);
  const [dmToken, setDmToken] = useState("");

  // ── v2 布局 UI state ──
  const [panelOpen, setPanelOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<PanelTab>("char");
  const [menuOpen, setMenuOpen] = useState(false);

  // ── 弹窗/扩展功能 ──
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [monsterName, setMonsterName] = useState<string | null>(null);
  const [roomInfoOpen, setRoomInfoOpen] = useState(false);
  const [featsOpen, setFeatsOpen] = useState(false);
  const [magicItemsOpen, setMagicItemsOpen] = useState(false);
  // ── HITL ──
  const [hitlMode, setHitlMode] = useState(false);
  const [hitlData, setHitlData] = useState<{ threadId: string; question: string } | null>(null);
  const [hitlLoading, setHitlLoading] = useState(false);

  const myNameRef = useRef(myName);
  myNameRef.current = myName;
  const diceLayerRef = useRef<DiceLayerHandle>(null);
  // 同配置重进（如从开场预览返回）时复用已建战役+角色，避免重复创建孤儿数据
  const createdRef = useRef<{ campId: number; charId: number; key: string } | null>(null);

  const toast = useCallback((msg: string, type = "info") => {
    setToastMsg({ msg, type });
    setTimeout(() => setToastMsg(null), 3000);
  }, []);

  // ── v2 状态层：叙事流/场景/队伍/时钟 + 角色卡 + 战斗 ──
  const gs = useGameState({
    getMyName: () => myNameRef.current,
    onDiceFace: (d) => {
      diceLayerRef.current?.play(d.d20);
    },
  });
  const { character, refreshChar, refreshDebounced } = useCharacter(charId);
  const { combat, setCombat, handleCombatUpdate, handleCombatEnd, loadCombat } = useCombat();

  // ── 拉取种族/职业/背景/法术列表 ──
  useEffect(() => {
    apiGet("/races").then((r: any) => setRaces(r.races || [])).catch(() => {});
    apiGet("/classes").then((r: any) => setClasses(r.classes || [])).catch(() => {});
    apiGet("/backgrounds").then((r: any) => setBackgrounds(r.backgrounds || [])).catch(() => {});
    apiGet("/spells").then((r: any) => setSpells(r.spells || [])).catch(() => {});
  }, []);

  // ── 自己 HP 同步到队伍条（依赖稳定的 syncOwnHp 而非 gs 对象，避免每渲染重跑） ──
  useEffect(() => {
    if (character && charId) gs.syncOwnHp(charId, character.hp, character.hp_max);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [character, charId, gs.syncOwnHp]);

  const { connectWS, send: socketSend, endTurn, ready, dmMonsterTurn, dmCombatEnd, disconnect } = useSocket({
    onLog: gs.onLog,
    onScene: gs.handleScene,
    onCombat: handleCombatUpdate,
    onChoices: gs.setChoices,
    onCharacterUpdate: refreshDebounced,
    onToast: toast,
    onServerDisconnect: () => setScreen("menu"),
    onCombatEnd: handleCombatEnd,
    onPartyUpdate: gs.onPartyUpdate,
    onResult: gs.onResult,
    onMonsterActionEvent: gs.onMonsterAction,
  });

  // ── ★ P0-04/P0-05: 连接前先经 /auth/session 换取服务器签名会话令牌 ──
  // DM 身份由后端校验 dm_token 后签发 role=dm 令牌决定；WS 凭据走 auth 载荷。
  const connectWithSession = useCallback(
    async (cid: number, chId: number, name: string) => {
      try {
        const r = await apiPost("/auth/session", {
          campaign_id: cid,
          character_id: chId,
          ...(isDm ? { dm_token: dmToken } : {}),
        });
        setSessionToken(r.token);
      } catch {
        setSessionToken("");
      }
      connectWS(cid, chId, name);
    },
    [connectWS, isDm, dmToken]
  );

  // ── 开始新游戏 ──
  const startNewGame = useCallback(async () => {
    if (starting) return;
    const name = myName.trim() || "冒险者";
    let setting = inp.trim();
    if (!setting) {
      setting = DEFAULT_SETTING;
      toast("未填写世界设定，已使用默认设定", "info");
    }

    // 校验全部前置：避免先建战役再校验失败留下孤儿数据
    const cls = classes.find((x) => x.name === charClass);
    const raceData = races.find((x) => x.name === charRace);
    if (!cls || !raceData) {
      toast("种族/职业数据未就绪，请稍候", "error");
      return;
    }
    const vals = Object.values(charAbilities);
    if (abilityMethod === "point_buy" && vals.reduce((s, v) => s + (POINT_BUY_COST[v] ?? 0), 0) > 27) {
      toast("购点法超支（>27），无法开始", "error");
      return;
    }
    if (abilityMethod === "standard_array" && [...vals].sort((a, b) => a - b).join() !== "8,10,12,13,14,15") {
      toast("标准阵列须为 [15,14,13,12,10,8] 的排列", "error");
      return;
    }

    setStarting(true);
    try {
      const cfgKey = JSON.stringify({ name, charRace, charClass, charSubclass, charBackground, charAlignment, charLevel, charAbilities, abilityMethod });
      let cid: number;
      let chid: number;
      if (createdRef.current && createdRef.current.key === cfgKey) {
        // 从开场预览返回后未改配置重新开始 → 直接复用
        cid = createdRef.current.campId;
        chid = createdRef.current.charId;
      } else {
        // 改了角色配置 → 复用已建战役，只重建角色
        cid = createdRef.current?.campId ?? (await apiPost("/campaign", { name: `${name}的冒险` })).id;
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
          campaign_id: cid,
        });
        chid = ch.id;
        createdRef.current = { campId: cid, charId: chid, key: cfgKey };
      }

      setCampId(cid);
      setCharId(chid);
      setMyName(name);
      setWorldSetting(setting);

      toast("DM 生成开场中...(约10秒)", "info");
      const r = await apiPost("/open", {
        setting,
        tone: "",
        campaign_id: cid,
        character_id: chid,
      });

      setOpening({ narration: r.narration || "", action_options: r.action_options || [], scene: r.scene });
      setScreen("openingReview");
    } catch (e: any) {
      toast("创建游戏失败: " + errMsg(e), "error");
    } finally {
      setStarting(false);
    }
  }, [starting, myName, inp, charRace, charClass, charSubclass, charBackground, charAlignment, charLevel, charAbilities, abilityMethod, classes, races, toast]);

  const confirmOpening = useCallback(() => {
    if (!campId || !charId) return;
    const name = myName.trim() || "冒险者";
    gs.reset(opening?.narration ? [{ type: "dm", speaker: "地下城主", text: opening.narration }] : []);
    if (opening?.action_options) gs.setChoices(opening.action_options);
    if (opening?.scene) gs.setScene(opening.scene);
    setScreen("game");
    connectWithSession(campId, charId, name);
    refreshChar();
    setInp("");
    createdRef.current = null; // 正式开局，下次新游戏从零创建
  }, [campId, charId, myName, opening, gs, connectWS, refreshChar, isDm, dmToken]);

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

  const buildCharacter = useCallback(
    (name: string) => {
      const cls = classes.find((x) => x.name === charClass);
      const raceData = races.find((x) => x.name === charRace);
      const hitDie = cls?.hit_die ?? 8;
      const armor = cls?.armor_training ?? "轻甲";
      const speed = raceData?.speed ?? 30;
      return {
        race: charRace,
        char_class: charClass,
        subclass: charSubclass,
        background: charBackground,
        alignment: charAlignment,
        level: charLevel,
        abilities: charAbilities,
        ability_method: abilityMethod,
        hp_max: suggestHP(hitDie, abilityMod(charAbilities.con), charLevel),
        ac: suggestAC(armor, abilityMod(charAbilities.dex)),
        speed,
      };
    },
    [charRace, charClass, charSubclass, charBackground, charAlignment, charLevel, charAbilities, abilityMethod, classes, races]
  );

  const switchAbilityMethod = useCallback((m: "standard_array" | "point_buy" | "roll" | "free") => {
    setAbilityMethod(m);
    if (m === "standard_array") setCharAbilities({ str: 15, dex: 14, con: 13, int: 12, wis: 10, cha: 8 });
    else if (m === "point_buy") setCharAbilities({ str: 8, dex: 8, con: 8, int: 8, wis: 8, cha: 8 });
  }, []);

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
  }, [toast]);

  const enterRoomGame = useCallback(
    (r: RoomJoinResult, host: boolean, name: string, setting?: string) => {
      setCampId(r.campaign_id);
      setCharId(r.character_id);
      setMyName(name);
      setRoomId(r.room_id);
      setIsHost(host);
      gs.reset([{ type: "event", text: `加入房间 ${r.room_id}${host ? "（房主）" : ""}`, eventCls: "" }]);
      setScreen("game");
      connectWithSession(r.campaign_id, r.character_id, name);
      setTimeout(() => {
        apiGet(`/scene/${r.campaign_id}`).then(gs.setScene).catch(() => {});
        loadCombat(r.campaign_id);
      }, 100);
      // 房主带世界设定建房 → 生成开场（与单人 /open 同链路，补齐多人局无开场的缺口）
      if (host && setting) {
        setWorldSetting(setting);
        gs.pushEvent("⛳ DM 正在生成开场（约 10 秒）...", "");
        apiPost("/open", {
          setting,
          tone: "",
          campaign_id: r.campaign_id,
          character_id: r.character_id,
        })
          .then((o: any) => {
            gs.onResult({ player: name, narration: o.narration || "", action_options: o.action_options || [], scene: o.scene });
          })
          .catch((e) => toast("开场生成失败: " + errMsg(e), "error"));
      }
    },
    [gs, connectWS, loadCombat, isDm, dmToken, toast]
  );

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

  const showContinue = useCallback(async () => {
    setScreen("continue");
    try {
      const data = await apiGet("/campaigns");
      setCampaigns(data.campaigns || []);
    } catch (e) {
      toast("加载战役失败", "error");
    }
  }, [toast]);

  /** 选定角色后完成恢复：历史叙事流 + 场景/战斗 + 行动选项 + 房间上下文 */
  const finishResume = useCallback(
    (cid: number, st: any, ch: { id: number; name: string }) => {
      setCharId(ch.id);
      setMyName(ch.name);
      setCampId(cid);
      setPendingResume(null);
      // 历史恢复：摘要在前，最近对话（Log 表）在后
      const initial: { type: "event" | "dm" | "player"; text: string; speaker?: string; eventCls?: "" }[] = [];
      if (st.summary) initial.push({ type: "event", text: `📖 剧情回顾：${st.summary}`, eventCls: "" });
      for (const h of st.history || []) {
        if (h.player_input) initial.push({ type: "player", speaker: ch.name, text: h.player_input });
        if (h.dm_output) initial.push({ type: "dm", speaker: "地下城主", text: h.dm_output });
      }
      gs.reset(initial);
      gs.setScene(st.scene ?? null);
      // 行动选项：场景出路优先，否则给通用探索选项，避免恢复后快捷条空白
      const exits: string[] = st.scene?.exits || [];
      gs.setChoices(exits.length ? exits : ["观察四周", "回忆当前处境", "检查随身装备"]);
      setCombat(st.combat ?? null);
      setScreen("game");
      connectWithSession(cid, ch.id, ch.name);
      // 房间上下文恢复（房间为内存对象，重启后 404 属正常 → 静默忽略）
      apiGet(`/room/by-campaign/${cid}`)
        .then((room: any) => {
          setRoomId(room.room_id);
          const host = (room.players || []).find((p: any) => p.is_host);
          setIsHost(!!host && host.character_id === ch.id);
        })
        .catch(() => {});
    },
    [gs, setCombat, connectWS, isDm, dmToken]
  );

  const resumeCampaign = useCallback(
    async (cid: number) => {
      try {
        const st = await apiGet(`/campaign/${cid}/state`);
        const chars = st.characters || [];
        if (chars.length === 0) {
          toast("该战役没有角色", "warn");
        } else if (chars.length === 1) {
          finishResume(cid, st, chars[0]);
        } else {
          // 多角色战役 → 弹窗选择“我是谁”
          setPendingResume({ cid, st });
        }
      } catch (e: any) {
        toast("继续游戏失败: " + errMsg(e), "error");
      }
    },
    [finishResume, toast]
  );

  const joinGame = useCallback(async () => {
    const cid = parseInt(inp);
    if (!cid) {
      toast("请填写战役编号", "warn");
      return;
    }
    const name = myName.trim() || "冒险者";
    try {
      const ch = await apiPost("/join", { name, campaign_id: cid, ...buildCharacter(name) });
      setCharId(ch.character_id || ch.id);
      setCampId(cid);
      setMyName(name);
      gs.reset([{ type: "event", text: `加入战役 #${cid}`, eventCls: "" }]);
      setScreen("game");
      connectWithSession(cid, ch.character_id || ch.id, name);
      setInp("");
      // 同步当前场景/战斗（晚于 WS 连接，作为兼容兑底）
      setTimeout(() => {
        apiGet(`/scene/${cid}`).then(gs.setScene).catch(() => {});
        loadCombat(cid);
      }, 100);
    } catch (e: any) {
      toast("加入战役失败: " + errMsg(e), "error");
    }
  }, [inp, myName, gs, connectWS, toast, buildCharacter, isDm, dmToken, loadCombat]);

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

  // ── HITL：REST /chat 结果复用 WS result 的结构化消费路径 ──
  const applyChatResult = useCallback(
    (r: any) => {
      gs.onResult({ ...r, player: myNameRef.current });
      if (r.combat) setCombat(r.combat);
      refreshChar();
    },
    [gs, setCombat, refreshChar]
  );

  const sendWithHITL = useCallback(
    async (text: string) => {
      if (!campId || !charId) return;
      setHitlLoading(true);
      try {
        const r = await apiPost("/chat", {
          player_input: text,
          campaign_id: campId,
          character_id: charId,
          // 与 WS 路径（ws.on_action）同一 LangGraph 线程，避免双路径上下文分叉
          thread_id: `campaign_${campId}`,
          hitl: true,
        });
        if (r.interrupted) {
          setHitlData({ threadId: r.thread_id || `campaign_${campId}`, question: r.question || "确认执行此行动？" });
        } else {
          applyChatResult(r);
        }
      } catch (e: any) {
        toast("HITL 请求失败: " + errMsg(e), "error");
      } finally {
        setHitlLoading(false);
      }
    },
    [campId, charId, applyChatResult, toast]
  );

  const handleHITLConfirm = useCallback(async () => {
    if (!hitlData) return;
    setHitlLoading(true);
    try {
      // ★ P1-03: resume 需携带角色身份（ownership 校验）
      const r = await apiPost("/chat/resume", {
        thread_id: hitlData.threadId,
        answer: "y",
        character_id: charId,
      });
      if (r.interrupted) {
        setHitlData({ threadId: r.thread_id || hitlData.threadId, question: r.question || hitlData.question });
      } else {
        applyChatResult(r);
        setHitlData(null);
      }
    } catch (e: any) {
      toast("确认失败: " + errMsg(e), "error");
      setHitlData(null);
    } finally {
      setHitlLoading(false);
    }
  }, [hitlData, charId, applyChatResult, toast]);

  const handleHITLCancel = useCallback(() => {
    setHitlData(null);
    gs.pushEvent("行动已取消", "");
  }, [gs]);

  // ── 唯一行动入口：chips / 输入框 / 法术施展 / 死亡豁免 全部汇聚于此 ──
  const send = useCallback(
    (text: string) => {
      if (!text) return;
      gs.pushPlayer(text);
      if (hitlMode) sendWithHITL(text);
      else socketSend(text);
    },
    [gs, socketSend, hitlMode, sendWithHITL]
  );

  // ── 自由掷骰（本地，不发后端） ──
  const handleFreeRoll = useCallback(async () => {
    const v = await diceLayerRef.current?.rollFree();
    if (v) {
      gs.pushDiceCard({
        title: "自由掷骰",
        formula: `d20 = ${v}`,
        face: v,
        verdict: v === 20 ? "大成功" : v === 1 ? "大失败" : "结果",
        vcls: v === 20 ? "crit" : v === 1 ? "miss" : "hit",
        fcls: v === 20 ? "crit" : v === 1 ? "fail" : "",
      });
    }
  }, [gs]);

  // ── 模式派生：战斗 > 社交（场景有 NPC）> 探索（§1.4） ──
  const mode: GameMode = combat?.active ? "combat" : gs.scene?.npcs?.length ? "social" : "explore";

  // ── 全局 Toast ──
  const toastEl = toastMsg ? (
    <div className={`toast toast-${toastMsg.type === "error" ? "error" : toastMsg.type === "warn" ? "warn" : toastMsg.type === "success" ? "success" : "info"}`}>
      {toastMsg.msg}
    </div>
  ) : null;

  // ════════════════════════════════════════════════════════════════════
  // 非游戏屏幕（onboarding，保留原有交互）
  // ════════════════════════════════════════════════════════════════════

  if (screen === "menu") {
    return (
      <main className="screen">
        {toastEl}
        <div className="screen-card flex-col" style={{ alignItems: "center", gap: 12 }}>
          <h1 className="title-lg" style={{ fontSize: 28, marginBottom: 4 }}>🐉 AI DM</h1>
          <p className="text-muted text-sm" style={{ marginBottom: 16 }}>D&D 5E 硬性判定链跑团系统</p>
          <div className="flex-col w-full" style={{ gap: 8 }}>
            <button className="btn btn-primary w-full" onClick={() => setScreen("newGame")}>🆕 开始新游戏</button>
            <button className="btn btn-secondary w-full" onClick={showContinue}>📖 继续游戏</button>
            <button className="btn btn-secondary w-full" onClick={() => setScreen("join")}>🚪 加入游戏</button>
            <button className="btn btn-secondary w-full" onClick={() => setScreen("createRoom")}>🏰 创建房间</button>
            <button className="btn btn-secondary w-full" onClick={() => setScreen("roomList")}>📋 房间列表</button>
            <button className="btn btn-amber w-full" onClick={() => { setIsDm(true); setScreen("join"); }}>🎭 以 DM 身份加入</button>
          </div>
        </div>
      </main>
    );
  }

  if (screen === "newGame") {
    if (!races.length || !classes.length) {
      return (
        <main className="screen">
          {toastEl}
          <div className="text-muted">加载种族/职业数据...</div>
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
      <main className="screen">
        {toastEl}
        <div className="screen-card flex-col" style={{ gap: 12 }}>
          <h2 className="title-lg">开始新冒险</h2>

          <input className="form-input" value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." />

          <div className="flex-row" style={{ gap: 8 }}>
            <label className="form-label" style={{ flex: 1 }}>
              <span>种族</span>
              <select className="form-input" value={charRace} onChange={(e) => setCharRace(e.target.value)}>
                {races.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
              </select>
            </label>
            <label className="form-label" style={{ flex: 1 }}>
              <span>职业</span>
              <select className="form-input" value={charClass} onChange={(e) => setCharClass(e.target.value)}>
                {classes.map((c) => <option key={c.name} value={c.name}>{c.name}</option>)}
              </select>
            </label>
            <label className="form-label" style={{ flex: 1 }}>
              <span>等级</span>
              <input type="number" min={1} max={20} className="form-input" value={charLevel}
                onChange={(e) => setCharLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))} />
            </label>
          </div>

          {(() => {
            const cls2 = classes.find((x) => x.name === charClass);
            const subs = cls2?.subclasses || [];
            const subLv = cls2?.subclass_level || 3;
            if (subs.length === 0 || charLevel < subLv) return null;
            return (
              <label className="form-label">
                <span>子职（{subLv}级解锁）</span>
                <select className="form-input" value={charSubclass} onChange={(e) => setCharSubclass(e.target.value)}>
                  <option value="">(不选)</option>
                  {subs.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
            );
          })()}

          <div className="flex-row" style={{ gap: 8 }}>
            <label className="form-label" style={{ flex: 1 }}>
              <span>背景</span>
              <select className="form-input" value={charBackground} onChange={(e) => setCharBackground(e.target.value)}>
                <option value="">(无)</option>
                {backgrounds.map((b) => <option key={b.name} value={b.name}>{b.name}</option>)}
              </select>
            </label>
            <label className="form-label" style={{ flex: 1 }}>
              <span>阵营</span>
              <select className="form-input" value={charAlignment} onChange={(e) => setCharAlignment(e.target.value)}>
                {ALIGNMENTS.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </label>
          </div>

          <div className="flex-col" style={{ gap: 8 }}>
            <div className="flex-between">
              <span className="text-xs text-muted">六维属性</span>
              <div className="flex-row" style={{ gap: 4 }}>
                {(["standard_array", "point_buy", "roll", "free"] as const).map((m) => (
                  <button key={m} onClick={m === "roll" ? rollAbilities : () => switchAbilityMethod(m)}
                    className={`btn ${abilityMethod === m ? "btn-amber" : "btn-secondary"}`}
                    style={{ padding: "4px 8px", fontSize: 11 }}>
                    {METHOD_LABEL[m]}
                  </button>
                ))}
              </div>
            </div>
            {abilityMethod === "point_buy" && (
              <div className="text-xs" style={{ color: pbRemaining < 0 ? "var(--text-red)" : pbRemaining > 0 ? "var(--text-tertiary)" : "var(--text-green)" }}>
                购点 {pbTotal}/27 剩余 {pbRemaining}{pbRemaining < 0 ? " 超支!" : ""}
              </div>
            )}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 4 }}>
              {ABILITY_KEYS.map(([k, label]) => {
                const v = charAbilities[k] || 10;
                const m = abilityMod(v);
                const lo = abilityMethod === "point_buy" ? 8 : 1;
                const hi = abilityMethod === "point_buy" ? 15 : 20;
                return (
                  <div key={k} style={{ background: "var(--bg-secondary)", borderRadius: 6, padding: 4, textAlign: "center" }}>
                    <div className="text-10 text-muted">{label}</div>
                    <input type="number" min={lo} max={hi} value={v}
                      onChange={(e) => setCharAbilities({ ...charAbilities, [k]: Math.max(lo, Math.min(hi, parseInt(e.target.value) || lo)) })}
                      style={{ width: "100%", textAlign: "center", background: "var(--bg-primary)", border: "0.5px solid var(--border)", borderRadius: 4, fontSize: 14, padding: "2px 0" }}
                    />
                    <div className="text-10 text-purple">{m >= 0 ? `+${m}` : m}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="text-xs flex-row" style={{ gap: 16 }}>
            <span>生命值上限 <b className="text-purple">{hpPreview}</b></span>
            <span>护甲 <b className="text-purple">{acPreview}</b></span>
            <span>速度 <b className="text-purple">{raceData.speed}</b></span>
          </div>

          <textarea className="form-input" value={inp} onChange={(e) => setInp(e.target.value)} placeholder="输入世界设定..." rows={4}
            style={{ resize: "none" }} />
          <div className="flex-row" style={{ gap: 8 }}>
            <button className="btn btn-secondary" onClick={generateWorld}>✨ AI 生成世界设定</button>
            <button className="btn btn-secondary" onClick={() => setScreen("menu")}>← 返回</button>
          </div>
          <button className="btn btn-primary w-full" onClick={startNewGame} disabled={starting}>
            {starting ? "⏳ 创建中...（DM 生成开场约 10 秒）" : "🗺️ 开始冒险"}
          </button>
        </div>
      </main>
    );
  }

  if (screen === "continue") {
    return (
      <main className="screen">
        {toastEl}
        <div className="screen-card flex-col" style={{ gap: 12 }}>
          <h2 className="title-lg">继续冒险</h2>
          {campaigns.length === 0 ? (
            <p className="text-muted">暂无保存的战役</p>
          ) : (
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
              {campaigns.map((c) => (
                <li key={c.id}>
                  <button className="btn btn-secondary w-full" style={{ textAlign: "left" }} onClick={() => resumeCampaign(c.id)}>
                    <div className="text-purple text-bold">#{c.id} {c.name}</div>
                    <div className="text-xs text-muted">{c.setting || "(无设定)"}</div>
                    {c.summary && <div className="text-xs text-muted">📖 {c.summary}</div>}
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button className="btn btn-secondary" onClick={() => setScreen("menu")}>← 返回</button>
        </div>

        {/* 多角色战役：选择“我是谁” */}
        {pendingResume && (
          <div className="modal-overlay visible" onClick={() => setPendingResume(null)}>
            <div className="modal" style={{ maxWidth: 380 }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <span className="mh-title">选择你的角色</span>
                <button className="modal-close" onClick={() => setPendingResume(null)}>✕</button>
              </div>
              <div className="modal-body flex-col" style={{ gap: 8 }}>
                {(pendingResume.st.characters || []).map((ch: any) => (
                  <button key={ch.id} className="btn btn-secondary w-full" style={{ textAlign: "left" }}
                    onClick={() => finishResume(pendingResume.cid, pendingResume.st, ch)}>
                    <div className="text-purple text-bold">{ch.name}</div>
                    <div className="text-xs text-muted">Lv{ch.level} {ch.char_class} · HP {ch.hp}/{ch.hp_max} · AC {ch.ac}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    );
  }

  if (screen === "join") {
    return (
      <main className="screen">
        {toastEl}
        <div className="screen-card flex-col" style={{ gap: 12 }}>
          <h2 className="title-lg">{isDm ? "以 DM 身份加入" : "加入战役"}</h2>
          <input className="form-input" value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." />
          <div className="flex-row" style={{ gap: 8 }}>
            <label className="form-label" style={{ flex: 1 }}>
              <span>种族</span>
              <select className="form-input" value={charRace} onChange={(e) => setCharRace(e.target.value)}>
                {races.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
              </select>
            </label>
            <label className="form-label" style={{ flex: 1 }}>
              <span>职业</span>
              <select className="form-input" value={charClass} onChange={(e) => setCharClass(e.target.value)}>
                {classes.map((c) => <option key={c.name} value={c.name}>{c.name}</option>)}
              </select>
            </label>
            <label className="form-label" style={{ flex: 1 }}>
              <span>等级</span>
              <input type="number" min={1} max={20} className="form-input" value={charLevel}
                onChange={(e) => setCharLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))} />
            </label>
          </div>
          <input className="form-input" value={inp} onChange={(e) => setInp(e.target.value)} placeholder="战役编号（数字，好友屏幕右下角“战役 #”后的数字）..." />
          <p className="text-xs text-muted" style={{ margin: 0 }}>若好友给的是 6 位房间短码，请从主菜单“📋 房间列表”加入</p>
          {isDm && (
            <input className="form-input" type="password" value={dmToken} onChange={(e) => setDmToken(e.target.value)}
              placeholder="DM 口令（服务未配置 AIDM_DM_TOKEN 时可留空）..." />
          )}
          <div className="flex-row" style={{ gap: 8 }}>
            <button className="btn btn-primary" style={{ flex: 1 }} onClick={joinGame}>🚪 加入</button>
            <button className="btn btn-secondary" onClick={() => { setIsDm(false); setScreen("menu"); }}>← 返回</button>
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

  // ════════════════════════════════════════════════════════════════════
  // 游戏主界面（v2：叙事中心布局，见 docs/FRONTEND_REDESIGN.md）
  // ════════════════════════════════════════════════════════════════════

  return (
    <main className={`v2-app ${panelOpen ? "" : "panel-collapsed"}`} data-mode={mode}>
      {toastEl}

      <TopBar
        campaignName={gs.scene?.campaign_name || `${myName || "冒险者"}的冒险`}
        mode={mode}
        clock={gs.gameClock}
        onOpenMenu={() => setMenuOpen(true)}
        onTogglePanel={() => setPanelOpen((v) => !v)}
      />

      <PartyBar members={gs.party} myName={myName} combat={combat} />

      {/* ===== 主舞台 ===== */}
      <section className="v2-stage">
        <CombatBar
          combat={combat}
          myName={myName}
          onEnemyClick={(n) => setMonsterName(n)}
          onEndTurn={endTurn}
        />
        <NarrativeStream messages={gs.messages} busy={gs.busy || hitlLoading} />
        <QuickChips mode={mode} choices={gs.choices} onAction={send} disabled={gs.busy} />
        <ActionInput onSend={send} onFreeRoll={handleFreeRoll} disabled={gs.busy} />
      </section>

      {/* ===== 右栏（可折叠） ===== */}
      <SidePanel
        activeTab={activeTab}
        onTabChange={setActiveTab}
        charContent={
          <CharacterSheetTab
            character={character}
            onDeathSaveRoll={() => send("掷死亡豁免")}
            featSlot={charId ? <FeatDialog charId={charId} onSelected={refreshChar} toast={toast} /> : undefined}
          />
        }
        spellContent={
          <SpellbookTab character={character} spells={spells} onCast={(name) => send(`施放 ${name}`)} />
        }
        itemContent={
          charId ? (
            <InventoryTab
              characterId={charId}
              character={character}
              toast={toast}
              onUpdated={refreshChar}
              extra={
                <>
                  {campId && <LootPanel campaignId={campId} partyNames={[myName || "冒险者"]} toast={toast} />}
                  {campId && charId && <StrongholdPanel campaignId={campId} characterId={charId} toast={toast} />}
                </>
              }
            />
          ) : (
            <div className="v2-panel-loading">—</div>
          )
        }
        ruleContent={<RuleLookupTab />}
        footer={
          <div className="v2-panel-meta">
            <div>玩家：{myName}</div>
            {campId && <div>战役 #{campId}</div>}
            {roomId && (
              <div>
                房间 {roomId}
                {isHost ? " 👑" : ""}
              </div>
            )}
          </div>
        }
      />

      {/* ===== 3D 骰子动画层 ===== */}
      <DiceLayer ref={diceLayerRef} />

      {/* ===== 菜单弹窗 ===== */}
      {menuOpen && (
        <div className="modal-overlay visible" onClick={() => setMenuOpen(false)}>
          <div className="modal" style={{ maxWidth: 380 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="mh-title">☰ 菜单</span>
              <button className="modal-close" onClick={() => setMenuOpen(false)}>✕</button>
            </div>
            <div className="modal-body flex-col">
              {campId && (
                <button className="btn btn-secondary w-full" onClick={() => { setMenuOpen(false); saveSession(); }}>
                  💾 保存进度
                </button>
              )}
              {campId && (
                <button className="btn btn-secondary w-full" onClick={() => { setMenuOpen(false); setSummaryOpen(true); }}>
                  📖 剧情回顾
                </button>
              )}
              {roomId && (
                <button className="btn btn-secondary w-full" onClick={() => { setMenuOpen(false); setRoomInfoOpen(true); }}>
                  🏠 房间信息
                </button>
              )}
              <button className="btn btn-secondary w-full" onClick={() => { setMenuOpen(false); setFeatsOpen(true); }}>
                📋 专长参考
              </button>
              <button className="btn btn-secondary w-full" onClick={() => { setMenuOpen(false); setMagicItemsOpen(true); }}>
                🔮 魔法物品图鉴
              </button>
              {campId && charId && (
                <label className="flex-row" style={{ gap: 6, alignItems: "center", cursor: "pointer" }}>
                  <input type="checkbox" checked={hitlMode} onChange={(e) => setHitlMode(e.target.checked)} />
                  <span className="text-xs">HITL 确认模式（AI 判定前人工确认）</span>
                </label>
              )}
              {isDm && (
                <>
                  <div className="text-xs text-bold mt-2">DM 控制</div>
                  <button className="btn btn-secondary w-full" onClick={() => ready()}>
                    ✓ 准备就绪
                  </button>
                  <button className="btn btn-secondary w-full" onClick={() => dmMonsterTurn("怪物")}>
                    👾 怪物回合
                  </button>
                  <button className="btn btn-secondary w-full" onClick={() => { dmCombatEnd("victory"); setMenuOpen(false); }}>
                    ⚔️ 结束战斗
                  </button>
                </>
              )}
              {isHost && roomId && (
                <HostControls roomId={roomId} players={gs.party} toast={toast} onTransferred={() => setIsHost(false)} />
              )}
              <button className="btn btn-amber w-full" onClick={() => { disconnect(); setScreen("menu"); }}>
                🚪 退出到主菜单
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===== 扩展弹窗（逻辑保留自旧版） ===== */}
      {summaryOpen && campId && <SummaryModal campaignId={campId} onClose={() => setSummaryOpen(false)} />}
      {monsterName && <MonsterInfoModal monsterName={monsterName} onClose={() => setMonsterName(null)} />}
      {roomInfoOpen && roomId && <RoomInfoModal roomId={roomId} onClose={() => setRoomInfoOpen(false)} />}
      {featsOpen && <FeatsBrowser onClose={() => setFeatsOpen(false)} />}
      {magicItemsOpen && <MagicItemsBrowser onClose={() => setMagicItemsOpen(false)} toast={toast} />}

      {/* ===== HITL 确认弹窗 ===== */}
      {hitlData && (
        <HITLDialog question={hitlData.question} onConfirm={handleHITLConfirm} onCancel={handleHITLCancel} />
      )}
      {hitlLoading && (
        <div className="modal-overlay visible" style={{ background: "rgba(0,0,0,0.25)" }}>
          <div className="modal" style={{ maxWidth: 300, padding: 24, textAlign: "center" }}>
            <div className="text-muted">⏳ DM 判定中...</div>
          </div>
        </div>
      )}
    </main>
  );
}

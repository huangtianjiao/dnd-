/** 类型定义 */

export interface AbilityScore {
  score: number;
  mod: number;
}

export interface CharacterSheet {
  id: number;
  name: string;
  race: string;
  char_class: string;
  subclass?: string;
  background?: string;
  alignment?: string;
  level: number;
  proficiency: number;
  abilities: Record<string, AbilityScore>;
  hp: number;
  hp_max: number;
  temp_hp?: number;
  ac: number;
  speed: number;
  conditions: string[];
  exhaustion: number;
  spell_slots?: Record<string, number>;
  known_spells?: string[];
  attuned_items?: string[];
  equipped_weapon?: string;
  hit_dice_current?: number;
  hit_dice_max?: number;
  dead?: boolean;
  stable?: boolean;
  death_successes?: number;
  death_failures?: number;
}

export interface SceneData {
  location?: string;
  time?: string;
  atmosphere?: string;
  environment?: string;
  npcs?: { name: string; attitude: string; role: string }[];
  exits?: string[];
  situation?: string;
  story_log?: string;
  world_background?: string;
  campaign_name?: string;
}

export interface Combatant {
  name: string;
  initiative: number;
  side: string;
  cid?: string;
  is_player?: boolean;
  hp?: number;
  hp_max?: number;
  surprised?: boolean;
  dead?: boolean;
}

export interface CombatData {
  active: boolean;
  round: number;
  current_turn?: string;
  initiative_order?: Combatant[];
}

// ── 叙事流消息（v2 重设计，见 docs/FRONTEND_REDESIGN.md §1.3） ──

export type GameMode = "explore" | "social" | "combat";

export interface DiceCardData {
  title: string;
  formula: string;
  face: string | number;
  verdict: string;
  vcls: "hit" | "miss" | "crit";
  fcls?: "crit" | "fail" | "";
}

export interface HarmCardData {
  text: string;
  amount: number;
  kind: "dmg" | "heal";
  kill?: boolean;
}

export interface StreamMessage {
  id: number;
  type: "dm" | "player" | "dice" | "harm" | "event" | "meta";
  speaker?: string;
  text?: string;
  dice?: DiceCardData;
  harm?: HarmCardData;
  eventCls?: "" | "combat" | "time";
}

/** 游戏内时钟（后端 result.dice.time 推送，B4 时间推进） */
export interface GameClock {
  day: number;
  label: string; // 凌晨/早晨/上午/午后/下午/黄昏/夜晚/深夜
}

export type AdvantageMode = "normal" | "adv" | "dis";

export interface DiceRollResult {
  sides: number;
  count: number;
  rolls: number[];
  total: number;
  modifier: number;
  finalTotal: number;
  advantage: AdvantageMode;
}

export interface LogEntry {
  c: "dm" | "you" | "dice" | "meta" | "npc" | "damage" | "system" | "other";
  t: string;
  speaker?: string;
  roll?: DiceRollResult;
  // 旧格式兼容：后端 result 事件可能携带结构化骰子数据
  diceData?: { d20: number; hit: boolean; crit: boolean; damage?: number };
}

// ── 行动日志（右栏，纯前端） ──

export interface ActionLogEntry {
  text: string;
  time: string; // "HH:MM"
  cls?: "highlight" | "damage" | "";
}

// ── 派对成员（从 socket join/leave 事件推导） ──

export interface PartyMember {
  name: string;
  characterId: number;
  isDm: boolean;
  connected: boolean;
  hp?: number;
  hpMax?: number;
}

// ── 房间（多人） ──

export interface RoomInfo {
  room_id: string;
  campaign_id: number;
  campaign_name: string;
  has_password: boolean;
  max_players: number;
  player_count?: number;
  players?: string[];
  host?: string;
}

export interface RoomJoinResult {
  room_id: string;
  campaign_id: number;
  character_id: number;
  name: string;
  ws_url?: string;
}

// ── 战利品 ──

export interface LootItem {
  item_id: string;
  name: string;
  type: string;
  rarity: string;
  value_gp: number;
  quantity: number;
  description?: string;
}

export interface LootPool {
  pool_id: string;
  gold: number;
  items: LootItem[];
}

export type LootMode = "NEED_FIRST" | "ROUND_ROBIN" | "ROLL_OFF" | "DM_ASSIGN";

export interface LootDistribution {
  record_id: string;
  mode: string;
  gold_distribution: Record<string, number>;
  item_distribution: Record<string, LootItem[] | string[] | any>;
  timestamp?: string;
}

// ── 专长 ──

export interface FeatInfo {
  name: string;
  description?: string;
  prerequisite?: string;
  [key: string]: any;
}

export interface AvailableFeats {
  level: number;
  feat_available: boolean;
  available_feats: (FeatInfo | string)[];
  count: number;
}

// ── 开场 ──

export interface OpeningData {
  narration: string;
  action_options: string[];
  scene?: SceneData;
}

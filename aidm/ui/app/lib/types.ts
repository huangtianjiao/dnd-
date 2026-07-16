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
  attuned_items?: string[];
  dead?: boolean;
  stable?: boolean;
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

export interface CombatData {
  active: boolean;
  round: number;
  current_turn?: string;
  initiative_order?: { name: string; initiative: number; side: string }[];
}

export interface LogEntry {
  c: string; // dm | you | dice | meta | npc | damage | system | other
  t: string;
  roll?: { d20: number; hit: boolean; crit: boolean; damage?: number };
}

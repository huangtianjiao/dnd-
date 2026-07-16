"use client";

import { useState } from "react";

interface ConditionTrackerProps {
  conditions: string[];
  onAdd: (condition: string) => void;
  onRemove: (condition: string) => void;
}

const CONDITION_LIST = [
  "目盲", "魅惑", "耳聋", "恐慌", "受擒",
  "失能", "隐形", "麻痹", "石化", "力竭",
  "中毒", "倒地", "束缚", "震慑", "昏迷",
];

const CONDITION_COLORS: Record<string, string> = {
  中毒: "bg-green-900 border-green-700 text-green-300",
  倒地: "bg-amber-900 border-amber-700 text-amber-300",
  恐慌: "bg-red-900 border-red-700 text-red-300",
  束缚: "bg-neutral-700 border-neutral-500 text-neutral-300",
  目盲: "bg-gray-800 border-gray-600 text-gray-300",
  魅惑: "bg-pink-900 border-pink-700 text-pink-300",
  麻痹: "bg-purple-900 border-purple-700 text-purple-300",
  昏迷: "bg-red-950 border-red-800 text-red-400",
  力竭: "bg-orange-900 border-orange-700 text-orange-300",
};

export function ConditionTracker({ conditions, onAdd, onRemove }: ConditionTrackerProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const available = CONDITION_LIST.filter((c) => !conditions.includes(c));

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] text-neutral-500 uppercase">状态</span>
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="text-[10px] px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400"
        >
          + 添加
        </button>
      </div>

      {/* 下拉菜单 */}
      {dropdownOpen && (
        <div className="absolute z-50 mt-1 w-32 bg-neutral-900 border border-neutral-700 rounded shadow-lg max-h-48 overflow-y-auto">
          {available.length === 0 ? (
            <div className="px-2 py-1 text-[10px] text-neutral-600">无可添加状态</div>
          ) : (
            available.map((c) => (
              <button
                key={c}
                onClick={() => {
                  onAdd(c);
                  setDropdownOpen(false);
                }}
                className="w-full text-left px-2 py-1 text-xs hover:bg-neutral-800"
              >
                {c}
              </button>
            ))
          )}
        </div>
      )}

      {/* 当前条件标签 */}
      <div className="flex flex-wrap gap-1">
        {conditions.length === 0 ? (
          <span className="text-[10px] text-neutral-700">无状态</span>
        ) : (
          conditions.map((c) => (
            <span
              key={c}
              className={`text-[10px] px-1.5 py-0.5 rounded border cursor-pointer ${
                CONDITION_COLORS[c] || "bg-neutral-800 border-neutral-700 text-neutral-300"
              }`}
              onClick={() => onRemove(c)}
              title={`点击移除 ${c}`}
            >
              {c} ✕
            </span>
          ))
        )}
      </div>
    </div>
  );
}

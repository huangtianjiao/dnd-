"use client";

import { useState } from "react";

interface TacticalGridProps {
  rows?: number;
  cols?: number;
}

interface Cell {
  type: "empty" | "wall" | "difficult" | "player" | "enemy";
  label?: string;
}

export function TacticalGrid({ rows = 6, cols = 10 }: TacticalGridProps) {
  const [grid, setGrid] = useState<Cell[][]>(() => {
    const g: Cell[][] = Array.from({ length: rows }, () =>
      Array.from({ length: cols }, () => ({ type: "empty" as const }))
    );
    // 示例布局
    g[2][1] = { type: "player", label: "P" };
    g[3][4] = { type: "enemy", label: "E" };
    g[0][0] = { type: "wall" };
    g[5][9] = { type: "wall" };
    return g;
  });

  const [selected, setSelected] = useState<[number, number] | null>(null);

  const handleClick = (r: number, c: number) => {
    const cell = grid[r][c];
    if (cell.type === "wall") return;

    if (selected) {
      // 移动选中的单位到新位置
      const [sr, sc] = selected;
      if (sr === r && sc === c) {
        setSelected(null);
        return;
      }
      const newGrid = grid.map((row) => [...row]);
      newGrid[r][c] = newGrid[sr][sc];
      newGrid[sr][sc] = { type: "empty" };
      setGrid(newGrid);
      setSelected(null);
    } else if (cell.type === "player" || cell.type === "enemy") {
      setSelected([r, c]);
    }
  };

  const cellColor = (type: Cell["type"]) => {
    switch (type) {
      case "wall":
        return "bg-neutral-600";
      case "difficult":
        return "bg-amber-900/50";
      case "player":
        return "bg-blue-700";
      case "enemy":
        return "bg-red-700";
      default:
        return "bg-neutral-900";
    }
  };

  return (
    <div className="space-y-1">
      <div className="text-[10px] text-neutral-500 uppercase">战术网格</div>
      <div
        className="inline-grid gap-0.5"
        style={{ gridTemplateColumns: `repeat(${cols}, 20px)` }}
      >
        {grid.map((row, r) =>
          row.map((cell, c) => (
            <button
              key={`${r}-${c}`}
              onClick={() => handleClick(r, c)}
              className={`w-5 h-5 rounded-sm border border-neutral-800 ${cellColor(
                cell.type
              )} ${
                selected && selected[0] === r && selected[1] === c
                  ? "ring-1 ring-amber-400"
                  : ""
              }`}
            >
              {cell.label && (
                <span className="text-[8px] text-white">{cell.label}</span>
              )}
            </button>
          ))
        )}
      </div>
      <div className="text-[9px] text-neutral-600">
        点击单位选中，再点击空格移动
      </div>
    </div>
  );
}

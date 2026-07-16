"use client";

interface PartyMember {
  name: string;
  hp: number;
  hp_max: number;
  active?: boolean;
}

interface PartyBarProps {
  members: PartyMember[];
  onSelect?: (index: number) => void;
}

export function PartyBar({ members, onSelect }: PartyBarProps) {
  if (members.length === 0) return null;

  const hpState = (pct: number) =>
    pct > 50 ? "full" : pct > 25 ? "hurt" : pct > 0 ? "critical" : "down";

  return (
    <div className="flex gap-1 mb-2">
      {members.map((m, i) => {
        const pct = m.hp_max > 0 ? (m.hp / m.hp_max) * 100 : 0;
        const state = hpState(pct);
        return (
          <button
            key={i}
            onClick={() => onSelect?.(i)}
            className={`flex-1 px-1 py-1 rounded text-center border ${
              m.active
                ? "border-amber-400 bg-neutral-800"
                : "border-neutral-700 bg-neutral-900"
            }`}
          >
            <div className="text-[10px] font-bold truncate">{m.name}</div>
            <div className="flex justify-center gap-0.5 mt-0.5">
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  state === "full"
                    ? "bg-green-500"
                    : state === "hurt"
                    ? "bg-yellow-500"
                    : state === "critical"
                    ? "bg-red-500"
                    : "bg-neutral-700"
                }`}
              />
            </div>
          </button>
        );
      })}
    </div>
  );
}

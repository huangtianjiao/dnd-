"use client";

interface RestButtonsProps {
  onRest: (type: "short" | "long") => void;
}

export function RestButtons({ onRest }: RestButtonsProps) {
  return (
    <div className="rest-section">
      <button className="rest-btn" onClick={() => onRest("short")}>
        短休 1h
      </button>
      <button className="rest-btn" onClick={() => onRest("long")}>
        长休 8h
      </button>
    </div>
  );
}

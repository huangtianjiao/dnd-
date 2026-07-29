"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";

/**
 * DiceLayer —— 全屏 3D 骰子动画层（见 docs/FRONTEND_REDESIGN.md §6）
 *
 * 双实现：
 *  - play(face)：服务器已给出确定结果（result.dice.d20），用 CSS d20 动画
 *    落定到该确切面值——保证动画与裁决一致；
 *  - rollFree()：本地自由掷骰，优先走 @3d-dice/dice-box 真实 3D 物理掷骰，
 *    初始化失败时回退 CSS 动画。
 */
export interface DiceLayerHandle {
  /** 播放一次 d20 动画并落定到指定面值（face 为空则随机） */
  play: (face?: number | null) => Promise<number>;
  /** 自由掷骰：dice-box 优先，返回掷出值（失败回退 CSS 随机） */
  rollFree: () => Promise<number>;
}

let boxPromise: Promise<any> | null = null;

async function getBox(): Promise<any> {
  if (!boxPromise) {
    boxPromise = (async () => {
      const mod = await import("@3d-dice/dice-box");
      const DiceBox = (mod as any).default;
      const box = new DiceBox("#v2-dice-box-host", {
        assetPath: "/assets/dice-box/",
        theme: "default",
        scale: 10,
      });
      await box.init();
      return box;
    })().catch((e) => {
      boxPromise = null; // 允许下次重试
      throw e;
    });
  }
  return boxPromise;
}

const DiceLayer = forwardRef<DiceLayerHandle>(function DiceLayer(_props, ref) {
  const [show, setShow] = useState(false);
  const [mode, setMode] = useState<"css" | "box">("css");
  const [face, setFace] = useState<number>(20);
  const busyRef = useRef(false);
  // 集中管理动画定时器，卸载时统一清理，避免卸载后 setState
  const timersRef = useRef<{ iv?: ReturnType<typeof setInterval>; t1?: ReturnType<typeof setTimeout>; t2?: ReturnType<typeof setTimeout> }>({});
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      const t = timersRef.current;
      if (t.iv) clearInterval(t.iv);
      if (t.t1) clearTimeout(t.t1);
      if (t.t2) clearTimeout(t.t2);
    };
  }, []);

  /** CSS d20 动画：快速翻数后落定到 final，返回落定值 */
  const cssRoll = useCallback((final: number | null): Promise<number> => {
    return new Promise((res) => {
      setMode("css");
      setShow(true);
      const t = timersRef.current;
      t.iv = setInterval(() => {
        if (mountedRef.current) setFace(1 + Math.floor(Math.random() * 20));
      }, 70);
      t.t1 = setTimeout(() => {
        if (t.iv) clearInterval(t.iv);
        const f = final ?? 1 + Math.floor(Math.random() * 20);
        if (mountedRef.current) setFace(f);
        t.t2 = setTimeout(() => {
          if (mountedRef.current) setShow(false);
          res(f);
        }, 550);
      }, 750);
    });
  }, []);

  const play = useCallback(
    async (faceIn?: number | null): Promise<number> => {
      if (busyRef.current) return faceIn ?? 0; // 防重入：连掷场景直接跳过本次动画
      busyRef.current = true;
      try {
        return await cssRoll(faceIn ?? null);
      } finally {
        busyRef.current = false;
      }
    },
    [cssRoll]
  );

  const rollFree = useCallback(async (): Promise<number> => {
    if (busyRef.current) return 0;
    busyRef.current = true;
    try {
      const box = await getBox();
      setMode("box");
      setShow(true);
      try {
        const r = await box.roll("1d20");
        const v: number | undefined = r?.[0]?.rolls?.[0]?.value;
        if (typeof v === "number") return v;
        // dice-box 返回结构异常 → 回退
        return await cssRoll(null);
      } finally {
        setShow(false);
      }
    } catch {
      return await cssRoll(null);
    } finally {
      busyRef.current = false;
    }
  }, [cssRoll]);

  useImperativeHandle(ref, () => ({ play, rollFree }), [play, rollFree]);

  return (
    <div className={`v2-dice-layer ${show ? "show" : ""}`}>
      {/* dice-box 画布挂载点（box 模式时由其接管渲染） */}
      <div id="v2-dice-box-host" className="v2-dice-box-host" />
      {mode === "css" && (
        <div className="v2-d20-stage">
          <div className="v2-d20">{face}</div>
        </div>
      )}
      <div className="v2-dice-hint">骰 子 裁 决</div>
    </div>
  );
});

export default DiceLayer;

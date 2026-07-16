declare module '@3d-dice/dice-box' {
  interface DiceBoxOptions {
    assetPath: string;
    container?: string;
    thème?: string;
    scale?: number;
    throwForce?: number;
    lightIntensity?: number;
    zIndex?: number;
  }
  interface DiceRollResult {
    rolls: Array<{ value: number; qty: number; sides: number; }>;
    success?: boolean;
    modifier?: number;
    value?: number;
  }
  class DiceBox {
    constructor(selector: string, options: DiceBoxOptions);
    init(): Promise<void>;
    roll(notation: string): Promise<DiceRollResult>;
    rollCustom(values: number[]): Promise<DiceRollResult>;
    clear(): void;
    hide(): void;
    show(): void;
    updateConfig(options: Partial<DiceBoxOptions>): void;
  }
  export default DiceBox;
}

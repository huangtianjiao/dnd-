import { create } from "zustand"
import type { StreamMessage } from "@/app/lib/types"

interface ChatState {
  messages: StreamMessage[]
  inputText: string
  isStreaming: boolean
  addMessage: (msg: Omit<StreamMessage, "id">) => void
  setMessages: (msgs: StreamMessage[]) => void
  clearMessages: () => void
  setInputText: (text: string) => void
  setStreaming: (v: boolean) => void
  /** 追加一条 DM 叙事消息 */
  pushDm: (text: string, speaker?: string) => void
  /** 追加一条玩家消息 */
  pushPlayer: (text: string, speaker?: string) => void
}

let _seq = 1

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  inputText: "",
  isStreaming: false,

  addMessage: (msg) =>
    set((s) => ({
      messages: [...s.messages, { ...msg, id: _seq++ }],
    })),

  setMessages: (msgs) => {
    _seq = msgs.length + 1
    set({ messages: msgs })
  },

  clearMessages: () => {
    _seq = 1
    set({ messages: [] })
  },

  setInputText: (text) => set({ inputText: text }),
  setStreaming: (v) => set({ isStreaming: v }),

  pushDm: (text, speaker) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { id: _seq++, type: "dm", speaker: speaker || "地下城主", text },
      ],
    })),

  pushPlayer: (text, speaker) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { id: _seq++, type: "player", speaker: speaker || "你", text },
      ],
    })),
}))

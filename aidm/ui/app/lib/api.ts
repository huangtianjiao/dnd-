/** API 封装 — fetch 包装 + 统一错误契约
 *
 * 后端错误形态（两种都兼容）：
 * 1. HTTP 4xx + {"detail": {"error": "<错误码>", "message": "<中文描述>"}}
 * 2. 旧端点 200 + {"error": "..."}
 */

/** API 基址（review 建议：生产全 same-origin）。
 *  ★ 生产（Docker）：不配置 NEXT_PUBLIC_API → 返回 ""（相对路径），
 *    前端与 API 由同一个后端（8000）提供，无端口错配/无 CORS。
 *  ★ 本地开发：Next dev(3000) → 后端(8080)，需显式配置 NEXT_PUBLIC_API。 */
function resolveApiBase(): string {
  if (process.env.NEXT_PUBLIC_API !== undefined && process.env.NEXT_PUBLIC_API !== "") {
    return process.env.NEXT_PUBLIC_API;
  }
  return "";  // same-origin（生产默认）
}

const API = resolveApiBase();

/** 后端启用 AIDM_API_KEY 时，前端用 NEXT_PUBLIC_API_KEY 配套（REST 走 X-API-Key 头）。
 *  ★ 审查 P0-5：浏览器内密钥不是秘密——仅作局域网内网的门卫；
 *    真正的权限边界是后端 session token（P0-4 ownership 校验）。 */
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

/** 会话令牌（P0-4 ownership）：连接游戏后由 useSocket 设置，
 *  REST 请求自动携带 Authorization: Bearer，供后端归属校验。 */
let sessionToken = "";
export function setSessionToken(token: string) {
  sessionToken = token;
}
export function getSessionToken() {
  return sessionToken;
}

function authHeaders(): Record<string, string> {
  const h: Record<string, string> = {};
  if (API_KEY) h["X-API-Key"] = API_KEY;
  if (sessionToken) h["Authorization"] = `Bearer ${sessionToken}`;
  return h;
}

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  let data: any = null;
  try {
    data = await res.json();
  } catch {
    /* body 非 JSON，忽略 */
  }

  if (!res.ok) {
    const detail = data?.detail;
    if (detail && typeof detail === "object") {
      throw new ApiError(
        res.status,
        detail.error || `HTTP_${res.status}`,
        detail.message || detail.error || JSON.stringify(detail)
      );
    }
    if (typeof detail === "string") {
      throw new ApiError(res.status, detail, detail);
    }
    // body 本身是字符串（如纯文本错误）时直接用作 message
    if (typeof data === "string" && data) {
      throw new ApiError(res.status, `HTTP_${res.status}`, data);
    }
    throw new ApiError(res.status, `HTTP_${res.status}`, `HTTP ${res.status}`);
  }

  // 旧端点：200 + {"error": "..."}
  if (data && typeof data === "object" && data.error) {
    throw new ApiError(200, String(data.error), data.message || String(data.error));
  }

  return data as T;
}

export async function apiPost<T = any>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

/** 带 Bearer 会话令牌的 POST（P0-02：房主管理操作按令牌鉴权，不再传名字）。 */
export async function apiPostAuth<T = any>(path: string, body: any, token: string): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

export async function apiGet<T = any>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { headers: authHeaders() });
  return handleResponse<T>(res);
}

/** 从任意异常中取展示消息 */
export function errMsg(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return String(e);
}

export { API, API_KEY };

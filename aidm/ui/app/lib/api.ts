/** API 封装 — fetch 包装 + 统一错误契约
 *
 * 后端错误形态（两种都兼容）：
 * 1. HTTP 4xx + {"detail": {"error": "<错误码>", "message": "<中文描述>"}}
 * 2. 旧端点 200 + {"error": "..."}
 */

const API = process.env.NEXT_PUBLIC_API || "";

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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

export async function apiGet<T = any>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`);
  return handleResponse<T>(res);
}

/** 从任意异常中取展示消息 */
export function errMsg(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return String(e);
}

export { API };

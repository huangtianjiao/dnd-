# 本地服务安全与质量检测报告

**检测目标**: http://127.0.0.1:8080/  
**检测时间**: 2026-07-14  
**检测方式**: curl 命令行探测 + 响应头/体分析  
**服务类型**: uvicorn (Python ASGI)

---

## 一、服务可用性

| 检测项       | 结果          | 说明                           |
|--------------|---------------|--------------------------------|
| TCP 端口连通 | ✅ 正常       | 127.0.0.1:8080 可正常访问      |
| GET 请求     | ✅ 正常       | 返回 HTTP/1.1 200 + HTML 内容  |
| HEAD 请求    | ⚠️ 405 异常   | 服务器不支持 HEAD，返回 405    |

> **建议**：uvicorn 默认可能未正确处理 HEAD 请求。虽然浏览器主要使用 GET，但支持 HEAD 是 HTTP/1.1 规范要求（RFC 7231）。可在 ASGI 框架（如 FastAPI/Starlette）中显式处理 HEAD 方法，或确认是否使用了自定义路由过滤。

---

## 二、HTTP 响应头安全审计

| 响应头                    | 当前状态 | 风险等级 | 说明与建议                                          |
|---------------------------|----------|----------|-----------------------------------------------------|
| `Server`                  | `uvicorn`| ℹ️ 信息  | 暴露服务器类型，建议在生产环境中隐藏或修改            |
| `X-Frame-Options`         | ❌ 缺失  | 🟠 中    | 存在点击劫持风险。建议添加 `DENY` 或 `SAMEORIGIN`   |
| `X-Content-Type-Options`  | ❌ 缺失  | 🟠 中    | 存在 MIME 嗅探攻击风险。建议添加 `nosniff`          |
| `Content-Security-Policy` | ❌ 缺失  | 🔴 高    | 无法限制 XSS 攻击面。建议配置 CSP 策略                |
| `Strict-Transport-Security`| ❌ 缺失 | 🟡 低    | 未启用 HSTS。若使用 HTTPS，建议添加 `max-age` 指令   |
| `Referrer-Policy`         | ❌ 缺失  | 🟡 低    | 建议添加 `strict-origin-when-cross-origin`           |
| `Cache-Control`           | ❌ 缺失  | 🟡 低    | 单页应用建议添加缓存策略，避免敏感信息被缓存         |

---

## 三、前端代码安全审计

通过分析返回的 HTML/JS 代码，发现以下**安全风险**：

### 🔴 高危：存在 XSS（跨站脚本攻击）漏洞

**问题位置**：前端 JavaScript 中多处使用 `innerHTML` 直接插入接口返回内容。

**问题代码示例**：
```javascript
document.getElementById('log').innerHTML='';
add('dm',r.narration.replace(/\n/g,'<br>'));
```

**风险描述**：
- `r.narration` 来自后端 API 返回数据。如果后端未对 narration 内容做充分转义，攻击者可通过构造包含 `<script>` 标签的内容注入恶意代码。
- 同理，日志显示函数 `add()` 若使用 `innerHTML`，任何用户输入（如角色名、玩家输入等）都可能成为 XSS 载体。

**修复建议**：
1. 将 `innerHTML` 替换为 `textContent` 或 `innerText`，或使用 `DOMPurify` 等库对 HTML 内容进行净化。
2. 若确实需要富文本（如换行转 `<br>`），应在前端进行严格的 HTML 实体编码后再插入。

```javascript
// 安全的做法示例
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
// 然后使用 textContent 插入，或 innerHTML = escapeHtml(r.narration).replace(/\n/g, '<br>')
```

### 🟠 中危：错误信息直接透传

```javascript
if(st.error){alert(st.error);return;}
```

**风险描述**：API 返回的 `error` 字段直接通过 `alert()` 弹窗显示。如果后端错误信息包含恶意脚本或未过滤的特殊字符，可能导致 XSS 或信息泄露。

**修复建议**：对错误信息进行前端转义后再显示。

---

## 四、功能与兼容性检查

| 检测项         | 状态     | 说明                                                    |
|----------------|----------|---------------------------------------------------------|
| HTML 完整性    | ✅ 完整  | 文档以 `</html>` 结尾，无截断或损坏                     |
| 字符编码       | ✅ 正常  | `<meta charset="UTF-8">` 声明正确，支持中文            |
| 移动端适配     | ✅ 良好  | 包含 viewport meta 标签 (`width=device-width`)          |
| 响应体积       | ⚠️ 21KB | 单页应用 HTML+CSS+JS 内联，体积尚可接受                 |
| WebSocket      | ℹ️ 待验证| 代码中包含 `connectWS()`，但 curl 无法直接测试 WS 连通性 |

---

## 五、API 与 CORS 风险推测

根据前端代码分析，应用存在以下 API 调用：
- `POST /open`
- `GET /campaign/{cid}/state`
- `POST /join`
- WebSocket 连接（路径未完全暴露）

**潜在风险**：
1. **CORS 配置错误**：如果 API 端点未正确限制 `Access-Control-Allow-Origin`，可能导致跨域数据泄露。
2. **缺少 CSRF 防护**：`POST` 请求中没有看到 `X-CSRF-Token` 或类似防护机制。
3. **身份验证不明**：从代码中未看到 `Authorization` 请求头或 Session/Cookie 的明确使用，需确认玩家身份如何校验，防止未授权访问他人战役数据。

---

## 六、总结与整改优先级

| 优先级 | 问题                             | 修复措施                              |
|--------|----------------------------------|---------------------------------------|
| 🔴 P0  | XSS 漏洞（innerHTML）            | 全部替换为 textContent 或引入 DOMPurify |
| 🔴 P0  | 响应头缺失 CSP                   | 配置 `Content-Security-Policy`       |
| 🟠 P1  | 响应头缺失 X-Frame-Options       | 添加 `X-Frame-Options: DENY`           |
| 🟠 P1  | 响应头缺失 X-Content-Type-Options| 添加 `X-Content-Type-Options: nosniff` |
| 🟠 P1  | HEAD 请求 405                    | 在 ASGI 框架中支持 HEAD 方法           |
| 🟡 P2  | API 鉴权与 CSRF 防护             | 增加身份验证和 CSRF Token              |
| 🟡 P2  | Server 头信息泄露                | 隐藏或修改 `Server` 响应头             |
| 🟢 P3  | 缓存策略缺失                     | 添加 `Cache-Control` 响应头            |

---

**结论**：服务可正常运行，但存在**严重的 XSS 安全隐患**，建议优先修复前端 `innerHTML` 使用问题，并补充必要的 HTTP 安全响应头。

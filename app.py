import os
import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.transport.sse import SSEContext

# 1. Khởi tạo MCP Server với tên "telegram-assistant"
mcp = FastMCP("telegram-assistant")

# Đọc cấu hình Telegram Bot Token từ biến môi trường (Environment Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@mcp.tool()
async def send_telegram_message(chat_id: str, message: str) -> str:
    """
    Gửi một tin nhắn văn bản tới một tài khoản hoặc nhóm Telegram qua Chat ID.
    
    Args:
        chat_id: ID của phòng chat Telegram (Ví dụ: '123456789' hoặc '@channelname')
        message: Nội dung tin nhắn cần gửi đi.
    """
    if not TELEGRAM_BOT_TOKEN:
        return "Lỗi: Chưa cấu hình TELEGRAM_BOT_TOKEN trên Render Cloud!"

    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                return f"Gửi tin nhắn thành công tới Chat ID {chat_id}!"
            else:
                return f"Telegram API lỗi: {result.get('description', 'Không rõ nguyên nhân')}"
        except Exception as e:
            return f"Lỗi kết nối hệ thống: {str(e)}"

# 2. Tạo một ứng dụng FastAPI để chuyển đổi giao thức sang SSE (Server-Sent Events) giúp kết nối Cloud URL
app = FastAPI(title="Xiaozhi Telegram MCP Endpoint")

# Tích hợp kết nối MCP trực tiếp vào FastAPI theo chuẩn Render
@app.get("/mcp")
async def mcp_endpoint(ctx: SSEContext):
    await mcp.handle_sse(ctx)

# Khởi chạy server lắng nghe Port của Cloud Render cấp phát
if __name__ == "__main__":
    import uvicorn
    # Render yêu cầu chạy trên host 0.0.0.0 và PORT do hệ thống tự cấp
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

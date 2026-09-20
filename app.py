import os
import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Khởi tạo MCP Server
mcp = FastMCP("telegram-assistant")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@mcp.tool()
async def send_telegram_message(chat_id: str, message: str) -> str:
    """
    Gửi một tin nhắn văn bản tới một tài khoản hoặc nhóm Telegram qua Chat ID.
    """
    if not TELEGRAM_BOT_TOKEN:
        return "Lỗi: Chưa cấu hình TELEGRAM_BOT_TOKEN trên Render Cloud!"

    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                return f"Gửi tin nhắn thành công tới Chat ID {chat_id}!"
            else:
                return f"Telegram API lỗi: {result.get('description', 'Không rõ')}"
        except Exception as e:
            return f"Lỗi hệ thống: {str(e)}"

# Tạo app FastAPI và tích hợp MCP tự động bằng hàm build_fastapi_app()
app = mcp.build_fastapi_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

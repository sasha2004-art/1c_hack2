# backend/app/routers/utils.py

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/utils",
    tags=["utils"]
)

# Создаем асинхронный HTTP-клиент, который будет переиспользоваться
# Это более эффективно, чем создавать новый клиент на каждый запрос
client = httpx.AsyncClient()

@router.get("/image-proxy")
async def image_proxy(url: str = Query(...)):
    """
    Прокси-эндпоинт для получения изображений с внешних источников.
    Это помогает обойти ограничения CORS и hotlinking.
    """
    try:
        # Делаем асинхронный GET-запрос к указанному URL
        response = await client.get(url)
        
        # Если внешний сервер ответил ошибкой, пробрасываем ее
        response.raise_for_status()

        # Проверяем, что контент действительно является изображением
        content_type = response.headers.get("content-type")
        if not content_type or not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="URL does not point to a valid image.")

        # Возвращаем контент изображения как потоковый ответ.
        # Это эффективно для больших файлов, так как не загружает их полностью в память.
        return StreamingResponse(response.iter_bytes(), media_type=content_type)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Error response from external server.")
# backend/app/routers/utils.py

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import os # <-- Добавить импорт

router = APIRouter(
    prefix="/utils",
    tags=["utils"]
)

# Создаем асинхронный HTTP-клиент, который будет переиспользоваться
# Это более эффективно, чем создавать новый клиент на каждый запрос
client = httpx.AsyncClient()

# --- НОВЫЙ ЭНДПОИНТ ДЛЯ ПОИСКА ИЗОБРАЖЕНИЙ ---
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

@router.get("/image-suggestions")
async def get_image_suggestions(query: str = Query(..., min_length=2)):
    """
    Получает список предложенных изображений от Unsplash API по поисковому запросу.
    """
    if not UNSPLASH_ACCESS_KEY:
        raise HTTPException(status_code=500, detail="Unsplash API key is not configured on the server.")

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": 9,  # Запросим 9 картинок для сетки 3x3
        "orientation": "landscape"
    }

    try:
        response = await client.get(UNSPLASH_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Упрощаем ответ, чтобы на фронтенд ушли только нужные данные
        simplified_results = [
            {
                "id": photo["id"],
                "description": photo.get("alt_description"),
                "urls": {
                    "small": photo["urls"]["small"],
                    "regular": photo["urls"]["regular"]
                }
            }
            for photo in data.get("results", [])
        ]
        return simplified_results

    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Error connecting to image service.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Error response from image service.")


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
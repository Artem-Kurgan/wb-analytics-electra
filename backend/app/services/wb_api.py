import asyncio
from functools import wraps
import httpx
import structlog
from typing import List, Optional, Dict, Any
from aiolimiter import AsyncLimiter
from .exceptions import APIError, InvalidTokenError, RateLimitError

logger = structlog.get_logger()

def retry(tries=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 0:
                try:
                    return await func(*args, **kwargs)
                except InvalidTokenError:
                    raise
                except (RateLimitError, httpx.RequestError) as e:
                    if mtries == 1:
                        raise
                    logger.warning("retry_request", method=func.__name__, error=str(e), attempt=tries-mtries+1)
                except APIError as e:
                    if e.status_code and e.status_code >= 500:
                        if mtries == 1:
                            raise
                        logger.warning("retry_request", method=func.__name__, error=str(e), status=e.status_code, attempt=tries-mtries+1)
                    else:
                        raise

                await asyncio.sleep(mdelay)
                mtries -= 1
                mdelay *= backoff
        return wrapper
    return decorator

class WildberriesAPIClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.content_limiter = AsyncLimiter(100, 60)
        self.statistics_limiter = AsyncLimiter(1, 60)
        self.logger = logger.bind(service="wb_api")

    async def close(self):
        await self.client.aclose()

    @retry(tries=3, delay=1, backoff=2)
    async def _request(self, method: str, url: str, headers: Dict[str, str], **kwargs) -> Any:
        if "content-api" in url:
            limiter = self.content_limiter
        else:
            limiter = self.statistics_limiter

        async with limiter:
            response = await self.client.request(method, url, headers=headers, **kwargs)

        self.logger.info("wb_api_request", method=method, url=url, status=response.status_code)

        if response.status_code == 401:
            raise InvalidTokenError("Неверный API токен", status_code=401)
        elif response.status_code == 429:
            raise RateLimitError("Too Many Requests", status_code=429)
        elif response.status_code >= 500:
            raise APIError(f"WB API error: {response.status_code}", status_code=response.status_code)
        elif response.status_code >= 400:
            raise APIError(f"WB API error: {response.status_code}", status_code=response.status_code)

        try:
            return response.json()
        except Exception:
            raise APIError("Invalid JSON response", status_code=response.status_code)

    async def get_products(self, api_token: str, limit: int = 100) -> List[dict]:
        url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
        headers = {"Authorization": api_token}

        products = []
        cursor_data = {"limit": limit}

        while True:
            payload = {"settings": {"cursor": cursor_data}}
            response_data = await self._request("POST", url, headers=headers, json=payload)

            cards = response_data.get("cards", [])
            if not cards:
                break

            for card in cards:
                nm_id = card.get("nmID")
                vendor_code = card.get("vendorCode")
                brand = card.get("brand")
                obj_name = card.get("object")

                barcode = None
                sizes = card.get("sizes", [])
                if sizes and isinstance(sizes, list) and len(sizes) > 0:
                     first_size = sizes[0]
                     if isinstance(first_size, dict):
                         skus = first_size.get("skus", [])
                         if skus and isinstance(skus, list) and len(skus) > 0:
                             barcode = skus[0]

                tag_names = []
                tags = card.get("tags", [])
                if isinstance(tags, list):
                    for tag in tags:
                        if isinstance(tag, dict) and "name" in tag:
                            tag_names.append(tag["name"])
                        elif isinstance(tag, str):
                            tag_names.append(tag)

                photo = None
                media_files = card.get("mediaFiles", [])
                if media_files and isinstance(media_files, list) and len(media_files) > 0:
                    photo = media_files[0]

                products.append({
                    "nmID": nm_id,
                    "vendorCode": vendor_code,
                    "brand": brand,
                    "object": obj_name,
                    "barcode": barcode,
                    "tags": tag_names,
                    "photo": photo
                })

            response_cursor = response_data.get("cursor", {})
            updated_at = response_cursor.get("updatedAt")
            nm_id_cursor = response_cursor.get("nmID")

            if not updated_at and not nm_id_cursor:
                break

            cursor_data = {
                "limit": limit,
                "updatedAt": updated_at,
                "nmID": nm_id_cursor
            }

            if len(cards) < limit:
                break

        return products

    async def get_stocks(self, api_token: str, date_from: str = None) -> List[dict]:
        url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
        headers = {"Authorization": api_token}
        params = {}
        if date_from:
            params["dateFrom"] = date_from

        return await self._request("GET", url, headers=headers, params=params)

    async def get_sales(self, api_token: str, date_from: str, flag: int = 0) -> List[dict]:
        url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"
        headers = {"Authorization": api_token}
        params = {"dateFrom": date_from, "flag": flag}

        data = await self._request("GET", url, headers=headers, params=params)

        if isinstance(data, list):
            results = []
            for item in data:
                sale_id = item.get("saleID")
                if not sale_id:
                    continue

                cancel_id = item.get("cancelID")
                # is_buyout if cancelID is empty/None
                is_buyout = not cancel_id

                item["is_buyout"] = is_buyout
                results.append(item)
            return results
        return data

    async def get_orders(self, api_token: str, date_from: str, flag: int = 0) -> List[dict]:
        url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
        headers = {"Authorization": api_token}
        params = {"dateFrom": date_from, "flag": flag}

        return await self._request("GET", url, headers=headers, params=params)

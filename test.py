import httpx
import asyncio
import json

async def fetch(url, params):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        return res.json()

async def main():
    url = "https://my.spbstu.ru/home/get-abit-list"
    params = {
        "filter_1": 2, 
        "filter_2": 1, 
        "filter_3": 649, 
        "education_level": "bachelor"
    }

    req = await fetch(url, params)
    
    # 1. Смотрим, сколько всего людей вернул сайт
    print(f"Всего абитуриентов в списке: {len(req.get('results', []))}")
    
    # 2. Выводим ПЕРВОГО человека в красивом, читаемом JSON-формате
    if req.get('results'):
        print("\nСтруктура данных одного абитуриента:")
        print(json.dumps(req['results'][0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())


import os
import asyncio
from playwright.async_api import async_playwright

# 🛠️ КРИТИЧЕСКИЙ ФИКС ДЛЯ NIXOS:
# Переопределяем временные директории на короткие пути ДО запуска Playwright.
# Chromium использует их для создания SingletonSocket, и длина пути не должна превышать 108 символов.
os.environ["TMPDIR"] = "/tmp/pw"
os.environ["XDG_RUNTIME_DIR"] = "/tmp/pw"
os.makedirs("/tmp/pw", exist_ok=True)


async def test_spbpu_parser():
    executable_path = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    short_tmp_dir = "/tmp/pw-chromium"
    os.makedirs(short_tmp_dir, exist_ok=True)

    async with async_playwright() as p:
        print("🚀 Запускаем Chromium...")
        print(f"   Исполняемый файл: {executable_path or 'default'}")
        print(f"   TMPDIR переопределен на: {os.environ.get('TMPDIR')}")

        context = await p.chromium.launch_persistent_context(
            user_data_dir=short_tmp_dir,
            headless=True,
            executable_path=executable_path,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = context.pages[0]

        print("📥 Загружаем страницу Политеха...")
        await page.goto("https://my.spbstu.ru/home/abit/list-applicants/bachelor")
        await page.wait_for_load_state("networkidle")

        print("🔍 Слушаем сетевые запросы...")
        api_responses = {}

        def handle_response(response):
            if "get-code-list" in response.url:
                api_responses["code_list"] = response
            elif "get-abit-list" in response.url:
                api_responses["abit_list"] = response

        page.on("response", handle_response)

        print("🖱️ Пытаемся взаимодействовать со страницей...")
        try:
            await page.wait_for_selector("select", timeout=10000)
            selects = await page.query_selector_all("select")
            print(f"   Найдено полей выбора: {len(selects)}")

            if len(selects) >= 2:
                await selects[0].select_option(value="2")  # Очная
                print("   ✅ Выбрана очная форма")
                await page.wait_for_timeout(1000)

                await selects[1].select_option(value="1")  # Бюджет
                print("   ✅ Выбран бюджет")
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"   ⚠️ Не удалось кликнуть: {e}")
            await page.wait_for_timeout(3000)

        if "code_list" in api_responses:
            response = api_responses["code_list"]
            print("\n🎯 УСПЕХ! Перехвачен запрос get-code-list!")
            print(f"   Статус: {response.status}")

            try:
                data = await response.json()
                codes = data.get("code_list", [])
                print(f"   📦 Получено направлений: {len(codes)}")

                for item in codes:
                    title = item.get("title", "")
                    if "09.03.04" in title:
                        print(f"   🔥 НАЙДЕНО: {title} -> ID: {item.get('id')}")

                print("\n   Первые 5 направлений из списка:")
                for item in codes[:5]:
                    print(f"   - ID {item.get('id')}: {item.get('title')}")

            except Exception as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
                text = await response.text()
                print(f"   Ответ сервера: {text[:300]}")
        else:
            print("\n❌ Не удалось перехватить запрос get-code-list.")

        await context.close()


if __name__ == "__main__":
    asyncio.run(test_spbpu_parser())

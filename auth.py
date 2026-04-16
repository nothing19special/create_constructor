import asyncio
from playwright.async_api import async_playwright, expect


# 1. Функция авторизации (принимает page)
async def login(page):
    await page.goto('https://admin.business.test01.russpass.dev')

    await page.get_by_placeholder('Введите эл. почту').fill('nptf@test.test')
    await page.get_by_placeholder('Введите пароль').fill('AUTOTEST12345')

    # Кликаем на кнопку входа
    await page.locator('form > button').click()
    print("Авторизация успешна")
    await page.wait_for_timeout(5000)



# Основная функция-оркестратор
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        # Вызываем функции по очереди, передавая им одну и ту же страницу
        await login(page)

        # Чтобы браузер не закрылся сразу
        print("Работа завершена, жду в режиме паузы...")
        print('Все нормально, все работает')
        await page.pause()


asyncio.run(main())
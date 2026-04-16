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


# 2. Новая функция для действий внутри (тоже принимает page)
async def create_service(page):
    await page.goto('https://admin.business.test01.russpass.dev/events-control/53e78557-b33d-4de5-94e5-2298569fa15d')
    await page.locator('#eventsConstructor').click()
    await page.locator('.LocaleSwitcher_label__cBPWl').last.click()

    # Создание раздела
    divider1 = page.locator(".CreateElement_divider__PeTfV").last
    await divider1.click()
    btn2 = page.locator('[data-test-value="modal:constructorSection"]').last
    await btn2.wait_for(state="attached", timeout=5000)
    await btn2.evaluate("node => node.click()")

    await page.get_by_placeholder('Введите название раздела').fill(f'Второй раздел')

    await page.locator('[data-test="addButton"]').click()
    #Инициализация типов вопросов
    questions = ['Ссылки','Текстовое поле','Номер телефона'
            ,'Текстовая область','Число','Один вариант ответа',
            'Несколько вариантов ответа','Оценка','Файл','Приоритизация',
            'Таблица с файлами','Таблица со списком','Таблица с полями', 'Дата','Страна','Город']
    # Создание вопроса
    k = 0
    for j in questions:
        divider2 = page.locator(".CreateElement_divider__PeTfV").first
        await divider2.click()
        btn2 = page.locator('[data-test-value="modal:constructorQuestion"]').first
        await btn2.wait_for(state="attached", timeout=5000)
        await btn2.evaluate("node => node.click()")

        await page.get_by_placeholder('Введите текст вопроса').fill(j)
        await page.get_by_text('Выберите тип вопроса').click()
        await page.locator(f'[id$="-option-{k}"]').click()
        k += 1
        element_text = await page.locator('[data-test="selectOneQuestionType"]').inner_text()
        text_validate_types = ['Один вариант ответа', 'Несколько вариантов ответа', 'Приоритизация']
        if any(q_type in element_text for q_type in text_validate_types):
            for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                await page.get_by_placeholder('Введите ответ').fill(answer)
                await page.keyboard.press('Enter')


        table_validate_types = ['Таблица с файлами','Таблица с полями','Таблица со списком']
        if any(q_type in element_text for q_type in table_validate_types):
            for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                await page.get_by_placeholder('Введите название колонки').fill(answer)
                await page.keyboard.press('Enter')
            # Значение выпадающего списка
            if 'Таблица со списком' in element_text:
                for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                    await page.get_by_placeholder('Введите ответ').fill(answer)
                    await page.keyboard.press('Enter')


        await page.locator('[name="checkQuestionRequired"]').click()
        await page.locator('[name="checkboxAppraiseCantAnswer"]').click()
        await page.locator('[data-test="addButton"]').click()






# Основная функция-оркестратор
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        # Вызываем функции по очереди, передавая им одну и ту же страницу
        await login(page)
        await create_service(page)

        # Чтобы браузер не закрылся сразу
        print("Работа завершена, жду в режиме паузы...")
        await page.pause()


asyncio.run(main())
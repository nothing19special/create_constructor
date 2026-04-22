import asyncio
import os
from playwright.async_api import async_playwright, expect


count_pages = int(os.getenv('COUNT_PAGES'))
count_section = int(os.getenv('COUNT_SECTION'))
questions_used = os.environ['QUESTIONS_USED'].split(',')
event_id = os.getenv('EVENT_ID')

print(f'DEBUG: original={questions_used}')


# 1. Функция авторизации
async def login(page):

    await page.goto('https://admin.business.test01.russpass.dev')

    await page.get_by_placeholder('Введите эл. почту').fill('nptf@test.test')
    await page.get_by_placeholder('Введите пароль').fill('AUTOTEST12345')

    # Кликаем на кнопку входа
    await page.locator('form > button').click()
    print("Авторизация успешна")
    await page.wait_for_timeout(1000)


# 2. Новая функция для действий внутри (тоже принимает page)
async def create_service(page):
    #Переход в конструктор
    await page.goto(f'https://admin.business.test01.russpass.dev/events-control/{event_id}')
    #Костыль, чтобы сохранить текущую логику перебора. Пока просто будет удаляться в конце
    await page.locator('#eventsConstructor').click()
    await page.locator('[data-test="addQuestion"]').click()
    await page.get_by_placeholder('Введите текст вопроса').fill('Вопрос')
    await page.get_by_text('Выберите тип вопроса').click()
    await page.get_by_text('Ссылки').last.click()
    await page.locator('[data-test="addButton"]').click()

    for i in range(count_pages):

        # Создание страниц
        await page.locator('[data-test="addPageButton"]').click()
        await page.get_by_placeholder('Введите название страницы').fill(f'Страница {i+1}')
        await page.locator('[data-test="addButton"]').click()

        # Создание разделов
        for k in range(count_section):
            divider1 = page.locator(".CreateElement_divider__PeTfV").last
            await divider1.click()
            btn2 = page.locator('[data-test-value="modal:constructorSection"]').last
            await btn2.wait_for(state="attached", timeout=5000)
            await btn2.evaluate("node => node.click()")
            await page.get_by_placeholder('Введите название раздела').fill(f'Раздел номер {k+1}')
            await page.locator('[data-test="addButton"]').click()

            # Создание вопросов
            for j in questions_used:
                await page.locator(".CreateElement_divider__PeTfV").last.click()
                btn2 = page.locator('[data-test-value="modal:constructorQuestion"]').last
                await btn2.wait_for(state="attached", timeout=1000)
                await btn2.evaluate("node => node.click()")

                await page.get_by_placeholder('Введите текст вопроса').fill(j)
                await page.get_by_text('Выберите тип вопроса').click()
                await page.get_by_text(j).last.click()

                #Проверка вопросов с полями для ответа
                element_text = await page.locator('[data-test="selectOneQuestionType"]').inner_text()
                text_validate_types = ['Один вариант ответа', 'Несколько вариантов ответа', 'Приоритизация']
                if any(q_type in element_text for q_type in text_validate_types):
                    for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                        await page.get_by_placeholder('Введите ответ').fill(answer)
                        await page.keyboard.press('Enter')

                #Проверка вопросов с табличным типом
                table_validate_types = ['Таблица с файлами', 'Таблица с полями', 'Таблица со списком']
                if any(q_type in element_text for q_type in table_validate_types):
                    for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                        await page.get_by_placeholder('Введите название колонки').fill(answer)
                        await page.keyboard.press('Enter')
                    # Значение выпадающего списка
                    if 'Таблица со списком' in element_text:
                        for answer in ['Первый вариант', 'Второй вариант', 'Третий вариант']:
                            await page.get_by_placeholder('Введите ответ').fill(answer)
                            await page.keyboard.press('Enter')
                #Добавление чек-боксов для каждого вопроса
                await page.locator('[name="checkQuestionRequired"]').click()
                await page.locator('[name="checkboxAppraiseCantAnswer"]').click()
                await page.locator('[data-test="addButton"]').click()

    #Удаление лишнего раздела
    find_trash_button = page.locator('[data-test="trashButton"]').first
    await find_trash_button.wait_for(state="attached", timeout=1000)
    await find_trash_button.evaluate("node => node.click()")
    await page.get_by_text('Удалить').last.click()

    #Сохранение черновика. Таймаут после завершения работы
    await page.get_by_text('Сохранить черновик').click()
    await page.wait_for_timeout(5000)










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
        print("Работа завершена, сэр. Пошел отдыхать")
        await page.close()


asyncio.run(main())

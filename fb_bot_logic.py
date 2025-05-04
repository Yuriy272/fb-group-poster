from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import traceback
import random

def post_to_facebook_groups(post_text, group_links, image_path, status_log, stop_flag, counter):
    if not os.path.exists(image_path):
        status_log.append(f"❌ Фото не знайдено: {image_path}")
        return

    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\SeleniumProfile")
    chrome_options.add_argument("profile-directory=Profile 1")
    driver = webdriver.Chrome(options=chrome_options)

    for link in group_links:
        if stop_flag["stop"]:
            status_log.append("🛑 Зупинено користувачем.")
            break

        try:
            status_log.append(f"\n➡️ Переходимо в групу: {link}")
            driver.get(link)
            time.sleep(10)

            create_post = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Напишіть щось') or contains(text(),\"What's on your mind\")]"))
            )
            create_post.click()
            status_log.append("📝 Відкрито редактор публікації")
            time.sleep(3)

            post_area = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_area)
            ActionChains(driver).move_to_element(post_area).click().send_keys(post_text).perform()
            status_log.append("💬 Вставлено текст")
            time.sleep(2)

            photo_buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
            photo_clicked = False
            for button in photo_buttons:
                label = button.get_attribute("aria-label")
                if label and ('світлина' in label.lower() or 'photo' in label.lower()):
                    driver.execute_script("arguments[0].click();", button)
                    photo_clicked = True
                    status_log.append("🖼️ Натиснуто іконку 'Світлина/відео'")
                    break

            if not photo_clicked:
                raise Exception("❌ Не знайдено кнопку 'Світлина/відео'")

            time.sleep(2)

            file_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @multiple]"))
            )
            absolute_image_path = os.path.abspath(image_path)
            file_input.send_keys(absolute_image_path)
            status_log.append("📷 Фото додано до поста")
            time.sleep(5)

            publish_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Опублікувати' or @aria-label='Post']"))
            )
            publish_button.click()
            status_log.append(f"✅ Пост опубліковано в {link}")
            counter["count"] += 1

        except Exception as e:
            status_log.append(f"❌ Помилка в {link}: {str(e)}")
            traceback.print_exc()

        if stop_flag["stop"]:
            status_log.append("🛑 Зупинено користувачем під час очікування.")
            break

        delay = random.randint(60, 120)
        status_log.append(f"⏳ Очікування {delay} секунд перед наступною групою...")
        time.sleep(delay)

    driver.quit()
    status_log.append("✅ Завершено публікацію.")



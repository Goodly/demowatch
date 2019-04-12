import os
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep

website = driver.get("https://www.rewritertools.com/paraphrasing-tool")
input_text = driver.find_element_by_xpath(".//div[@id='input-data-frame']/div[1]/textarea")
start_button = driver.find_element_by_xpath(".//div[@id='input-data-frame']/div[2]/button")
progress = driver.find_element_by_xpath(".//div[@id='input-data-frame']/div[2]/div[1]/div/div[2]/div/div/div")
output_text = driver.find_element_by_xpath(".//div[@id='input-data-frame']/div[2]/div[2]/div/div")

for city_num in range(164):
    for text_num in range(12):
        try:
            text = open("Texts/%d_%d" % (city_num, text_num), "r")
        except Exception:
            continue
        try:
            dummy_text = open("Paraphrased/%d_%d" % (city_num, text_num), "r")
        except Exception:
            contents = text.read()
            contents = contents.decode('utf-8').encode('ascii', errors='ignore')
            input_text.clear()
            input_text.send_keys(contents)
            text.close()
            start_button.click()
            while (int(progress.get_attribute("aria-valuenow")) < 50 or int(progress.get_attribute("aria-valuenow")) > 99):
                sleep(0.5)
            if (int(progress.get_attribute("aria-valuenow")) >= 80):
                sleep(15)
            else:
                while (int(progress.get_attribute("aria-valuenow")) < 80 or int(progress.get_attribute("aria-valuenow")) > 99):
                    sleep(0.5)
                sleep(8)
                if (int(progress.get_attribute("aria-valuenow")) >= 95):
                    sleep(25)
                else:
                    while (int(progress.get_attribute("aria-valuenow")) < 95 or int(progress.get_attribute("aria-valuenow")) > 99):
                        sleep(0.5)
                    sleep(8)
                    if (int(progress.get_attribute("aria-valuenow")) >= 98):
                        sleep(40)
                    else:
                        while (int(progress.get_attribute("aria-valuenow")) < 98 or int(progress.get_attribute("aria-valuenow")) > 99):
                            sleep(0.5)
                        sleep(60)
            output = output_text.text
            paraphrased = open("Paraphrased/%d_%d" % (city_num, text_num), "w")
            paraphrased.write(output)
            paraphrased.close()

driver.close()

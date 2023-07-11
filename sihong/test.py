import googletrans
from googletrans import Translator

def translate_english_to_chinese(text):
    translator = googletrans.Translator(service_urls=['translate.google.com/?sl=auto&tl=zh-CN&op=translate'])
    translation = translator.translate(text, src='en', dest='zh-cn')
    return translation.text

# 示例用法
english_text = "Hello, how are you?"
translated_text = translate_english_to_chinese(english_text)
print(translated_text)

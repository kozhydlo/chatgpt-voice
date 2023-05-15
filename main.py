import os
import openai
from telegram import Update, Voice
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import Filters
from google.cloud import speech

TELEGRAM_API_KEY = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("ТОКЕТ")

openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привіт! Відправ мені голосове повідомлення, і я намагатимусь відповісти на твоє запитання.")

def process_voice_message(update: Update, context: CallbackContext):
    voice_message = update.message.voice
    file = context.bot.get_file(voice_message.file_id)
    file.download("voice_message.ogg")

    text_from_voice = transcribe("voice_message.ogg")
    prompt = text_from_voice
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=50, n=1, stop=None, temperature=0.5)
    reply = response.choices[0].text.strip()
    update.message.reply_text(reply)

def transcribe(file_path):
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        input_audio = audio_file.read()

    audio = speech.RecognitionAudio(content=input_audio)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code="uk-UA",
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

def main():
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, process_voice_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import asyncio
import os
import re
from dotenv import load_dotenv

from pathlib import Path 
from yt_dlp import YoutubeDL

from aiogram import Bot, Dispatcher , F
from aiogram.types import Message , FSInputFile , InputMediaPhoto , BotCommand
from aiogram.filters import CommandStart , Command , CommandObject 

import requests

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

Path("downloads").mkdir(exist_ok=True) #папка с файлами


async def set_command(bot: Bot):
	commands = [
		BotCommand(command="start", description="Запустить бота"),
		BotCommand(command="mp3" , description="Скачать звук"),
		BotCommand(command="mp4" , description="Скачать видео"),
		BotCommand(command="pic" , description="Скачать картинку"),

	]

	await bot.set_my_commands(commands)


def cookie_choose(url: str) -> Path:
	def_cookie = "cookie_def"

	if "tiktok" in url:
		def_cookie = "tt_cookie"

	elif "youtu.be" in url or "youtube.com" in url:
		def_cookie = "yt_cookie"

	elif "instagram" in url:
		def_cookie = "ig_cookie"



def get_tiktok_photos(url: str):
	resp = requests.post(
		"https://tikwm.com/api/", #отправляем запрос
		data={"url": url}, #передаем ссылку(эт тело запроса/настройка так скажем)
		timeout=30, #время ожидания запроса
	)
	data = resp.json() #разворачиваем джсон в словарь
	return data.get("data", {}).get("images", []) #кидаем юзеру список изображений



def download_mp3(url: str) -> Path:
	opts = {
		"format": "bestaudio/best", #правило набора потока
		"outtmpl": "downloads/%(title)s [%(id)s].%(ext)s", #шаблон имени файла
		"noplaylist": True, #скачивает ток 1 из плейлиста
		"cookiefile": cookie_choose(url),
		"postprocessors": [ #обработка после скачивания
			{
				"key": "FFmpegExtractAudio", #вызов ffmpeg
				"preferredcodec": "mp3" , #формат файла
				"preferredquality": "192", #битрейт
			}
		],
	}  #это правила для нашей функции

	with YoutubeDL(opts) as ydl:
		info = ydl.extract_info(url, download=True) #главная функция для скачивания
		file_path = Path(ydl.prepare_filename(info)) #берет шаблон и подставляет данные
		#file_path = Path(ydl.prepare_filename(info))
		return file_path.with_suffix(".mp3") #меняем расширение(наверняка без заеба что бы было)



def download_mp4(url: str) -> Path:
	opts1 = {
		"format": "bestvideo+bestaudio/best",
		"outtmpl": "downloads/%(title)s [%(id)s].%(ext)s",
		"noplaylist": True,
		"merge_output_format": "mp4",
		"cookiefile": "tt_cookie.txt",
	}

	with YoutubeDL(opts1) as ydl:
		info = ydl.extract_info(url, download=True)
		file_path = Path(ydl.prepare_filename(info))
		return file_path.with_suffix(".mp4")




async def download_audio(url: str) -> Path:
	return await asyncio.to_thread(download_mp3, url) #отдельный не блокирующий поток(что б быстрее было типа)


async def download_video(url: str) -> Path:
	return await asyncio.to_thread(download_mp4, url)


async def download_image(url: str):
	return await asyncio.to_thread(get_tiktok_photos, url)




@dp.message(CommandStart())
async def start_cmd(message: Message):
	await message.answer('Привет <tg-emoji emoji-id="5240033415935312251">✋</tg-emoji>\n\nЯ бот для скачивания аудио/видео/фото\n\nЧтобы скачать — отправь команду и ссылку.\nНапример: /mp3 ссылка (доступные команды в меню)\n\nПоддерживаемые платформы:\n\n<tg-emoji emoji-id="5359321549851598370">🌐</tg-emoji>Instagram\n<tg-emoji emoji-id="5359523920120651432">🌐</tg-emoji>Youtube\n<tg-emoji emoji-id="5359640777590841912">🌐</tg-emoji>Tiktok\n<tg-emoji emoji-id="5359480691274817678">🎵</tg-emoji>SoundCloud\n\n\nВыбери команду в меню и отправь ссылку<tg-emoji emoji-id="5470177992950946662">👇</tg-emoji>' , parse_mode="HTML")



@dp.message(F.document , F.from_user.id == ADMIN_ID)
async def cookie_get(message: Message):
	doc = message.document.file_id #документ принятия ботом
	file = await bot.get_file(doc) #ждем этот файл
	file_path = file.file_path
	#выбираем один из файлов для скачивания
	if message.document.file_name in ["tt_cookie.txt", "ig_cookie.txt" , "yt_cookie.txt"]:
		await message.answer('Ваш файл принят <tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji>' , parse_mode="HTML")
		await bot.download_file(file_path, message.document.file_name)
	else: 
		await message.answer('Неверный формат или ошибка <tg-emoji emoji-id="5210952531676504517">❌</tg-emoji>' , parse_mode="HTML")



@dp.message(Command("mp3"))
async def audio_handler(message: Message , command: CommandObject):
	url = command.args

	if not url:
		await message.answer("Используйте: /mp3 ссылка")
		return

	msg = await message.answer("⏳")

	try:
		path = await download_audio(url) #получаем путь к файлу из папки 
		await message.answer_audio(audio=FSInputFile(path) , caption="🖤@Downloadvideoormp3bot") #отправляем файл

		
		path.unlink(missing_ok=True) #удадяем файл из папки

		await msg.delete()

	except Exception as e:
		await msg.delete()
		await message.answer('⛔️Не удалось получить информацию по ссылке\n\n\nВозможные причины:\n\n▫️закрытый (приватный) аккаунт\n▫️возрастные ограничения\n▫️неверный формат для скачивания\n\n\n<tg-emoji emoji-id="5240443340498944908">✨</tg-emoji>Попробуйте отправить другую ссылку', parse_mode="HTML") #если пошло по пизде




@dp.message(Command("mp4"))
async def video_handler(message: Message , command: CommandObject):
	url = command.args

	if not url:
		await message.answer("Используйте формат: /mp4 ссылка")
		return

	msg1 = await message.answer("⏳")

	try:
		path = await download_video(url) #отсылаемся к нашей СИНХРОННОЙ хуйне 
		await message.answer_video(video=FSInputFile(path) , caption="🖤@Downloadvideoormp3bot") #отправляем файл с подписью нашего тг бота


		path.unlink(missing_ok=True) #удадяем файл из папки

		await msg1.delete()

	except Exception as e:
		await msg.delete()
		await message.answer('⛔️Не удалось получить информацию по ссылке\n\n\nВозможные причины:\n\n▫️закрытый (приватный) аккаунт\n▫️возрастные ограничения\n▫️неверный формат для скачивания\n\n\n<tg-emoji emoji-id="5240443340498944908">✨</tg-emoji>Попробуйте отправить другую ссылку', parse_mode="HTML") #если пошло по пизде





@dp.message(Command("pic"))
async def download_image_cmd(message: Message):
	url = message.text.strip()

	if not url:
		await message.answer("Используйте формат: /pic ссылка")
		return

	ms = await message.answer("⏳")

	try:
		images = await download_image(url) #обращаемся к асинхронной функции

		if not images:
			await message.answer("Не удалось получить файл из-за неверного формата или ошибки")
			await ms.delete()
			return #останавливаем , если пошло по пизде

		media = [InputMediaPhoto(media=img) for img in images[:10]] #лимит 10 фото
		await message.answer_media_group(media) #кидает фотки именно группой, а не каждую отдельно

		await ms.delete()

	except Exception as e:
		await msg.delete()
		await message.answer('⛔️Не удалось получить информацию по ссылке\n\n\nВозможные причины:\n\n▫️закрытый (приватный) аккаунт\n▫️возрастные ограничения\n▫️неверный формат для скачивания\n\n\n<tg-emoji emoji-id="5240443340498944908">✨</tg-emoji>Попробуйте отправить другую ссылку', parse_mode="HTML") #если пошло по пизде



@dp.message()
async def all_handler(message: Message):
	await message.reply("Неизвестное сообщение\nДля команд используйте меню или команду /help")



async def main():
	await set_command(bot)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
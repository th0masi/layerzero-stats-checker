from loguru import logger
import time
import math


def load_wallets_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        logger.error(f"Ошибка: файл не найден – {file_path}")
        exit()


def get_hours(rank_updated_at):
    current_time = int(time.time() * 1000)
    time_difference = current_time - rank_updated_at
    hours_difference = time_difference / (1000 * 60 * 60)
    return math.floor(hours_difference)

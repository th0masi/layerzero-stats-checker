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
    current_time = get_current_time()
    time_difference = current_time - rank_updated_at
    hours_difference = time_difference / (1000 * 60 * 60)
    return math.floor(hours_difference)


def get_current_time():
    return int(time.time() * 1000)


def format_chain_list(chain_list):
    if not chain_list:
        return None
    chains = chain_list.split(',')
    formatted_chains = [chain.capitalize() for chain in chains]
    return ', '.join(formatted_chains)


def format_number(value):
    if not value:
        return value
    if isinstance(value, int):
        return "{:,}".format(value).replace(",", " ")
    else:
        return "{:,.2f}".format(value).replace(",", " ")

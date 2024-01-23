import requests
from core.database import DBManager
from core.utils import get_hours
from loguru import logger
from pyuseragents import random as random_useragent


def check_stats():
    wallets_data = DBManager.get_all_wallets()

    for wallet in wallets_data:
        stat = Stats(wallet=wallet.address, proxy=wallet.proxy)
        stat.get_stat_by_wallet()

    logger.info(f'Получил данные для всех кошельков')


class Stats:
    def __init__(self, wallet, proxy):
        self.url = 'https://nftcopilot.com/p-api/layer-zero-rank/check'
        self.proxy_str = proxy
        self.proxy = {
            "http": f"http://{self.proxy_str}",
            "https": f"http://{self.proxy_str}"
        }
        self.wallet = wallet

    def get_stat_by_wallet(
            self,
            attempts: int = 3,

    ):
        for attempt in range(attempts):
            try:
                response = self.send_request()
                data = response.json()
                if data:
                    data = data[0]
                    wallet_data = {
                        'address': self.wallet,
                        'rankUpdatedAt': get_hours(int(data.get('rankUpdatedAt'))),
                        'rank': int(data.get('rank')),
                        'txsCount': int(data.get('txsCount')),
                        'volume': float(data.get('volume')),
                        'distinctMonths': int(data.get('distinctMonths')),
                        'networks': int(data.get('networks')),
                        'contracts': int(data.get('contracts')),
                        'destChains': int(data.get('destChains')),
                    }

                    logger.success(f'Получил данные для кошелька {self.wallet}')
                    DBManager.merge_wallet_data(wallet_data)
                    break
                else:
                    logger.error(f'Попытка {attempt} / {attempts} | '
                                 f'Пустой ответ API для {self.wallet}:'
                                 f' {response.text}')
            except Exception as e:
                logger.error(f'Попытка {attempt} / {attempts} | '
                             f'Ошибка при получении данных {self.wallet}:'
                             f' {e}')

    def send_request(self):
        headers = {
            "Content-Type": 'application/json',
            "origin": 'https://nftcopilot.com',
            "referer": f'https://nftcopilot.com/layer-zero-rank-check?address={self.wallet}',
            "User-Agent": random_useragent()
        }

        data = {
            "address": f'{self.wallet}',
            "addresses": [
                f'{self.wallet}'
            ],
            "c": 'check'
        }

        response = requests.post(
            url=self.url,
            headers=headers,
            json=data,
            proxies=self.proxy
        )

        return response

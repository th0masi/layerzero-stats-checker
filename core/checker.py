import json

from core.utils import get_current_time
from web3 import Web3
from datetime import datetime
import requests
from core.database import DBManager
from loguru import logger
from pyuseragents import random as random_useragent
import uuid


def check_stats():
    wallets_data = DBManager.get_all_wallets()

    for wallet in wallets_data:
        stat = Stats(wallet=wallet.address, proxy=wallet.proxy)
        stat.get_stat_by_wallet()

    logger.info(f'Получил данные для всех кошельков')


class Stats:
    def __init__(self, wallet, proxy):
        self.copilot_url = 'https://nftcopilot.com/p-api/layer-zero-rank/check'
        self.l0_url = 'https://layerzeroscan.com/api/trpc/messages.list'
        self.w3 = Web3(Web3.HTTPProvider('https://eth.drpc.org'))
        self.proxy_str = proxy
        self.proxy = {
            "http": f"http://{self.proxy_str}",
            "https": f"http://{self.proxy_str}"
        }
        self.wallet = wallet
        self.attempts = 3

    def get_stat_by_wallet(
            self,

    ):
        copilot_data = self.get_data_from_copilot()
        layerzero_data = self.get_data_from_layerzero_api()
        nonce = self.is_mannet_txn()
        mainnet_status = nonce >= 1

        if not copilot_data and not layerzero_data:
            logger.error(f'Не удалось получить данные для кошелька {self.wallet}')
            return

        wallet_data = {
            'address': self.wallet,
            'is_mainnet': mainnet_status,
        }

        if copilot_data:
            copilot_data = copilot_data[0]
            wallet_data.update({
                'last_update': int(copilot_data.get('rankUpdatedAt')),
                'rank': int(copilot_data.get('rank')),
                'volume': float(copilot_data.get('volume')),
                'distinct_months': int(copilot_data.get('distinctMonths')),
                'contracts': int(copilot_data.get('contracts')),
            })

        if layerzero_data:
            wallet_data.update({
                'last_update': int(get_current_time()),
                'count_txn': layerzero_data['count_txn'],
                'src_chains_count': int(layerzero_data['count_src_chain_list']),
                'dst_chains_count': int(layerzero_data['count_dst_chain_list']),
                'dst_chains_list': layerzero_data.get('dst_chain_list'),
                'src_chains_list': layerzero_data.get('src_chain_list'),
                'last_activity': layerzero_data.get('last_activity'),
            })

        logger.success(f'Получил данные для кошелька {self.wallet}')
        DBManager.merge_wallet_data(wallet_data)

    def get_data_from_copilot(
            self,
    ):
        for attempt in range(self.attempts):
            try:
                query = {
                    "address": f'{self.wallet}',
                    "addresses": [
                        f'{self.wallet}'
                    ],
                    "c": 'check'
                }

                response = self.send_request(method='post', url=self.copilot_url, data=query)
                data = response.json()
                return data

            except json.decoder.JSONDecodeError:
                logger.error(f'COPILOT | Ошибка при получении данных {self.wallet}: '
                             f'Невозможно декодировать JSON из ответа сервера')
                continue

            except Exception as e:
                logger.error(f'COPILOT | Ошибка при получении данных {self.wallet}:'
                             f' {e}')
                continue

    def get_data_from_layerzero_api(self):
        for attempt in range(self.attempts):
            try:
                params = {
                    "filters": {
                        "address": self.wallet,
                        "stage": "mainnet",
                        "created": {}
                    }
                }
                query_string = json.dumps(params)
                url_with_params = f"{self.l0_url}?input={query_string}"

                response = self.send_request(method='get', url=url_with_params)
                data = response.json()

                messages = data.get('result', {}).get('data', {}).get('messages', None)
                if not messages:
                    return False

                dst_chain_list = set()
                src_chain_list = set()
                created_date = None

                for message in messages:
                    dst_chain_list.add(message.get('dstChainKey'))
                    src_chain_list.add(message.get('srcChainKey'))

                    if not created_date and message.get('mainStatus') == 'DELIVERED':
                        created_timestamp = int(message.get('created'))
                        created_date = datetime.fromtimestamp(created_timestamp).date()

                response_data = {
                    'last_activity': created_date,
                    'dst_chain_list': ','.join(map(str, dst_chain_list)),
                    'src_chain_list': ','.join(map(str, src_chain_list)),
                    'count_dst_chain_list': len(dst_chain_list),
                    'count_src_chain_list': len(src_chain_list),
                    'count_txn': len(messages),
                }

                return response_data

            except Exception as e:
                logger.error(f'LAYERZERO | При получении данных возникла ошибка: {e}')
                continue

    def send_request(self, method, url, data=None):
        headers = self.get_headers(url)

        if method.lower() == 'get':
            response = requests.get(
                url=url,
                headers=headers,
                proxies=self.proxy
            )
        else:
            response = requests.post(
                url=url,
                headers=headers,
                json=data,
                proxies=self.proxy
            )

        return response

    def get_headers(self, url):
        base_headers = {
            "Content-Type"  : 'application/json',
            "User-Agent"    : random_useragent()
        }
        if url == self.copilot_url:
            base_headers.update({
                "origin"    : 'https://nftcopilot.com',
                "referer"   : f'https://nftcopilot.com/layer-zero-rank-check?address={self.wallet}',
            })
        else:
            unique_trace_id = uuid.uuid4()
            base_headers.update({
                "referer"   : f'https://layerzeroscan.com/address/{self.wallet}',
                "baggage"   : f"sentry-environment=vercel-production,"
                              f"sentry-release=8db980a63760b2e079aa1e8cc36420b60474005a,"
                              f"sentry-public_key=7ea9fec73d6d676df2ec73f61f6d88f0,"
                              f"sentry-trace_id={unique_trace_id}"
            })

        return base_headers

    def is_mannet_txn(self):
        try:
            nonce = self.w3.eth.get_transaction_count(
                self.w3.to_checksum_address(self.wallet)
            )

            return nonce
        except Exception as e:
            logger.error(f'NONCE | Ошибка при получении данных {self.wallet}: {e}')
            return 0

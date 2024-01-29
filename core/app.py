import logging
import tempfile

from core.checker import check_stats
from core.database import DBManager
from core.utils import get_hours, format_chain_list, format_number
from flask import Flask, render_template, request, jsonify, send_file

logging.getLogger('flask.app').setLevel(logging.WARNING)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['get_hours'] = get_hours
app.jinja_env.filters['format_chain_list'] = format_chain_list


@app.route('/')
def wallet_table():
    sort_by = request.args.get('sort', 'rank')
    (wallets,
     min_rank,
     total_volume,
     top_500k_wallets,
     top_1m_wallets) = DBManager.get_sorted_wallets(sort_by)

    month_age = DBManager.get_wallets_with_options(
        address='address',
        sort='last_activity',
        params='less',
        values='01.01.2024',
    )

    without_eth_tx = DBManager.get_wallets_with_options(
        address='address',
        sort='is_mainnet',
        params='miss',
        values='1',
    )

    without_src_optimism = DBManager.get_wallets_with_options(
        address='address',
        sort='src_chains_list',
        params='miss',
        values='optimism',
    )

    without_src_arbitrum = DBManager.get_wallets_with_options(
        address='address',
        sort='src_chains_list',
        params='miss',
        values='arbitrum',
    )

    without_src_polygon = DBManager.get_wallets_with_options(
        address='address',
        sort='src_chains_list',
        params='miss',
        values='polygon',
    )

    without_dst_optimism = DBManager.get_wallets_with_options(
        address='address',
        sort='dst_chains_list',
        params='miss',
        values='optimism',
    )

    without_dst_arbitrum = DBManager.get_wallets_with_options(
        address='address',
        sort='dst_chains_list',
        params='miss',
        values='arbitrum',
    )

    without_dst_polygon = DBManager.get_wallets_with_options(
        address='address',
        sort='dst_chains_list',
        params='miss',
        values='polygon',
    )

    return render_template(
        'index.html',
        wallets=wallets,
        wallets_count=len(wallets),
        min_rank=min_rank,
        total_volume=total_volume,
        top_500k_wallets=top_500k_wallets,
        top_1m_wallets=top_1m_wallets,
        month_age=len(month_age) if month_age else 0,
        without_eth_tx=len(without_eth_tx),
        without_src_optimism=len(without_src_optimism) if without_src_optimism else 0,
        without_src_arbitrum=len(without_src_arbitrum) if without_src_arbitrum else 0,
        without_src_polygon=len(without_src_polygon) if without_src_polygon else 0,
        without_dst_optimism=len(without_dst_optimism) if without_dst_optimism else 0,
        without_dst_arbitrum=len(without_dst_arbitrum) if without_dst_arbitrum else 0,
        without_dst_polygon=len(without_dst_polygon) if without_dst_polygon else 0,
    )


@app.route('/refresh')
def refresh_data():
    check_stats()
    return jsonify({'status': 'success', 'message': 'Data refreshed successfully'})


@app.route('/export_csv')
def export_csv():
    try:
        sort_by = request.args.get('sort', 'rank')
        (sorted_wallets, _, _, _, _) = DBManager.get_sorted_wallets(sort_by)

        temp_file_path = tempfile.mktemp(suffix='.csv')
        with open(temp_file_path, 'w+', encoding='utf-8') as temp_file:
            headers = ['Адрес кошелька',
                       'Имя кошелька',
                       'Ранг',
                       'Объем',
                       'Кол-во транзакций',
                       'Исх. сети / Сети назнач.',
                       'Уник. контракты',
                       'Использовали майннет',
                       'Активных месяцев',
                       'Исходящие сети',
                       'Сети назначения',
                       'Последняя активность'
                       ]
            temp_file.write(','.join(headers) + '\n')

            for wallet in sorted_wallets:
                data = [
                    wallet.address or 'None',
                    wallet.wallet_name or 'None',
                    str(wallet.rank) if wallet.rank is not None else 'None',
                    str(wallet.volume) if wallet.volume is not None else 'None',
                    str(wallet.count_txn) if wallet.count_txn is not None else 'None',
                    f"{wallet.src_chains_count or 'None'} / {wallet.dst_chains_count or 'None'}",
                    str(wallet.contracts) if wallet.contracts is not None else 'None',
                    'Да' if wallet.is_mainnet else 'Нет',
                    str(wallet.distinct_months) if wallet.distinct_months is not None else 'None',
                    (wallet.src_chains_list or 'None').replace(',', ';'),
                    (wallet.dst_chains_list or 'None').replace(',', ';'),
                    wallet.last_activity.strftime('%d.%m-%Y') if wallet.last_activity else 'None',
                ]
                temp_file.write(','.join(data) + '\n')

            temp_file_path = temp_file.name

        return send_file(temp_file_path, as_attachment=True, download_name='layerzero_stats.csv')

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/download_with_parameters')
def download_wallets():
    address = request.args.get('address')
    sort = request.args.get('sort')
    params = request.args.get('params')
    values = request.args.get('values')
    try:
        wallets_list = DBManager.get_wallets_with_options(
            address=address,
            sort=sort,
            params=params,
            values=values,
        )

        temp_file_path = tempfile.mktemp(suffix='.txt')
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            for wallet, in wallets_list:
                temp_file.write(wallet + '\n')

        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=f'{sort}-{params}-{values}-{len(wallets_list) if wallets_list else 0}.txt'
        )

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

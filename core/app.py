import logging
import tempfile

from core.checker import check_stats
from core.database import DBManager
from flask import Flask, render_template, request, jsonify, send_file
from loguru import logger

logging.getLogger('flask.app').setLevel(logging.WARNING)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)


def format_number(value):
    if not value:
        return value
    if isinstance(value, int):
        return "{:,}".format(value).replace(",", " ")
    else:
        return "{:,.2f}".format(value).replace(",", " ")


app.jinja_env.filters['format_number'] = format_number


@app.route('/')
def wallet_table():
    sort_by = request.args.get('sort', 'rank')
    (wallets,
     min_rank,
     total_volume,
     top_500k_wallets,
     top_1m_wallets) = DBManager.get_sorted_wallets(sort_by)

    return render_template(
        'index.html',
        wallets=wallets,
        wallets_count=len(wallets),
        min_rank=min_rank,
        total_volume=total_volume,
        top_500k_wallets=top_500k_wallets,
        top_1m_wallets=top_1m_wallets
    )


@app.route('/refresh')
def refresh_data():
    check_stats()
    return jsonify({'status': 'success', 'message': 'Data refreshed successfully'})


@app.route('/download_wallets')
def download_wallets():
    try:
        rank = int(request.args.get('rank', 500))
        wallets_data = DBManager.get_all_wallets()

        # Создание временного файла
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            filtered_wallets = [wallet for wallet in wallets_data if wallet.rank > rank]
            for wallet in filtered_wallets:
                temp_file.write(wallet.address + '\n')
            temp_file_path = temp_file.name

        # Отправка файла пользователю
        return send_file(temp_file_path, as_attachment=True, download_name=f'wallets_above_{rank}.txt')
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Ошибка: {str(e)}'})

import aiohttp
import ssl
import certifi
async def fetch_binance_price(symbol: str) -> float:
    url = f'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol.upper()}
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=ssl_context) as response:
            data = await response.json()
            if 'price' in data:
                return float(data['price'])
            else:
                raise ValueError(f"Не удалось получить цену для {symbol.upper()}. Ответ: {data}")

async def test_fetch_binance_price():
    try:
        symbol = 'BTCUSDT'  # Пример тикера
        price = await fetch_binance_price(symbol)
        print(f"Текущая цена {symbol}: {price} USDT")
    except Exception as e:
        print(f"Ошибка: {e}")
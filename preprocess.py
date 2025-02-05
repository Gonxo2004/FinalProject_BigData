from TradingviewData import TradingViewData,Interval
import os
import pandas as pd

request = TradingViewData()
cryptos = {
    "BTCUSD": "CRYPTO",
    "ETHUSD": "CRYPTO",
    "XRPUSD": "CRYPTO",
    "SOLUSD": "CRYPTO",
    "DOGEUSD": "CRYPTO",
    "ADAUSD": "CRYPTO",
    "SHIBUSD": "CRYPTO",
    "DOTUSD": "CRYPTO",
    "AAVEUSD": "CRYPTO",
    "XLMUSD": "CRYPTO",
}

crypto_names = [
    "Bitcoin", "Ethereum", "Ripple", "Solana", "Dogecoin",
    "Cardano", "Shiba_Inu", "Polkadot", "Aave", "Stellar"
]

# Crear el directorio base
output_folder = "crypto_data"
os.makedirs(output_folder, exist_ok=True)

for i, (symbol, exchange) in enumerate(cryptos.items()):
    crypto_name = crypto_names[i]
    
    # Crear subdirectorio para cada criptomoneda
    crypto_folder = os.path.join(output_folder, crypto_name)
    os.makedirs(crypto_folder, exist_ok=True)

    # Obtener datos históricos
    data = request.get_hist(symbol=symbol, exchange=exchange, interval=Interval.daily, n_bars=1600, extended_session=True)
    data = data.reset_index()

    # Convertir a datetime y agregar columnas de fecha
    data["datetime"] = pd.to_datetime(data["datetime"])
    data["year"] = data["datetime"].dt.year
    data["month"] = data["datetime"].dt.month
    data["day"] = data["datetime"].dt.day

    # Separar exchange y símbolo
    data["exchange"] = data["symbol"].apply(lambda x: x.split(":")[0])
    data["symbol"] = data["symbol"].apply(lambda x: x.split(":")[1])

    # Redondear precios
    for col in ["open", "close", "high", "low"]:
        data[col] = data[col].round(2)

    # Eliminar columnas innecesarias
    data.drop(columns=["volume"], inplace=True)

    # Guardar datos en archivos separados por año
    for year in range(2021, 2025):
        yearly_data = data[data["year"] == year].copy()
        yearly_data.drop(columns=["datetime"], inplace=True)
        
        csv_filename = os.path.join(crypto_folder, f"{crypto_name}_{year}.csv")
        yearly_data.to_csv(csv_filename, sep=";", index=False, encoding="utf-8")

print(f"Archivos CSV guardados en la carpeta: {output_folder}")
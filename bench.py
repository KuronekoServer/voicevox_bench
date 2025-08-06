import requests
import random
import json
from time import perf_counter
import argparse
import os
import sys
from typing import Optional, Dict, Any


def load_config() -> Dict[str, Any]:
    """設定ファイルを読み込み"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: config.json not found at {config_path}")
        return {
            "default_address": "http://127.0.0.1:50021",
            "default_speaker": 0,
            "benchmark_settings": {
                "lengths": [10, 50, 100],
                "count_per_length": 10
            }
        }


def check_dependencies() -> bool:
    """必要な依存関係をチェック"""
    try:
        import requests
        return True
    except ImportError:
        print("Error: requests library is not installed.")
        print("Please install it by running:")
        print("  pip install requests")
        return False


def get_api_address_interactive(default_address: str) -> str:
    """対話的にAPIアドレスを取得"""
    print(f"\nVOICEVOX APIサーバーのアドレスを入力してください。")
    print(f"デフォルト: {default_address}")
    user_input = input("APIアドレス (Enterでデフォルト): ").strip()
    
    if not user_input:
        return default_address
    
    # http:// または https:// がない場合は自動で追加
    if not user_input.startswith(("http://", "https://")):
        user_input = f"http://{user_input}"
    
    return user_input


def test_connection(address: str, headers: Optional[Dict[str, str]] = None) -> bool:
    """APIサーバーとの接続をテスト"""
    try:
        print(f"Connecting to {address}...")
        response = requests.get(f"{address}/version", headers=headers, timeout=5)
        response.raise_for_status()
        version = response.text.strip('"')
        print(f"✓ Connection successful! VOICEVOX Engine version: {version}")
        return True
    except requests.RequestException as e:
        print(f"✗ Connection failed: {e}")
        print("Please check:")
        print("  1. VOICEVOX Engine is running")
        print("  2. The address is correct")
        print("  3. No firewall is blocking the connection")
        return False


def parse_headers(header_list: list) -> Dict[str, str]:
    """ヘッダーリストを辞書形式に変換"""
    headers = {}
    for header in header_list:
        key, value = header.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def synthesis(
    text: str,
    address: str,
    headers: Optional[Dict[str, str]] = None,
    speaker: int = 0,
    pitch: float = 0.0,
    speed: float = 1.0,
) -> float:
    """音声生成

    Args:
        text : 生成する文章
        address : VOICEVOXのAPIサーバーのフルアドレス
        headers : リクエストに追加するヘッダー
        speaker : speaker_id
        pitch : ピッチ
        speed : スピード

    Returns:
        生成時間(秒)
    """
    query_payload = {"text": text, "speaker": speaker}
    try:
        resp = requests.post(f"{address}/audio_query", params=query_payload, headers=headers)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to send audio_query request: {e}")

    query_data = resp.json()
    query_data["speedScale"] = speed
    query_data["pitchScale"] = pitch

    try:
        before = perf_counter()
        resp = requests.post(f"{address}/synthesis", params={"speaker": speaker}, json=query_data, headers=headers)
        resp.raise_for_status()
        after = perf_counter()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to send synthesis request: {e}")

    return after - before


def gen_text(count: int) -> str:
    """ランダムなひらがなの文字列を生成"""
    return "".join(random.choice("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん") for _ in range(count))


def bench(length: int, count: int, address: str, headers: Optional[Dict[str, str]] = None, quiet: bool = False) -> float:
    """ベンチマークを実行"""
    synthesis("test", address, headers)  # 初回呼び出しでキャッシュなどをウォームアップ
    total_time = 0
    for i in range(count):
        text = gen_text(length)
        elapsed_time = synthesis(text, address, headers)
        total_time += elapsed_time
        if not quiet:
            print(f"Run {i + 1}, Time: {elapsed_time:.4f} seconds")
    return round(total_time / count, 4)


if __name__ == "__main__":
    # 依存関係チェック
    if not check_dependencies():
        sys.exit(1)
    
    # 設定読み込み
    config = load_config()
    
    parser = argparse.ArgumentParser(description="VOICEVOX Benchmark Script")
    parser.add_argument(
        "-a",
        "--address",
        help="Full VOICEVOX API Server Address (e.g., http://127.0.0.1:50021)",
        default=None,
    )
    parser.add_argument(
        "--header",
        help="Specify request headers (e.g., 'Authorization: Bearer token')",
        action="append",
        default=[],
    )
    parser.add_argument("-q", "--quiet", help="Suppress benchmark logs", action="store_true")
    parser.add_argument("--no-interactive", help="Skip interactive prompts", action="store_true")
    args = parser.parse_args()

    # ヘッダーをパース
    headers = parse_headers(args.header)

    # APIアドレスの決定
    if args.address:
        api_address = args.address
    elif args.no_interactive:
        api_address = config["default_address"]
    else:
        api_address = get_api_address_interactive(config["default_address"])

    # 接続テスト
    if not test_connection(api_address, headers):
        print("\nベンチマークを中止します。")
        sys.exit(1)

    print("Starting benchmark...")
    
    benchmark_settings = config["benchmark_settings"]
    lengths = benchmark_settings["lengths"]
    count = benchmark_settings["count_per_length"]
    
    scores = {}
    total_time = 0
    
    for length in lengths:
        score = bench(length=length, count=count, address=api_address, headers=headers, quiet=args.quiet)
        scores[length] = score
        total_time += score
    
    avg_score = round(total_time / len(lengths), 4)

    try:
        version = requests.get(f"{api_address}/version", headers=headers).text.strip('"')
        devices = requests.get(f"{api_address}/supported_devices", headers=headers).json()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch engine info: {e}")

    device_type = "CUDA" if devices.get("cuda") else "DirectML" if devices.get("dml") else "CPU"

    print("\n=========== Info ===========")
    print(f" Engine: {version}")
    print(f" Device: {device_type}")
    print("========== Result ==========")
    print(f" 10 char: {scores[10]} sec")
    print(f" 50 char: {scores[50]} sec")
    print(f"100 char: {scores[100]} sec")
    print(f" Avg: {avg_score} sec")
    print("============================\n")

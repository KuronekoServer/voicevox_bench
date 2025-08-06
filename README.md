# VOICEVOXベンチマーク

VOICEVOX Engineの音声合成性能を測定するためのベンチマークツールです。

## 🚀 簡単実行方法

### 方法1: バッチファイル実行（推奨）
1. VOICEVOXを起動
2. `run_benchmark.bat` をダブルクリック
3. 画面の指示に従ってAPIアドレスを入力（Enterでデフォルト使用）

### 方法2: 手動実行
1. [Python](https://www.python.org/)をインストール
2. コマンドプロンプトでこのフォルダに移動
3. VOICEVOXを起動
4. 以下のコマンドを実行：
   ```cmd
   pip install requests
   python bench.py
   ```

## 📝 設定変更

### APIアドレスの変更
- **対話的に変更**: スクリプト実行時にプロンプトで入力
- **コマンドラインで指定**: `python bench.py -a http://192.168.1.100:50021`
- **設定ファイルで変更**: `config.json` の `default_address` を編集

### ベンチマーク設定の変更
`config.json` ファイルを編集して以下を変更可能：
- テスト文字数（デフォルト: 10, 50, 100文字）
- 各テストの実行回数（デフォルト: 10回）

## 💡 使用例

```cmd
# デフォルト設定で実行
python bench.py

# 特定のアドレスを指定
python bench.py -a http://192.168.1.100:50021

# ヘッダーを指定（認証が必要な場合）
python bench.py --header "Authorization: Bearer your-token"

# ログを非表示にして実行
python bench.py -q

# 対話的プロンプトをスキップ
python bench.py --no-interactive
```

## 📊 結果の共有
ベンチマーク結果を以下のフォームで共有してください：
https://forms.gle/WPXeRtJeACFdoFhF8

## 🔧 トラブルシューティング

### Pythonが見つからない
- [Python公式サイト](https://www.python.org/)からインストール
- インストール時に「Add Python to PATH」をチェック

### 接続エラーが発生する
- VOICEVOXが起動していることを確認
- ファイアウォールの設定を確認
- APIアドレスが正しいことを確認

### requestsライブラリエラー
```cmd
pip install requests
```

# 書籍レビュー調査エージェント

Microsoft Foundry SDKとPythonを使い、指定した書籍についてウェブ上の公開レビューを検索し、評価傾向や主なテーマを日本語で分析するサンプルです。検索にはFoundryプロジェクトに接続したGrounding with Bing Searchを使います。

## 準備

1. Microsoft Foundryプロジェクトを作成し、モデルをデプロイします。
2. プロジェクトにGrounding with Bing Searchリソースを接続します。
3. Azureへの認証を設定します。ローカル開発では、たとえば `az login` を実行してください。実行ユーザーにはプロジェクトと接続を利用する権限が必要です。
4. Python 3.10以降の環境で依存パッケージをインストールします。

```bash
python -m pip install -r requirements.txt
```

以下の環境変数を設定してください。値はFoundryポータルのプロジェクト概要、モデル一覧、接続一覧から確認できます。

| 環境変数 | 説明 |
| --- | --- |
| `PROJECT_ENDPOINT` | Foundryプロジェクトのエンドポイント |
| `MODEL_DEPLOYMENT_NAME` | デプロイ済みモデル名 |
| `BING_CONNECTION_NAME` | Grounding with Bing Search接続名 |

## 実行

```bash
python book_reviews.py "コンビニ人間" --author "村田沙耶香"
```

著者名は省略できます。エージェントは複数の情報源をもとにレビューを分析し、利用可能な出典をリンクとして表示します。ウェブ上で確認できるレビューには偏りや制限があるため、回答に含まれる調査上の限界も確認してください。

## テスト

```bash
python -m unittest discover -s tests
```
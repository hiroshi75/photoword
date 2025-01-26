# Photoword (フォトワード)

## 概要
Photowordは、写真をアップロードすると画像に写っているものからスペイン語の単語帳を自動生成するWebアプリケーションです。Anthropic社のClaude Haiku（AWS Bedrock経由）を活用して画像解析を行い、写真に写っている物体や風景から関連するスペイン語の単語を抽出し、その日本語訳と例文を提供します。

## 主な機能
- 画像アップロード（対応形式：JPG、JPEG、PNG）
- AI画像解析による単語抽出
- 各単語に対して以下の情報を提供：
  - スペイン語単語
  - 品詞（名詞、動詞、形容詞、副詞）
  - 日本語訳
  - 例文

## 技術スタック
- **フロントエンド**: Streamlit
- **AI モデル**: Anthropic Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)
- **フレームワーク**: Langchain, AWS Bedrock
- **データモデル**: Pydantic

## セットアップ方法
1. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
pip install langchain-aws  # AWS Bedrock用のパッケージ
```

2. 環境変数の設定:
```bash
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
```

3. アプリケーションの起動:
```bash
streamlit run main.py
```

## 使い方
1. ブラウザで表示されるアプリケーションにアクセス
2. 「写真をアップロードしてください」の部分に画像ファイルをドラッグ＆ドロップまたはクリックして選択
3. アップロードが完了すると、AIが自動で画像を解析
4. 抽出された単語一覧が表示され、各単語について以下の情報が確認可能：
   - スペイン語単語
   - 品詞
   - 日本語訳
   - 例文

## 今後の開発予定
- 単語帳の時系列表示と閲覧機能
- クイズ機能の実装
- 単語帳の編集機能
- 学習進捗管理機能

## ライセンス
このプロジェクトは [ライセンス情報を追加] の下で公開されています。

## 開発者向け情報
- Python 3.12以上推奨
- コードスタイル：PEP 8準拠
- テストフレームワーク：pytest

### 重要な依存関係
- `langchain-aws`: AWS Bedrockを使用するために必要
- プログラム内での使用例:
```python
from langchain_aws import ChatBedrock

chat = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1"
)

## 貢献について
プルリクエストやイシューの報告は大歓迎です。新機能の提案や改善案についても、ぜひGitHubのイシューでディスカッションさせていただければと思います。

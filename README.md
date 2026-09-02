# LINE Stamp Studio

[![Tests](https://github.com/yamanaka907-oss/line-stamp-studio/actions/workflows/tests.yml/badge.svg)](https://github.com/yamanaka907-oss/line-stamp-studio/actions/workflows/tests.yml)

オリジナルキャラクターの考案から、LINEスタンプ素材（メイン画像・タブ画像・スタンプ本体）の企画、
背景透過・自動リサイズ、LINE Creators Market申請用テキストの下書き作成、ZIP一括出力までを
ブラウザだけで行える Streamlit 製 Web アプリのひな形です。

画像そのものは、**①各アセット用の画像生成プロンプトをアプリが自動で組み立てて表示し、
Gemini等の無料画像生成AIに貼り付けて生成した画像をアップロードする**（無料・推奨）か、
**②OPENAI_API_KEYを設定してアプリから直接自動生成する**（有料）かを選べます。
セリフは日本語の文字化けを避けるため、画像生成AIには描かせずアプリ側（Pillow）で
表情に応じたフォントを自動選択して文字入れします。

## ディレクトリ構成

```
line-stamp-studio/
├── app.py                       # トップページ（エントリーポイント）
├── pages/
│   ├── 1_🎨_キャラクター生成.py   # パラメータ選択 → AIキャラクター生成
│   ├── 2_📚_キャラクター管理.py   # 保存済みキャラクターの一覧・選択・削除
│   ├── 3_😊_スタンプ企画生成.py   # セリフ・表情・ポーズ企画 → 画像生成・加工
│   ├── 4_📝_申請情報作成.py       # LINE Creators Market向けテキスト下書き
│   └── 5_📦_エクスポート.py       # ZIP一括ダウンロード
├── core/
│   ├── config.py                 # サイズ規定・選択肢・APIキー等の定数
│   ├── storage.py                # キャラクターのJSON永続化（DB差し替え可）
│   ├── character_generator.py    # AIによるキャラクター設定生成
│   ├── stamp_planner.py          # AIによるスタンプ企画（セリフ/表情/ポーズ/プロンプト）
│   ├── image_generator.py        # 画像生成バックエンド（OpenAI Images / プレースホルダー）
│   ├── image_processor.py        # 背景透過・リサイズ・パディング・シート分割
│   ├── text_overlay.py           # スタンプへのセリフ文字入れ（表情ごとにフォントを自動選択）
│   ├── metadata_generator.py     # 申請用タイトル・説明文・タグ等の下書き生成
│   └── zip_export.py             # 画像＋メタデータのZIP一括出力
├── assets/fonts/                 # 文字入れ用フォント（Google Fonts, OFLライセンス）
├── data/
│   ├── characters.json           # キャラクター保存先（実行時に自動作成）
│   └── generated/                # 生成物の一時保存用（任意）
├── .streamlit/config.toml        # テーマ・サーバー設定
├── .env.example                  # 環境変数サンプル
├── requirements.txt
├── requirements-dev.txt          # pytest等、開発時のみ必要な依存
└── tests/                        # coreモジュールの自動テスト（pytest）
```

## セットアップ（ローカル）

```bash
cd line-stamp-studio
python -m venv .venv
.venv\Scripts\activate   # Windows / macOS,Linuxは source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # macOS,Linuxは cp .env.example .env
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開くと利用できます。スマートフォンから同一Wi-Fi内で
確認したい場合は `streamlit run app.py --server.address 0.0.0.0` で起動し、
表示される Network URL にスマートフォンからアクセスしてください。

### APIキーなしでも動作確認できます

`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` が未設定の場合、各生成機能は自動的に
オフラインのモックロジック（キャラクター生成・スタンプ企画・申請文言）や
プレースホルダー画像生成にフォールバックし、画面遷移や一括出力まで一通り試せます。
本番品質のテキスト・画像を得るには、`.env` に有効なAPIキーを設定してください。

- テキスト生成: [Anthropic API](https://docs.anthropic.com/)（`ANTHROPIC_API_KEY`）
- 画像生成（自動生成モード時のみ）: OpenAI Images API（`OPENAI_API_KEY`）。他社の画像生成APIを
  使う場合は `core/image_generator.py` の `ImageBackend` を実装したクラスを追加し、
  `get_image_backend()` の分岐を変更してください。

### 画像の準備方法（手動アップロード / 自動生成）

「スタンプ企画・生成」ページでは、企画したセリフ・表情・ポーズをもとに `core/stamp_planner.py` が
各アセット（メイン・タブ・スタンプ1枚ずつ）の画像生成プロンプトを自動で組み立てます。

- **手動アップロード（無料・デフォルト）**: 各プロンプトを `st.code` ブロックからコピーし、
  ページ内のリンクボタン（Gemini / Leonardo.ai / Bing Image Creator / Ideogram / Canva）から
  好きな無料画像生成AIを開いて貼り付け、生成した画像を保存してアップロードします。
  アップロード後は自動で背景透過・規定サイズへのリサイズが行われます。
  - **スタンプ本体はさらに「シートでまとめて生成」がデフォルト**です。スタンプごとに個別のプロンプトを
    毎回投げると（例: 40枚なら40回）無料枠をすぐ消費するうえ、生成のたびにキャラクターの見た目が
    微妙にぶれるため、複数枚分の表情・ポーズを1枚のグリッド画像として一括生成するようプロンプトを
    組み立てています（`core/stamp_planner.py` の `build_sheet_prompt()`）。アップロードされたシート画像は
    `core/image_processor.py` の `slice_sheet()` が読み順（左上→右へ、行ごとに下へ）でセルに自動分割します。
    1シートあたりの枚数（4 or 8）は選択可能で、スタンプごとに個別アップロードする従来モードにも
    切り替えられます。

### セリフの文字入れ（フォント自動選択）

画像生成AIに日本語のセリフを直接描かせると文字が崩れやすいため、セリフは常にアプリ側
（`core/text_overlay.py`、Pillow使用）で確実に描き込みます。表情の文字列をキーワードで
判定し、10種類のムードから雰囲気に合ったフォントを自動選択します（`core/text_overlay.py`の
`_MOOD_FONTS`）:

| ムード | フォント | 主な表情例 |
|---|---|---|
| rage（激怒） | Rampart One（グラフィティ風極太） | 怒り心頭 |
| impact（怒り） | Reggae One（インパクト） | 怒り、ダメ出し |
| surprise（驚き） | Dela Gothic One（重量感インパクト） | 驚き、びっくり |
| playful（ポップ） | Hachi Maru Pop（丸ポップ） | 疑問、困惑 |
| celebration（祝福） | Yuji Syuku（筆文字） | お祝い、祝福、感激、ハート |
| dramatic（決意） | Yuji Boku（太めの筆文字） | 決意 |
| shy（繊細） | Yomogi（手書き風） | 照れ、悲しみ、ごめんね、笑い泣き |
| calm（穏やか） | Zen Maru Gothic（柔らかい丸ゴシック） | 眠い、おやすみ、リラックス |
| energetic（明るい） | Kosugi Maru（丸ゴシック） | 喜び、笑い、感謝、がんばる |
| default（標準） | Noto Sans JP | 上記以外 |

「スタンプ企画・生成」ページのチェックボックスでON/OFFを切り替えられ、セリフが空の場合や
対応フォントが見つからない場合は自動的にスキップされます。
同梱フォントはすべて Google Fonts の SIL Open Font License 1.1 準拠（詳細は
`assets/fonts/LICENSE-fonts.txt`）。
- **自動生成（有料）**: `OPENAI_API_KEY` を設定していれば、ラジオボタンで切り替えてアプリから
  直接一括生成できます（この場合は引き続き1枚ずつ個別に生成します）。

AI API呼び出し自体が失敗した場合（レート制限・ネットワーク障害・応答形式の不整合など）も、
各生成関数は自動的にオフラインロジックへフォールバックし、画面には警告メッセージで
「AI生成に失敗したため代替表示している」ことを明示します（例外でアプリが落ちることはありません）。

## テスト

```bash
pip install -r requirements-dev.txt
pytest
```

`core/` 配下のロジック（保存・画像加工・企画・ZIP出力等）をオフラインモードで検証する
ユニットテストを `tests/` に用意しています。API呼び出し部分はモック化せず、
APIキー未設定時のオフラインパスのみを対象にしているため、追加のシークレットなしで実行できます。

## クラウドへのデプロイ

### Streamlit Community Cloud
1. 本リポジトリをGitHubにpushする。
2. [share.streamlit.io](https://share.streamlit.io) でアプリを新規作成し、
   Main file path に `app.py` を指定。
3. 「Secrets」に `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` を設定。
4. デプロイ後に発行されるURLへ、PC・スマートフォンどちらのブラウザからでもアクセス可能。

### Render
1. Web Service を作成し、Build Command に `pip install -r requirements.txt`、
   Start Command に `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` を指定。
2. Environment に `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` を設定。

## LINEスタンプ規定サイズ（`core/config.py`）

| アセット | サイズ |
|---|---|
| メイン画像 | 240×240 px |
| タブ画像 | 96×74 px |
| スタンプ本体 | 最大 370×320 px（アスペクト比維持＋透明パディング） |

## 申請情報（メタデータ）生成について

「申請情報作成」ページで生成されるタイトル・説明文・タグ・コピーライト表記・審査対策チェックリスト等は、
**あくまで下書きの提案**です。LINE Creators Marketへの自動送信・申請は行いません。
生成内容は必ずご自身で確認・編集のうえ、申請画面へ手動でコピー＆ペーストしてください
（各項目は `st.code` ブロックで表示しており、右上のアイコンからワンクリックでコピーできます）。

## 実装メモ / 拡張ポイント

- **背景透過**: `rembg` を使用。「スタンプ企画・生成」ページのチェックボックスでON/OFFを
  切り替えられるほか、未インストール時やモデル取得失敗時も自動的に「透過なし」にフォールバックして
  動作します。Streamlit Community Cloud等リソース制限のある環境で `onnxruntime` を含む依存が
  重い場合は、`requirements.txt` から除外しても問題ありません。
- **DB化**: 現状は `data/characters.json` によるファイル保存です。複数ユーザーでの本番運用時は
  `core/storage.py` の関数群をSQLite/PostgreSQL等に差し替えてください（呼び出し側のインターフェースは
  そのまま使えるよう設計しています）。
- **画像生成の縦横比**: 自動生成モードでは `image_generator.py` がメイン（正方形）・タブ（横長）・
  スタンプ（横長寄り）それぞれの向きに近いプリセットサイズをAPIにリクエストし、最終的に
  `fit_and_pad()` で規定サイズへ収めます。
- **レスポンシブ対応**: Streamlitのカラムはビューポート幅に応じて自動的に縦積みへ切り替わります。
  `app.py` に追加したCSSでスマートフォン時の余白・見出しサイズを調整しています。

#!/bin/bash

set -eu

# メッセージを一時保存する場所
MESSAGEFILE=$(mktemp -t webhooksXXXX)
# 終了時に削除
trap "rm ${MESSAGEFILE}" 0

# パイプの有無
if [ -p /dev/stdin ]; then
    # 改行コードを変換して格納
    cat - | tr '\n' '\\' | sed 's/\\/\\n/g' > ${MESSAGEFILE}
else
    echo "nothing stdin"
    exit 1
fi

# WebHookのURL
URL='https://hooks.slack.com/services/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'
# 送信先のチャンネル
CHANNEL=${CHANNEL:-'#903_旧サーバー容量-bot'}
# botの名前
BOTNAME=${BOTNAME:-'地方自治体スクレイパ'}
# 絵文字
EMOJI=${EMOJI:-':coffee:'}
# 見出し
HEAD=${HEAD:-"scraping results.\n"}
#HEAD=${HEAD:-"--- 画像アップロード --- \n"}

# メッセージをシンタックスハイライト付きで取得
MESSAGE='```'`cat ${MESSAGEFILE}`'```'

# json形式に整形
payload="payload={
    \"channel\": \"${CHANNEL}\",
    \"username\": \"${BOTNAME}\",
    \"icon_emoji\": \"${EMOJI}\",
    \"text\": \"${HEAD}${MESSAGE}\",
}"

# 送信
curl -s -S -X POST --data-urlencode "${payload}" ${URL} > /dev/null

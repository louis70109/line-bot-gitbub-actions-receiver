# Receiver with GitHub Actions and Notes

![](https://raw.githubusercontent.com/louis70109/line-bot-gitbub-actions-receiver/master/functions.png)

1.  When CI fail, will push a fail Flex message notification to ADMIN LINE account.
    - Let status readable and deploy again with ADMIN. So Receiver will parse the request and re-run GitHub actions.
2.  If you have some ideas at a moment. You can type it into LINE Bot, will commit to another repo to record it. ([reference](https://github.com/louis70109/ideas-tree/tree/master))
3. Find Nijia's side project entrance. Input `入口` on LINE bot.

> [GitHub Actions Sample](https://github.com/louis70109/nijia-blog-backup/blob/master/.github/workflows/deploy.yml)

![](https://github.com/louis70109/line-bot-gitbub-actions-receiver/blob/f1e1956e67391b66dc32a30001e11587debac62c/file_path.jpg?raw=true)

# Deployment

## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Google Cloud Run

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

# Developer Side

## LINE account

- Got a LINE Bot API developer account
  Make sure you already registered, if you need use LINE Bot.

- Go to LINE Developer Console
  - Close auto-reply setting on "Messaging API" Tab.
  - Setup your basic account information. Here is some info you will need to know.
    - Callback URL: `https://{NGROK_URL}/webhooks/line`
    - Verify your webhook.
- You will get following info, need fill back to `.env` file.
  - Channel Secret
  - Channel Access Token (You need to issue one here)

## Normal testing

1. first terminal window

```
cp .env.sample .env
pip install -r requirements.txt --user
python api.py
```

2. Create a provisional https:

```
ngrok http 5000
```

or maybe you have npm environment:

```
npx ngrok http 5000
```

![](https://i.imgur.com/azVdG8j.png)

3. Use `change.bot_url.sh` to change your webhook url.

```
sh change_bot_url.sh YOUR_LINE_BOT_ACCESS_TOKEN  https://DOMAIN_URL/webhooks/line
```

Then will see below message:

```
--------------------------

{}

--------------------------

{"endpoint":"https://DOMAIN_URL/webhooks/line","active":true}
-------------------------

{"success":true,"timestamp":"2022-09-17T12:18:58.936898Z","statusCode":200,"reason":"OK","detail":"200"}%
```

# License

MIT License

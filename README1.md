# PyTaroBot
A telegram bot that guesses on a layout of three Tarot cards using Chat GPT.


## About this app

This application is a rewritten version of [this](https://github.com/pamnard/TaroBot) JavaScript application for Python 3.11.


## How to install


```bash
cd /home
git clone https://github.com/Vadimmmz/py-taro-bot.git
python -m venv env

# Activate virtual environment for Windows
source env/Scripts/activate

# Activate virtual environment fo for Linux
source env/bin/activate

# install all the libraries that are needed to work
pip install -r requirements.txt

deactivate

# Add .env file
echo OPENAPI_MODEL="gpt-3.5-turbo" > .env && echo 'OPENAI_API_KEY="PUT_OPENAI_API_KEY_HERE"' >> .env && echo 'TELEGRAM_TOKEN="PUT_TELEGRAM_TOKEN_HERE"' >> .env

# Making a service for bot
sudo cp /home/py-taro-bot/py-taro-bot.service /etc/systemd/system/py-taro-bot.service

# Run the service
sudo systemctl enable py-taro-bot.service
sudo systemctl start py-taro-bot.service
```

## Used packages

- pyTelegramBotAPI==4.16.1
- openai==1.13.3
- python-dotenv==1.0.1

## License

MIT License
# taro2

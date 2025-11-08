# Geming Bot

Geming Bot is a silly bot I made for myself.

## "Key" features

It has:

- Cool logging because I wanna call it cool (you won't be able to do anything agaisn't that :3)
- Free bot tokens (trust)
- Ai because yes (not like you would be able to run any good model with your gpu from 1973)
- Sqlite integration because I am NOT storing stuff into a json (\*cough cough* tjc)
- Uhhh: todo: add more stuff
- shit moderation tools (only for the ai)
- it also logs your ip and then sends it to china's governement

## Entry point

It's literally in `./src/main.py`.
I'm too lazy to make a `run.sh` and `run.bat` file

## Keys in `.env`

- `TOKEN`: The bot's token, **this is needed**
- `CONFIG-PATH`: Defaults to `./config.jsonc`
- `AI-HOST`: The host for the AI server. Defaults to `localhost`

## TODO

[ ] fix the temp folder stuff (`delete_on_close` arg on linux)
[ ] allow for multiple roles display in `/get-role`
[ ] increase timeout to check if the ai is up
[ ] in `/set-model` add a `force: bool` param to force set a model (even if it doesn't exist !!)
[ ] in `/set-model` fix autocomplete (`HOST` arg missing maybe ?)

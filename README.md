## wproject

[README-RU.md](https://github.com/fxnxtic/wproject/blob/master/README-RU.md)

Simple AI roleplay Telegram chatbot. Adaptation of commercial project for learning and research purposes.

### Features
* Access and role system <i>(powered by [Raito](https://github.com/Aidenable/Raito))</i>
* Separated context for every dm, chat and topic
* Smart context with cutoff and summary
* AI via [Openrouter API](https://openrouter.ai/)

### Usage

<b>Commands:</b>
```
# Administrate
[.w assign] - assign role
[.w revoke] - revoke role
[.w staff] - list of users
[.w instructions] - edit system prompt

# Context
[/start] - enable listening in DM and register user if not exists
[.w enable/disable] - enable/disable listening in group chats
[.w clean] - clean chat context
[.w context] - print current context (only for developers)
```

### Deployment

<b>Clone</b>
```
git clone https://github.com/fxnxtic/wproject.git && cd wproject
```

<b>Environment</b>

Create `.env` file from `.env.dist` and put your Telegram bot token and Openrouter API key inside. Add your Telegram ID to developers list.

<b>Docker Compose</b>
```
docker compose up
```

<b>Manual</b>

Fill `DATABASE_URL` and `REDIS_URL` in `.env` file.

```
pip install uv
uv sync --frozen
uv run -m app
```

---

### Stack

* aiogram3
* raito
* sqlalchemy
* alembic
* postgresql
* redis
* uv
* docker

---

### Contacts
**Telegram:** [@fxnxtic](https://t.me/fxnxtic)

`with 💜 by dinalt`
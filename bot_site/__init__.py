from quart import Quart, render_template, redirect
from quart_discord import DiscordOAuth2Session
from disnake_ipc.ext.ipc import Client

from .config import *

app = Quart(__name__)
app.template_folder = "templates/"
app.secret_key = config.SECRET_SITE_KEY
ipc = Client(secret_key=config.SECRET_IPC_KEY)

app.config["DISCORD_CLIENT_ID"] = config.DISCORD_CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = config.DISCORD_CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = config.DISCORD_REDIRECT_URI

discord = DiscordOAuth2Session(app)


@app.route("/")
async def main_page():
    return await render_template("main.html")


@app.route("/callback")
async def discord_callback():
    return await discord.callback() if not await discord.authorized else redirect("/")


@app.route("/login/")
async def login():
    return await discord.create_session()


from .api import *

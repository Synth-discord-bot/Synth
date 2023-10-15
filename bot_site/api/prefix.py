from quart import request
from .. import app, ipc


@app.get("/prefix/")
async def get_prefix():
    if request.headers.get("guild_id") is None:
        raise Exception("Please provide a guild_id parameter in the request header")

    response = await ipc.request("get_prefix", guild_id=request.headers.get("guild_id"))
    return response.response


@app.post("/prefix/")
async def prefix():
    guild_id = request.headers.get("guild_id")
    bot_prefix = request.headers.get("prefix")

    if guild_id and bot_prefix:
        response = await ipc.request("set_prefix", prefix=bot_prefix, guild_id=guild_id)
        return response.response
    raise Exception("Please provide a guild_id or/and bot_prefix parameters in the request header")

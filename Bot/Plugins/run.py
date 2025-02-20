import os, sys, io, traceback
from datetime import datetime 
from contextlib import redirect_stdout
from subprocess import getoutput as run
from pyrogram.enums import ChatAction
from Bot import app 
from pyrogram import filters

prefix = [".","!","?","*","$","#","/"]

DEVS_ID = [6495253163]

@app.on_message(filters.command("sh", prefix) & filters.user(DEVS_ID))
async def sh(_, message):

    if len(message.command) <2:
         await message.reply_text("`No Input Found!`")
    else:
          code = message.text.replace(message.text.split(" ")[0], "")
          x = run(code)
          string = f"**📎 Input**: `{code}`\n\n**📒 Output **:\n`{x}`"
          try:
             await message.reply_text(string) 
          except Exception as e:
              with io.BytesIO(str.encode(string)) as out_file:
                 out_file.name = "shell.text"
                 await message.reply_document(document=out_file, caption=e)


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)



#run your codes 
@app.on_message(filters.command(["eval"], prefix) & filters.user(DEVS_ID))
async def eval(client, message):
    if len(message.text.split()) <2:
          return await message.reply_text("`No codes found!`")
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(None, 1)[1]
    start = datetime.now()
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    end = datetime.now()
    ping = (end-start).microseconds / 1000
    final_output = "<b>📎 Input</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>📒 Output</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n\n"
    final_output += f"<b>✨ Taken Time</b>: {ping}<b>ms</b>"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await status_message.edit_text(final_output)

@app.on_message(filters.command(["log", "logs"], prefix) & filters.user(DEVS_ID))
async def logs(app, message):
    run_logs = run("tail log.txt")
    text = await message.reply_text("`Getting Logs...`")
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    await message.reply_text(f"```shell\n{run_logs}```")
    await text.delete()

@app.on_message(filters.command(["flogs", "flog"], prefix) & filters.user(DEVS_ID))
async def flogs(app, message):
    run_logs = run("cat log.txt")
    text = await message.reply_text("`Sending Full Logs...`")
    await app.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    with io.BytesIO(str.encode(run_logs)) as logs:
        logs.name = "log.txt"
        await message.reply_document(
            document=logs,
        )
    await text.delete()

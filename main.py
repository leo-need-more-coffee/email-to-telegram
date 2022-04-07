import db
import bot
import mail
import asyncio
import time

async def main():
    while (True):
        users = await db.get_users()
        for user in users:
            if not user["is_editing"]:
                msg, att, msg_id = mail.get_last_mail(user["imap"], user["username"], user["password"], user["last_email"], pathname=str(user["id"]))
                print(msg)
                if msg_id is None:
                    await bot.send(user["chat_id"], msg)
                    await db.delete_email(user["id"], user["number"])
                    continue
                if msg_id != user["last_email"]:
                    if att:
                        await bot.send(user["chat_id"], msg)
                        await bot.files(user["chat_id"], user["id"])
                    else:
                        await bot.send(user["chat_id"], msg)
                    user["last_email"] = msg_id
                    await db.edit_user(user)
        #time.sleep(30)


asyncio.run(main())

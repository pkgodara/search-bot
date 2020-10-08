import os

import discord
from dotenv import load_dotenv
from googlesearch import search
import pymysql

load_dotenv('config.env')

TOKEN = os.getenv('DISCORD_TOKEN')
DbHost = os.getenv('DB_host')
DbUser = os.getenv('DB_user')
DbPasswd = os.getenv('DB_passwd')

connection = pymysql.connect(host=DbHost,
                             user=DbUser,
                             password=DbPasswd,
                             db='recent')

print("Connected to database...")

with connection.cursor() as cursor:
    tsql = "CREATE TABLE IF NOT EXISTS `history` " \
          "(`channel` BIGINT, `author` BIGINT, `query` VARCHAR(256), `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(tsql)
connection.commit()


# Bot url: https://discord.com/api/oauth2/authorize?client_id=763236009323921409&permissions=8&scope=bot

def print_hi(name):
    print(f'Hi, {name}')


def g_search(query):
    response = search(query, num=5, stop=5, pause=2)
    res = ""
    for i in response:
        res += i + '\n'
    # print(res)
    return res


def db_put(channel, author, query):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `history` (`channel`, `author`, `query`) " \
              "VALUES (%s,%s,%s)"
        cursor.execute(sql, (channel, author, query,))
    connection.commit()


def db_get(channel, author, query):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `history` " \
              "WHERE `channel`=" + str(channel) + " AND `author`=" + str(author) + " AND `query` LIKE '%" + query + "%' " \
              "ORDER BY `ts` DESC limit 10"
        cursor.execute(sql)
        result = cursor.fetchall()
        # print(result)
    return result


if __name__ == '__main__':
    print_hi('PyCharm')

    client = discord.Client()


    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

        print(f'{client.user} is connected to the following guild:\n')

        for guild in client.guilds:
            print(
                f'{guild.name}(id: {guild.id})'
            )


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        intro = 'hi'

        print("Message:: ", message.author.id, message.channel.id, message.content)

        if message.content.lower().startswith('!google'):
            msg = message.content.split(' ', 1)

            if len(msg) == 2 and len(msg[1]) > 0:
                query = msg[1]
                print("query:: ", query)
                db_put(message.channel.id, message.author.id, query)
                response = g_search(query)
            else:
                response = 'Ooo! Please specify some search term.'
            await message.channel.send(response)

        elif message.content.lower() == 'hey':
            response = intro
            await message.channel.send(response)

        elif message.content.lower().startswith('!recent'):
            msg = message.content.split(' ', 1)

            if len(msg) == 2 and len(msg[1]) > 0:
                query = msg[1]
                print("query:: ", query)
                response = db_get(message.channel.id, message.author.id, query)
            else:
                response = 'Ooo! Please specify some search term.'
            await message.channel.send(response)


    client.run(TOKEN)

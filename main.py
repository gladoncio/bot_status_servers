import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import cv2
import asyncio

# Lee el archivo JSON
with open('config.json') as f:
    config = json.load(f)


# Accede a las variables
steam_code = config['steam_code']
server_ip = config['server_ip']
server_port = config['server_port']
update_interval_seconds = config['update_interval_seconds']
discord_bot_token = config['discord_bot_token']
url_image = config['url_image']

url = f"https://api.steampowered.com/IGameServersService/GetServerList/v1/?key={config['steam_code']}&filter=addr\\{config['server_ip']}:{config['server_port']}"

# Imprimir la URL para verificar
print("URL:", url)



intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Función para obtener el número de jugadores en el servidor
async def obtener_jugadores():
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            server_data = response.json()["response"]["servers"][0]
            jugadores = server_data['players']
            jugadores_max = server_data['max_players']
            map = server_data['map']
            texto = f"{jugadores}/{jugadores_max} ({map})"
            await client.change_presence(activity=discord.Game(name=texto))
        else:
            await client.change_presence(activity=discord.Game(name="Error al obtener jugadores"))
        await asyncio.sleep(update_interval_seconds) 


@tree.command(name = 'avataruser', description='Muestra el avatar de otro usuario')
async def slash2(interaction: discord.Interaction, user: discord.Member):
    avatar = (user.avatar)
    x=600
    y=600
    if x<=3000 and y<=3000:
        nombre_local_imagen = f"banners/perfil.png"
        imagen = requests.get(avatar).content
        with open(nombre_local_imagen, 'wb') as handler:
            handler.write(imagen)
        img1 = cv2.imread(f'banners/perfil.png')
        img1 = cv2.resize(img1,(x,y))
        cv2.imwrite('banners/perfil.png', img1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        await interaction.response.send_message(f'',file=discord.File('banners/perfil.png'))
    else:
        await interaction.response.send_message(f'El numero no debe ser mayor a 3000.')


@tree.command(name = 'clear', description='Borra la cantidad de mensajes que ingrese')
async def slash2(interaction: discord.Interaction,limit: int):
    permisos = interaction.permissions.administrator
    if (permisos==True):
        if limit<=15:
            deleted = await interaction.channel.purge(limit=limit)
            cofirmdelete_embed = discord.Embed(title='Delete Successfull!', description=f'Deleted {len(deleted)} messages in #{interaction.channel}', color=0x4fff4d)
            cofirmdelete_embed.set_thumbnail(url=url_image)
            await interaction.response.send_message(embed=cofirmdelete_embed)
        else:
            await interaction.response.send_message("Maximo 15 caracteres.")
    else:
        await interaction.response.send_message("Debe tener administrador para usar este comando.", ephemeral = True)

@tree.command(name = 'serverinfo', description='Información del servidor')
async def slash2(interaction: discord.Interaction):
    response = requests.get(url)
    if response.status_code == 200:
        server_data = response.json()["response"]["servers"][0]
        # Formatear la información en un mensaje embed
        embed = discord.Embed(title="Información del servidor", color=discord.Color.green())
        embed.set_thumbnail(url=url_image)
        embed.add_field(name="Nombre", value=server_data["name"], inline=False)
        players_info = f"{server_data['players']}/{server_data['max_players']}"
        embed.add_field(name="Jugadores", value=players_info, inline=False)
        embed.add_field(name="IP", value=server_data["addr"], inline=True)
        embed.add_field(name="Versión", value=server_data["version"], inline=True)
        if server_data["secure"]:
            embed.add_field(name="Seguro", value="Sí", inline=True)
        else:
            embed.add_field(name="Seguro", value="No", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral = True)




@client.event
async def on_ready():
    client.loop.create_task(obtener_jugadores())
    await tree.sync()  # Reemplaza YOUR_GUILD_ID con el ID de tu servidor
    print("Ready!")

client.run(discord_bot_token)

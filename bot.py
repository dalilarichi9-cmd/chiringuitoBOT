import os
import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread

# 1. TRUCO PARA RENDER: Creamos un mini servidor web
app = Flask('')

@app.route('/')
def home():
    return "¡Bot activo 24/7!"

def run_web_server():
    # Render asigna automáticamente un puerto en la variable PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# 2. CONFIGURACIÓN DEL BOT DE DISCORD
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"🤖 Conectado con éxito como {bot.user}")

# Comando para LaLiga
@bot.command(name="laliga")
async def laliga(ctx):
    await obtener_clasificacion(ctx, "140", "LaLiga EA Sports")

# Comando para LaLiga Hypermotion (Segunda)
@bot.command(name="hypermotion")
async def hypermotion(ctx):
    await obtener_clasificacion(ctx, "141", "LaLiga Hypermotion")

# Comando para la Champions League
@bot.command(name="champions")
async def champions(ctx):
    await obtener_clasificacion(ctx, "2", "UEFA Champions League")

# Función interna que hace la llamada a la API
async def obtener_clasificacion(ctx, league_id, league_name):
    url = "https://api-sports.io"
    # Año de la temporada actual
    querystring = {"league": league_id, "season": "2026"}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        try:
            standings_list = data["response"][0]["league"]["standings"][0]
            tabla = f"🏆 **Clasificación de {league_name}:**\n"
            for team_data in standings_list[:5]:
                pos = team_data["rank"]
                name = team_data["team"]["name"]
                points = team_data["points"]
                tabla += f"{pos}. {name} - {points} pts\n"
            await ctx.send(tabla)
        except (KeyError, IndexError, TypeError):
            await ctx.send(f"❌ No se encontraron datos. Asegúrate de tener tu API_KEY activa de API-Sports.")
    else:
        await ctx.send("❌ Error al conectar con los servidores de fútbol.")

# Arrancamos el servidor web para Render y luego el bot
keep_alive()
bot.run(TOKEN)

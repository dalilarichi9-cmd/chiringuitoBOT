import os
import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread

# 1. SERVIDOR WEB PARA MANTENER EL BOT ACTIVO 24/7
app = Flask('')

@app.route('/')
def home():
    return "¡ChiringuitoBOT activo 24/7!"

def run_web_server():
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

# --- COMANDOS PARA CADA COMPETICIÓN ---

@bot.command(name="laliga")
async def laliga(ctx):
    await obtener_clasificacion(ctx, "140", "LaLiga EA Sports")

@bot.command(name="hypermotion")
async def hypermotion(ctx):
    await obtener_clasificacion(ctx, "141", "LaLiga Hypermotion")

@bot.command(name="champions")
async def champions(ctx):
    await obtener_clasificacion(ctx, "2", "UEFA Champions League")

@bot.command(name="europaleague")
async def europaleague(ctx):
    await obtener_clasificacion(ctx, "3", "UEFA Europa League")

@bot.command(name="conference")
async def conference(ctx):
    await obtener_clasificacion(ctx, "848", "UEFA Conference League")

@bot.command(name="copadelrey")
async def copadelrey(ctx):
    await obtener_clasificacion(ctx, "143", "Copa del Rey")

@bot.command(name="supercopa")
async def supercopa(ctx):
    await obtener_clasificacion(ctx, "142", "Supercopa de España")

# --- FUNCIÓN INTERNA PARA LLAMAR A API-FOOTBALL ---
async def obtener_clasificacion(ctx, league_id, league_name):
    url = "https://api-sports.io"
    # Ajustado a la temporada activa en curso
    querystring = {"league": league_id, "season": "2026"}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        try:
            standings_list = data["response"]["league"]["standings"]
            
            # Algunas copas/torneos cortos devuelven listas anidadas diferentes, validamos la estructura
    if isinstance(standings_list[0], list):
        teams = standings_list[0]
    else:
        teams = standings_list



                
            tabla = f"🏆 **Clasificación / Fase actual de {league_name}:**\n"
            for team_data in teams[:5]: # Muestra los 5 primeros
                pos = team_data["rank"]
                name = team_data["team"]["name"]
                points = team_data["points"]
                tabla += f"{pos}. {name} - {points} pts\n"
            await ctx.send(tabla)
        except (KeyError, IndexError, TypeError):
            await ctx.send(f"❌ No se encontraron datos para {league_name}. Asegúrate de que tu cuenta de API-Sports tenga acceso a esta liga.")
    else:
        await ctx.send("❌ Error al conectar con los servidores de fútbol.")

keep_alive()
bot.run(TOKEN)

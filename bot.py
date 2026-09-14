import os
import discord
from discord.ext import commands
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno (en desarrollo local)
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("FOOTBALL_API_KEY")

# Configurar el bot de Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command(name="partidos")
async def get_fixtures(ctx):
    # Endpoint de API-Football para los partidos de hoy
    url = "https://api-sports.io"
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Parámetros (ejemplo para la liga española, ID: 140. Puedes cambiarlo o quitarlo)
    querystring = {"date": today, "league": "140", "season": "2026"}
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring).json()
        fixtures = response.get("response", [])
        
        if not fixtures:
            await ctx.send("No hay partidos programados para hoy en esta liga.")
            return
            
        mensaje = f"⚽ **Partidos de hoy ({today}):**\n"
        for f in fixtures[:10]: # Limitar a 10 para no saturar el chat
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            status = f['fixture']['status']['short']
            
            # Si el partido está en vivo, muestra el resultado
            if status in ["1H", "2H", "HT"]:
                goals_home = f['goals']['home']
                goals_away = f['goals']['away']
                mensaje += f"🔴 {home} {goals_home} - {goals_away} {away} ({status})\n"
            else:
                hora = f['fixture']['date'].split("T")[1][:5]
                mensaje += f"⏳ {home} vs {away} - {hora} UTC\n"
                
        await ctx.send(mensaje)
        
    except Exception as e:
        await ctx.send("Hubo un error al conectar con la API de fútbol.")
        print(e)

bot.run(TOKEN)


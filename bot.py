import os
import discord
from discord.ext import commands
import aiohttp
from flask import Flask
from threading import Thread

# ========================================================
# 1. SERVIDOR WEB PARA MANTENER EL BOT ACTIVO 24/7
# ========================================================
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


# ========================================================
# 2. CONFIGURACIÓN DEL BOT DE DISCORD (CON INTENTS)
# ========================================================
TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")

# Activamos el intent de contenido de mensajes obligatoriamente
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Conectado con éxito como {bot.user}")


# ========================================================
# 3. COMANDOS PARA CADA COMPETICIÓN
# ========================================================
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


# ========================================================
# 4. FUNCIÓN INTERNA ASÍNCRONA PARA LLAMAR A API-FOOTBALL
# ========================================================
async def obtener_clasificacion(ctx, league_id, league_name):
    url = "https://api-sports.io"
    
    # Ajustado a la temporada activa en curso (2026)
    querystring = {"league": league_id, "season": "2026"}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    try:
        # Usamos aiohttp de forma asíncrona para que Render no bloquee la conexión
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=querystring) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    try:
                        # Estructura oficial de API-Football para la clasificación
                        standings_data = data["response"][0]["league"]["standings"]
                        
                        # Algunas ligas devuelven una lista de listas (sub-grupos)
                        if isinstance(standings_data, list) and len(standings_data) > 0:
                            if isinstance(standings_data[0], list):
                                teams = standings_data[0]
                            else:
                                teams = standings_data
                        else:
                            teams = []
                        
                        if not teams:
                            await ctx.send(f"❌ No se encontraron datos de clasificación para {league_name} en la temporada 2026.")
                            return

                        tabla = f"🏆 **Clasificación / Fase actual de {league_name}:**\n\n"
                        
                        # Muestra los primeros 5 equipos
                        for team_data in teams[:5]:
                            pos = team_data["rank"]
                            name = team_data["team"]["name"]
                            points = team_data["points"]
                            tabla += f"**{pos}.** {name} — `{points} pts`\n"
                            
                        await ctx.send(tabla)
                        
                    except (KeyError, IndexError, TypeError) as err:
                        print(f"Error al procesar el JSON de la API: {err}")
                        await ctx.send(f"❌ Estructura de datos no reconocida para {league_name}.")
                else:
                    print(f"Error de API HTTP Status: {response.status}")
                    await ctx.send(f"❌ Error al conectar con los servidores de fútbol (Código HTTP {response.status}).")
                    
    except Exception as e:
        print(f"Error crítico inesperado en el comando: {e}")
        await ctx.send(f"❌ Ocurrió un error inesperado al procesar el comando.")


# ========================================================
# 5. ENCENDIDO DEL BOT
# ========================================================
keep_alive()
bot.run(TOKEN)

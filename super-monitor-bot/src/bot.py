import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


import database
import scraper


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def verificar_precos_automatico(context: ContextTypes.DEFAULT_TYPE):
    """Essa função é chamada automaticamente pelo robô."""
    print("⏰ Hora da ronda! Verificando preços automaticamente...")
    
    produtos = database.buscar_todos_produtos()
    
    if not produtos:
        print("📭 Nada para vigiar.")
        return

    for produto in produtos:
        p_id, chat_id, url, preco_alvo, ultimo_preco = produto
        
  
        resultado = await scraper.buscar_preco(url)
        
        if resultado:
            preco_atual = resultado['preco']
            titulo = resultado['titulo']
            
        
            database.atualizar_preco_produto(p_id, preco_atual, titulo)
            
            
            if preco_atual <= preco_alvo:
                print(f"🚨 ALERTA enviado para o produto {p_id}")
                msg = (
                    f"🔥 **ALERTA DE PROMOÇÃO!** 🔥\n\n"
                    f"📦 {titulo}\n"
                    f"💰 **Preço Atual: R$ {preco_atual:.2f}**\n"
                    f"🎯 Seu Alvo: R$ {preco_alvo:.2f}\n\n"
                    f"🔗 [Comprar Agora]({url})"
                )
                try:
                    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")
        else:
            print(f"Erro ao ler produto {p_id}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Super Monitor Bot Online!**\n\n"
        "Eu verifico os preços a cada 30 minutos automaticamente.\n\n"
        "Comandos:\n"
        "/vigiar <link> <preço>\n"
        "/lista\n"
        "/remover <id>"
    )

async def vigiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text("⚠️ Use: /vigiar <link> <preço>")
        return

    url = args[0]
    try:
        preco_alvo = float(args[1].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("⚠️ Preço inválido.")
        return

    await update.message.reply_text("🔎 Testando link na Amazon...")
    
  
    resultado = await scraper.buscar_preco(url)
    
    if resultado:
        database.adicionar_produto(chat_id, url, preco_alvo)
        await update.message.reply_text(
            f"✅ **Vigilância Ativada!**\n\n"
            f"📦 {resultado['titulo']}\n"
            f"Vou te avisar se baixar de R$ {preco_alvo}!"
        )
    else:
        await update.message.reply_text("❌ Não consegui ler esse link.")

async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    produtos = database.buscar_todos_produtos()
    meus = [p for p in produtos if p[1] == chat_id]
    
    if not meus:
        await update.message.reply_text("📭 Lista vazia.")
        return

    msg = "📋 **Sua Lista:**\n\n"
    for p in meus:
        msg += f"🔹 ID: {p[0]} | Alvo: {p[3]} | Atual: {p[4]}\n[Link]({p[2]})\n\n"
    
    msg += "Use /remover <ID> para apagar."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        p_id = int(context.args[0])
        database.remover_produto(p_id)
        await update.message.reply_text("✅ Removido.")
    except:
        await update.message.reply_text("Erro. Use: /remover <ID>")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Erro: Sem token no .env")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

  
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vigiar", vigiar))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("remover", remover))

    
    job_queue = app.job_queue
    job_queue.run_repeating(verificar_precos_automatico, interval=1800, first=10)

    print("🤖 Bot Automático Iniciado! (Ctrl+C para parar)")
    app.run_polling()
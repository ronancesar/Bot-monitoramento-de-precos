import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

os
import database
import scraper


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def verificar_precos():
    print(" Iniciando ronda de verificação...")
    
  
    produtos = database.buscar_todos_produtos()
    
    if not produtos:
        print(" Nenhum produto cadastrado para monitorar.")
        return

    
    bot = Bot(token=TOKEN)

  
    for produto in produtos:
     
        p_id, chat_id, url, preco_alvo, ultimo_preco = produto
        
        print(f" Verificando ID {p_id}...")
        
        
        resultado = await scraper.buscar_preco(url)
        
        if resultado:
            preco_atual = resultado['preco']
            titulo_novo = resultado['titulo']
            
            print(f"   Preço Atual: {preco_atual} (Alvo: {preco_alvo})")
            
            
            database.atualizar_preco_produto(p_id, preco_atual, titulo_novo)
            
         
            if preco_atual <= preco_alvo:
                print("   🚨 PREÇO BOM! Enviando notificação...")
                
                mensagem = (
                    f" **ALERTA DE PROMOÇÃO!** \n\n"
                    f" {titulo_novo}\n"
                    f" **Preço Atual: R$ {preco_atual:.2f}**\n"
                    f" Seu Alvo: R$ {preco_alvo:.2f}\n\n"
                    f" [Comprar Agora]({url})"
                )
                
                try:
                    await bot.send_message(chat_id=chat_id, text=mensagem, parse_mode='Markdown')
                except Exception as e:
                    print(f" Erro ao enviar mensagem: {e}")
            else:
                print("  Ainda está caro.")
        
        else:
            print(f" Erro ao ler site para o produto {p_id}")

    print(" Verificação concluída.")

if __name__ == "__main__":
    
    asyncio.run(verificar_precos())
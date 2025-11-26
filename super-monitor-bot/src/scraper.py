from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import random

async def buscar_preco(url): 
    print(f"🕷️ Scraper (Async) acessando: {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False, 
                args=["--start-maximized"] 
            )
            
            context = await browser.new_context(no_viewport=True)
            
           
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=60000)
                
               
                await asyncio.sleep(7) 
                
                titulo = await page.title()
                html = await page.content()
                print(f" Título encontrado: {titulo}")
                
            except Exception as e:
                print(f" Erro no carregamento da página: {e}")
                await browser.close()
                return None

            await browser.close()
            
            soup = BeautifulSoup(html, 'html.parser')
            preco_encontrado = 0.0
            
           
            if "amazon" in url:
                price_whole = soup.select_one('span.a-price-whole')
                price_off = soup.select_one('span.a-offscreen')
                
                if price_whole:
                    texto = price_whole.text.replace('.', '').replace(',', '')
                    preco_encontrado = float(texto)
                elif price_off:
                    texto = price_off.text.replace('R$', '').strip()
                    texto = texto.replace('.', '').replace(',', '.')
                    preco_encontrado = float(texto)

           
            elif "mercadolivre" in url:
                meta_price = soup.find("meta", itemprop="price")
                if meta_price:
                    preco_encontrado = float(meta_price["content"])
                else:
                    visual = soup.select_one("span.andes-money-amount__fraction")
                    if visual:
                        texto = visual.text.replace('.', '').replace(',', '')
                        preco_encontrado = float(texto)

            if preco_encontrado > 0:
                titulo_limpo = titulo.replace("Amazon.com.br:", "").strip()[:50]
                return {
                    'preco': preco_encontrado,
                    'titulo': titulo_limpo
                }
            
            print("Página carregou, mas não achei o seletor de preço.")
            return None

    except Exception as e:
        print(f"Erro crítico: {e}")
        return None
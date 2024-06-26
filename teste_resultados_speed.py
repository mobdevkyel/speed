import asyncio
import nodriver as uc
import json
import logging
import re

# Configuração do logging
logging.basicConfig(
    filename="script.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

url_speed = "https://mobile.bet365.com/#/AVR/B24/C20120644/R^1"


async def obter_speedway(url):
    try:
        logging.info("Iniciando a função obter_speedway")
        browser = await uc.start()
        page = await browser.get(url)

        # Aceita cookies se o elemento for encontrado
        logging.info('Procurando o botão "aceitar cookies"')
        aceite = await page.find("ccm-CookieConsentPopup_Accept", best_match=True)
        if aceite:
            logging.info('"Aceitar cookies" => clique')
            await aceite.click()
        else:
            logging.warning('Botão "aceitar cookies" não encontrado')

        # Espera 2 segundos
        await page.sleep(2)

        speed_dados_atual = []

        dados_atual = await page.select_all(
            "div.gl-MarketGroupContainer.svc-MarketGroup_Container"
        )

        for dados in dados_atual:
            geral = dados.text_all.strip()

            padrao = r"([a-zA-Z]+\s+[a-zA-Z]+)\s+(\d+\.\d+)"
            matches = re.findall(padrao, geral)

            # Adicionando os dados formatados à lista
            for match in matches:
                speed_dados_atual.extend([match[0], match[1]])

        # Encontra e clica no botão de resultados
        logging.info("Procurando o botão de resultados")
        resultados = await page.find("ResultsNavBarButton", best_match=True)
        if resultados:
            logging.info('"Resultados" => clique')
            await resultados.click()
        else:
            logging.warning("Botão de resultados não encontrado")

        # Espera mais 2 segundos
        await page.sleep(2)

        # Seleciona todos os elementos relevantes
        logging.info("Selecionando elementos de pilotos e odds")

        pilotos = await page.select_all("div.vrr-ParticipantInfo_Runner")
        odds = await page.select_all("div.vrr-Price")
        previsao = await page.select_all("div.vrr-ResultParticipant_Text")
        tricast = await page.select_all("div.vrr-ResultParticipant_Text")
        oddprevisao = await page.select_all("div.vrr-DividendParticipant_Text")

        # Cria uma lista para armazenar os resultados
        ds_piloto = []
        ds_odd = []
        ds_previsao = []
        ds_tricast = []
        ds_oddprevisao = []

        # Itera sobre os elementos capturados e armazena no dicionário
        for piloto, odd, previsao, tricast, oddprevisao in zip(
            pilotos, odds, previsao, tricast, oddprevisao
        ):
            piloto_text = piloto.text_all.strip()  # Remove espaços em branco extras
            odd_text = odd.text_all.strip()  # Remove espaços em branco extras
            previsao_text = previsao.text_all.strip()
            tricast_text = tricast.text_all.strip()
            oddprevisao_text = oddprevisao.text_all.strip()

            ds_piloto.append(piloto_text)
            ds_odd.append(odd_text)
            ds_previsao.append(previsao_text)
            ds_tricast.append(tricast_text)
            ds_oddprevisao.append(oddprevisao_text)

        resultado = {
            "speedway_atual": {
                "piloto1": speed_dados_atual[0],
                "odd1": speed_dados_atual[1],
                "piloto2": speed_dados_atual[2],
                "odd2": speed_dados_atual[3],
                "piloto3": speed_dados_atual[4],
                "odd3": speed_dados_atual[5],
                "piloto4": speed_dados_atual[6],
                "odd4": speed_dados_atual[7],
            },
            "speedway_anterior": {
                "piloto": ds_piloto[0],
                "odd": ds_odd[0],
                "previsao": ds_previsao[0],
                "tricast": ds_tricast[1],
                "oddprevisao": ds_oddprevisao[0],
            },
        }

        # Salva os resultados em um arquivo JSON
        with open("resultados.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
        logging.info("Resultados salvos no arquivo resultados.json")

        # Imprime os resultados para verificação
        print(json.dumps(resultado, ensure_ascii=False, indent=4))

    except Exception as e:
        logging.error(f"Ocorreu um erro: {str(e)}")

    finally:
        logging.info("Função obter_speedway finalizada")
        await page.close()
        await page.sleep(5)
        await obter_speedway(url)


async def main(url):
    while True:
        await obter_speedway(url)


if __name__ == "__main__":
    logging.info("Executando a função main no loop de evento assíncrono")
    asyncio.run(main(url_speed))

<p align="center"><a href="https://dialogs.yandex.ru/store/skills/6be45955-fil-m-na-veche"><img src="https://ie.wampi.ru/2023/04/21/logo.png" width="100px" height="100px" alt="logo"></a></p>

<h1 align="center">Movie Guru</h1>

This is a skill for Yandex's voice assistant — Alisa(Alice). It works on every device from Yandex station to Yandex Navigator. 
It will help you by recommending films or TV series, either randomly or by genre you have specified.

## Structure
- Main logic
- NLP (Natural Language Processing) tools
- Auxiliary tools

## Main logic
Skill logic is contained in `main.py`. It's built using if-else statements. 
Small tasks were divided into multiple functions, 
whereas the main processing happens in the `handler()` function, which is responsible for accepting user requests and sending back responses.

![Main logic preview](https://im.wampi.ru/2023/04/21/main_logic_preview.png)

## NLP
Natural Language Processing was done using Yandex's intents, which use their own language.

![NLP preview](https://ic.wampi.ru/2023/04/21/nlp_preview.png)

## Auxiliary tools
Auxiliary functions are contained in `api.py`. Content was generated using two Kinopoisk unofficial REST APIs.
Overall, the code was deployed on Yandex's serverless platform.

## Tools
- [Yandex.Cloud's serverless service](https://cloud.yandex.com/en-ru/solutions/serverless) 
- [Kinopoisk Unofficial API](https://kinopoiskapiunofficial.tech/)
- [Kinopoisk.dev API](https://github.com/mdwitr0/kinopoiskdev)
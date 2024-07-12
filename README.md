# AI狼人杀 / AI Werewolf

## 项目说明 / Project Description
让几个大模型玩一局狼人杀,观察模型之后的互动，推理和决策能力  
Have several large models play a game of Werewolf, observe their interactions, reasoning, and decision-making abilities.  
娱乐用，没实际价值  
For entertainment purposes, no practical value.

## 安装说明 / Installation Instructions
请按照以下步骤来安装和配置此项目：  
Please follow these steps to install and configure this project:

1. 克隆此仓库到本地：  
   Clone this repository to your local machine:
    ```bash
    git clone https://github.com/mewamew/wolf_bot.git
    ```
2. 进入项目目录：  
   Enter the project directory:
    ```bash
    cd wolf_bot
    ```
3. 安装依赖项：  
   Install dependencies:
    ```bash
    conda create -n wolf python=3.10
    conda activate wolf
    pip install -r requirements.txt
    ```

## 运行说明 / Running Instructions
安装完成后，你可以使用以下命令来运行项目：  
After installation, you can use the following commands to run the project:

0. 配置模型API KEY  
   Configure the model API KEY  
   支持的模型有：  
   Supported models are:
   - 通义千问
   - Deepseek
   - 百川4
   - GPT4o
   - Gemini-1.5-Pro
   - Claude-3.5-Sonnet

   其中GPT,Gemini,Claude 依赖Poe的API (Poe 的API_KEY申请地址是 https://poe.com/api_key）  
   GPT, Gemini, and Claude rely on Poe's API (Poe's API_KEY application address is https://poe.com/api_key)  
   其他的几个模型都是接入原生API  
   Other models are connected via native APIs  
   如果想接入其他的模型，扩展 BaseLlm 这个类就可以了哦  
   If you want to connect other models, just extend the BaseLlm class.

1. 启动服务：
    ```bash
    python web.py
    ```

2. 打开浏览器并访问 `http://localhost:8000` 以查看项目
   Open a browser and access `http://localhost:8000` to view the project.
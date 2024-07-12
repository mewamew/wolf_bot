from openai import OpenAI
from pprint import pprint
from dashscope import Generation
from http import HTTPStatus
from zhipuai import ZhipuAI
import json
import fastapi_poe
import asyncio
import dashscope
import requests

class BaseLlm():
    def __init__(self, model_name, force_json=False):
        self.model_name = model_name
        self.force_json = force_json
        
    def generate(self, message, chat_history=[]):
        pass

    def get_response(self, message, chat_history=[]):
        """
        """
        resp = self.generate(message, chat_history)
        if self.force_json:
            try:
                resp = resp.replace("\n", "").replace("\\", "")
                resp_dict = json.loads(resp)
            except:
                resp = resp.replace("```json", "").replace("```", "")
        return resp
    

class PoeLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        '''
        api_key在下面生成
        https://poe.com/api_key
        '''
        self.api_key = api_key
        

    async def get_response_async(self, message, chat_history=[]):
        resp=""
        context = [fastapi_poe.ProtocolMessage(role=msg["role"], content=msg["content"]) for msg in chat_history]
        context.append(fastapi_poe.ProtocolMessage(role="user", content=message))

        async for partial in fastapi_poe.get_bot_response(messages=context, bot_name=self.model_name, api_key=self.api_key):
            #print(partial.text, end="", flush=True)
            resp += partial.text
        #print('\n')
        return resp
    
    def generate(self, message, chat_history=[]):
        return asyncio.run(self.get_response_async(message, chat_history))



class DeepSeekLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key

    def generate(self, message, chat_history=[]):
        client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        messages = []
        if self.force_json:
            messages = [{"role": "system", "content": "请严格使用JSON格式输出，确保返回的字符串是有效的JSON"}]
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False,
            temperature=1.25
        )
        resp = response.choices[0].message.content
        return resp




'''
    可选的模型
    qwen-max
    qwen-max-longcontext
    qwen-plus
    qwen-long
'''
class QwenLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        dashscope.api_key = self.api_key

    def generate(self, message, chat_history=[]):
        messages = []
        if self.force_json:
            messages = [{"role": "system", "content": "请严格使用JSON格式输出，确保返回的字符串是有效的JSON"}]
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = Generation.call(
            self.model_name,
            messages=messages,
            result_format='message',
            stream=True,
            incremental_output=True
        )

        full_response = ""
        for partial_response in response:
            if partial_response.status_code == HTTPStatus.OK:
                content = partial_response.output.choices[0]['message']['content']
                full_response += content
            else:
                print(f'请求 ID: {partial_response.request_id}, 状态码: {partial_response.status_code}, 错误代码: {partial_response.code}, 错误信息: {partial_response.message}')
        return full_response

'''
Baichuan4
Baichuan3-Turbo
Baichuan3-Turbo-128k
Baichuan2-Turbo
Baichuan2-Turbo-192k
'''
class BaichuanLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.api_url = "https://api.baichuan-ai.com/v1/chat/completions"

    def generate(self, message, chat_history=[]):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        messages = []
        if self.force_json:
            messages = [{"role": "system", "content": "请严格使用JSON格式输出，确保返回的字符串是有效的JSON"}]
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"请求失败: {response.status_code}, {response.text}")

class ZhipuLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = ZhipuAI(api_key=self.api_key)

    def generate(self, message, chat_history=[]):
        messages = []
        if self.force_json:
            messages = [{"role": "system", "content": "请严格使用JSON格式输出，确保返回的字符串是有效的JSON"}]
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        full_response = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content is not None:
                full_response += content
                #print(content, end='', flush=True)
        return full_response


PoeModelList = [
    "Claude-3.5-Sonnet", 
    "Claude-3.5-Sonnet-200k", 
    "GPT-4o",
    "GPT-4o-128k",
    "Gemini-1.5-Pro",
    "Gemini-1.5-Flash",
    "Gemini-1.5-Pro-128k",
    "Gemini-1.5-Pro-2M"
]

def BuildModel(model_name, api_key, force_json=False):
    if model_name in PoeModelList:
        return PoeLlm(model_name, api_key, force_json)
    elif model_name == "deepseek-chat":
        return DeepSeekLlm(model_name, api_key, force_json)
    elif model_name in ["豆包-Pro-4K", "豆包-Pro-32K", "豆包-Pro-128K"]:
        return DoubaoLlm(model_name, api_key, force_json)
    elif model_name in ["qwen-max", "qwen-max-longcontext", "qwen-plus", "qwen-long"]:
        return QwenLlm(model_name, api_key, force_json)
    elif model_name in ["Baichuan4", "Baichuan3-Turbo", "Baichuan3-Turbo-128k", "Baichuan2-Turbo", "Baichuan2-Turbo-192k"]:
        return BaichuanLlm(model_name, api_key, force_json)
    elif model_name in ["glm-3-turbo", "glm-4", "glm-4v"]:
        return ZhipuLlm(model_name, api_key, force_json)
    else:
        raise ValueError("未知的模型名称:", model_name)
    
    



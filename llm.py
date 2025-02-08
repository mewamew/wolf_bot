from openai import OpenAI
from dashscope import Generation
from http import HTTPStatus
from zhipuai import ZhipuAI
import json
import dashscope
import requests
import http.client
import re
import logging

logger = logging.getLogger(__name__)

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
            resp_dict = None
            try:
                # 匹配被```json包裹的JSON块（非贪婪匹配）
                json_block_pattern = r'```json\s*([\s\S]*?)\s*```'
                json_match = re.search(json_block_pattern, resp, re.DOTALL)
                
                if json_match:
                    clean_resp = json_match.group(1)
                else:
                    # 直接尝试解析整个响应（已自动去除多余符号）
                    clean_resp = re.sub(r'```json|```', '', resp).strip()

                resp_dict = json.loads(clean_resp)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}\n清洗后响应: {clean_resp[:200]}")
            except Exception as e:
                logger.error(f"意外错误: {str(e)}\n原始响应: {resp[:200]}")
            finally:
                return resp_dict
        return resp
    
class M302Llm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key

    def generate(self, message, chat_history=[]):
        messages = []
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        payload = json.dumps({
            "model": self.model_name,
            "reasoning_effort": "high",
            "messages": messages
        })
        conn = http.client.HTTPSConnection("api.302.ai")
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        response = json.loads(data)
        return response["choices"][0]["message"]["content"]


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

'''
硅基流动的推理模型: 
https://api.siliconflow.cn/v1/
deepseek-ai/DeepSeek-R1
Pro/deepseek-ai/DeepSeek-R1 (比较快)
'''
class SiliconReasoner(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.client = OpenAI(
                base_url='https://api.siliconflow.cn/v1/',
                api_key=api_key
            )

    def generate(self, message, chat_history=[]):
        messages = [{"role": "user", "content": message}]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True, 
            max_tokens=4096
        )
        content = ""
        reasoning_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end='', flush=True)
            if chunk.choices[0].delta.reasoning_content:
                reasoning_content += chunk.choices[0].delta.reasoning_content
                print(chunk.choices[0].delta.reasoning_content, end='', flush=True)
        with open('reasoning.txt', 'a', encoding='utf-8') as f:
            f.write(f'{chunk.choices[0].delta.reasoning_content}\n')
        return content



M302LLM_SUPPORTED_MODELS = [
    "o3-mini",
    "o3-mini-2025-01-31", 
    "gemini-2.0-flash-thinking-exp-01-21"]

SILICONFLOW_SUPPORTED_MODELS = [
    "deepseek-ai/DeepSeek-R1",
    "Pro/deepseek-ai/DeepSeek-R1"]


def BuildModel(model_name, api_key, force_json=False):
    if model_name in M302LLM_SUPPORTED_MODELS:
        return M302Llm(model_name, api_key, force_json)
    elif model_name in SILICONFLOW_SUPPORTED_MODELS:
        return SiliconReasoner(model_name, api_key, force_json)
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
    
    

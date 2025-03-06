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
import socket
import datetime
import os


logger = logging.getLogger(__name__)

class BaseLlm():
    def __init__(self, model_name, force_json=False):
        
        self.model_name = model_name
        self.force_json = force_json
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    def prepare_messages(self, message, chat_history):
        messages = []
        for msg in chat_history:
            messages.append({"role": "assistant" if msg["role"] == "bot" else "user", "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        return messages

    def openai_like_generate(self, messages, stream=True, extra_body=None, **kwargs):
        try:
            params = {"model": self.model_name, "messages": messages, "stream": stream}
            if extra_body:
                params["extra_body"] = extra_body
            params.update(kwargs)
            response = self.client.chat.completions.create(**params)
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        print(content, end="", flush=True)
                return full_response, None
            else:
                return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e)

    def generate(self, message, chat_history=[]):
        pass

    def get_response(self, message, chat_history=[]):
        max_retries = 3
        retry_count = 0
        print(f" ---  请求LLM {self.model_name} ---")
        print(message)
        print("---")
        
        while retry_count < max_retries:
            try:
                resp, reason = self.generate(message, chat_history)
                if resp is None:
                    raise Exception(reason if reason else "未知错误")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"在尝试{max_retries}次后仍然失败。错误: {str(e)}")
                    resp = None
                    reason = str(e)
                    break
                logger.warning(f"发生错误: {str(e)}。正在进行第{retry_count}次重试...")
                import time
                time.sleep(retry_count * 2)  # 指数退避
        
        if reason:
            print(" --- 推理内容 ---")
            print(reason)
            print("-------")
        
        print(" --- LLM 响应 ---")
        print(resp)
        print("-------")

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
                return resp_dict, reason
        return resp, reason
    
class M302Llm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False, timeout=30):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.timeout = timeout  

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        payload = json.dumps({
            "model": self.model_name,
            "reasoning_effort": "high",
            "messages": messages
        })
        try:
            conn = http.client.HTTPSConnection("api.302.ai", timeout=self.timeout)  
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self.api_key,
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            response = json.loads(data)
            content = response["choices"][0]["message"]["content"]
            # 提取推理内容
            reasoning_patterns = [
                re.compile(r'> Reasoning\n(.*?)\nReasoned for .*?\n\n', re.DOTALL),  # 原始格式
                re.compile(r'<thinking>(.*?)</thinking>', re.DOTALL),  # 新格式1
                re.compile(r'<think>(.*?)</think>', re.DOTALL)  # 新格式2
            ]
            
            match = None
            for pattern in reasoning_patterns:
                match = pattern.search(content)
                if match:
                    break
                    
            if match:
                reasoning = match.group(1).strip()
                # 如果是<thinking>格式，直接返回内容，否则按原方式处理
                if '<thinking>' in content or '<think>' in content:
                    # 移除<thinking>部分返回剩余内容
                    clean_content = re.sub(r'<thinking>.*?</thinking>|<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    return clean_content, reasoning
                else:
                    # 原始格式处理方式
                    return content.split('\n\n')[1].strip(), None
            return content, None
        except socket.timeout:
            logger.warning("API请求超时")
            return None, None
        except Exception as e:
            logger.error(f"请求失败：{str(e)}")
            return None, None
        finally:
            conn.close()


class DeepSeekLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com", timeout=1800)

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        return self.openai_like_generate(messages, stream=False, temperature=1.25)


class QwenLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        dashscope.api_key = self.api_key

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
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
        return full_response, None

class BaichuanLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.api_url = "https://api.baichuan-ai.com/v1/chat/completions"

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'], None
        else:
            raise Exception(f"请求失败: {response.status_code}, {response.text}")


class ZhipuLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = ZhipuAI(api_key=self.api_key)

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        return self.openai_like_generate(messages, stream=True)


class KimiLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.moonshot.cn/v1", timeout=1800)

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        return self.openai_like_generate(messages, stream=True)


class DouBaoLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = OpenAI(
                base_url='https://ark.cn-beijing.volces.com/api/v3/',
                api_key=self.api_key
            )

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        return self.openai_like_generate(messages, stream=True)


class HunyuanLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.hunyuan.cloud.tencent.com/v1",
            timeout=1800
        )

    def generate(self, message, chat_history=[]):
        messages = self.prepare_messages(message, chat_history)
        return self.openai_like_generate(messages, stream=True, extra_body={"enable_enhancement": True})


class SiliconReasoner(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        
        self.client = OpenAI(
                base_url='https://api.siliconflow.cn/v1/',
                api_key=api_key,
                timeout=1800
            )

    def generate(self, message, chat_history=[]):
        messages = [{"role": "user", "content": message}]
        return self.openai_like_generate(messages, stream=True, max_tokens=4096)


class HumanLlm(BaseLlm):
    def __init__(self, model_name):
        super().__init__(model_name)
        pass
    
    def generate(self, message, chat_history=[]):
        pass


M302LLM_SUPPORTED_MODELS = [
    "o3-mini",
    "o3-mini-2025-01-31",
    "gemini-2.0-flash-thinking-exp-01-21",
    "claude-3-7-sonnet-latest",
    "claude-3-7-sonnet-thinking"
    ]

SILICONFLOW_SUPPORTED_MODELS = [
    "deepseek-ai/DeepSeek-R1",
    "Pro/deepseek-ai/DeepSeek-R1"
    ]


def BuildModel(model_name, api_key, force_json=False):
    if model_name in M302LLM_SUPPORTED_MODELS:
        return M302Llm(model_name, api_key, force_json)
    elif model_name in SILICONFLOW_SUPPORTED_MODELS:
        return SiliconReasoner(model_name, api_key, force_json)
    elif model_name in ["deepseek-reasoner", "deepseek-chat"]:
        return DeepSeekLlm(model_name, api_key, force_json)
    elif model_name in ["qwen-max", "qwen-max-longcontext", "qwen-plus", "qwen-long", "qwen-max-2025-01-25"]:
        return QwenLlm(model_name, api_key, force_json)
    elif model_name in ["Baichuan4", "Baichuan3-Turbo", "Baichuan3-Turbo-128k", "Baichuan2-Turbo", "Baichuan2-Turbo-192k"]:
        return BaichuanLlm(model_name, api_key, force_json)
    elif model_name in ["glm-3-turbo", "glm-4", "glm-4v", "glm-4-plus"]:
        return ZhipuLlm(model_name, api_key, force_json)
    elif model_name in ["moonshot-v1-32k"]:
        return KimiLlm(model_name, api_key, force_json)
    elif model_name.startswith("ep-"):
        return DouBaoLlm(model_name, api_key, force_json)
    elif model_name in ["hunyuan-large", "hunyuan-turbo-latest"]:
        return HunyuanLlm(model_name, api_key, force_json)
    elif model_name == "human":
        return HumanLlm(model_name)
    else:
        raise ValueError("未知的模型名称:", model_name)
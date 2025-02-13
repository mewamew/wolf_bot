from openai import OpenAI
from dashscope import Generation
from http import HTTPStatus
from zhipuai import ZhipuAI
import google.generativeai as genai
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
        
    def generate(self, message, chat_history=[]):
        pass

    def get_response(self, message, chat_history=[]):
        print(f" ---  请求LLM {self.model_name} ---")
        print(message)
        print("---")
        resp, reason = self.generate(message, chat_history)
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
            reasoning_pattern = re.compile(
                r'> Reasoning\n(.*?)\nReasoned for .*?\n\n',
                re.DOTALL
            )
            match = reasoning_pattern.search(content)
            if match:
                reasoning = match.group(1).strip()
                print(f"\n[推理过程]\n{reasoning}\n")
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
        return resp, None



'''
    可选的模型
    qwen-max
    qwen-max-longcontext
    qwen-plus
    qwen-long
    qwen-max-2025-01-25 (qwen2.5 max)
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
        return full_response, None

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

        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'], None
        else:
            raise Exception(f"请求失败: {response.status_code}, {response.text}")

'''
谷歌帐号没申请成功，比较麻烦，推荐直接用302ai的模型
gemini-2.0-flash-thinking-exp-01-21

'''
class GeminiLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    def generate(self, message, chat_history=[]):
        messages = []
        if self.force_json:
            messages = ["请严格使用JSON格式输出，确保返回的字符串是有效的JSON"]
        for msg in chat_history:
            if msg["role"] == "bot":
                messages.append(msg["content"])
            else:
                messages.append(msg["content"])
        messages.append(message)

        model = genai.GenerativeModel(self.model_name)
        chat = model.start_chat()
        response = chat.send_message("\n".join(messages))
        return response.text, None

'''
glm-3-turbo
glm-4
glm-4v
'''
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
        return full_response, None

'''
moonshot-v1-32k
'''
class KimiLlm(BaseLlm):
    def __init__(self, model_name, api_key, force_json=False):
        super().__init__(model_name, force_json)
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.moonshot.cn/v1")

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
        return full_response, None

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
        return content, reasoning_content



M302LLM_SUPPORTED_MODELS = [
    "o3-mini",
    "o3-mini-2025-01-31",
    "gemini-2.0-flash-thinking-exp-01-21"
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
    elif model_name == "deepseek-chat":
        return DeepSeekLlm(model_name, api_key, force_json)
    elif model_name in ["qwen-max", "qwen-max-longcontext", "qwen-plus", "qwen-long", "qwen-max-2025-01-25"]:
        return QwenLlm(model_name, api_key, force_json)
    elif model_name in ["Baichuan4", "Baichuan3-Turbo", "Baichuan3-Turbo-128k", "Baichuan2-Turbo", "Baichuan2-Turbo-192k"]:
        return BaichuanLlm(model_name, api_key, force_json)
    elif model_name in ["glm-3-turbo", "glm-4", "glm-4v"]:
        return ZhipuLlm(model_name, api_key, force_json)
    elif model_name in ["moonshot-v1-32k"]:
        return KimiLlm(model_name, api_key, force_json)
    else:
        raise ValueError("未知的模型名称:", model_name)




def get_model_options():
    """获取所有支持的模型选项"""
    return {
        # M302LLM模型组
        "302": {
            "name": "302 AI",
            "api_key": "sk-8JaZfqVt87pgbC1NZKQUH95EBLnL4rlpZHGLCmRNJiW16WN2",
            "models": {
                1: "o3-mini",
                2: "o3-mini-2025-01-31",
                3: "gemini-2.0-flash-thinking-exp-01-21"
            }
        },
        
        
        # SiliconFlow模型组
        "silicon": {
            "name": "Silicon Flow",
            "api_key": "sk-xvfyfadzvhixthbpnrcmfzkmnbiehvwshhryvidumxgiseih",
            "models": {
                4: "deepseek-ai/DeepSeek-R1",
                5: "Pro/deepseek-ai/DeepSeek-R1"
            }
        },
        
        # DeepSeek模型组
        "deepseek": {
            "name": "DeepSeek",
            "api_key": "sk-456392e75afa4efb812dc0e1bf792248",
            "models": {
                6: "deepseek-chat"
            }
        },
        
        # 通义千问模型组
        "qwen": {
            "name": "通义千问",
            "api_key": "sk-62081a7ee50143b298f2a92127867985",
            "models": {
                7: "qwen-max",
                8: "qwen-max-longcontext",
                9: "qwen-plus",
                10: "qwen-long",
                11: "qwen-max-2025-01-25"
            }
        },
        
        # 百川模型组
        "baichuan": {
            "name": "百川",
            "api_key": "sk-9d3d6ed146af1bd138c8f90898d14f94",
            "models": {
                12: "Baichuan4",
                13: "Baichuan3-Turbo",
                14: "Baichuan3-Turbo-128k",
                15: "Baichuan2-Turbo",
                16: "Baichuan2-Turbo-192k"
            }
        },
        
        # 智谱模型组
        "zhipu": {
            "name": "智谱",
            "api_key": "027a60991fe4462fab7507bbf40fff52.jdq81S9F0brOBHJM",
            "models": {
                17: "glm-3-turbo",
                18: "glm-4",
                19: "glm-4v"
            }
        },

        # Kimi模型组
        "Kimi": {
            "name": "Kimi", 
            "api_key": "sk-KerkHwJnibU8D4cYDPaflzc0BPsucl99LzB1U5pH5drfDKx7",
            "models": {
                20: "moonshot-v1-32k"
            }
        }
    }


def get_api_key_by_model(model_name):
    """根据模型名称获取对应的API密钥"""
    model_options = get_model_options()
    
    # 遍历所有模型组
    for provider in model_options.values():
        # 检查模型是否在当前提供商的模型列表中
        if any(model == model_name for model in provider["models"].values()):
            return provider["api_key"]
    return None

class ModelTester:
    def __init__(self):
        self.model_options = get_model_options()
        self.logger = logging.getLogger(__name__)
        self.current_color = "\033[94m"  # 初始为蓝色

    def test_single_model(self, model_name, api_key, color=None):
        """测试单个模型"""
        try:
            self.logger.info(f"开始测试模型: {model_name}")
            model = BuildModel(model_name, api_key)
            response, reason = model.get_response("你好，请介绍自己")
            
            if reason:
                print(f"{color}\n推理过程: {reason}\033[0m")
            
            print(f"{color}\n模型响应:\033[0m")
            print(f"{color}{response}\033[0m")
            self.logger.info(f"模型 {model_name} 测试成功")
            return True
        except Exception as e:
            self.logger.error(f"模型 {model_name} 测试失败: {str(e)}")
            print(f"\033[91m测试失败: {str(e)}\033[0m")
            return False

    def test_all_models(self):
        """测试所有模型"""
        success_count = 0
        total_models = sum(len(provider['models']) for provider in self.model_options.values())
        
        for provider in self.model_options.values():
            for model_id, model_name in provider['models'].items():
                # 交替使用蓝色和黄色
                self.current_color = "\033[94m" if self.current_color == "\033[93m" else "\033[93m"
                print(f"{self.current_color}\n=== 测试模型 {model_id}: {model_name} ===\033[0m")
                api_key = provider['api_key']
                
                if not api_key:
                    print(f"\033[91m跳过模型 {model_name}: 未找到API密钥\033[0m")
                    continue
                    
                if self.test_single_model(model_name, api_key, self.current_color):
                    success_count += 1
                
                print(f"{self.current_color}{'=' * 50}\033[0m")
        
        result_msg = f"\n测试完成: 成功 {success_count}/{total_models} 个模型"
        self.logger.info(result_msg)
        print(f"{self.current_color}{result_msg}\033[0m")

    def print_model_options(self):
        """打印所有可用的模型选项"""
        print("\n可用的模型选项:")
        print("-" * 50)
        
        for provider_key, provider in self.model_options.items():
            print(f"\n{provider['name']}模型:")
            for model_id, model_name in provider['models'].items():
                print(f"{model_id}. {model_name}")
        
        print("-" * 50)

def test_model():
    """测试不同模型的对话功能"""
    tester = ModelTester()
    tester.print_model_options()
    
    while True:
        try:
            choice = int(input("\n请输入要测试的模型编号(1-20，输入-1循环测试所有模型): "))
            
            if choice == -1:
                tester.test_all_models()
                break
            elif 1 <= choice <= 20:
                # 查找选择的模型
                model_name = None
                api_key = None
                for provider in tester.model_options.values():
                    if choice in provider['models']:
                        model_name = provider['models'][choice]
                        api_key = provider['api_key']
                        break
                
                if model_name and api_key:
                    tester.test_single_model(model_name, api_key)
                else:
                    print("未找到指定的模型!")
                break
            else:
                print("请输入-1或1-19之间的数字!")
        except ValueError:
            print("请输入有效的数字!")

if __name__ == "__main__":
    test_model()



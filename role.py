from llm import BuildModel
from history import *
from log import *
import yaml
import json
import time
from datetime import datetime
import random

class BaseRole:
    def __init__(self, player_index, role_type, model_name, api_key, game):
        self.player_index = player_index
        self.role_type = role_type
        self.is_alive = True
        self.game = game
        self.model = BuildModel(model_name, api_key, force_json=True) 


    def __str__(self):
        return f"你的玩家编号: {self.player_index}, 角色类型: {self.role_type}"
    
    def error(self, e, resp):
        print("\033[91m发生错误:\033[0m")
        print("\033[91m{}\033[0m".format(e))
        print("\033[91m{}\033[0m".format(resp))

    def get_players_state(self):
        state = []
        for player in self.game.players:
            state.append(f"{player.player_index}号玩家: {'存活' if player.is_alive else '死亡'}")
        return state

    def prompt_preprocess(self, prompt_template):
        prompt_template['角色'] = f"你是一名{self.role_type}"
        prompt_template['第几天'] = f'当前是第{self.game.current_day}天'
        prompt_template['你的玩家编号'] = f"你是{self.player_index}号玩家"
        prompt_template['事件'] = self.game.history.get_history()
        prompt_template['玩家状态'] = self.get_players_state()
        prompt_template['随机数种子'] = int(time.time() * 1000) + random.randint(1, 1000)
        return prompt_template

    def handle_action(self, prompt_file, extra_data=None, retry_count=0):
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompt_template = yaml.safe_load(file)
            prompt_dict = self.prompt_preprocess(prompt_template)
            # 获取公共规则
            with open('prompts/prompt_game_rule.yaml', 'r', encoding='utf-8') as rule_file:
                prompt_gamerule = yaml.safe_load(rule_file)
                prompt_dict.update(prompt_gamerule)
            
            # 根据角色阵营加载策略规则
            '''
            # TODO: 暂时不要加载任何策略
            if self.role_type == '狼人':
                strategy_file = 'prompts/prompt_wolf_strategy.yaml'
                with open(strategy_file, 'r', encoding='utf-8') as strategy_file:
                    strategy_rules = yaml.safe_load(strategy_file)
                    prompt_dict.update(strategy_rules)
                
            
            elif self.role_type == '村民':
                strategy_file = 'prompts/prompt_villager_strategy.yaml'
            else:
                # 神职角色（预言家、女巫、猎人）使用神职策略
                strategy_file = 'prompts/prompt_god_strategy.yaml'
            '''
            
            if extra_data:
                prompt_dict.update(extra_data)
            
            prompt_str = json.dumps(prompt_dict, ensure_ascii=False)
            resp, reason = self.model.get_response(prompt_str)
            
            if resp is None:
                self.error("请求失败", prompt_str)
                if retry_count < 10:
                    print_red("重新发起请求")
                    time.sleep(10)
                    return self.handle_action(prompt_file, extra_data, retry_count+1)
                return None

            # 检查响应中是否包含必要字段
            required_fields = prompt_template.get('required_fields', [])
            if required_fields:
                missing_fields = [field for field in required_fields if field not in resp]
                if missing_fields:
                    self.error(f"响应缺少必要字段: {missing_fields}", resp)
                    if retry_count < 10:
                        print_red("重新发起请求")
                        time.sleep(10)
                        return self.handle_action(prompt_file, extra_data, retry_count+1)
                    return None

            # 日志记录保持原样
            with open(f'logs/llm_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                log_file.write(f"--- {self.player_index}号玩家 ({self.role_type}) ---\n")
                log_file.write(f"---输入---:\n{prompt_str}\n")
                log_file.write(f"---输出---:\n{json.dumps(resp, ensure_ascii=False)}\n")
                if reason:
                    log_file.write(f"---推理过程---:\n{reason}\n")

            # 2025年02月16日 R1的推理实在太长受不了了，直接忽略
            #存在推理过程，用推理过程替代thinking
            #if 'thinking' in resp and reason:
            #    resp['thinking'] = reason
            return resp

    def speak(self, content, extra_data=None):
        if not content:
            if extra_data is None:
                extra_data={}
            resp_dict = self.handle_action('prompts/prompt_speak.yaml', extra_data)
            if resp_dict:
                self.game.history.add_event(SpeakEvent(self.player_index, resp_dict['speak']))
                return resp_dict
        else:
            self.game.history.add_event(SpeakEvent(self.player_index, content))
            return {'thinking':'', 'speak': content}

    def vote(self, vote_id, extra_data=None):
        if vote_id == -100:
            if extra_data is None:
                extra_data={}
            resp_dict = self.handle_action('prompts/prompt_vote.yaml', extra_data)
            if resp_dict:
                vote_id = resp_dict['vote']
                self.game.history.add_event(VoteEvent(self.player_index, vote_id))
                return resp_dict
        else:
            self.game.history.add_event(VoteEvent(self.player_index, vote_id))
            return {
                'vote': vote_id,
                'thinking': ''
            }


    def last_words(self, speak, death_reason, extra_data=None):
        """发表遗言(死后)"""
        resp_dict = {}
        if extra_data is None:
            extra_data={}
        extra_data['reason'] = death_reason

        if not speak:
            resp_dict = self.handle_action('prompts/prompt_lastword.yaml', extra_data)
        else:
            resp_dict['speak'] = speak
            resp_dict['thinking'] = ''
        if resp_dict:
            self.game.history.add_event(LastWordEvent(self.player_index, resp_dict['speak']))
        
        return resp_dict
    
    def be_executed(self, vote_result):
        '''被放逐'''
        self.is_alive = False
        self.game.history.add_event(ExecuteEvent(self.player_index, vote_result))
        with open(f'logs/result_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"【{self.game.current_day} {self.game.current_phase}】 【{self.player_index}】号【{self.role_type}】被处决\n")

    def be_attacked(self):
        '''被攻击'''
        self.is_alive = False
        self.game.history.add_event(AttackEvent(self.player_index))
        with open(f'logs/result_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"【{self.game.current_day} {self.game.current_phase}】 【{self.player_index}】号【{self.role_type}】被猎人反击杀死\n")

    def be_killed(self):
        '''被杀'''
        self.is_alive = False
        self.game.history.add_event(KillEvent(self.player_index))
        with open(f'logs/result_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"【{self.game.current_day} {self.game.current_phase}】 【{self.player_index}】号【{self.role_type}】被狼人杀死\n")

    def be_poisoned(self):
        '''被毒杀'''
        self.is_alive = False
        self.game.history.add_event(PoisonEvent(self.player_index))
        self.game.history.add_event(KillEvent(self.player_index))
        with open(f'logs/result_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"【{self.game.current_day} {self.game.current_phase}】 【{self.player_index}】号【{self.role_type}】被女巫毒死\n")
        
    def be_cured(self):
        '''被治愈'''
        self.is_alive = True
        self.game.history.add_event(CureEvent(self.player_index))
    
        
class Villager(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "村民", model_name, api_key, game)
    
class Hunter(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "猎人", model_name, api_key,  game)
    
    def make_extra_data(self):
        extra_data = {
            "猎人技能": "当猎人被狼人杀死或者被投票出局时，猎人可以选择发动反击技能带走一名玩家"
        }
        return extra_data

    def last_words(self, speak, death_reason):
        extra_data = self.make_extra_data()
        return super().last_words(speak, death_reason, extra_data)

    def revenge(self, death_reason):
        extra_data = {
            "出局的原因": death_reason
        }
        return  self.handle_action('prompts/prompt_hunter_revenge.yaml', extra_data)


class Seer(BaseRole):
    def __init__(self, player_index, model_name, api_key, game):
        super().__init__(player_index, "预言家", model_name, api_key, game)
        self.divine_result = []

    def make_extra_data(self):
        extra_data = None
        if len(self.divine_result) > 0:
            extra_data = {'你已经掌握的信息': self.divine_result}
        return extra_data

    def last_words(self, speak, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(speak, death_reason, extra_data)

    def speak(self, content):
        extra_data = self.make_extra_data()
        return super().speak(content, extra_data)

    def vote(self, vote_id):
        extra_data = self.make_extra_data()
        return super().vote(vote_id, extra_data)
        
    def divine(self):
        """决定查看谁的身份"""
        extra_data = self.make_extra_data()
        resp_dict = self.handle_action('prompts/prompt_divine.yaml', extra_data)
        if resp_dict:
            divine_id = resp_dict['divine']
            is_good_man = "好人" if self.game.players[divine_id-1].role_type != "狼人" else "狼人"
            self.divine_result.append(
                f"【{divine_id}号玩家】是 {is_good_man}."
            )
            return resp_dict
    

class Wolf(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "狼人", model_name, api_key,  game)
    

    def make_extra_data(self):
        wolves  = self.game.get_wolves()
        wolves_list = []
        for wolf in wolves:
            if wolf["player_index"] == self.player_index:
                continue
            is_alive = "存活" if wolf["is_alive"] else "已死亡"
            wolves_list.append(f"{wolf['player_index']}号玩家是狼人, 目前{is_alive}")
        extra_data = {
            "你的狼人队友": wolves_list
        }
        return extra_data

    def last_words(self, speak, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(speak, death_reason, extra_data)

    def vote(self, vote_id):
        extra_data = self.make_extra_data()
        return super().vote(vote_id, extra_data)

    def speak(self, content):
        extra_data = self.make_extra_data()
        return super().speak(content, extra_data)
    
    
    def decide_kill(self, kill_id, want_kill=None):
        extra_data = self.make_extra_data()
        if want_kill:
            extra_data['第几轮投票'] = 2
            extra_data['第一轮投票结果'] = want_kill
        else:
            extra_data['第几轮投票'] = 1
        resp_dict = {}
        if kill_id == -100:
            resp_dict = self.handle_action('prompts/prompt_kill.yaml', extra_data)
        else:
            resp_dict['kill'] = kill_id
            resp_dict['reason'] = ''
        if resp_dict:
            return resp_dict
        


class Witch(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "女巫", model_name, api_key,  game)
        self.cured_someone = 0
        self.poisoned_someone = -1
    
    def make_extra_data(self):
        extra_data = {
            'cured_someone': f'已经使用解药救过{self.cured_someone}号玩家，不允许再次使用解药技能' if self.cured_someone != 0 else "还没使用过救治技能",
            'poisoned_someone': f'已经使用毒药杀了{self.poisoned_someone}号玩家， 不允许再次使用解药技能' if self.poisoned_someone != -1 else "还没使用过毒杀技能"
        }
        return extra_data

    def last_words(self, speak, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(speak, death_reason, extra_data)

    def vote(self, vote_id):
        extra_data = self.make_extra_data()
        return super().vote(vote_id, extra_data)

    def speak(self, content):
        extra_data = self.make_extra_data()
        return super().speak(content, extra_data)
    
    def decide_cure_or_poison(self, someone_will_be_killed):
        """决定是否要治疗或毒杀"""
        extra_data = self.make_extra_data()
        if someone_will_be_killed != -1:
            extra_data['今晚发生了什么'] = f'{someone_will_be_killed}号玩家将被杀害'
        else:
            extra_data['今晚发生了什么'] = "没有人将被杀害"
        resp_dict = self.handle_action('prompts/prompt_cure_or_poison.yaml', extra_data)
        if resp_dict:
            self.cured_someone = someone_will_be_killed if resp_dict['cure'] == 1 else 0
            self.poisoned_someone = resp_dict['poison'] if resp_dict['poison'] != -1 else self.poisoned_someone
            return resp_dict
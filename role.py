from llm import BuildModel
from history import *
from log import *
import yaml
import json
import time
from datetime import datetime

class BaseRole:
    def __init__(self, player_index, role_type, model_name, api_key, game):
        self.player_index = player_index
        self.role_type = role_type
        self.is_alive = True
        self.game = game
        self.model = BuildModel(model_name, api_key, force_json=True) 
        print_white(f"{self.player_index}号玩家的角色是{self.role_type}, 模型使用{self.model.model_name}")

    def __str__(self):
        return f"玩家编号: {self.player_index}, 角色类型: {self.role_type}"
    
    def error(self, e, resp):
        print("\033[91m发生错误:\033[0m")
        print("\033[91m{}\033[0m".format(e))
        print("\033[91m{}\033[0m".format(resp))

    def get_players_state(self):
        state = []
        for player in self.game.players:
            state.append({
                "player_index": f"{player.player_index}号玩家",
                "is_alive": "存活" if player.is_alive else "死亡"
            })
        return state

    def prompt_preprocess(self, prompt_template):
        prompt_template['role'] = f"你是一名{self.role_type}"
        prompt_template['day'] = f'当前是第{self.game.current_day}天'
        prompt_template['player_index'] = f"你是{self.player_index}号玩家"
        prompt_template['curr_state'] = self.game.history.get_history()
        prompt_template['players_state'] = self.get_players_state()
        return prompt_template

    def handle_action(self, prompt_file, extra_data=None, retry_count=0):
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompt_template = yaml.safe_load(file)
            prompt_dict = self.prompt_preprocess(prompt_template)
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

            # 日志记录保持原样
            with open(f'logs/llm_{self.game.start_time}.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                log_file.write(f"--- {self.player_index}号玩家 ({self.role_type}) ---\n")
                log_file.write(f"---输入---:\n{prompt_str}\n")
                log_file.write(f"---输出---:\n{json.dumps(resp, ensure_ascii=False)}\n")
                if reason:
                    log_file.write(f"---推理过程---:\n{reason}\n")

            #存在推理过程，用推理过程替代thinking
            if 'thinking' in resp and reason:
                resp['thinking'] = reason
            return resp

    def speak(self, extra_data=None ):
        background = f"您是一名经验丰富的狼人杀玩家,你正在玩的是标准的6人局狼人杀, 你是【{self.player_index}号玩家】, 你扮演的是【{self.role_type}】, 目前是白天的发言环节,在全部人发言完毕之后，会进入投票环节"
        if extra_data is None:
            extra_data = {}
        extra_data['任务背景'] = background
        resp_dict = self.handle_action('prompts/prompt_speak.yaml', extra_data)
        if resp_dict:
            self.game.history.add_event(SpeakEvent(self.player_index, resp_dict['speak']))
            return resp_dict

    def vote(self, extra_data=None):
        """投票（决定谁是狼人）"""
        background = f"您是一名经验丰富的狼人杀玩家,你是【{self.player_index}号玩家】, 你扮演的是【{self.role_type}】, 目前你正在玩的是标准的6人局狼人杀, 目前是白天的投票环节"
        if extra_data is None:
            extra_data={}
        extra_data['任务背景'] = background

        resp_dict = self.handle_action('prompts/prompt_vote.yaml', extra_data)
        if resp_dict:
            vote_id = resp_dict['vote']
            self.game.history.add_event(VoteEvent(self.player_index, vote_id))
            return resp_dict

    def last_words(self, death_reason, extra_data=None):
        """发表遗言(死后)"""
        background = f"您是一名经验丰富的狼人杀玩家,你正在玩的是标准的6人局狼人杀, 你是【{self.player_index}号玩家】, 你扮演的是【{self.role_type}】, 目前你由于游戏出局，需要做最后发言"
        if extra_data is None:
            extra_data={}
        extra_data['reason'] = death_reason
        extra_data['任务背景'] = background
        resp_dict = self.handle_action('prompts/prompt_lastword.yaml', extra_data)
        if resp_dict:
            self.game.history.add_event(LastWordEvent(self.player_index, resp_dict['speak']))
            return resp_dict
    
    def be_executed(self):
        '''被放逐'''
        self.is_alive = False
        self.game.history.add_event(ExecuteEvent(self.player_index))

    def be_attacked(self):
        '''被攻击'''
        self.is_alive = False
        self.game.history.add_event(AttackEvent(self.player_index))

    def be_killed(self):
        '''被杀'''
        self.is_alive = False
        self.game.history.add_event(KillEvent(self.player_index))

    def be_poisoned(self):
        '''被毒杀'''
        self.is_alive = False
        self.game.history.add_event(PoisonEvent(self.player_index))
    
        
class Villager(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "村民", model_name, api_key, game)
    
class Hunter(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "猎人", model_name, api_key,  game)
    
    def last_words(self, death_reason):
        """发表遗言(死后)"""
        background = f"您是一名经验丰富的狼人杀玩家,你正在玩的是标准的6人局狼人杀, 你是【{self.player_index}号玩家】, 你扮演的是【{self.role_type}】, 目前你由于游戏出局，需要做最后发言"
        extra_data = {
            'reason': death_reason,
            '任务背景': background
        }
        resp_dict = self.handle_action('prompts/prompt_hunter_lastword.yaml', extra_data)
        if resp_dict:
            self.game.history.add_event(LastWordEvent(self.player_index, resp_dict['speak']))
            return resp_dict


class Seer(BaseRole):
    def __init__(self, player_index, model_name, api_key, game):
        super().__init__(player_index, "预言家", model_name, api_key, game)
        self.divine_result = []

    def make_extra_data(self):
        extra_data = None
        if len(self.divine_result) > 0:
            extra_data = {'你已经知道的玩家身份': self.divine_result}
        return extra_data

    def last_words(self, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(death_reason, extra_data)

    def speak(self):
        extra_data = self.make_extra_data()
        return super().speak(extra_data)

    def vote(self):
        extra_data = self.make_extra_data()
        return super().vote(extra_data)
        
    def divine(self):
        """决定查看谁的身份"""
        extra_data = self.make_extra_data()
        resp_dict = self.handle_action('prompts/prompt_divine.yaml', extra_data)
        if resp_dict:
            divine_id = resp_dict['divine']
            self.divine_result.append(
                {
                    "player_index": f"{divine_id}号玩家",
                    "role_type": self.game.players[divine_id-1].role_type
                }
            )
            return resp_dict
    

class Wolf(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "狼人", model_name, api_key,  game)
    

    def make_extra_data(self):
        extra_data = {
            "狼人列表": self.game.get_wolves()
        }
        return extra_data

    def last_words(self, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(death_reason, extra_data)

    def vote(self):
        extra_data = self.make_extra_data()
        return super().vote(extra_data)

    def speak(self):
        extra_data = self.make_extra_data()
        return super().speak(extra_data)
    
    
    def decide_kill(self, want_kill=None):
        extra_data = self.make_extra_data()
        if want_kill:
            extra_data['第几轮投票'] = 2
            extra_data['第一轮投票结果'] = want_kill
        else:
            extra_data['第几轮投票'] = 1
        resp_dict = self.handle_action('prompts/prompt_kill.yaml', extra_data)
        
        if resp_dict:
            return resp_dict
        


class Witch(BaseRole):
    def __init__(self, player_index, model_name, api_key,  game):
        super().__init__(player_index, "女巫", model_name, api_key,  game)
        self.cured_someone = -1
        self.poisoned_someone = -1
    
    def make_extra_data(self):
        extra_data = {
            'cured_someone': f'已经救治了{self.cured_someone}号玩家' if self.cured_someone != -1 else "还没使用过救治技能",
            'poisoned_someone': f'已经毒杀了{self.poisoned_someone}号玩家' if self.poisoned_someone != -1 else "还没使用过毒杀技能"
        }
        return extra_data

    def last_words(self, death_reason):
        """发表遗言(死后)"""
        extra_data = self.make_extra_data()
        return super().last_words(death_reason, extra_data)

    def vote(self):
        extra_data = self.make_extra_data()
        return super().vote(extra_data)

    def speak(self):
        extra_data = self.make_extra_data()
        return super().speak(extra_data)
    
    def decide_cure_or_poison(self, someone_will_be_killed):
        """决定是否要治疗或毒杀"""
        extra_data = self.make_extra_data()
        if someone_will_be_killed != -1:
            extra_data['今晚发生了什么'] = f'{someone_will_be_killed}号玩家将被杀害'
        else:
            extra_data['今晚发生了什么'] = "没有人将被杀害"
        resp_dict = self.handle_action('prompts/prompt_cure_or_poison.yaml', extra_data)
        if resp_dict:
            self.cured_someone = resp_dict['cure'] if resp_dict['cure'] != -1 else self.cured_someone
            self.poisoned_someone = resp_dict['poison'] if resp_dict['poison'] != -1 else self.poisoned_someone
            return resp_dict



    
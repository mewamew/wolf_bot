from datetime import datetime

class Event:
    def __init__(self, event_type, player_idx):
        self.event_type = event_type  # 事件类型
        self.player_idx = player_idx

    def desc(self)->str:
        pass


class SpeakEvent(Event):
    def __init__(self, player_idx, description):
        super().__init__("speak", player_idx)
        self.description = description

    def desc(self)->str:
        return f'【{self.player_idx}号玩家】发言: "{self.description})"'


class VoteEvent(Event):
    def __init__(self, player_idx, target_idx):
        super().__init__("vote", player_idx)
        self.target_idx = target_idx

    def desc(self)->str:
        return f'【{self.player_idx}号玩家】投票给: 【{self.target_idx}号玩家】'

class ExecuteEvent(Event):
    def __init__(self, player_idx):
        super().__init__("execute", player_idx)
        
    def desc(self)->str:
        return f'【{self.player_idx}号玩家】被处决'

class AttackEvent(Event):
    def __init__(self, player_idx):
        super().__init__("attack", player_idx)

    def desc(self)->str:
        return f'【{self.player_idx}号玩家】被猎人反击杀死'

class LastWordEvent(Event):
    def __init__(self, player_idx, description):
        super().__init__("last_word", player_idx)
        self.description = description
    def desc(self)->str:
        return f'【{self.player_idx}号玩家】最后发言: "{self.description}"'

class KillEvent(Event):
    def __init__(self, player_idx):
        super().__init__("kill", player_idx)

    def desc(self)->str:
        return f'【{self.player_idx}号玩家】被杀死'

class CureEvent(Event):
    def __init__(self, player_idx):
        super().__init__("cure", player_idx)

    def desc(self)->str:
        return f'某个玩家被女巫救治'
    
class PoisonEvent(Event):
    def __init__(self, player_idx):
        super().__init__("poison", player_idx)

    def desc(self)->str:
        return f'【{self.player_idx}号玩家】被投毒'

class Round:
    def __init__(self, day_count):
        self.day_count = day_count
        self.day_events = []
        self.night_events = []

    def get_events(self):
        events = {
            "day": f"第{self.day_count+1}天",
            "day_events": [],
            "night_events": []
        }
        for event in self.day_events:
            events["day_events"].append(event.desc())
        for event in self.night_events:
            events["night_events"].append(event.desc())
        return events

    def add_event(self, is_daytime, event):
        if is_daytime:
            self.day_events.append(event)
        else:
            self.night_events.append(event)

class History:
    def __init__(self):
        self.day_count = 0  # 当前是第几天,从0开始
        self.rounds = []  # 存储所有事件
        self.rounds.append(Round(self.day_count)) #创建第一个回合
        self.is_daytime = True  # 当前是白天还是晚上

    def dump(self):
        for round in self.rounds:
            print(round.get_events())

    def add_event(self, event):
        self.rounds[self.day_count].add_event(self.is_daytime, event)

    def get_history(self):
        '''
        构造一个事件列表
        '''
        history = []
        for round in self.rounds:
            history.append(round.get_events())
        return history

    def toggle_day_night(self):
        self.is_daytime = not self.is_daytime
        if self.is_daytime:
            self.day_count += 1
            #新的一天开始新回合
            self.rounds.append(Round(self.day_count))


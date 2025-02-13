from game import WerewolfGame




if __name__ == "__main__":
    game = WerewolfGame()
    game.start()
   
    #player = game.get_players()
    #print(player)
    
    #测试第一晚
    game.divine(5) #预言家查验
    kill_votes=[]
    kill_votes.append(game.decide_kill(1)) #狼人决定杀人
    kill_votes.append(game.decide_kill(8)) #狼人决定杀人
    kill_votes.append(game.decide_kill(9)) #狼人决定杀人
    
    killed_player = process_kill_votes(kill_votes)
    if killed_player != -1:
        print(f"第一轮投票结果: {killed_player} 号玩家被杀")
    else:
        print("投票无效，继续第二轮投票")
        kill_votes.append(game.decide_kill(1)) #狼人决定杀人
        kill_votes.append(game.decide_kill(8)) #狼人决定杀人
        kill_votes.append(game.decide_kill(9)) #狼人决定杀人
        killed_player = process_kill_votes(kill_votes)
        if killed_player != -1:
            print(f"第二轮投票结果: {killed_player} 号玩家被杀")
        else:
            print(f"第二轮投票结果: 平安夜")
            
    print(game.get_wolf_want_kill())
    
    decision = game.decide_cure_or_poison(6, killed_player)
    if decision["cure"] == 0 and killed_player != -1:
        game.last_words(killed_player, "被狼人杀死")
        game.kill(killed_player)
    
    if decision["poison"] != -1:
        game.last_words(decision["poison"], "被女巫毒死")
        game.poison(decision["poison"])
    
    #第一个夜晚结束
    game.toggle_day_night()
    
    #发言
    for player_idx in range(1,10):  
        game.speak(player_idx)
        
    #投票
    for player_idx in range(1,10):  
        game.vote(player_idx)
    
    vote_result = game.get_vote_result()
    print("投票结果：")
    print(vote_result)

    # 找出得票最多的玩家
    max_votes = max(vote_result.values())
    executed_players = [player for player, votes in vote_result.items() if votes == max_votes]

    # 如果只有一个人得票最高，处决该玩家
    if len(executed_players) == 1:
        executed_player = executed_players[0]
        # 让被处决玩家发表遗言
        last_words_result = game.last_words(executed_player, "被投票处决")
        # 处决玩家
        game.execute(executed_player)
        
        #如果被处决的玩家是猎人，判断是否要发动技能
        if "attack" in last_words_result:
            # 发动技能
            if last_words_result["attack"] != -1:
                game.attack(last_words_result["attack"])
    else:
        print("出现平票，本轮无人被处决")
        
    check_result = game.check_winner()
    print(check_result)
    
    #再次进入夜晚
    game.toggle_day_night()
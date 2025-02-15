import GameData from "./data.js";


class Action {
    constructor(game) {
        this.game = game;
    }

    async do() {}
}

class DivineAction extends Action {
    constructor(game) {
        super(game);
    }
    async do() {
        /// divine
        const diviner = this.game.get_diviner();
        if (diviner.is_alive) {
            console.log("== 预言家开始预言 ==");
            const role = this.game.show_role ? diviner.role_type : "玩家";
            const response = await this.game.gameData.divine({player_idx: diviner.index});
            await this.game.ui.showPlayer(diviner.index);
            if (this.game.show_thinking) {
                await this.game.ui.speak(`${diviner.index}号 ${role} 思考中`, response.thinking, true);
            }
        }
        return false;
    }
}

class WolfAction extends Action {
    constructor(game) {
        super(game);
    }
    
    async do() {
        console.log("== 狼人开始行动 ==");
        //重置投票
        await this.game.gameData.resetWolfWantKill();
        const wolves = this.game.get_wolves();
        /// 第一轮投票
        for (const wolf of wolves) {
            if (wolf.is_alive) {
                const response = await this.game.gameData.decideKill({ player_idx: wolf.index,is_second_vote: false });
                console.log(response);
                await this.game.ui.showPlayer(wolf.index);
                let killWho = "我决定今晚不杀人！"
                if (-1 !== response.kill) {
                    killWho = `我决定杀掉【${response.kill}】 号玩家!`;
                }
                const role = this.game.show_role ? wolf.role_type : "玩家";
                if (this.game.show_thinking) {
                    await this.game.ui.speak(`${wolf.index}号 ${role} 思考中：`, response.reason+killWho, true);
                }
            }
        }

        /// 获取投票结果
        const result = await this.game.gameData.getWolfWantKill();
        console.log("狼人投票结果：", result);
        const killedPlayer = result.wolf_want_kill;
        if (killedPlayer != -1) {
            console.log(`被杀死的玩家是：${killedPlayer} 号玩家`);
        } else {
            //无效投票，继续下一轮投票
            console.log("无效投票，继续下一轮投票");
            for (const wolf of wolves) {
                if (wolf.is_alive) {
                    const response = await this.game.gameData.decideKill({ player_idx: wolf.index,is_second_vote: true });
                    console.log(response);
                    await this.game.ui.showPlayer(wolf.index);
                    let killWho = "我决定今晚不杀人！"
                    if (-1 !== response.kill) {
                        killWho = `我决定杀掉【${response.kill}】 号玩家!`;
                    }
                    const role = this.game.show_role ? wolf.role_type : "玩家";
                    if (this.game.show_thinking) {
                        await this.game.ui.speak(`${wolf.index}号 ${role} 思考中：`, response.reason+killWho, true);
                    }
                }
            }
            /// 获取投票结果
            const result = await this.game.gameData.getWolfWantKill();
            console.log("狼人投票结果：", result);
            const killedPlayer = result.wolf_want_kill;
            if (killedPlayer != -1) {
                console.log(`被杀死的玩家是：${killedPlayer}`);
            } else {
                console.log("投票无效，今晚狼人不杀人");
            }
        }
        return false;
    }
}

class WitchAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        const witch = this.game.get_witch();
        const result = await this.game.gameData.getWolfWantKill();
        const killedPlayer = result.wolf_want_kill;
        if (!witch.is_alive) {
            //女巫已经死了
            if (killedPlayer != -1) {
                await this.game.gameData.kill({ player_idx: killedPlayer });
                await this.game.someone_die(killedPlayer, "被狼人杀死");
            }
        } else {
            console.log("== 女巫开始行动 ==");
            const result = await this.game.gameData.decideCureOrPoison({ player_idx: witch.index });
            console.log(result);
            await this.game.ui.showPlayer(witch.index);
            let cureWho = "我决定今晚不治疗！"
            if (1 == result.cure) {
                cureWho = `我决定治疗【${killedPlayer}】号玩家！`;
                const result = await this.game.gameData.cure({ player_idx: killedPlayer });
                console.log(result);
            }

            let poisonWho = "我决定今晚不毒杀！"
            if (-1 != result.poison) {
                poisonWho = `我决定毒杀【${result.poison}】 号玩家！`;
            }
            const role = this.game.show_role ? witch.role_type : "玩家";
            if (this.game.show_thinking) {
                await this.game.ui.speak(`${witch.index}号 ${role} 思考中：`, result.thinking + cureWho + poisonWho, true);
            }
            //根据女巫的决策结果进行操作
            if (1 != result.cure) {
                //不治疗，玩家死
                const result = await this.game.gameData.getWolfWantKill();
                const killedPlayer = result.wolf_want_kill;
                if (killedPlayer != -1) {
                    await this.game.gameData.kill({ player_idx: killedPlayer });
                    await this.game.someone_die(killedPlayer, "被狼人杀死");
                }
            }

            if (-1 != result.poison) {
                //不毒杀，玩家死
                await this.game.gameData.poison({ player_idx: result.poison });
                await this.game.someone_die(result.poison, "被女巫毒杀");
            }
        }
        return false;
    }
}

class EndNightAction extends Action {
    constructor(game) {
        super(game);
    }
    async do() {
        console.log("=== 天亮了 ===");
        await this.game.gameData.toggleDayNight();
        const result = await this.game.gameData.getCurrentTime();
        let death_list = "";
        for (const death of this.game.deaths) {
            death_list += `${death}号玩家死亡 \n`
        }
        if(death_list == "") {
            death_list = "今晚是平安夜"
        }
        await this.game.ui.showBigText(death_list, 2000);
        await this.game.ui.showBigText("天亮了", 2000);
        //切换到白天的背景
        await this.game.ui.hidePlayer();
        await this.game.ui.hideSpeak();
        await this.game.ui.showDayBackground();
        await this.game.ui.showDay(result.current_day);
        //重置投票结果
        await this.game.gameData.resetVoteResult();
        //重置死亡名单
        this.game.clear_deaths();
        return false;
    }
}

class EndDayAction extends Action {
    constructor(game) {
        super(game);
    }
    async do() {
        console.log("=== 天黑了，请闭眼 ===");
        await this.game.gameData.toggleDayNight();
        let death_list = "";
        for (const death of this.game.deaths) {
            death_list += `${death}号玩家死亡 \n`
        }
        if(death_list == "") {
            death_list = "无人被处决"
        }
        await this.game.ui.showBigText(death_list, 2000);
        await this.game.ui.showBigText("天黑了，请闭眼", 2000);
        await this.game.ui.hidePlayer();
        await this.game.ui.hideSpeak();
        await this.game.ui.hideAllVotes();
        //切换到夜晚的背景
        await this.game.ui.showNightBackground();
        this.game.clear_deaths();
        return false;
    }
}

class SpeakAction extends Action {
    constructor(game, player_idx) {
        super(game);
        this.player_idx = player_idx;
    }

    async do() {
        if (this.game.players[this.player_idx - 1].is_alive) {
            const result = await this.game.gameData.speak({ player_idx: this.player_idx });
            console.log(result);
            const role = this.game.show_role ? this.game.players[this.player_idx - 1].role_type : "玩家";
            await this.game.ui.showPlayer(this.player_idx);
            if (this.game.show_thinking) {
                await this.game.ui.speak(`${this.player_idx}号 ${role} 思考中：`, result.thinking, true);
            }
            await this.game.ui.speak(`${this.player_idx}号 ${role} 发言：`, result.speak);
        }
        return false;
    }
}

class VoteAction extends Action {
    constructor(game, player_idx) {
        super(game);    
        this.player_idx = player_idx;
    }

    async do() {
        if (this.game.players[this.player_idx - 1].is_alive) {
            const result = await this.game.gameData.vote({ player_idx: this.player_idx });
            console.log(result);
            const role = this.game.show_role ? this.game.players[this.player_idx - 1].role_type : "玩家";
            await this.game.ui.showPlayer(this.player_idx);
            if (this.game.show_thinking) {
                await this.game.ui.speak(`${this.player_idx}号 ${role} 思考中：`, result.thinking, true);
            }
            const vote_id = result.vote;
            if (vote_id == -1) {
                await this.game.ui.speak(`${this.player_idx}号 ${role} 投票：`, "我决定不投票！");
            } else { 
                await this.game.ui.speak(`${this.player_idx}号 ${role} 投票：`, `我决定投票投给【${vote_id}】号玩家！`);
            } 
            ///更新投票结果
            const vote_result = await this.game.gameData.getVoteResult();
            console.log(vote_result);
            
            // 遍历投票结果字典并显示
            for (const [player_idx, votes] of Object.entries(vote_result.vote_result)) {
                await this.game.ui.showVote(player_idx, votes);
            }
        }
        return false;
    }
}

class ExecuteAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        //处决接口
        const result = await this.game.gameData.execute();
        console.log(result);
        ///玩家发表遗言
        if (-1 != result.executed_player) {
            await this.game.someone_die(result.executed_player, "被投票处决");
        }
    }
}

class CheckWinnerAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        const result = await this.game.gameData.checkWinner();
        console.log(result);
        
        if (result.winner != "胜负未分") {
            this.game.ui.showBigText(result.winner, -1);
            return true;
        }
        return false;
    }
}

class Game {
    constructor(ui, show_role, show_thinking) {
        this.gameData = new GameData();
        this.players = {}
        this.ui = ui;
        this.current_action_index  = 0;
        this.deaths = []; //死亡名单
        this.show_role = show_role;
        this.show_thinking = show_thinking;
    }
    clear_deaths() {
        this.deaths = [];
    }

    async someone_die(player_idx, death_reason) {
        console.log(`被杀死的玩家是：${player_idx}`);
        this.deaths.push(player_idx);

        await this.ui.killPlayer(player_idx);
        const result = await this.gameData.getCurrentTime();
        console.log(result);
        if (1 == result.current_day || result.current_phase == "白天") {
            //如果是第一夜，允许发表遗言
            const result = await this.gameData.lastWords({ player_idx: player_idx, death_reason: death_reason });
            console.log(result);
            await this.ui.showPlayer(player_idx);
            const role = this.show_role ? this.players[player_idx - 1].role_type : "玩家";
            if (this.show_thinking) {
                await this.ui.speak(`${player_idx}号 ${role} 思考中：`, result.thinking, true);
            }
            await this.ui.speak(`${player_idx}号 ${role} 发言：`, result.speak);

            //如果是猎人，允许反击
            const  hunter = this.get_hunter();
            if (hunter.index == player_idx) {
                if (result.attack !== undefined && result.attack !== -1) {
                    await this.gameData.attack({ player_idx: player_idx, target_idx: result.attack });
                    await this.gameData.attack({ player_idx: player_idx, target_idx: result.attack });
                    console.log(`猎人发动反击，杀死了：${player_idx}号玩家`);
                } else {
                    console.log(`猎人决定不反击`);
                }
            }
        }
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        
        ///获取玩家列表
        const playersData = await this.gameData.getStatus();
        this.players = Object.values(playersData);
        console.log(this.players);

        ///设置模型logo
        const model_name = {
            "o3-mini": "gpt",
            "o3-mini-2025-01-31": "gpt",
            "deepseek-ai/DeepSeek-R1": "deepseek",
            "Pro/deepseek-ai/DeepSeek-R1": "deepseek",
            "gemini-2.0-flash-thinking-exp-01-21": "gemini",
            "qwen-max-2025-01-25":"qwen",
            "moonshot-v1-32k":"kimi",
            "glm-4-plus":"glm",
            "Baichuan4":"baichuan"
        };
        for (const player of this.players) {
            if (player.model in model_name) {
                this.ui.showModelLogo(player.index, model_name[player.model]);
            }
        }

        ///按顺序设置行动类
        this.actions = []
        this.actions.push(new DivineAction(this));
        this.actions.push(new WolfAction(this));
        this.actions.push(new WitchAction(this));
        this.actions.push(new CheckWinnerAction(this));//检查胜利
        this.actions.push(new EndNightAction(this));
        for (const player of this.players) {
            this.actions.push(new SpeakAction(this, player.index));
        }
        for (const player of this.players) {
            this.actions.push(new VoteAction(this, player.index));
        }

        ///白天最后一个环节是处决投票
        this.actions.push(new ExecuteAction(this));
        this.actions.push(new CheckWinnerAction(this));//检查胜利
        this.actions.push(new EndDayAction(this));
    }

    async run() {
        //更新玩家状态
        const playersData = await this.gameData.getStatus();
        this.players = Object.values(playersData);
        
        const action = this.actions[this.current_action_index++];
        this.current_action_index = this.current_action_index % this.actions.length;
        return await action.do();
    }

    get_diviner() {
        return this.players.find(player => player.role_type === "预言家");
    }

    get_wolves() {
        return this.players.filter(player => player.role_type === "狼人");
    }

    get_witch() {
        return this.players.find(player => player.role_type === "女巫");
    }

    get_hunter() {
        return this.players.find(player => player.role_type === "猎人");
    }
}

export default Game;
import GameData from "./data.js";
import { sleep } from "./utils.js";

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

            const response = await this.game.gameData.divine({player_idx: diviner.index});
            await this.game.ui.showPlayer(diviner.index);
            await this.game.ui.speak(`${diviner.index}号玩家 预言家 思考中：`, response.thinking);
        }
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
                await this.game.ui.speak(`${wolf.index}号玩家 狼人 思考中：`, response.reason+killWho);
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
                    await this.game.ui.speak(`${wolf.index}号玩家 狼人 思考中：`, response.reason+killWho);
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
    }
}

class WitchAction extends Action {
    constructor(game) {
        super(game);
    }

    async do() {
        const witch = this.game.get_witch();
        if (witch.is_alive) {
            console.log("== 女巫开始行动 ==");
            const result = await this.game.gameData.decideCureOrPoison({ player_idx: witch.index });
            console.log(result);
            await this.game.ui.showPlayer(witch.index);
            let cureWho = "我决定今晚不治疗！"
            if (1 == result.cure) {
                cureWho = `我决定治疗玩家！`;
            }

            let poisonWho = "我决定今晚不毒杀！"
            if (-1 != result.poison) {
                poisonWho = `我决定毒杀【${result.poison}】 号玩家！`;
            }
            await this.game.ui.speak(`${witch.index}号玩家 女巫 思考中：`, result.thinking + cureWho + poisonWho);
            //根据女巫的决策结果进行操作
            if (1 != result.cure) {
                //不治疗，玩家死
                const result = await this.game.gameData.getWolfWantKill();
                if (killedPlayer != -1) {
                    console.log(`被杀死的玩家是：${killedPlayer}`);
                    await this.game.gameData.kill({ player_idx: killedPlayer });

                    const result = await this.game.gameData.getCurrentTime();
                    console.log(result);
                    if (1 == result.current_day) {
                        //如果是第一夜，允许发表遗言
                        const result = await this.game.gameData.lastWords({ player_idx: killedPlayer, death_reason: "被狼人杀死" });
                        console.log(result);
                        await this.game.ui.showPlayer(killedPlayer);
                        await this.game.ui.speak(`${killedPlayer}号玩家思考中：`, result.thinking);
                        await this.game.ui.speak(`${killedPlayer}号玩家发言：`, result.speak);

                        //如果是猎人，允许反击
                        const  hunter = this.game.get_hunter();
                        if (hunter.index == killedPlayer) {
                            if (result.attack !== undefined && result.attack !== -1) {
                                await this.game.gameData.attack({ player_idx: killedPlayer, target_idx: result.attack });
                                console.log(`猎人发动反击，杀死了：${killedPlayer}号玩家`);
                            } else {
                                console.log(`猎人决定不反击`);
                            }
                        }
                    }
                }
            }
        }
    }
}

class Game {
    constructor(ui) {
        this.gameData = new GameData();
        this.players = {}
        this.ui = ui;
        this.current_action_index  = 0;
        this.kill_player = -1;
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        
        ///设置行动类
        this.actions = []
        this.actions.push(new DivineAction(this));
        this.actions.push(new WolfAction(this));
        this.actions.push(new WitchAction(this));
    }



    async run() {
        //更新玩家状态
        const playersData = await this.gameData.getStatus();
        this.players = Object.values(playersData);
        
        if (this.current_action_index < this.actions.length) {
            const action = this.actions[this.current_action_index++];
            await action.do();
        } else {
            console.log("没事干了")
        }
        await sleep(1000);
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
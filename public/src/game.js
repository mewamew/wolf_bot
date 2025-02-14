import GameData from "./data.js";
import Player from "./player.js";


class Game {
    constructor(ui) {
        this.gameData = new GameData();
        this.players = {}
        this.ui = ui;
    }

    async start() {
        console.log("== Start Game ==");
        const result = await this.gameData.startGame();
        console.log(result.message);
        const playersData = await this.gameData.getStatus();
        const players = Object.values(playersData);
        for (const player of players) {
            this.players[player.index] = new Player(this, player.name, player.index, player.role_type);
        }
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async run() {
        await this.sleep(1000);
    }

}

export default Game;
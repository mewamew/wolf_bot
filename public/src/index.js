import Game from "./game.js";
import Ui from "./ui.js";
import { sleep } from "./utils.js";

// Asynchronous IIFE
(async () => {
    const ui = new Ui();
    await ui.setup();
    await ui.preload();
    await ui.loadSprites();

    //await ui.showPlayer(1);
    //await ui.showHumanInput("请输入你的名字");

    
    await ui.showBigText("游戏开始", 1000);
    await ui.showBigText("天黑了，请闭眼", 2000);

    //如果不想显示角色名称，可以传 false
    const game = new Game(ui);
    await game.start();

    let is_end = false;
    while (!is_end) {
        is_end = await game.run();
    }
})();

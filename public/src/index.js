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
    let isPaused = false;

    document.addEventListener('keydown', (event) => {
        if (event.code === 'Space') {
            isPaused = !isPaused;
            if(isPaused) {
                console.log("暂停");
            } else {
                console.log("恢复");
            }
        }
    });

    while (!is_end) {
        if (!isPaused) {
            is_end = await game.run();
        } else {
            await sleep(100);
        }
    }


})();

import Game from "./game.js";
import Ui from "./ui.js";
import { sleep } from "./utils.js";

// Asynchronous IIFE
(async () => {
    const ui = new Ui();
    await ui.setup();
    await ui.preload();
    await ui.loadSprites();
    await ui.showBigText("游戏开始", 3000);


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

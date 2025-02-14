import Game from "./game.js";
import Ui from "./ui.js";

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Asynchronous IIFE
(async () => {
    const ui = new Ui();
    await ui.setup();
    await ui.preload();
    await ui.loadSprites();
    await ui.showNightBackground();
    const game = new Game(ui);
    //await game.start();

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

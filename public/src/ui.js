import { sleep } from "./utils.js";

class Ui {
    constructor() {
        this.app = new PIXI.Application();
        this.currentBg = "night"; // 新增属性，用于保存当前背景状态
        this.bg = null; // 新增属性，用于保存背景精灵
    }

    async preload()
    {
        const assets = [
            { alias: 'bg_day', src: 'assets/bg_day.png' }, //3840 x 2160
            { alias: 'bg_night', src: 'assets/bg_night.png' },
            { alias: 'bg_black', src: 'assets/bg_black.png' },
            { alias: 'chat_box', src: 'assets/chat_box.png' },
            { alias: 'status_bar', src: 'assets/status_bar.png' },
            //数字
            { alias: '1', src: 'assets/1.png' },
            { alias: '2', src: 'assets/2.png' },
            { alias: '3', src: 'assets/3.png' },
            { alias: '4', src: 'assets/4.png' },
            { alias: '5', src: 'assets/5.png' },
            { alias: '6', src: 'assets/6.png' },
            { alias: '7', src: 'assets/7.png' },
            { alias: '8', src: 'assets/8.png' },
            { alias: '9', src: 'assets/9.png' },
            //玩家编号
            { alias: 'n1', src: 'assets/n1.png' },
            { alias: 'n2', src: 'assets/n2.png' },
            { alias: 'n3', src: 'assets/n3.png' },
            { alias: 'n4', src: 'assets/n4.png' },
            { alias: 'n5', src: 'assets/n5.png' },
            { alias: 'n6', src: 'assets/n6.png' },
            { alias: 'n7', src: 'assets/n7.png' },
            { alias: 'n8', src: 'assets/n8.png' },
            { alias: 'n9', src: 'assets/n9.png' },
            //玩家大头像
            { alias: 'player_1', src: 'assets/player_1.png' },
            { alias: 'player_2', src: 'assets/player_2.png' },
            { alias: 'player_3', src: 'assets/player_3.png' },
            { alias: 'player_4', src: 'assets/player_4.png' },
            { alias: 'player_5', src: 'assets/player_5.png' },
            { alias: 'player_6', src: 'assets/player_6.png' },
            { alias: 'player_7', src: 'assets/player_7.png' },
            { alias: 'player_8', src: 'assets/player_8.png' },
            { alias: 'player_9', src: 'assets/player_9.png' },
            //玩家小头像
            { alias: 'player_1_small', src: 'assets/player_1_small.png' },
            { alias: 'player_2_small', src: 'assets/player_2_small.png' },
            { alias: 'player_3_small', src: 'assets/player_3_small.png' },
            { alias: 'player_4_small', src: 'assets/player_4_small.png' },
            { alias: 'player_5_small', src: 'assets/player_5_small.png' },
            { alias: 'player_6_small', src: 'assets/player_6_small.png' },
            { alias: 'player_7_small', src: 'assets/player_7_small.png' },
            { alias: 'player_8_small', src: 'assets/player_8_small.png' },
            { alias: 'player_9_small', src: 'assets/player_9_small.png' },
            //墓碑
            { alias: 'death', src: 'assets/death.png' },

            //模型logo
            { alias: 'logo_deepseek', src: 'assets/logo_deepseek.png' },
            { alias: 'logo_gpt', src: 'assets/logo_gpt.png' },
            { alias: 'logo_qwen', src: 'assets/logo_qwen.png' },
            { alias: 'logo_kimi', src: 'assets/logo_kimi.png' },
            { alias: 'logo_gemini', src: 'assets/logo_gemini.png' },
            { alias: 'logo_glm', src: 'assets/logo_glm.png' },
            { alias: 'logo_baichuan', src: 'assets/logo_baichuan.png' },
            { alias: 'logo_doubao', src: 'assets/logo_doubao.png' },
            { alias: 'logo_hunyuan', src: 'assets/logo_hunyuan.png' }
        ];
        await PIXI.Assets.load(assets);
    }

    async setup()
    {
        this.bgSize = this.calculateSize();
        console.log("初始化： 背景宽=", this.bgSize.width, "背景高=", this.bgSize.height)
        await this.app.init({ 
            resolution: window.devicePixelRatio || 1,  // 设置分辨率
            autoDensity: true,  // 自动调整密度
            background: '#F00000',
            width: this.bgSize.width,
            height: this.bgSize.height
        });
        document.body.appendChild(this.app.canvas);
    }

    async loadSprites() {
        this.bg_day = await this.loadSprite('bg_day', 1, false, 0, 0); //背景图
        this.bg_night = await this.loadSprite('bg_night', 1, true, 0, 0); //对话框
        this.bg_black = await this.loadSprite('bg_black', 1, false, 0, 0); //黑色底图，用来盖住整个游戏画面
        this.chat_box = await this.loadSprite('chat_box', 3, false, 1450, 150); //聊天框
        this.status_bar = await this.loadSprite('status_bar', 3, true, 0, 1710); //状态栏

        // 生成并随机打乱1到9的数组
        const playerIndices = Array.from({ length: 9 }, (_, i) => i + 1);
        playerIndices.sort(() => Math.random() - 0.5);

        // 加载玩家大头像
        this.players = [];
        for (const i of playerIndices) {
            this.players.push(await this.loadSprite(`player_${i}`, 2, false, 0, 0));
        }

        // 加载玩家小头像
        this.players_small = [];
        for (const i of playerIndices) {
            this.players_small.push(await this.loadSprite(`player_${i}_small`, 4, true, 100+(playerIndices.indexOf(i))*420, 1700, 0.7));
        }

        //加载墓碑
        this.death = []
        for (let i = 1; i <= 9; i++) {
            this.death.push(await this.loadSprite(`death`, 5, false, 100+(i-1)*420, 1700, 0.8));
        }

        //加载数字
        this.players_vote = [];
        for (let i = 1; i <= 9; i++) {
            let votes = [];
            for (let j = 1; j <= 9; j++) {
                votes.push(await this.loadSprite(`${j}`, 4, false, 100+(i-1) * 420, 1500, 0.9));
            }
            this.players_vote.push(votes);
        }

        //加载模型logo
        this.player_model_logos= [];
        for (let i = 1; i <= 9; i++) {
            let logo_map = {};
            logo_map["deepseek"] = await this.loadSprite(`logo_deepseek`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["gpt"] = await this.loadSprite(`logo_gpt`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["qwen"] = await this.loadSprite(`logo_qwen`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["kimi"] = await this.loadSprite(`logo_kimi`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["gemini"] = await this.loadSprite(`logo_gemini`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["glm"] = await this.loadSprite(`logo_glm`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["baichuan"] = await this.loadSprite(`logo_baichuan`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["doubao"] = await this.loadSprite(`logo_doubao`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            logo_map["hunyuan"] = await this.loadSprite(`logo_hunyuan`, 6, false, 240+(i-1) * 420, 1920, 0.5);
            this.player_model_logos.push(logo_map);
        }
        //加载玩家编号
        this.players_number = [];
        for (let i = 1; i <= 9; i++) {
            this.players_number.push(await this.loadSprite(`n${i}`, 7, true, 100+(i-1) * 420, 1910));
        }

        //加载文字spirit
        this.speakTextSpirit = this.initTextSpirit(5, 1600, 400, 70, 100, '#ffffff', 'left');
        this.titleTextSpirit = this.initTextSpirit(5, 1600, 200, 90, 90, '#00ffff', 'left');

        this.bg_black2 = await this.loadSprite('bg_black', 101, false, 0, 0); //黑色底图2，用来盖住整个游戏画面
        this.bigTextSpirit = this.initTextSpirit(102, 1920, 1080, 200, 200, '#ffffff', 'center');
        this.dayTextSpirit = this.initTextSpirit(102, 1920, 1080, 700, 700, '#ffffff', 'center');

        //加载角色名称
        this.playerRoleTexts = [];
        for (let i = 1; i <= 9; i++) {
            const role_text = await this.initTextSpirit(6, 180+(i-1) * 420, 2050, 64, 64, '#ffffff', 'left');
            role_text.visible = false;
            this.playerRoleTexts.push(role_text);
        }

        //显示当前第几天
        this.littleDayTextSpirit = await this.initTextSpirit(6, 200, 100, 64, 64, '#ffffff', 'center');
        this.littleDayTextSpirit.visible = true;
        this.littleDayTextSpirit.text = "第1天";

        //创建人类输入控件
        await this.createHumanInputContainer();
    }

    async createHumanInputContainer() {
        // 添加人类玩家输入界面
        this.humanInputContainer = new PIXI.Container();
        this.humanInputContainer.zIndex = 300;  // 确保显示在最上层
        
        // 创建HTML输入框
        const input = document.createElement('textarea');
        input.style.position = 'absolute';
        
        // 原始画布尺寸
        const originalWidth = 3840;
        const originalHeight = 2160;
        
        // 输入框原始尺寸
        const originalInputWidth = 2000;
        const originalInputHeight = 500;
        
        // 计算缩放比例
        const scaleX = this.bgSize.width / originalWidth;
        const scaleY = this.bgSize.height / originalHeight;
        
        // 计算居中位置和缩放后的尺寸
        const scaledWidth = originalInputWidth * scaleX;
        const scaledHeight = originalInputHeight * scaleY;
        const left = (this.bgSize.width - scaledWidth*0.7) / 2;
        const top = (this.bgSize.height - scaledHeight*0.8) / 2;
        
        input.style.left = `${left}px`;
        input.style.top = `${top}px`;
        input.style.width = `${scaledWidth}px`;
        input.style.height = `${scaledHeight}px`;
        input.style.fontSize = `${64 * scaleY}px`;
        input.style.fontFamily = '钉钉进步体';
        input.style.padding = `${10 * scaleY}px`;
        input.style.display = 'none';
        input.style.resize = 'none';
        document.body.appendChild(input);
        this.humanInput = input;
        
    }

    async showHumanInput(prompt) {
        return new Promise((resolve) => {
            this.humanInputContainer.visible = true;
            this.humanInput.style.display = 'block';
            this.humanInput.value = '';
            this.humanInput.focus();
            this.humanInput.placeholder = prompt;
            
            const onConfirm = () => {
                const text = this.humanInput.value.trim();
                if (text) {
                    this.humanInputContainer.visible = false;
                    this.humanInput.style.display = 'none';
                    resolve(text);
                }
            };

            // 添加Enter键确认
            this.humanInput.onkeypress = (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    onConfirm();
                }
            };
        });
    }
    
    hideHumanInput() {
        this.humanInputContainer.visible = false;
        this.humanInput.style.display = 'none';
    }

    async showDay(day) {
        this.dayTextSpirit.text = `第${day}天`;
        this.dayTextSpirit.visible = true;
        await sleep(3000);
        this.dayTextSpirit.visible = false;
        this.littleDayTextSpirit.text= `第${day}天`;
    }

    async showRoleText(player_index, role) {
        this.playerRoleTexts[player_index-1].text = role;
        this.playerRoleTexts[player_index-1].visible = true;
    }

    async showModelLogo(player_index, model_name) {
        console.log("显示模型logo", player_index, model_name);
        this.player_model_logos[player_index-1][model_name].visible = true;
    }

    async showBigText(text, displayTime) {
        this.bigTextSpirit.text = text;
        this.bigTextSpirit.visible = true;
        this.bg_black2.visible = true;
        if (displayTime == -1) {
            return;
        }
        await sleep(displayTime);
        this.bigTextSpirit.visible = false;
        this.bg_black2.visible = false;
    }

    //显示说话内容
    async speak(title,  is_auto_play,text, is_dark_bg=false) {
        const lines = this.formatText(text);
        //console.log("说话内容：");
        //console.log(lines);

        this.titleTextSpirit.text = title;
        this.titleTextSpirit.visible = true;

        this.speakTextSpirit.text = "";
        this.speakTextSpirit.visible = true;
        this.chat_box.visible = true;
        
        // 保存当前背景状态
        const prevBg = this.currentBg;
        
        if (is_dark_bg) {
            this.showDarkBackground();
        }

        const groupSize = 9;
        for (let group = 0; group < Math.ceil(lines.length / groupSize); group++) {
            const start = group * groupSize;
            const end = start + groupSize;
            const currentLines = lines.slice(start, end);
            if (!is_auto_play) {
                currentLines.push("<按回车键继续>")
            }
            //console.log("---分组说话：----");
            //console.log(currentLines);

            this.speakTextSpirit.text = "";
            await this.typeWriterEffect(currentLines.join('\n'), this.speakTextSpirit);
            
            if (is_auto_play) {
                await sleep(100);
                // 等待用户按回车键继续
            } else {
                await new Promise(resolve => {
                    const keyHandler = (e) => {
                        if (e.key === 'Enter') {
                            document.removeEventListener('keypress', keyHandler);
                            resolve();
                        }
                    };
                    document.addEventListener('keypress', keyHandler);
                });
            }
        }
        //停留1秒
        await sleep(2000);
        await this.hideSpeak();
        // 恢复背景
        if (prevBg === 'day') {
            this.showDayBackground();
        } else if (prevBg === 'night') {

            this.showNightBackground();
        }
    }

    async hideSpeak() {
        this.chat_box.visible = false;
        this.titleTextSpirit.visible = false;
        this.speakTextSpirit.visible = false;
    }
    
    //在指定的玩家头顶显示投票
    async showVote(player_index, number) {
        for (let i = 0; i < this.players_vote[player_index-1].length; i++) {
            this.players_vote[player_index-1][i].visible = false;
        }
        this.players_vote[player_index-1][number-1].visible = true;
    }

    async killPlayer(player_index) {
        this.death[player_index-1].visible = true;
    }

    //隐藏所有投票
    async hideAllVotes() {
        for (let i = 0; i < this.players_vote.length; i++) {
            for (let j = 0; j < this.players_vote[i].length; j++) {
                this.players_vote[i][j].visible = false;
            }
        }
    }

    async showPlayer(player_index) {
        for (let i = 0; i < this.players.length; i++) {
            this.players[i].visible = false;
        }
        this.players[player_index-1].alpha = 0;
        this.players[player_index-1].visible = true;
        //渐现
        for (let i = 0; i < 100; i++) {
            this.players[player_index-1].alpha += 0.01;
            await sleep(5);
        }
    }

    async hidePlayer() {
        for (let i = 0; i < this.players.length; i++) {
            this.players[i].visible = false;
        }
    }


    async showDayBackground() {
        this.bg_day.visible = true;
        this.bg_night.visible = false;
        this.bg_black.visible = false;
        this.bg.tint = 0xFFFFFF; // 恢复白天背景色
        this.currentBg = 'day';
    }

    async showNightBackground() {
        this.bg_day.visible = false;
        this.bg_night.visible = true;
        this.bg_black.visible = false;
        this.bg.tint = 0x666666; // 暗色背景
        this.currentBg = 'night';
    }

    async showDarkBackground() {
        this.bg_day.visible = false;
        this.bg_night.visible = false;
        this.bg_black.visible = true;
        this.bg.tint = 0x333333; // 更暗的对话背景
        this.currentBg = 'dark';
    }

    async loadSprite(sprite_name, zIndex, visible, x, y, scale=1.0) {
        console.log("loadSprite ", sprite_name);
        let sprite = PIXI.Sprite.from(sprite_name);
        sprite.width *= this.bgSize.scale * scale;
        sprite.height *= this.bgSize.scale * scale;
        sprite.visible = visible;//默认不显示
        sprite.zIndex = zIndex;
        sprite.x = x * this.bgSize.scale;
        sprite.y = y * this.bgSize.scale;
        this.app.stage.addChild(sprite);
        if (sprite_name === 'bg_day') {
            this.bg = sprite;
        }
        return sprite;
    }

    calculateSize() {
        const targetRatio = 3840 / 2160;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const windowRatio = windowWidth / windowHeight;
        let width, height, scale;
        if (windowRatio > targetRatio) {
            // 窗口太宽，以高度为基准
            height = windowHeight;
            width = height * targetRatio;
        } else {
            // 窗口太高，以宽度为基准
            width = windowWidth;
            height = width / targetRatio;
        }
        scale = width / 3840;
        return { width, height, scale };
    }

    initTextSpirit(zIndex, x, y, fontSize, lineHeight, color, align = 'left', strokeEnabled = true, need_scale=true) {
        if (need_scale) {
            fontSize *= this.bgSize.scale;
            lineHeight *= this.bgSize.scale;
        }
        const textStyle = new PIXI.TextStyle({
            fontFamily: '钉钉进步体',
            fontSize: fontSize,
            fill: color,
            lineHeight: lineHeight,
            stroke: strokeEnabled ? { color: '#000000', width: 2*this.bgSize.scale } : undefined
        });
        const textSpirit = new PIXI.Text({text:"", style:textStyle});
        if (align === 'center') {
            textSpirit.anchor.set(0.5, 0.5);
        }
        if (need_scale) {
            textSpirit.x = x * this.bgSize.scale;
            textSpirit.y = y * this.bgSize.scale;
        } else {
            textSpirit.x = x;
            textSpirit.y = y;
        }
        textSpirit.zIndex = zIndex;
        textSpirit.visible = true;
        this.app.stage.addChild(textSpirit);
        return textSpirit;
    }

    async typeWriterEffect(formattedText, textSpirit) {
        const interval = 10; // 每个字符显示的间隔时间，单位为毫秒
        let currentIndex = 0;
        textSpirit.text = "";
        textSpirit.visible = true;
        return new Promise((resolve) => {
            const typeWriter = () => {
                if (currentIndex < formattedText.length) {
                    textSpirit.text += formattedText[currentIndex];
                    currentIndex++;
                    setTimeout(typeWriter, interval);
                } else {
                    resolve();
                }
            };
            typeWriter();
        });
    }

    formatText(what) {
        // 按标点符号分割字符串，并在每个标点后添加换行符
        let formattedText = what.replace(/([。！？，,]|\.{3})/g, '$1\n');
        
        // 合并短行，确保每行不超过20个字
        let lines = formattedText.split('\n').filter(line => line.trim());
        let result = [];
        lines.forEach(line => {
            while (line.length > 24) {
                result.push(line.substring(0, 20));
                line = line.substring(20);
            }
            result.push(line);
        });
        return result;
    }


}

export default Ui;
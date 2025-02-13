export const LAYOUT = {
    // 基础布局配置
    BASE_WIDTH: 1800,
    BASE_HEIGHT: 900,
    
    // 主角色精灵位置
    MAIN_SPIRIT: {
        x: 0,
        y: 450
    },
    
    // 小精灵布局
    SMALL_SPIRIT: {
        START_X: 520,
        Y: 200,
        SPACING: 192, // 152 + 40 (原始间距)
    },
    
    // 标题文本
    TITLE_TEXT: {
        OFFSET_X: 560,
        Y: 360,
        FONT_SIZE: 30
    },
    
    // 投票文本
    VOTE_TEXT: {
        FONT_SIZE: 48
    }
};

// 文本样式配置
export const TEXT_STYLES = {
    TITLE: {
        fontFamily: '钉钉进步体',
        fill: '#ffffff',
        strokeThickness: 2,
        stroke: '#000000'
    },
    VOTE: {
        fontFamily: 'Arial',
        fill: '#ff0000',
        strokeThickness: 2,
        stroke: '#000000'
    }
};

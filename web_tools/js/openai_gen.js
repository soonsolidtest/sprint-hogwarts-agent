function getElements() {
    // 获取所有常用的元素
    const importantTags = ['button', 'input', 'textarea', 'select', 'form', 'a', 'img'];

    // 定义需要过滤的无用元素选择器（如广告、弹窗等）
    const uselessSelectors = [
        '.ads', // 广告
        '.popup', // 弹窗
        '.footer', // 页脚
        '.header', // 页头
        '.sidebar', // 侧边栏
        '.cookie-banner', // Cookie 提示条
        '.social-links', // 社交媒体链接
        'script', // 删除所有脚本标签
        'style'  // 删除所有样式标签
    ];

    // 定义不需要的属性（比如事件处理属性）
    const unnecessaryAttributes = ['style', 'onclick', 'onload', 'onerror'];

    // 获取页面所有元素
    function getFilteredDom() {
        const allElements = document.querySelectorAll('*');
        let domString = '';

        allElements.forEach(element => {
            const tagName = element.tagName.toLowerCase();

            // 如果是常用的测试元素，保留并转换为字符串
            if (importantTags.includes(tagName)) {
                domString += `<${tagName}${getAttributes(element)}>${element.innerHTML}</${tagName}>`;
            }
            // 处理空的div/span等元素
            else if ((tagName === 'div' || tagName === 'span') && !element.innerHTML.trim()) {
                domString += `<${tagName}${getAttributes(element)}></${tagName}>`;
            }
            // 忽略不可见或尺寸过小的元素
            else if (isVisibleAndLargeEnough(element)) {
                domString += `<${tagName}${getAttributes(element)}>${element.innerHTML}</${tagName}>`;
            }
        });

        return domString;
    }

    // 获取元素的属性（用于生成结构字符串）
    function getAttributes(element) {
        let attributesString = '';

        // 获取元素所有属性
        Array.from(element.attributes).forEach(attr => {
            // 过滤不需要的属性
            if (!unnecessaryAttributes.includes(attr.name)) {
                attributesString += ` ${attr.name}="${attr.value}"`;
            }
        });

        return attributesString;
    }

    // 判断元素是否可见且尺寸足够大
    function isVisibleAndLargeEnough(element) {
        const style = window.getComputedStyle(element);
        const width = parseInt(style.width);
        const height = parseInt(style.height);
        const display = style.display;
        const visibility = style.visibility;

        // 判断元素是否可见
        const isVisible = display !== 'none' && visibility !== 'hidden' && width > 0 && height > 0;

        // 判断元素尺寸是否足够大（比如宽度和高度都大于10px）
        const isLargeEnough = width > 10 && height > 10;

        return isVisible && isLargeEnough;
    }

    // 生成缩略版DOM结构的字符串
    const cleanedDomString = getFilteredDom();

    // 返回页面结构字符串
    console.log("页面结构字符串：", cleanedDomString);

    return cleanedDomString;
}
return getElements();

function filterLargeElementsOnly() {
    // 检查元素的宽高是否大于 10px
    function isLargeEnough(element) {
        const style = window.getComputedStyle(element);
        const width = parseFloat(style.width);
        const height = parseFloat(style.height);
        return width > 10 && height > 10;
    }

    // 递归地复制符合条件的元素
    function copyLargeElements(element) {
        // 如果当前元素不符合尺寸要求，返回 null
        if (!isLargeEnough(element)) return null;

        // 创建当前元素的克隆，并不复制其子节点
        const clone = element.cloneNode(false);

        // 遍历子节点，并递归添加符合条件的子元素
        element.childNodes.forEach(child => {
            if (child.nodeType === Node.ELEMENT_NODE) {
                const childClone = copyLargeElements(child);
                if (childClone) {
                    clone.appendChild(childClone);
                }
            } else if (child.nodeType === Node.TEXT_NODE) {
                // 保留文本节点
                clone.appendChild(child.cloneNode(true));
            }
        });

        return clone;
    }

    // 获取 <body> 标签并过滤元素
    const bodyClone = copyLargeElements(document.body);

    // 创建一个新的 HTML 文档结构来包含过滤后的内容
    const newDoc = document.implementation.createHTMLDocument("Filtered Document");
    newDoc.body.appendChild(bodyClone);

    // 使用示例
    // 返回新的 HTML 文档结构
    content= newDoc.documentElement.outerHTML;
    return content;
}
const filteredHtml = filterLargeElementsOnly();
console.log(filteredHtml);
return filteredHtml;
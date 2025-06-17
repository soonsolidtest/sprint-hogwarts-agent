function getElements(){
  // 获取页面的 body 内容
  const body = document.body;

  // 克隆 body，确保不影响原始 DOM
  const bodyClone = body.cloneNode(true);

  // 获取 body 中的所有子元素
  const allElements = bodyClone.querySelectorAll('*');

  // 定义交互元素的标签列表
  const interactiveTags = ['A', 'BUTTON', 'INPUT', 'TEXTAREA', 'SELECT', 'FORM', 'LABEL', 'DETAILS', 'SUMMARY', 'VIDEO', 'AUDIO'];

  // 遍历所有元素
  allElements.forEach(element => {
    // 判断是否是可交互的元素
    const isInteractive = interactiveTags.includes(element.tagName);

    // 删除不需要的自定义标签或隐藏元素
    if (!isInteractive) {
      // 删除 <script>、<style>、<meta>、<link> 等标签
      if (['SCRIPT', 'STYLE', 'META', 'LINK', 'NOSCRIPT'].includes(element.tagName)) {
        element.remove();
      }
      // 删除自定义的无关标签，例如 <discourse-assets> 和其他不必要的组件
      else if (element.tagName.startsWith('DISCOURSE') || element.classList.contains('hidden') || element.hasAttribute('hidden')) {
        element.remove();
      }
//      // 获取 z-index 样式并添加到元素中
//      const zIndex = window.getComputedStyle(element).zIndex;
//      // 如果 z-index 存在并且不为 'auto'，将其作为属性存储
//      if (zIndex !== 'auto') {
//      element.setAttribute('data-z-index', zIndex);
//    }
    }
  });

   // 获取过滤后的 HTML 内容
  let filteredHTML = bodyClone.innerHTML;

  // 删除多余的换行和空格
  filteredHTML = filteredHTML
    .replace(/\n+/g, ' ')       // 删除多余的换行
    .replace(/\s{2,}/g, ' ')     // 删除连续多个空格
    .replace(/^\s+|\s+$/g, '');  // 删除开头和结尾的空格

  // 返回过滤并清理后的 HTML 内容
  return filteredHTML;

  // 返回过滤后的 HTML 内容，确保交互元素的属性也被保留
  return bodyClone.innerHTML;
};
return getElements();
(() => {
    function recur(node, depth) {
        if (node.nodeType === Node.ELEMENT_NODE) {
            let style = window.getComputedStyle(node)
            let isVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && node.offsetHeight > 2 && node.offsetWidth > 2

            let element = {
                uid: node.id,
                tag: node.tagName.toLowerCase(),
                text: null,
                visible: isVisible,
                attribute_dict: {},
                events: [],
                items: []
            }

            if (node.id) {
                element.attribute_dict['id'] = node.id
            }

            if (isVisible) {
                for (let attr of node.attributes) {
                    element.attribute_dict[attr.name] = attr.value
                }


                for (let name in node) {
                    if (name.startsWith('on')) {
                        let event = name.substring(2)
                        if (node[event]) {
                            element.events.push(event)
                        }
                    }
                }
            }

            if (node.children.length === 0) {
                element.text = node.textContent
            }

            for (let child of node.children) {
                let element_child = recur(child, depth + 1)
                if (element_child && element_child.visible) {
                    element.items.push(element_child)
                    //可见的元素可能有不可见的父级
                    element.visible = element_child.visible
                } else {

                }
            }
            if (element.visible) {
                return element
            } else {

            }

        } else {
            console.log('no element')
            console.log(node)
        }
    }

    element = recur(document.body, 0)
    content = JSON.stringify(element)
    return content
})()

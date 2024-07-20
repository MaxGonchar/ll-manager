const leftSightSymbols =  ".,:;!?"

const isLetter = function (str) {
    return str.length === 1 && str.match(/[a-z]/i);
}

export {isLetter, leftSightSymbols}
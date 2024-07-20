import { Template } from "./template.js";
import { isLetter, leftSightSymbols } from "./utils.js";

let hint = false

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

const renderExpression = function(symbols, notShow) {
    const expression_input = document.querySelector(".expression-input-template")
    removeAllChildNodes(expression_input)
    for (const symbol of symbols) {
            const box = document.createElement('div')
            
            if (symbol === notShow) {
                box.classList.add('letter-box')
                box.textContent = ""
            } else {
                box.classList.add("non-letter-box")
                if (leftSightSymbols.includes(symbol)) box.style.setProperty("text-align", "left")
                box.textContent = symbol
        }
        
        expression_input.appendChild(box)
    }
}

const handleKeyPress = function(event) {
    if (event.defaultPrevented) {
        return; // Do nothing if the event was already processed
    }
    
    const symbol = event.key
    
    if (isLetter(symbol)) {
        template.addLetter(symbol);
    } else if (symbol === "Backspace") {
        template.deleteLetter();
    } else if (symbol === "Enter") {
        doSubmit()
    } else {
        return; // Quit when this doesn't handle the key event.
    }
    
    renderExpression(template.placeHolders, template.placeholder)
    
    // Cancel the default action to avoid it being handled twice
    event.preventDefault();
};

const doSubmit = function() {
    if (!template.canBeSubmitted()) return
    
    const form = document.createElement("form")
    document.body.appendChild(form)
    form.action = action
    form.method = "post"
    form.hidden = true
    
    const expressionIdInput = document.createElement("input")
    expressionIdInput.name = "expression_id"
    expressionIdInput.value = challenge.expression_id
    form.appendChild(expressionIdInput)
    
    const answerInput = document.createElement("input")
    answerInput.name = "answer"
    answerInput.value = template.toString()
    form.appendChild(answerInput)
    
    const hintInput = document.createElement("input")
    hintInput.name = "hint"
    hintInput.value = hint
    form.appendChild(hintInput)
    
    form.submit()
}

const doHint = function() {
    // hint already rendered
    if (document.querySelector(".tip")) return
    
    const article = document.querySelector(".daily-training")
    const tip = document.createElement("div")
    tip.classList.add("tip")
    tip.innerHTML = `<p>${challenge.tip}<p/>`
    const inputTemplate = document.querySelector(".expression-input-template")
    article.insertBefore(tip, inputTemplate)
    hint = true
}

const template = new Template(challenge.answer);

renderExpression(template.placeHolders, template.placeholder)

window.addEventListener("keydown", handleKeyPress, true);
document.getElementById('button-hint').addEventListener('click', doHint);
document.getElementById('button-submit').addEventListener('click', doSubmit);

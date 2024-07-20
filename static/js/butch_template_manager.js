import { Template } from "./template.js";
import { isLetter } from "./utils.js";

let hint = false;

const tpl = challenge.tpl;
const values = challenge.values;

class Templates {
    constructor(templates) {
        if (templates.length === 0) throw new Error("Can't init Template class with an empty array");

        this.templates = templates;
        this.currentIndex = 0;
    }

    get current() {
        return this.templates[this.currentIndex];
    }

    get previous() {
        this.currentIndex = this.currentIndex === 0 ? 0 : this.currentIndex - 1;
        return this.current;
    }

    get next() {
        this.currentIndex = this.currentIndex === (this.templates.length - 1) ? this.currentIndex : this.currentIndex + 1;
        return this.current;
    }

    get all() {
        return this.templates
    }
}

const templates = values.map(value => new Template(value));

class ButchTemplateManager {
    // is initialized with an array of Template instances
    constructor(templates) {
        this.templates = new Templates(templates);
        this.target = this.templates.current;
    }

    addLetter(letter) {
        if (this.target.isFilled) this.target = this.templates.next;
        this.target.addLetter(letter)
    }

    deleteLetter() {
        if (this.target.isEmpty) this.target = this.templates.previous;
        this.target.deleteLetter()
    }

    canBeSubmitted() {
        return this.templates.all.every(item => item.canBeSubmitted())
    }
}

const manager = new ButchTemplateManager(templates);

const renderTemplate = function(symbols, notShown) {
    const element = document.createElement("span");
    element.classList.add('sentence-train--word-box')
    let content = "";
    for (const symbol of symbols) {
        if (symbol === notShown) {
            content += "_"
        } else {
            content += symbol
        }
    }
    element.textContent = content
    return element.outerHTML
}

const renderSentence = function(sentenceTemplate, templates) {
    const box = document.querySelector('.box');
    let boxTextContent = sentenceTemplate;

    for (const tpl of templates) {
        boxTextContent = boxTextContent.replace("{}", renderTemplate(tpl.placeHolders, tpl.placeholder));
    }

    box.innerHTML = boxTextContent;
}

const sentenceToString = function(tpl, placeholder_values) {
    let rez = tpl;
    for (const value of placeholder_values) {
        rez = rez.replace('{}', value);
    };

    return rez;
}

const doSubmit = function() {
    if (!manager.canBeSubmitted()) return
    
    const form = document.createElement("form")
    document.body.appendChild(form)
    form.action = action
    form.method = "post"
    form.hidden = true
    
    const expressionIdInput = document.createElement("input")
    expressionIdInput.name = "expression_id"
    expressionIdInput.value = challenge.expression_id
    form.appendChild(expressionIdInput)

    const contextIdInput = document.createElement('input');
    contextIdInput.name = "context_id";
    contextIdInput.value = challenge.context_id;
    form.appendChild(contextIdInput);
    
    const answerInput = document.createElement("input")
    answerInput.name = "answer"
    answerInput.value = sentenceToString(tpl, templates.map(item => item.toString()))
    form.appendChild(answerInput)
    
    const hintInput = document.createElement("input")
    hintInput.name = "hint"
    hintInput.value = hint
    form.appendChild(hintInput)
    
    form.submit()
}

const handleKeyPress = function(event) {
    if (event.defaultPrevented) {
        return; // Do nothing if the event was already processed
    }
    
    const symbol = event.key
    
    if (isLetter(symbol)) {
        manager.addLetter(symbol);
    } else if (symbol === "Backspace") {
        manager.deleteLetter();
    } else if (symbol === "Enter") {
        doSubmit()
    } else {
        return; // Quit when this doesn't handle the key event.
    }
    
    renderSentence(challenge.tpl, templates)
    
    // Cancel the default action to avoid it being handled twice
    event.preventDefault();
};

const doHint = function() {
    if (hint) return;

    document.getElementById('sentence-training--hint').style = "";
    hint = true
};

renderSentence(challenge.tpl, templates);
window.addEventListener("keydown", handleKeyPress, true);
document.getElementById('button-hint').addEventListener('click', doHint);
document.getElementById('button-submit').addEventListener('click', doSubmit);

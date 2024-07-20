import { isLetter, leftSightSymbols } from "./utils.js";

function renderAnswers(usersAnswer, correctAnswer) {
    const usersAnswerContainer = document.querySelector('.user-answer');
    const correctAnswerContainer = document.querySelector('.correct-answer')

    const usersAnswerList = [...usersAnswer];
    const correctAnswerList = [...correctAnswer];

    const zippedSymbols = usersAnswerList.map(function(e, i) {return [e, correctAnswerList[i]]});

    for (const [userSymbol, correctSymbol] of zippedSymbols) {
        const userLetterBox = document.createElement('div');
        const correctLetterBox = document.createElement('div');

        correctLetterBox.classList.add('message-success')

        if (userSymbol.toLowerCase() === correctSymbol.toLowerCase()) {
            userLetterBox.classList.add('message-success')
        } else {
            userLetterBox.classList.add('message-error')
        }

        fillLetterBox(userLetterBox, userSymbol);
        fillLetterBox(correctLetterBox, correctSymbol);

        usersAnswerContainer.appendChild(userLetterBox);
        correctAnswerContainer.appendChild(correctLetterBox);
    };
};

function fillLetterBox(box, symbol) {
    if (isLetter(symbol)) {
        box.classList.add('letter-box');
    } else {
        box.classList.add('non-letter-box');
        if (leftSightSymbols.includes(symbol)) box.style.setProperty("text-align", "left");
    };

    box.textContent = symbol;
};

renderAnswers(usersAnswer, correctAnswer)
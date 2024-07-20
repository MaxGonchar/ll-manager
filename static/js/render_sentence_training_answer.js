// const userAnswer = "The quick brown fox jumps over the lazy dog";
// const correctAnswer = "The quick brown fox pumps over the lazy dog";

function renderAnswers(usersAnswer, correctAnswer) {
    const correctAnswerContainer = document.querySelector('.correct-answer');
    correctAnswerContainer.classList.add('message-success');

    const usersAnswerContainer = document.querySelector('.user-answer');
    usersAnswerContainer.classList.add('message-success');

    const usersAnswerList = [...usersAnswer];
    const correctAnswerList = [...correctAnswer];

    for (let i = 0; i < correctAnswerList.length; i++) {
        if (usersAnswerList[i] !== correctAnswerList[i]) {
            usersAnswerList[i] = `<span style="color: red;">${usersAnswerList[i]}</span>`
        }
    }

    correctAnswerContainer.textContent = correctAnswerList.join('');
    usersAnswerContainer.innerHTML = usersAnswerList.join('');
};

renderAnswers(userAnswer, correctAnswer)

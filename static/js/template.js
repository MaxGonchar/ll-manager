import { isLetter } from "./utils.js";


export class Template {
    constructor(initString) {
        this.placeholder = "<>";
        this.placeHolders = [];
        this.letterIndexes = [];
        this.letters = [];
        this.maxLetters = 0;

        this.#buildPlaceHolders(initString);
    }

    #buildPlaceHolders(initString) {
        for (let i = 0; i < initString.length; i++) {
            if (isLetter(initString[i])) {
                this.placeHolders.push(this.placeholder);
                this.maxLetters += 1;
                this.letterIndexes.push(i);
            } else {
                this.placeHolders.push(initString[i]);
            };
        };
    }

    addLetter(letter) {
        if (this.letters.length < this.maxLetters) {
            this.letters.push(letter);
            this.placeHolders[this.letterIndexes[this.letters.length - 1]] = letter;
        };
    }

    deleteLetter() {
        if (this.letters.length > 0) {
            this.placeHolders[this.letterIndexes[this.letters.length - 1]] = this.placeholder;
            this.letters.pop();
        };
    }

    toString() {
        if (this.letters.length === this.maxLetters) {
            return this.placeHolders.join("");
        }
    }

    canBeSubmitted() {
        return this.letters.length === this.maxLetters;
    }

    get isFilled() {
        return this.letters.length === this.maxLetters;
    }

    get isEmpty() {
        return this.letters.length === 0;
    }
}

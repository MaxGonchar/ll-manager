'use strict';

const tipBox = document.getElementById('daily-training-settings-tips');
const tipBoxP = tipBox.children[0];

const showDailyTrainingSettingsTip = function(text) {
    tipBox.style.opacity = 1;
    tipBoxP.textContent = text;
};

const hideDailyTrainingSettingsTip = function() {
    tipBox.style.opacity = 0;
    tipBoxP.textContent = "";
};

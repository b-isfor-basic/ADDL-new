const awayName0 = document.querySelector("#id_away_0_player");
const awayName1 = document.querySelector("#id_away_1_player");
const homeName0 = document.querySelector("#id_home_0_player");
const homeName1 = document.querySelector("#id_home_1_player");

const awayOutput1 = document.getElementById("#away_1_player");
const homeOutput0 = document.getElementById("#home_0_player");
const homeOutput1 = document.getElementById("#home_1_player");


awayName0.addEventListener(
    'change', (event) => {
        const awayOutput0 = document.querySelectorAll("#away_0_player");
        awayOutput0.forEach(element => {
            element.textContent = event.target.value
        })
    }
);
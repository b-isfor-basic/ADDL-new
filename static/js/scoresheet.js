const awayName0 = document.getElementById("id_away-0-player");
const awayName1 = document.getElementById("id_away-1-player");
const homeName0 = document.getElementById("id_home-0-player");
const homeName1 = document.getElementById("id_home-1-player");

awayName0.addEventListener('change', (event) => {
    const text = awayName0.options[awayName0.selectedIndex].text;
    const output = document.getElementsByName("away_0_player");
    output.forEach(line => {
        line.innerHTML = text
    })
});

awayName1.addEventListener('change', (event) => {
    const text = awayName1.options[awayName1.selectedIndex].text;
    const output = document.getElementsByName("away_1_player");
    output.forEach(line => {
        line.innerHTML = text
    })
});

homeName0.addEventListener('change', (event) => {
    const text = homeName0.options[homeName0.selectedIndex].text;
    const output = document.getElementsByName("home_0_player");
    output.forEach(line => {
        line.innerHTML = text
    })
});

homeName1.addEventListener('change', (event) => {
    const text = homeName1.options[homeName1.selectedIndex].text;
    const output = document.getElementsByName("home_1_player");
    output.forEach(line => {
        line.innerHTML = text
    })
});

const reAway0 = /away_0/;
let away0Stars = 0;
let away0Perfects = 0;
let away0Points = 0;

const reAway1 = /away_1/;
let away1Stars = 0;
let away1Perfects = 0;
let away1Points = 0;

const reHome0 = /home_0/;
let home0Stars = 0;
let home0Perfects = 0;
let home0Points = 0;

const reHome1 = /home_1/;
let home1Stars = 0;
let home1Perfects = 0;
let home1Points = 0;


const stars = document.querySelectorAll(`[id$="stars"]`);
stars.forEach(i => {
    i.addEventListener('', e => {
        if (i.id.match(reAway0)) {
            away0Stars += parseInt(e.target.value);
            return console.log('Away 0 stars updated. New total = ' + away0Stars);
        } else if (i.id.match());
    });
})
console.log(stars)


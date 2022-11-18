const awayName0 = document.getElementById("id_away-0-player");
const awayName1 = document.getElementById("id_away-1-player");
const homeName0 = document.getElementById("id_home-0-player");
const homeName1 = document.getElementById("id_home-1-player");

awayName0.addEventListener('focusout', (event) => {
    const text = awayName0.input.text;
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



const a0StarsID = "input[id$='stars'][id^='id_away_0']";
const a0TotalStars = "span[id='#a0TotalStars']";
const a1StarsID = "input[id$='stars'][id^='id_away_1']";
const a1TotalStars = "span[id='#a1TotalStars']";
const h0StarsID = "input[id$='stars'][id^='id_home_0']";
const h0TotalStars = "span[id='#h0TotalStars']";
const h1StarsID = "input[id$='stars'][id^='id_home_1']";
const h1TotalStars = "span[id='#h1TotalStars']";

const a0PerfectsID = "input[id$='perfects'][id^='id_away_0']";
const a0TotalPerfects = "span[id='#a0TotalPerfects']";
const a1PerfectsID = "input[id$='perfects'][id^='id_away_1']";
const a1TotalPerfects = "span[id='#a1TotalPerfects']";
const h0PerfectsID = "input[id$='perfects'][id^='id_home_0']";
const h0TotalPerfects = "span[id='#h0TotalPerfects']";
const h1PerfectsID = "input[id$='perfects'][id^='id_home_1']";
const h1TotalPerfects = "span[id='#h1TotalPerfects']";

const a0PointsID = "input[id$='point'][id^='id_away_0']";
const a0TotalPoints = "span[id='#a0TotalPoints']";
const a1PointsID = "input[id$='point'][id^='id_away_1']";
const a1TotalPoints = "span[id='#a1TotalPoints']";
const h0PointsID = "input[id$='point'][id^='id_home_0']";
const h0TotalPoints = "span[id='#h0TotalPoints']";
const h1PointsID = "input[id$='point'][id^='id_home_1']";
const h1TotalPoints = "span[id='#h1TotalPoints']";

const statList = [a0StarsID, a1StarsID, h0StarsID, h1StarsID, a0PerfectsID, a1PerfectsID, h0PerfectsID, h1PerfectsID, a0PointsID, a1PointsID, h0PointsID, h1PointsID];
const totalList = [a0TotalStars, a1TotalStars, h0TotalStars, h1TotalStars, a0TotalPerfects, a1TotalPerfects, h0TotalPerfects, h1TotalPerfects, a0TotalPoints, a1TotalPoints, h0TotalPoints, h1TotalPoints];

$(function () {
    // load totals on page load
    LoadRunningTotals();

    // load totals on change
    $(statList).each(function () {
        $(this).on("focusout", function () {
            LoadRunningTotals($(this), totalList[$(this).index]);
        });
    });
});

// running total function
function LoadRunningTotals(selector, target) {
    var total = 0;
    $(selector).each(function () {
        var value = $(this).val();
        if (!isNaN(value) && value.length != 0) {
            total += Number.parseInt(value, 10);
        }
    });
    $(target).html(total);
}

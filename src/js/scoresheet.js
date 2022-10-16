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

let a0StarsID = "input[id$='stars'][id^='id_away_0']";
let a0TotalStars = "span[id='#a0TotalStars']";
let a1StarsID = "input[id$='stars'][id^='id_away_1']";
let a1TotalStars = "span[id='#a1TotalStars']";
let h0StarsID = "input[id$='stars'][id^='id_home_0']";
let h0TotalStars = "span[id='#h0TotalStars']";
let h1StarsID = "input[id$='stars'][id^='id_home_1']";
let h1TotalStars = "span[id='#h1TotalStars']";

let a0PerfectsID = "input[id$='perfects'][id^='id_away_0']";
let a0TotalPerfects = "span[id='#a0TotalPerfects']";
let a1PerfectsID = "input[id$='perfects'][id^='id_away_1']";
let a1TotalPerfects = "span[id='#a1TotalPerfects']";
let h0PerfectsID = "input[id$='perfects'][id^='id_home_0']";
let h0TotalPerfects = "span[id='#h0TotalPerfects']";
let h1PerfectsID = "input[id$='perfects'][id^='id_home_1']";
let h1TotalPerfects = "span[id='#h1TotalPerfects']";

let a0PointsID = "input[id$='point'][id^='id_away_0']";
let a0TotalPoints = "span[id='#a0TotalPoints']";
let a1PointsID = "input[id$='point'][id^='id_away_1']";
let a1TotalPoints = "span[id='#a1TotalPoints']";
let h0PointsID = "input[id$='point'][id^='id_home_0']";
let h0TotalPoints = "span[id='#h0TotalPoints']";
let h1PointsID = "input[id$='point'][id^='id_home_1']";
let h1TotalPoints = "span[id='#h1TotalPoints']";


$(document).ready(function(){

    LoadRunningTotals();
});

$(a0StarsID).blur(function () {
    $(a0TotalStars).html(function () {
        LoadRunningTotals($(a0StarsID), $(a0TotalStars));
    });
})
$(a1StarsID).blur(function () {
    $(a1TotalStars).html(function () {
        LoadRunningTotals($(a1StarsID), $(a1TotalStars));
    });
})
$(h0StarsID).blur(function () {
    $(h0TotalStars).html(function () {
        LoadRunningTotals($(h0StarsID), $(h0TotalStars));
    });
})
$(h1StarsID).blur(function () {
    $(h1TotalStars).html(function () {
        LoadRunningTotals($(h1StarsID), $(h1TotalStars));
    });
})

$(a0PerfectsID).blur(function () {
    $(a0TotalPerfects).html(function () {
        LoadRunningTotals($(a0PerfectsID), $(a0TotalPerfects));
    });
})
$(a1PerfectsID).blur(function () {
    $(a1TotalPerfects).html(function () {
        LoadRunningTotals($(a1PerfectsID), $(a1TotalPerfects));
    });
})
$(h0PerfectsID).blur(function () {
    $(h0TotalPerfects).html(function () {
        LoadRunningTotals($(h0PerfectsID), $(h0TotalPerfects));
    });
})
$(h1PerfectsID).blur(function () {
    $(h1TotalPerfects).html(function () {
        LoadRunningTotals($(h1PerfectsID), $(h1TotalPerfects));
    });
})

$(a0PointsID).blur(function () {
    $(a0TotalPoints).html(function () {
        LoadRunningTotals($(a0PointsID), $(a0TotalPoints));
    });
})
$(a1PointsID).blur(function () {
    $(a1TotalPoints).html(function () {
        LoadRunningTotals($(a1PointsID), $(a1TotalPoints));
    });
})
$(h0PointsID).blur(function () {
    $(h0TotalPoints).html(function () {
        LoadRunningTotals($(h0PointsID), $(h0TotalPoints));
    });
})
$(h1PointsID).blur(function () {
    $(h1TotalPoints).html(function () {
        LoadRunningTotals($(h1PointsID), $(h1TotalPoints));
    });
})


function LoadRunningTotals(sel, tar) {
    var tmp = 0;
    var total = 0;   
    $(sel).each( function(){
        tmp=parseInt($(this).val());
        if (isNaN(tmp)){tmp=0;};
        total = total + tmp;
    })
    $(tar).html(total);  
   }


console.log();


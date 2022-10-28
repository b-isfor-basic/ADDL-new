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

    LoadRunningTotals();

    for (let i = 0; i < statList.length; i++) {
        var sel = statList[i];
        var tar = totalList[i];

        LoadRunningTotals(sel, tar);
    };

});

$(a0StarsID).on("focusout", function () {
    $(a0TotalStars).html(function () {
        LoadRunningTotals($(a0StarsID), $(a0TotalStars));
    });
})
$(a1StarsID).on("focusout", function () {
    $(a1TotalStars).html(function () {
        LoadRunningTotals($(a1StarsID), $(a1TotalStars));
    });
})
$(h0StarsID).on("focusout", function () {
    $(h0TotalStars).html(function () {
        LoadRunningTotals($(h0StarsID), $(h0TotalStars));
    });
})
$(h1StarsID).on("focusout", function () {
    $(h1TotalStars).html(function () {
        LoadRunningTotals($(h1StarsID), $(h1TotalStars));
    });
})

$(a0PerfectsID).on("focusout", function () {
    $(a0TotalPerfects).html(function () {
        LoadRunningTotals($(a0PerfectsID), $(a0TotalPerfects));
    });
})
$(a1PerfectsID).on("focusout", function () {
    $(a1TotalPerfects).html(function () {
        LoadRunningTotals($(a1PerfectsID), $(a1TotalPerfects));
    });
})
$(h0PerfectsID).on("focusout", function () {
    $(h0TotalPerfects).html(function () {
        LoadRunningTotals($(h0PerfectsID), $(h0TotalPerfects));
    });
})
$(h1PerfectsID).on("focusout", function () {
    $(h1TotalPerfects).html(function () {
        LoadRunningTotals($(h1PerfectsID), $(h1TotalPerfects));
    });
})

$(a0PointsID).on("focusout", function () {
    $(a0TotalPoints).html(function () {
        LoadRunningTotals($(a0PointsID), $(a0TotalPoints));
    });
})
$(a1PointsID).on("focusout", function () {
    $(a1TotalPoints).html(function () {
        LoadRunningTotals($(a1PointsID), $(a1TotalPoints));
    });
})
$(h0PointsID).on("focusout", function () {
    $(h0TotalPoints).html(function () {
        LoadRunningTotals($(h0PointsID), $(h0TotalPoints));
    });
})
$(h1PointsID).on("focusout", function () {
    $(h1TotalPoints).html(function () {
        LoadRunningTotals($(h1PointsID), $(h1TotalPoints));
    });
})


function LoadRunningTotals(sel, tar) {
    var tmp = 0;
    var total = 0;
    $(sel).each(function () {
        tmp = parseInt($(this).val());
        if (isNaN(tmp)) { tmp = 0; };
        total = total + tmp;
    })
    $(tar).html(total);
}

function selectConfigs() {
    return {
        show: false,
        filter: '',
        selected: null,
        focusedOptionIndex: null,
        options: null,
        open() {
            this.show = true;
            this.filter = '';
        },
        close() {
            this.show = false;
        },
        toggle() {
            if (this.show) {
                this.close();
            }
            else {
                this.open();
            }
        },
        isOpen() {
            return this.show === true;
        },
        // fetchOptions() {
        //     fetch('http://127.0.0.1/scores/add/?results=5')
        //         .then(response => response.json())
        //         .then(data => this.options = data);
        // },
        // filteredOptions() {
        //     return this.options
        //     ? this.options.results.filter(option => {
        //             return (option.first_name.toLowerCase().indexOf(this.filter) > -1)
        //                 || (option.last_name.toLowerCase().indexOf(this.filter) > -1)
        //                 || (option.email.toLowerCase().indexOf(this.filter) > -1)
        //         })
        //         :{}
        // },
    }
}
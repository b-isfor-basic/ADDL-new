const listPlayerID = ['away_0', 'away_1', 'home_0', 'home_1'];
const listPlayerHyphen = ['away-0', 'away-1', 'home-0', 'home-1'];
const listStats = ['stars', 'perfects', 'point'];
const listAbbrPlayer = ['a0', 'a1', 'h0', 'h1'];
const listTotalStats = ['TotalStars', 'TotalPerfects', 'TotalPoints'];

$(function () {
    const statList = [];
    const totalList = [];

    listAbbrPlayer.forEach(function (player) {
        listTotalStats.forEach(function (stat) {
            const statID = `span[id='#${player}${stat}']`;
            totalList.push(statID);
        });
    });

    listPlayerID.forEach(function (player) {
        listStats.forEach(function (stat) {
            const statID = `input[id$='${stat}'][id^='id_${player}']`;
            statList.push(statID);
        });
    });

    statList.forEach(function (stat) {
        $(stat).on('change', function () {
            LoadRunningTotals(stat, totalList[statList.indexOf(stat)]);
        });
    });
    
    listPlayerHyphen.forEach(function (player) {
        setNames(player);
    });

    LoadRunningTotals();

    for (let i = 0; i < statList.length; i++) {
        const sel = statList[i];
        const tar = totalList[i];
        LoadRunningTotals(sel, tar);
    };
});

function LoadRunningTotals(sel, tar) {
    let tmp = 0;
    let total = 0;
    $(sel).each(function () {
        tmp = Number.parseInt($(this).val(), 10);
        if (isNaN(tmp)) { tmp = 0 }
        total += tmp;
    })
    $(tar).html(total);
}

function selectConfigs() {
    return {
        filter: '',
        show: false,
        options: null,
        selected: null,
        focusedOptionIndex: null,
        selectedOptionID: null,
        open() {
            this.show = true;
            this.filter='';
        },
        close() {
            this.show = false;
            this.filter = this.selectedName();
            this.focusedOptionIndex = this.selected ? this.focusedOptionIndex : null;
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
        selectedName() { 
            return this.selected ? this.selected.first_name + ' ' + this.selected.last_name : this.filter; },
        selectedID() { 
            return this.selectedOptionID ? this.selected.id : this.filter; },
        fetchOptions() {
            fetch('/api/v1/players')
                .then(response => response.json())
                .then(data => this.options = data);
        },
        filteredOptions() {
            return this.options
                ? this.options.filter(option => {
                return (option.first_name.toLowerCase().indexOf(this.filter.toLowerCase()) > -1) 
                || (option.last_name.toLowerCase().indexOf(this.filter.toLowerCase()) > -1)
                || (option.email.toLowerCase().indexOf(this.filter.toLowerCase()) > -1)
            })
            : {}
        },
        onOptionClick(index) {
            this.focusedOptionIndex = index;
            this.selectOption();
        },
        selectOption() {
            if (!this.isOpen()) {
                return;
            }
            this.focusedOptionIndex = this.focusedOptionIndex ?? 0;
            
            const selected = this.filteredOptions()[this.focusedOptionIndex]

            this.selected = selected;
            this.filter = this.selectedName();
            this.close();
        },
        focusPrevOption() {
            if (!this.isOpen()) {
                return;
            }
            const optionsNum = Object.keys(this.filteredOptions()).length - 1;
            if (this.focusedOptionIndex > 0 && this.focusedOptionIndex <= optionsNum) {
                this.focusedOptionIndex--;
            }
            else if (this.focusedOptionIndex == 0) {
                this.focusedOptionIndex = optionsNum;
            }
        },
        focusNextOption() {
            const optionsNum = Object.keys(this.filteredOptions()).length - 1;

            if (!this.isOpen()) {
                this.open();
            }
            if (this.focusedOptionIndex == null || this.focusedOptionIndex == optionsNum) {
                this.focusedOptionIndex = 0;
            }
            else if (this.focusedOptionIndex >= 0 && this.focusedOptionIndex < optionsNum) {
                this.focusedOptionIndex++;
            }
        }
    }
}


function setNames(player)  {
        $(`input[id='id_${player}-player']`).on('focusout', (e) => {
            console.log(this.value);
            console.log(e);
            const text = e.target.value;
            $(`span[name='${listPlayerID[listPlayerHyphen.indexOf(player)]}_player']`).val(text);
        });
    }
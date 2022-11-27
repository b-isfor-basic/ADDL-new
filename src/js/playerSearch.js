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
        selectedName() { return this.selected ? this.selected.first_name + ' ' + this.selected.last_name : this.filter; },
        selectedID() { return this.selected ? this.selected.id : this.filter; },
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
            this.selectedOptionID = this.selectedID();

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
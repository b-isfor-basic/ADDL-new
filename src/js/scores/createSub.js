const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function addSub() {
  return {
    show: false,
    firstName: null,
    lastName: null,
    inputData: null,
    newPlayer: null,
    open() { return this.show = true; },
    close() { return this.show = false; },
    isOpen() { return this.show === true; },
    toggle() { return this.isOpen() ? this.close() : this.open(); },
    async collectData() {
      this.inputData = {
        'first_name': this.$refs.firstName.value,
        'last_name': this.$refs.lastName.value
      };
      console.log('Sending... ', this.inputData)
      return fetch('../../api/v1/players/sub/create/', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken
        },
        mode: 'same-origin',
        body: JSON.stringify(this.inputData),
      })
        .then((response) => response.json())
        .then((data) => this.newPlayer = data)
        .then(() => console.log('Received new player: ', this.newPlayer))
        .then(() => this.close())
        .then(() => this.$refs.select.options[this.$refs.select.options.length] = new Option(this.newPlayer.first_name + ' ' + this.newPlayer.last_name, this.newPlayer.id, selected=true))
        .then(() => this.$refs.select.options[0].removeAttribute('selected'))
        .then(() => this.$refs.select.options[this.$refs.select.options.length - 1].selected = true)
        .then(() => console.log('New player added to select: ', this.newPlayer))
        .catch((error) => console.log('Error: ', error))
    },
    selectedPlayer() {
      if (this.newPlayer) {
        return this.newPlayer.id
      }
    }
  }
}
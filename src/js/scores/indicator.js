const tables = document.querySelectorAll('[id$="Standings"]')

function setIndicator(table) {
    const rows = table.tBodies[0].rows;
    const numTeams = rows.length;

    const prequalifiers = Math.floor((numTeams - 1) * 0.5);
    const wildcards = numTeams - 1;

    let color = '';
    for (let i = 0; i < numTeams; i++) {
        const row = rows[i];

        if (row.rowIndex <= prequalifiers) {
            color = 'emerald'
        } else if (row.rowIndex <= wildcards) {
            color = 'amber'
        } else {
            color = 'rose'
        }

        row.cells[0].children[0].children[0].children[0].classList.add(`bg-${color}-500`)
        row.cells[0].children[0].children[0].children[1].classList.add(`bg-${color}-400`, `outline-${color}-700`)
    }
}

document.addEventListener('DOMContentLoaded', () => {
    tables.forEach(table => setIndicator(table));
});

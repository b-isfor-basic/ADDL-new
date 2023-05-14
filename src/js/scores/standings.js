document.getElementById('search').addEventListener('input', e => {
    let filter = e.target.value.toLowerCase();
    const tables = document.getElementsByTagName('table');

    for (i = 0; i < tables.length; i++) {
        let tbody = tables[i].tBodies[0]
        let rows = Array.from(tbody.rows)

        rows.forEach(tr => {
            let td = tr.getElementsByTagName("td")[1];
            if (td) {
              let txtValue = td.textContent || td.innerText;
              txtValue = txtValue.toLowerCase()
            
              if (filter === '') {
                return tr.classList.remove('highlight')
              } else if (txtValue.indexOf(filter) > -1) {
                return tr.classList.add('highlight')
              } else {
                return tr.classList.remove('highlight')
              }
            } 
        });
    }

});


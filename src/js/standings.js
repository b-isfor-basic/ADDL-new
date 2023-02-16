import jQuery from "jquery";

$(document).ready(function() {

    // standings table search
    const tables = Array.from(Array(10).keys())

    $('#table-search').on('keyup', function() {
        
        let value = $(this).val().toLowerCase();
        
        tables.forEach((table) => {
            $(`#standings-table-${table + 1}.tbody.tr`).filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
    });
});
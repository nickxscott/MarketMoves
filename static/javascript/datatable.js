

$(document).ready( function () {
    $('table.display').DataTable({
    fixedHeader: {
        header: true,
        footer: true
    },
    paging: true,
    scrollCollapse: true,
    scrollY: '40vh',
    scrollX: true,
    scroller: true,
    dom: 'Bfrtip',
    buttons: ['pageLength', 'copy', 'csv', 'excel' ]
});
} );



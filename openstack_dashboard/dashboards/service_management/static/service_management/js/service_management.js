/* Additional JavaScript for service_management. */
$('#service_select_chart').on('change', function () {
    // var container_list_form = $("#container_list_form").empty();
    var num_container = $(this).val();
    container_line_chart.clear_chart_list();
});
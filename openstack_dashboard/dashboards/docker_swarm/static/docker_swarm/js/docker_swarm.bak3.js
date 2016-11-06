/* Additional JavaScript for chart_dashboard. */
// setup  ajax and handle select_date event

container_line_chart = {
    chart_timers: [],
    setup_line_chart: function (selector) {
        var self = this;
        $(selector).each(function () {
            var chart = $(this);
            // this.container_list_url = chart.data('container-list-url');
            // this.container_detail_url = chart.data('container-detail-url');
            self.update_charts(chart);

        });
    },
    update_charts: function (chart) {
        // console.log(chart);
        container_url_list = chart.data('container-list-url');
        console.log(container_url_list);
        $.getJSON(container_url_list, function (data) {
            data_list = data;
            $.when.apply($, data_list.map(function (container_id) {
                var container_detail_url = chart.data('container-detail-url') + "?id=" + container_id.id;
                return $.ajax(container_detail_url);
            })).done(function () {
                var results = [];
                // each argument is of this form [data, statusText, jqXHR]
                for (var i = 0; i < arguments.length; i++) {
                    results.push(arguments[i][0]);
                }

                var container_colors = 
                ["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"];
                for (var i = 0; i < results.length; i++) {
                    // console.log(results[i]);
                    results[i].value.forEach(function (d) {
                        d.x = new Date(d.x);
                        d.y = d.y;
                    });
                    results[i].color = container_colors[i]
                }
                // Set the dimensions of the canvas / graph
                var margin = { top: 30, right: 20, bottom: 30, left: 50 },
                    width = 1000 - margin.left - margin.right,
                    height = 500 - margin.top - margin.bottom;
                // Set the ranges
                var x = d3.time.scale().range([0, width]);
                var y = d3.scale.linear().range([height, 0]);
                // Define the axes
                var xAxis = d3.svg.axis().scale(x)
                    .orient("bottom").ticks(5).tickFormat(d3.time.format("%H:%M:%Ss"));
                var yAxis = d3.svg.axis().scale(y)
                    .orient("left").ticks(10);
                // Define the line
                var usage_line = d3.svg.line()
                    .interpolate("basis")
                    .x(function (d) {
                        console.log(x(d.x));
                        return x(d.x);
                    })
                    .y(function (d) {
                        return y(d.y);
                    });
                // console.log(chart);
                // Adds the svg canvas
                var svg = d3.select(chart.get(0))
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");
                // Scale the range of the data
                var combine_data = [];
                for (var i = 0; i < results.length; i++) {
                    for (var j = 0; j < results[i].value.length; j++) {
                        combine_data.push(results[i].value[j]);
                    }
                }
                x.domain([d3.min(combine_data, function (d) {
                    return d.x;
                }), d3.max(combine_data, function (d) {
                    return d.x;
                })]);
                y.domain([0, d3.max(combine_data, function (d) {
                    return d.y;
                }) * 1.5]);
                var k = 0;
                results.forEach(function (d) {
                    //console.log(usage_line(d.value));
                    svg.append("path")
                        .attr("class", "line")
                        .attr('stroke', d.color)
                        .attr("d", usage_line(d.value));
                    k += 1;
                });
                console.log(xAxis);
                // Add the X Axis
                svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);
                // Add the Y Axis
                svg.append("g")
                    .attr("class", "y axis")
                    .call(yAxis)
                    .append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", 6)
                    .attr("dy", ".71em")
                    .style("text-anchor", "end")
                    .text(results[0].unit);

                var legend_elements = chart.parent().find('.legend');
                console.log(legend_elements);
                var svg_legend = d3.select(legend_elements.get(0))
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", 60)
                    .append("g")
                    .attr("transform",
                    "translate('5,5')");

                var legend = svg_legend.selectAll(".legend")
                    .data(results)
                    .enter().append("g")
                    .attr("class", "legend")
                    .attr("transform", function (d, i) {
                        return "translate(" + i * 150 + ",0)";
                    });

                legend.append("rect")
                    .attr("x", 100 - 18)
                    .attr("width", 18)
                    .attr("height", 18)
                    .style("fill", function (d) {
                        return d.color;
                    });

                legend.append("text")
                    .attr("x", 100 - 24)
                    .attr("y", 9)
                    .attr("dy", ".35em")
                    .style("text-anchor", "end")
                    .text(function (d) {
                        //return d.name;
                        d_names = d.name.split(".");
                        console.log(d_names);
                        return_name = d_names[0];
                        for (var i = 1; i < d_names.length - 1; i++) {
                            return_name += d_names[i];
                        }
                        return return_name;
                    });
                // all data is now in the results array in order
            });
        }).fail(function (jqXHR) {
            if (jqXHR.status == 404) {
                alert("404 Not Found");
            } else {
                alert("Other non-handled error type");
            }
        });

    },
    set_realtime_chart: function (chart) {

    }

};

function LineChart(selector) {
    this.chart_selector = selector;
    this.containers = [];
    this.container_colors = ["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"];
    this.get_container_list = function () {
        container_url_list = $(this.chart_selector).data('container-list-url');
        $.getJSON(container_url_list, function (data) {
            this.containers = data;
        });
    };
    this.create_chart = function () {
        $.when(this.get_container_list).done(function () {
            $.when.apply($, data_list.map(function (container_id) {
                var container_detail_url = $(this.chart_selector).data('container-detail-url') + "?id=" + container_id.id;
                return $.ajax(container_detail_url);
            })).done(function () {
                var results = [];
                for (var i = 0; i < arguments.length; i++) {
                    results.push(arguments[i][0]);
                }
                for (var i = 0; i < results.length; i++) {
                    results[i].value.forEach(function (d) {
                        d.x = new Date(d.x);
                        d.y = d.y;
                    });
                    results[i].color = this.container_colors[i];
                }
                var margin = { top: 30, right: 20, bottom: 30, left: 50 },
                    width = 1000 - margin.left - margin.right,
                    height = 500 - margin.top - margin.bottom;
                // Set the ranges
                var x = d3.time.scale().range([0, width]);
                var y = d3.scale.linear().range([height, 0]);
                // Define the axes
                var xAxis = d3.svg.axis().scale(x)
                    .orient("bottom").ticks(5).tickFormat(d3.time.format("%H:%M:%Ss"));
                var yAxis = d3.svg.axis().scale(y)
                    .orient("left").ticks(10);
                // Define the line
                var usage_line = d3.svg.line()
                    .interpolate("basis")
                    .x(function (d) {
                        return x(d.x);
                    })
                    .y(function (d) {
                        return y(d.y);
                    });
                // console.log(chart);
                // Adds the svg canvas
                var svg = d3.select($(this.chart_selector).get(0))
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");
                // Scale the range of the data
                var combine_data = [];
                for (var i = 0; i < results.length; i++) {
                    for (var j = 0; j < results[i].value.length; j++) {
                        combine_data.push(results[i].value[j]);

                    }
                }
                x.domain([d3.min(combine_data, function (d) {
                    return d.x;
                }), d3.max(combine_data, function (d) {
                    return d.x;
                })]);
                y.domain([0, d3.max(combine_data, function (d) {
                    return d.y;
                }) * 1.5]);
                var k = 0;
                results.forEach(function (d) {
                    svg.append("path")
                        .attr("class", "line")
                        .attr('stroke', d.color)
                        .attr("d", usage_line(d.value));
                    k += 1;
                });
                // Add the X Axis
                svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);
                // Add the Y Axis
                svg.append("g")
                    .attr("class", "y axis")
                    .call(yAxis)
                    .append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", 6)
                    .attr("dy", ".71em")
                    .style("text-anchor", "end")
                    .text(results[0].unit);

                var legend_elements = $(this.chart_selector).parent().find('.legend');
                var svg_legend = d3.select(legend_elements.get(0))
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", 60)
                    .append("g")
                    .attr("transform",
                    "translate('5,5')");

                var legend = svg_legend.selectAll(".legend")
                    .data(results)
                    .enter().append("g")
                    .attr("class", "legend")
                    .attr("transform", function (d, i) {
                        return "translate(" + i * 150 + ",0)";
                    });

                legend.append("rect")
                    .attr("x", 100 - 18)
                    .attr("width", 18)
                    .attr("height", 18)
                    .style("fill", function (d) {
                        return d.color;
                    });

                legend.append("text")
                    .attr("x", 100 - 24)
                    .attr("y", 9)
                    .attr("dy", ".35em")
                    .style("text-anchor", "end")
                    .text(function (d) {
                        //return d.name;
                        d_names = d.name.split(".");
                        console.log(d_names);
                        return_name = d_names[0];
                        for (var i = 1; i < d_names.length - 1; i++) {
                            return_name += d_names[i];
                        }
                        return return_name;
                    });
                // all data is now in the results array in order
            });
        });
    };
    this.update_charts = function () {
        container_url_list = $(this.chart_selector).data('container-list-url');
        console.log(container_url_list);
        $.getJSON(container_url_list, function (data) {
            this.containers = data;

        }).fail(function (jqXHR) {
            if (jqXHR.status == 404) {
                alert("404 Not Found");
            } else {
                alert("Other non-handled error type");
            }
        });

    }

}
container_line_chart.setup_line_chart('div[data-chart-type="container_line_chart"]');

$(document).ready(function () {
    // Handle chart generation
    $("#generate_chart").click(function (e) {
        e.preventDefault();
        const chartType = $("#chart_type").val();
        if (!chartType) {
            alert("Please select a chart type!");
            return;
        }
        $.ajax({
            url: "/generate-chart",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ chart_type: chartType }),
            success: function (response) {
                $("#chart_container").html(`
                    <img src="${response.chart_img}" alt="Chart Visualization" class="img-fluid">
                    <div class="mt-3">
                        <label for="download_format" class="form-label">Save as:</label>
                        <select id="download_format" class="form-select d-inline-block w-auto">
                            <option value="png">PNG</option>
                            <option value="jpg">JPG</option>
                            <option value="pdf">PDF</option>
                        </select>
                        <button id="download_chart" class="btn btn-primary">Download Chart</button>
                    </div>
                `);
            },
            error: function () {
                alert("An error occurred while generating the chart.");
            },
        });
    });

    // Handle chart download
    $(document).on("click", "#download_chart", function () {
        const format = $("#download_format").val();
        if (!format) {
            alert("Please select a format!");
            return;
        }
        window.location.href = `/download-chart/${format}`;
    });

    // Handle Dark Mode Toggle
    $("#dark_mode_toggle").click(function () {
        $("body").toggleClass("dark-mode");
        $(this).text($("body").hasClass("dark-mode") ? "Light Mode" : "Dark Mode");
    });
});

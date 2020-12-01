function readSingleFile(evt) {
  var f = evt.target.files[0];
  if (f) {
    var r = new FileReader();
    var output = [];
    r.onload = function(e) {
        var contents = e.target.result;
        // document.write("File Uploaded! <br />" + "name: " + f.name + "<br />" + "type: " + f.type + "<br />" + "size: " + f.size + " bytes <br />");

        // var lines = contents.split("\n"), output = "";

        ProcessExcel(contents);

        // var columns = [];
        // var data = [];
        //
        // var lines = contents.split("\n");
        // // add columns
        // lines[0].split(",").forEach(column => columns.push({"data": column}));
        // // add data
        // for (var i=1; i<lines.length; i++) {
        //   var newData = {};
        //   var dataPoints = lines[i].split(",");
        //   // for (var j=0; j<dataPoints.length; j++) {
        //   //   newData[columns[j]["data"]] = dataPoints[j];
        //   // }
        //   data.push(dataPoints);
        // }
        //
        // var table = $('#dataTable').DataTable({"columns": columns});
        // table.rows.add(data[0]).draw();
    }
    r.readAsBinaryString(f);
  } else {
    alert("Failed to load file");
  }
}

function ProcessExcel(data) {
    //Read the Excel File data.
    var workbook = XLSX.read(data, {
        type: 'binary'
    });

    //Fetch the name of First Sheet.
    var firstSheet = workbook.SheetNames[0];

    //Read all rows from First Sheet into an JSON array.
    var excelRows = XLSX.utils.sheet_to_row_object_array(workbook.Sheets[firstSheet]);

    // Display data
    displayData("input", excelRows, firstSheet);

    var postData = { mrr: excelRows };
    console.log(postData);
    console.log(JSON.stringify(postData));

    // Run python script analysis
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/rev_analysis",
        contentType: 'application/json',
        data: JSON.stringify(postData),
        success: callbackFunc
    });

    function callbackFunc(response) {
        // do something with the response
        var excelRows = JSON.parse(response);
        console.log(excelRows);
        displayData("output", excelRows, "MRR by Customer");
    }
};

function displayData(type, data, firstSheet) {
    // first line is thead
    var output = "<thead>";
    output += "<tr><th>" + Object.keys(data[0]).join("</th><th>") + "</th></tr>";
    output += "</thead>";

    // subsequent lines are tbody
    output += "<tbody>";
    for (var i=1; i<data.length; i++){
      output += "<tr><td>" + Object.values(data[i]).join("</td><td>") + "</td></tr>";
    }
    output += "</tbody>";

    // wrap entire table
    output = '<table class="table table-bordered" id="dataTable" width="100%" cellspacing="0">' + output + "</table>";
    // document.write(output);

    if (type == 'input') {
      $("#input-file-pagination a").first().html(firstSheet);
      $("#input-table-container").html(output);
    } else {
      $("#output-file-pagination a").first().html(firstSheet);
      $("#output-table-container").html(output);
    }
}

document.getElementById('file').addEventListener('change', readSingleFile);

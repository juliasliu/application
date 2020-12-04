function readSingleFile(evt) {
  var f = evt.target.files[0];
  if (f) {
    var r = new FileReader();
    var output = [];
    r.onload = function(e) {
        var contents = e.target.result;

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

  // Name and rows from each sheet
  var sheets = {};
  workbook.SheetNames.forEach(sheetName => sheets[sheetName] = XLSX.utils.sheet_to_row_object_array(workbook.Sheets[sheetName]));
  console.log(sheets);

  // Display data
  displayData("input", sheets);

  console.log(JSON.stringify(sheets));

  // Run python script analysis
  $.ajax({
      type: "POST",
      url: "http://127.0.0.1:5000/analysis",
      contentType: 'application/json',
      data: JSON.stringify(sheets),
      success: callbackFunc
  });

  function callbackFunc(response) {
      // do something with the response
      console.log(JSON.parse(response));
      displayData("output", JSON.parse(response));
  }
};

function displayData(type, sheets) {

  for (sheet in sheets) {
    // first line is thead
    var output = "<thead>";
    output += "<tr><th>" + Object.keys(sheets[sheet][0]).join("</th><th>") + "</th></tr>";
    output += "</thead>";

    // subsequent lines are tbody
    output += "<tbody>";
    for (var i=0; i<sheets[sheet].length; i++){
      output += "<tr><td>" + Object.values(sheets[sheet][i]).join("</td><td>") + "</td></tr>";
    }
    output += "</tbody>";

    var sheetNameFiltered = sheet.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');

    // wrap entire table
    output = '<table class="table table-sm table-bordered table-hover hidden" id="' + sheetNameFiltered + '" width="100%" cellspacing="0">' + output + "</table>";

    // add table and pagination link
    if (type == 'input') {
      $("#input-table-container").append(output);
      $("#input-file-pagination ul").append('<li class="page-item" id="' + sheetNameFiltered + '"><a class="page-link" onclick="sheetTabClicked(\'input\', \'' + sheet + '\')">' + sheet + '</a></li>');
    } else if (type == 'output') {
      $("#output-table-container").append(output);
      $("#output-file-pagination ul").append('<li class="page-item" id="' + sheetNameFiltered + '"><a class="page-link" onclick="sheetTabClicked(\'output\', \'' + sheet + '\')">' + sheet + '</a></li>');
    }
  }

  // show first sheet by default
  if (type == 'input') {
    $('#input-table-container .table').first().removeClass('hidden');
    $('#input-file-pagination ul .page-item').first().addClass('active');
  } else if (type == 'output') {
    $('#output-table-container .table').first().removeClass('hidden');
    $('#output-file-pagination ul .page-item').first().addClass('active');
  }
}

function sheetTabClicked(type, sheetName) {
  var sheetNameFiltered = sheetName.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');

  if (type == 'input') {
    $('#input-table-container .table').addClass('hidden');
    $('#input-file-pagination ul .page-item').removeClass('active');
  } else if (type == 'output') {
    $('#output-table-container .table').addClass('hidden');
    $('#output-file-pagination ul .page-item').removeClass('active');
  }

  $('.table#' + sheetNameFiltered).removeClass("hidden");
  $('.page-item#' + sheetNameFiltered).addClass("active");
}

document.getElementById('file').addEventListener('change', readSingleFile);

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
  var is_dict = {}
  var bs_dict = {}
  var cf_dict = {}
  for (sheet_name in sheets) {
    var re = sheet_name.match(/\.*(\d+)/g)
    if (re) {
      if (sheet_name.includes("IS"))
          is_dict[sheet_name] = sheets[sheet_name]
      if (sheet_name.includes("BS"))
          bs_dict[sheet_name] = sheets[sheet_name]
      if (sheet_name.includes("CF"))
          cf_dict[sheet_name] = sheets[sheet_name]
    }
  }
  var full_sheet_data = {
    "ARR by Customer": {"ARR by Customer": sheets["ARR by Customer"]},
    "IS": is_dict,
    "BS": bs_dict,
    "CF": cf_dict
  }

  // Display data
  displayData("input", full_sheet_data);

  console.log(JSON.stringify(full_sheet_data));

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

function displayData(type, categories) {

  for (category in categories) {

    var categoryNameFiltered = category.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');

    var dropdown_btn =
    '<div class="btn-group" role="group">' +
      '<div class="dropdown page-item">' +
        '<button id="' + categoryNameFiltered + '" class="btn btn-outline-secondary dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
          category + '<span class="caret"></span>' +
        '</button>' +
        '<div class="dropdown-menu" id="' + categoryNameFiltered + '" aria-labelledby="' + categoryNameFiltered + '">'

    var sheets = categories[category];
    for (sheet in sheets) {
      // first line is thead
      // be able to hide columns
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

      // add table and pagination link dropdown
      $("#"+type+"-table-container").append(output);
      dropdown_btn +=
        '<li id="' + sheetNameFiltered + '">'+
          '<a class="dropdown-item" onclick="sheetTabClicked(\'' + type + '\', \'' + category + '\', \'' + sheet + '\')">' + sheet + '</a>'+
        '</li>'
    }
    dropdown_btn +=
        '</div>' +
      '</div>' +
    '</div>'
    $("#"+type+"-file-pagination").append(dropdown_btn);
    $('.dropdown-menu#'+categoryNameFiltered+' li').first().addClass("active");
  }

  // show first sheet by default
  $("#"+type+"-table-container .table").first().removeClass('hidden');
  $("#"+type+"-file-pagination .btn-group .dropdown .btn").first().addClass('active');
}

function sheetTabClicked(type, categoryName, sheetName) {
  var categoryNameFiltered = categoryName.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
  var sheetNameFiltered = sheetName.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');

  $("#"+type+"-table-container .table").addClass('hidden');
  $("#"+type+"-file-pagination .btn-group .dropdown .btn").removeClass('active');
  $('.dropdown-menu#'+categoryNameFiltered+' li').removeClass('active');

  $('.table#' + sheetNameFiltered).removeClass("hidden");
  $('.btn.dropdown-toggle#' + categoryNameFiltered).addClass("active");
  $('.dropdown-menu#'+categoryNameFiltered+' li#' + sheetNameFiltered).addClass("active");
}

document.getElementById('file').addEventListener('change', readSingleFile);

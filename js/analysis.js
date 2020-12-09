function readSingleFile(evt) {
  var r = new FileReader();
  var f = evt.target.files[0];
  if (f) {
    r.onload = function(e) {
        var contents = e.target.result;

        // Parse sheets in Excel spreadsheet file
        var processed = ProcessExcel(contents);
        var sheets = processed[0];
        var company_dict = {};
        company_dict[f.name.split(".")[0]] = sheets;
        var data_dict = processed[1];
        var company_data_dict = {};
        company_data_dict[f.name.split(".")[0]] = data_dict;

        try {
          // Display data
          displayData("input", company_data_dict, false);

          // Run python script analysis
          $.ajax({
              type: "POST",
              url: "http://127.0.0.1:5000/analysis",
              contentType: 'application/json',
              data: JSON.stringify(company_dict),
              success: successFunc,
              error: errorFunc
          });
        } catch(err) {
          errorFunc(err);
        }

        function successFunc(response) {
            // do something with the response
            var res_json = JSON.parse(response);
            displayData("output", res_json, false);
        }

        function errorFunc(error) {
          alert("Failed to complete analysis. Make sure to check that your input file is in the correct format.");
        }
    }
    r.readAsBinaryString(f);
  } else {
    alert("Failed to load file");
  }
}

function readMultipleFiles(evt) {
  var r = new FileReader();
  var files = evt.target.files;
  var company_dict = {};
  function readFile(index) {
    if (index >= files.length) {
      // Run python script benchmarking analysis
      $.ajax({
          type: "POST",
          url: "http://127.0.0.1:5000/benchmark",
          contentType: 'application/json',
          data: JSON.stringify(company_dict),
          success: successFunc,
          error: errorFunc
      });

      function successFunc(response) {
          // do something with the response
          var res_json = JSON.parse(response);
          displayCompanyCards(res_json);
          displayData("output", res_json, true);
      }

      function errorFunc(error) {
        alert("Failed to complete analysis. Make sure to check that your input files are in the correct format.");
      }
    } else {
      var f = files[index];
      r.onload = function(e) {
          var contents = e.target.result;
          // Parse sheets in Excel spreadsheet file
          var sheets = ProcessExcel(contents)[0];
          company_dict[f.name.split(".")[0]] = sheets;
          readFile(index + 1);
      }
      r.readAsBinaryString(f);
    }
  }
  readFile(0);
}

function ProcessExcel(data) {
  //Read the Excel File data.
  var workbook = XLSX.read(data, {
      type: 'binary'
  });

  // Name and rows from each sheet
  var sheets = {};
  workbook.SheetNames.forEach(sheetName => sheets[sheetName] = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName], {defval: ""}));
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
  var data_dict = {
    "ARR by Customer": {"ARR by Customer": sheets["ARR by Customer"]},
    "IS": is_dict,
    "BS": bs_dict,
    "CF": cf_dict
  }

  return [sheets, data_dict];
};

function displayData(type, companies, isBenchmark) {
  for (company in companies) {
    if (isBenchmark && company == "Benchmark" || !isBenchmark) {
      var categories = companies[company];
      for (category in categories) {
        if (category != "start_year" && category != "end_year") {
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
      }
    }
  }

  // show first sheet by default
  $("#"+type+"-table-container .table").first().removeClass('hidden');
  $("#"+type+"-file-pagination .btn-group .dropdown .btn").first().addClass('active');
}

function displayCompanyCards(companies) {
  for (company in companies) {
    if (company != "Benchmark") {
      var companyCard =
      '<div class="col-xl-3 col-md-4">' +
          '<div class="card mb-4">' +
              '<div class="card-body">' +
                '<h5>' + company + '</h5>' +
                '<div>' + companies[company]["start_year"] + '-' + companies[company]["end_year"] + '</div>' +
              '</div>' +
              '<div class="card-footer d-flex align-items-center justify-content-between">' +
                  '<a class="small stretched-link" href="#">View Details</a>' +
                  '<div class="small"><i class="fas fa-angle-right"></i></div>' +
              '</div>' +
          '</div>' +
      '</div>'
      $('#company-card-list').append(companyCard);
    }
  }
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

function toggleCardBodyDisplay(type) {
  $('#'+type+'-card-body').toggleClass("hidden");
  if ($('#'+type+'-card-body').hasClass("hidden")) {
    $('#'+type+'-toggle-button').html("Show");
  } else {
    $('#'+type+'-toggle-button').html("Hide");
  }
}

if (document.getElementById('file')) document.getElementById('file').addEventListener('change', readSingleFile);
if (document.getElementById('files')) document.getElementById('files').addEventListener('change', readMultipleFiles);

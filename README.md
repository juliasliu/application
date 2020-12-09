# Application

## File directory structure
- `css/`: CSS styles for the web app frontend
  - `dashboard.css`: raw input data for Icertis
  - `styles.css`: preloaded stylesheet from the Start Bootstrap dashboard template
- `flaskr/`: Python server code for receiving requests from JS frontend and running Pandas scripts for data analysis
  - `__init__.py`: raw input data for Icertis
  - `rev_analysis.py`: Rev Analysis script
  - `cohort_analysis.py`: Cohort Analysis script
  - `dashboard.py`: Dashboard script
  - `cac.py`: CAC script
  - `payback_chart.py`: Payback Chart script
  - `rev_charts.py`: Rev Charts script
  - `benchmark.py`: Benchmark script for multiple companies
  - `helpers.py`: helper methods for Python scripts
- `inputs/`: example company raw input data in the form of Excel spreadsheets
  - `Icertis.xlsx`: raw input data for Icertis
  - `Quantum Metric.xlsx`: raw input data for Quantum Metric
- `js/`: JS scripts for the website frontend
  - `analysis.js`: for uploading raw input data and displaying data and graphs in HTML pages
  - `scripts.js`: preloaded script from the Start Bootstrap dashboard template
- `pages/`: HTML pages for the website frontend
  - `company.html`: template for each individual company you upload
- `venv/`: a Python virtual environment where Flask and other dependencies are installed

## Running the app locally on your computer
1. Clone the repository: `git clone https://github.com/juliasliu/application.git`
2. Activate the Python venv environment: `. venv/bin/activate`
3. Set environment variables: `export FLASK_APP=flaskr`, `export FLASK_ENV=development`
4. Install Python modules: `pip install`
5. Run the Flask server: `flask run`

## Todo features
- [ ] Make interactive charts & graphs using the [Chart.js third-party plugin](https://www.chartjs.org/docs/latest/)
- [ ] Show loading spinner overlay when frontend is waiting for backend scripts to finish
- [ ] Connect the website to a SQLite backend database with Flask using [the tutorial](https://flask.palletsprojects.com/en/1.1.x/tutorial/database/)
- [ ] Upload and save companies to the database, and route the company cards on the Dashboard page to individual company pages (also located in the sidebar dropdown nav)
- [ ] Individual company pages should show uploaded input data, output data, and charts. Data can be updated by uploading a newer version of the input spreadsheet and saving it to the database.
- [ ] Implement Export to Excel spreadsheet functionality for the output data tables and charts
- [ ] Show specific error messages for invalid data inputs
- [ ] Implement authentication functionality, i.e. Register, Login for users within organizations
- [ ] Add more display flexibility for data tables, i.e. search bar, filter, sort, hide columns
- [ ] Accept each type of financial statement input all in one tab instead of spread out across different years

## Contributing to the code
- For more specific function descriptions, see the docstrings in the code

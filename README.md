# Application

## File directory structure
 - `css/`: styles for the web app frontend
 - `flaskr/`: server code for receiving requests from JS frontend and running Python/Pandas scripts for data analysis
 - `inputs/`: sample company input data Excel spreadsheets
 - `js/`: frontend scripts for uploading Excel spreadsheets and displaying data and graphs
 - `pages/`: web app frontend HTML pages
 - `venv/`: a Python virtual environment where Flask and other dependencies are installed

## Running the app locally on your computer
1. Clone the repository: `git clone https://github.com/juliasliu/application.git`
2. Activate the Python venv environment: `. venv/bin/activate`
3. Set environment variables: `export FLASK_APP=flaskr`, `export FLASK_ENV=development`
4. Install Python modules: `pip install`
5. Run the Flask server: `flask run`

## Contributing to the code
 - Make a pull request
